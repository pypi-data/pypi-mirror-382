use crate::tos_client::InnerTosClient;
use crate::tos_error::map_tos_error;
use async_channel::{Receiver, Sender};
use futures_util::future::join_all;
use pyo3::{pyclass, pymethods, PyRefMut, PyResult};
use std::collections::HashMap;
use std::sync::atomic::{AtomicI8, AtomicIsize, Ordering};
use std::sync::Arc;
use tokio::runtime::{Handle, Runtime};
use tokio::sync::{AcquireError, Mutex, Notify, RwLock, Semaphore, SemaphorePermit};
use tokio::task::JoinHandle;
use tracing::log::{error, info};
use tracing::warn;
use ve_tos_rust_sdk::asynchronous::multipart::MultipartAPI;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::enumeration::StorageClassType;
use ve_tos_rust_sdk::error::TosError;
use ve_tos_rust_sdk::multipart::{
    AbortMultipartUploadInput, CompleteMultipartUploadInput, CreateMultipartUploadInput,
    UploadPartFromBufferInput, UploadedPart,
};
use ve_tos_rust_sdk::object::PutObjectFromBufferInput;

const DEFAULT_PART_SIZE: isize = 8 * 1024 * 1024;
const DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT: isize = 50 * 1024 * 1024;
const DEFAULT_UPLOAD_PART_CONCURRENCY: isize = 20;
const MAX_UPLOAD_PART_SIZE: isize = 5 * 1024 * 1024 * 1024;
const MAX_PART_NUMBER: isize = 10000;
const OTHER_MU_KICK_OFF: i8 = 1;
const RELEASE_MU_KICK_OFF: i8 = 2;

#[pyclass(name = "WriteStream")]
pub struct WriteStream {
    object_writer: Arc<ObjectWriter>,
    runtime: Arc<Runtime>,
    offset: isize,
    #[pyo3(get)]
    bucket: String,
    #[pyo3(get)]
    key: String,
    #[pyo3(get)]
    storage_class: Option<String>,
}

#[pymethods]
impl WriteStream {
    pub fn write(mut slf: PyRefMut<'_, Self>, data: &[u8]) -> PyResult<isize> {
        let writer = slf.object_writer.clone();
        let runtime = slf.runtime.clone();
        let offset = slf.offset;
        match slf
            .py()
            .allow_threads(|| runtime.block_on(async move { writer.write(data, offset).await }))
        {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(written) => {
                slf.offset += written;
                Ok(written)
            }
        }
    }

    pub fn close(slf: PyRefMut<'_, Self>) -> PyResult<()> {
        let writer = slf.object_writer.clone();
        let runtime = slf.runtime.clone();
        match slf
            .py()
            .allow_threads(|| runtime.block_on(async move { writer.release().await }))
        {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(_) => Ok(()),
        }
    }
}

impl WriteStream {
    pub(crate) async fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
        part_size: isize,
    ) -> Result<Self, TosError> {
        let mut part_size = part_size;
        if part_size <= 0 {
            part_size = DEFAULT_PART_SIZE;
        } else if part_size > MAX_UPLOAD_PART_SIZE {
            part_size = MAX_UPLOAD_PART_SIZE;
        }

        let _bucket = bucket.clone();
        let _key = key.clone();
        let _storage_class = storage_class.clone();

        let object_writer =
            ObjectWriter::new(client, _bucket, _key, _storage_class, part_size).await?;
        Ok(Self {
            object_writer: Arc::new(object_writer),
            runtime,
            offset: 0,
            bucket,
            key,
            storage_class,
        })
    }

    fn do_write(&mut self, data: &[u8]) -> Result<isize, TosError> {
        let writer = self.object_writer.clone();
        let offset = self.offset;
        match self
            .runtime
            .block_on(async move { writer.write(data, offset).await })
        {
            Err(ex) => Err(ex),
            Ok(written) => {
                self.offset += written;
                Ok(written)
            }
        }
    }

    fn do_close(&mut self) -> Result<(), TosError> {
        let writer = self.object_writer.clone();
        self.runtime.block_on(async move { writer.release().await })
    }
}

struct ObjectWriter {
    ctx: Mutex<(ObjectUploader, isize)>,
    closed: Arc<AtomicI8>,
}

impl ObjectWriter {
    async fn new(
        client: Arc<InnerTosClient>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
        part_size: isize,
    ) -> Result<Self, TosError> {
        let wp = Arc::new(WriteParam {
            bucket,
            key,
            storage_class,
        });
        let ou = ObjectUploader::new(client, wp, part_size, 0, Arc::new(AtomicI8::new(0))).await?;
        Ok(Self {
            ctx: Mutex::new((ou, 0)),
            closed: Arc::new(AtomicI8::new(0)),
        })
    }

    async fn write(&self, data: &[u8], offset: isize) -> Result<isize, TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            warn!("write on closed object writer");
            return Err(TosError::TosClientError {
                message: "write on closed object writer".to_string(),
                cause: None,
            });
        }

        let mut ctx = self.ctx.lock().await;
        if offset != ctx.1 {
            warn!(
                "unexpected start to write, expect [{}], actual [{}]",
                ctx.1, offset
            );
            return Err(TosError::TosClientError {
                message: format!(
                    "unexpected start to write, expect [{}], actual [{}]",
                    ctx.1, offset
                ),
                cause: None,
            });
        }

        if ctx.0.is_aborted() {
            warn!("write on aborted object writer");
            return Err(TosError::TosClientError {
                message: "write on aborted object writer".to_string(),
                cause: None,
            });
        }

        if data.is_empty() {
            return Ok(0);
        }

        if ctx.0.is_sealed() {
            warn!("write on sealed object writer");
            return Err(TosError::TosClientError {
                message: "write on sealed object writer".to_string(),
                cause: None,
            });
        }

        if ctx.1 + data.len() as isize > ctx.0.max_size {
            warn!("exceed the max size, max size is [{}]", ctx.0.max_size);
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", ctx.0.max_size),
                cause: None,
            });
        }

        match ctx.0.write(data).await {
            Err(ex) => Err(ex),
            Ok(written) => {
                ctx.1 += written;
                Ok(written)
            }
        }
    }

    async fn flush(&self) -> Result<(), TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            return Err(TosError::TosClientError {
                message: "flush on closed object writer".to_string(),
                cause: None,
            });
        }

        let mut ctx = self.ctx.lock().await;
        ctx.0.flush(true).await
    }

    async fn fsync(&self) -> Result<(), TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            return Err(TosError::TosClientError {
                message: "fsync on closed object writer".to_string(),
                cause: None,
            });
        }
        let mut ctx = self.ctx.lock().await;
        ctx.0.fsync().await
    }

    async fn release(&self) -> Result<(), TosError> {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            let mut ctx = self.ctx.lock().await;
            match ctx.0.release().await {
                Err(ex) => return Err(ex),
                Ok(_) => {
                    if !ctx.0.is_created() {
                        return ctx.0.put_empty_object().await;
                    }
                }
            }
        }
        Ok(())
    }
}

struct WriteParam {
    bucket: String,
    key: String,
    storage_class: Option<String>,
}

struct ObjectUploader {
    next_write_offset: isize,
    uc: Arc<UploadContext>,
    current: Option<Part>,
    part_size: isize,
    max_size: isize,
    dp: Arc<Dispatcher>,
    st: Arc<Store>,
    ta: Arc<TokenAcquirer>,
    wait_dispatch: Option<JoinHandle<()>>,
    wait_execute: Option<JoinHandle<()>>,
    mu_ctx: Arc<MultipartUploadContext>,
}

impl ObjectUploader {
    async fn new(
        client: Arc<InnerTosClient>,
        wp: Arc<WriteParam>,
        part_size: isize,
        next_write_offset: isize,
        created: Arc<AtomicI8>,
    ) -> Result<Self, TosError> {
        let max_size = part_size * MAX_PART_NUMBER;
        if next_write_offset >= max_size {
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", max_size),
                cause: None,
            });
        }

        let mut ou = Self {
            next_write_offset,
            uc: Arc::new(UploadContext::new(created, wp, client)),
            current: None,
            part_size,
            max_size,
            dp: Arc::new(Dispatcher::new(calc_queue_size(part_size))),
            st: Arc::new(Store::new(part_size, next_write_offset)),
            ta: Arc::new(TokenAcquirer::new(DEFAULT_UPLOAD_PART_CONCURRENCY)),
            wait_dispatch: None,
            wait_execute: None,
            mu_ctx: Arc::new(MultipartUploadContext::new()),
        };
        ou.dispatch().await;
        ou.execute().await;
        Ok(ou)
    }

    async fn reset(&mut self) -> Result<(), TosError> {
        self.max_size = self.part_size * MAX_PART_NUMBER;
        if self.next_write_offset >= self.max_size {
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", self.max_size),
                cause: None,
            });
        }
        self.wait_dispatch = None;
        self.wait_execute = None;
        self.mu_ctx = Arc::new(MultipartUploadContext::new());
        self.dp = Arc::new(Dispatcher::new(calc_queue_size(self.part_size)));
        self.st = Arc::new(Store::new(self.part_size, self.next_write_offset));
        self.ta = Arc::new(TokenAcquirer::new(DEFAULT_UPLOAD_PART_CONCURRENCY));
        self.dispatch().await;
        self.execute().await;
        Ok(())
    }

    async fn write(&mut self, data: &[u8]) -> Result<isize, TosError> {
        let mut current;
        if let Some(part) = self.current.take() {
            current = part;
        } else {
            current = Part::new(self.part_size as usize);
        }
        let mut written = 0isize;
        loop {
            let filled = current.fill(&data[written as usize..]);
            written += filled;
            if current.is_full() {
                let (push_result, succeed) = self.dp.push(current).await;
                if !succeed {
                    if let Some(mut part) = push_result {
                        part.release();
                        self.uc.abort().await;
                    }
                    return Err(TosError::TosClientError {
                        message: "dispatch current part failed".to_string(),
                        cause: None,
                    });
                }

                current = Part::new(self.part_size as usize);
            }

            if written == data.len() as isize {
                self.current = Some(current);
                return Ok(written);
            }
        }
    }

    async fn flush(&mut self, flush_to_remote: bool) -> Result<(), TosError> {
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
            });
        }

        if flush_to_remote {
            return self.write_to_remote().await;
        }

        Ok(())
    }

    async fn fsync(&mut self) -> Result<(), TosError> {
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
            });
        }

        self.write_to_remote().await
    }

    async fn write_to_remote(&mut self) -> Result<(), TosError> {
        let result = self.flush_current().await;
        self.mu_ctx.kick_off(OTHER_MU_KICK_OFF).await;
        if result.is_err() {
            return result;
        }
        self.close_dispatch_and_store().await;
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
            });
        }

        let result = self.uc.complete_multipart_upload().await;
        if result.is_ok() {
            self.uc.seal();
        }
        result
    }

    async fn release(&mut self) -> Result<(), TosError> {
        let mut result = self.flush_current().await;
        self.mu_ctx.kick_off(RELEASE_MU_KICK_OFF).await;
        self.close_dispatch_and_store().await;

        if result.is_ok() && !self.uc.is_aborted() {
            result = self.uc.complete_multipart_upload().await;
        }

        // finally release
        loop {
            match self.dp.pull().await {
                None => break,
                Some(mut part) => {
                    part.release();
                }
            }
        }

        loop {
            match self.st.pull().await {
                None => break,
                Some(mut si) => {
                    si.release();
                }
            }
        }

        self.ta.close();
        self.st.destroy();
        result
    }

    async fn flush_current(&mut self) -> Result<(), TosError> {
        if let Some(current) = self.current.take() {
            if current.size() > 0 {
                let (push_result, succeed) = self.dp.push(current).await;
                if !succeed {
                    if let Some(mut part) = push_result {
                        part.release();
                        self.uc.abort().await;
                    }
                    return Err(TosError::TosClientError {
                        message: "flush current part failed".to_string(),
                        cause: None,
                    });
                }
            }
        }
        Ok(())
    }
    async fn close_dispatch_and_store(&mut self) {
        self.dp.close();
        if let Some(wait_dispatch) = self.wait_dispatch.take() {
            let _ = wait_dispatch.await;
        }
        self.st.close();
        if let Some(wait_execute) = self.wait_execute.take() {
            let _ = wait_execute.await;
        }
    }

    async fn dispatch(&mut self) {
        let dp = self.dp.clone();
        let st = self.st.clone();
        let uc = self.uc.clone();
        self.wait_dispatch = Some(Handle::current().spawn(async move {
            loop {
                match dp.pull().await {
                    None => return,
                    Some(mut part) => {
                        if uc.is_aborted() {
                            part.release();
                            continue;
                        }

                        let (send_result, succeed) = st.push(part).await;
                        if !succeed {
                            error!("push part to store failed");
                            if let Some(mut part) = send_result {
                                part.release();
                            }
                            uc.abort().await;
                        }
                    }
                }
            }
        }));
    }

    async fn execute(&mut self) {
        let dp = self.dp.clone();
        let st = self.st.clone();
        let ta = self.ta.clone();
        let uc = self.uc.clone();
        let mu_ctx = self.mu_ctx.clone();
        self.wait_execute = Some(Handle::current().spawn(async move {
            let mut wait_async_uploads = Vec::with_capacity(16);
            loop {
                match st.pull().await {
                    None => break,
                    Some(mut si) => {
                        if uc.is_aborted() {
                            si.release();
                            continue;
                        }

                        wait_async_uploads.push(
                            uc.clone()
                                .async_upload(
                                    dp.clone(),
                                    st.clone(),
                                    ta.clone(),
                                    mu_ctx.clone(),
                                    si,
                                )
                                .await,
                        );
                    }
                }
            }
            join_all(wait_async_uploads).await;
        }));
    }

    async fn put_empty_object(&self) -> Result<(), TosError> {
        self.uc.put_empty_object().await
    }

    fn is_aborted(&self) -> bool {
        self.uc.is_aborted()
    }

    fn is_sealed(&self) -> bool {
        self.uc.is_sealed()
    }

    fn is_created(&self) -> bool {
        self.uc.is_created()
    }
}

struct UploadContext {
    aborted: Arc<AtomicI8>,
    sealed: Arc<AtomicI8>,
    created: Arc<AtomicI8>,
    mum: RwLock<MultipartUploadMeta>,
    wp: Arc<WriteParam>,
    client: Arc<InnerTosClient>,
}

impl UploadContext {
    fn new(created: Arc<AtomicI8>, wp: Arc<WriteParam>, client: Arc<InnerTosClient>) -> Self {
        Self {
            aborted: Arc::new(AtomicI8::new(0)),
            sealed: Arc::new(AtomicI8::new(0)),
            created,
            mum: RwLock::new(MultipartUploadMeta::new("".to_string(), 16)),
            wp,
            client,
        }
    }

    fn is_aborted(&self) -> bool {
        self.aborted.load(Ordering::Acquire) == 1
    }

    fn is_sealed(&self) -> bool {
        self.sealed.load(Ordering::Acquire) == 1
    }
    fn seal(&self) {
        let _ = self
            .sealed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed);
    }
    fn is_created(&self) -> bool {
        self.created.load(Ordering::Acquire) == 1
    }

    async fn async_upload(
        self: Arc<Self>,
        dp: Arc<Dispatcher>,
        st: Arc<Store>,
        ta: Arc<TokenAcquirer>,
        mu_ctx: Arc<MultipartUploadContext>,
        mut si: StoreItem,
    ) -> JoinHandle<()> {
        let aborted = self.aborted.clone();
        Handle::current().spawn(async move {
            let _ = ta.acquire().await;
            if aborted.load(Ordering::Acquire) == 1 {
                si.release();
                return;
            }

            if si.part_number() > 1 {
                mu_ctx.kick_off(OTHER_MU_KICK_OFF).await;
                mu_ctx.wait_finished().await;
                if aborted.load(Ordering::Acquire) == 1 {
                    si.release();
                    return;
                }

                // upload part
                self.upload_part(si).await;
                return;
            }

            let flag = mu_ctx.wait_kick_off().await;
            if aborted.load(Ordering::Acquire) == 1 {
                si.release();
                return;
            }

            if flag == RELEASE_MU_KICK_OFF && dp.index() == 1 && st.index() == 1 {
                mu_ctx.mark_finished().await;
                // put object directly
                if let Some(data) = si.take() {
                    let mut input = PutObjectFromBufferInput::new(
                        self.wp.bucket.as_str(),
                        self.wp.key.as_str(),
                    );
                    input.set_content_length(data.len() as i64);
                    input.set_content(data);
                    if let Some(sc) = self.wp.storage_class.as_ref() {
                        if let Some(sc) = trans_storage_class(sc) {
                            input.set_storage_class(sc);
                        }
                    }
                    match self.client.put_object_from_buffer(&input).await {
                        Err(ex) => {
                            error!(
                                "put object in bucket [{}] with key [{}] failed, {}",
                                self.wp.bucket,
                                self.wp.key,
                                ex.to_string()
                            );
                            self.abort().await;
                        }
                        Ok(_) => {
                            let _ = self.created.compare_exchange(
                                0,
                                1,
                                Ordering::AcqRel,
                                Ordering::Relaxed,
                            );
                        }
                    }
                }
                return;
            }

            // init multipart upload first
            let mut input =
                CreateMultipartUploadInput::new(self.wp.bucket.as_str(), self.wp.key.as_str());
            if let Some(sc) = self.wp.storage_class.as_ref() {
                if let Some(sc) = trans_storage_class(sc) {
                    input.set_storage_class(sc);
                }
            }
            match self.client.create_multipart_upload(&input).await {
                Err(ex) => {
                    error!(
                        "init multipart upload in bucket [{}] with key [{}] failed, {}",
                        self.wp.bucket,
                        self.wp.key,
                        ex.to_string()
                    );
                    self.abort().await;
                    mu_ctx.mark_finished().await;
                }
                Ok(output) => {
                    {
                        self.mum.write().await.upload_id = output.upload_id().to_string();
                    }
                    mu_ctx.mark_finished().await;
                    self.upload_part(si).await;
                }
            }
        })
    }

    async fn upload_part(&self, mut si: StoreItem) {
        let rmum = self.mum.read().await;
        if rmum.upload_id != "" {
            if let Some(data) = si.take() {
                let mut input = UploadPartFromBufferInput::new(
                    self.wp.bucket.as_str(),
                    self.wp.key.as_str(),
                    rmum.upload_id.as_str(),
                );
                input.set_part_number(si.part_number());
                input.set_content_length(data.len() as i64);
                input.set_content(data);
                match self.client.upload_part_from_buffer(&input).await {
                    Err(ex) => {
                        error!("upload part in bucket [{}] with key [{}] failed upload id [{}], part number [{}], {}", self.wp.bucket, 
                                self.wp.key, rmum.upload_id.as_str(), si.part_number(), ex.to_string());
                        self.abort().await;
                    }
                    Ok(output) => {
                        drop(rmum);
                        self.mum.write().await.add_object_part(
                            si.part_number(),
                            ObjectPart {
                                uploaded_part: UploadedPart::new(si.part_number(), output.etag()),
                                crc64: output.hash_crc64ecma(),
                            },
                        );
                    }
                }
            }
        }
    }

    async fn abort(&self) {
        if let Ok(_) = self
            .aborted
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            let mum = self.mum.read().await;
            if mum.upload_id != "" {
                let input = AbortMultipartUploadInput::new(
                    self.wp.bucket.as_str(),
                    self.wp.key.as_str(),
                    mum.upload_id.as_str(),
                );
                if let Err(ex) = self.client.abort_multipart_upload(&input).await {
                    match ex {
                        TosError::TosClientError { message, .. } => {
                            warn!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key, mum.upload_id, message);
                        }
                        TosError::TosServerError {
                            message,
                            status_code,
                            ..
                        } => {
                            if status_code == 404 {
                                info!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key, mum.upload_id, message);
                            } else {
                                warn!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key, mum.upload_id, message);
                            }
                        }
                    }
                }
            }
        }
    }

    async fn complete_multipart_upload(&self) -> Result<(), TosError> {
        let mut mum = self.mum.write().await;
        if mum.upload_id != "" {
            let mut input = CompleteMultipartUploadInput::new(
                self.wp.bucket.as_str(),
                self.wp.key.as_str(),
                mum.upload_id.as_str(),
            );
            input.set_parts(mum.get_object_parts());
            match self.client.complete_multipart_upload(&input).await {
                Err(ex) => {
                    error!("complete multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}",
                        self.wp.bucket, self.wp.key, mum.upload_id, ex.to_string());
                    self.abort().await;
                    return Err(ex);
                }
                Ok(_) => {
                    let _ =
                        self.created
                            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed);
                }
            }
            mum.upload_id = "".to_string();
        }
        Ok(())
    }

    async fn put_empty_object(&self) -> Result<(), TosError> {
        let mut input =
            PutObjectFromBufferInput::new(self.wp.bucket.as_str(), self.wp.key.as_str());
        input.set_content_length(0);
        if let Some(sc) = self.wp.storage_class.as_ref() {
            if let Some(sc) = trans_storage_class(sc) {
                input.set_storage_class(sc);
            }
        }
        match self.client.put_object_from_buffer(&input).await {
            Err(ex) => {
                error!(
                    "put empty object in bucket [{}] with key [{}] failed, {}",
                    self.wp.bucket,
                    self.wp.key,
                    ex.to_string()
                );
                Err(ex)
            }
            Ok(_) => Ok(()),
        }
    }
}

struct Part {
    buf: Vec<u8>,
    capacity: usize,
}

impl Part {
    fn new(part_size: usize) -> Self {
        Self {
            buf: Vec::with_capacity(part_size),
            capacity: part_size,
        }
    }

    fn fill(&mut self, data: &[u8]) -> isize {
        if data.len() == 0 {
            return 0;
        }

        if self.is_full() {
            return 0;
        }

        let remaining = self.capacity - self.buf.len();
        if remaining >= data.len() {
            self.buf.extend_from_slice(data);
            return data.len() as isize;
        }

        self.buf.extend_from_slice(&data[..remaining]);
        remaining as isize
    }

    fn is_full(&self) -> bool {
        self.buf.len() == self.capacity
    }

    fn size(&self) -> isize {
        self.buf.len() as isize
    }

    fn release(&mut self) {
        // do nothing
    }
}

struct Dispatcher {
    sender: Sender<Part>,
    receiver: Receiver<Part>,
    inner_queue_size: isize,
    inner_index: AtomicIsize,
    closed: AtomicI8,
}

impl Dispatcher {
    fn new(inner_queue_size: isize) -> Self {
        let (sender, receiver) = async_channel::bounded(inner_queue_size as usize);
        Self {
            sender,
            receiver,
            inner_queue_size,
            inner_index: AtomicIsize::new(0),
            closed: AtomicI8::new(0),
        }
    }

    async fn push(&self, part: Part) -> (Option<Part>, bool) {
        match self.sender.send(part).await {
            Ok(_) => {
                self.inner_index.fetch_add(1, Ordering::Release);
                (None, true)
            }
            Err(ex) => (Some(ex.0), false),
        }
    }

    async fn pull(&self) -> Option<Part> {
        match self.receiver.recv().await {
            Ok(part) => Some(part),
            Err(_) => None,
        }
    }

    fn index(&self) -> isize {
        self.inner_index.load(Ordering::Acquire)
    }

    fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.sender.close();
        }
    }

    fn reopen(&mut self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(1, 0, Ordering::AcqRel, Ordering::Relaxed)
        {
            let (sender, receiver) = async_channel::bounded(self.inner_queue_size as usize);
            self.sender = sender;
            self.receiver = receiver;
        }
    }
}

struct Store {
    sender: Sender<StoreItem>,
    receiver: Receiver<StoreItem>,
    part_size: isize,
    next_part_number: AtomicIsize,
    next_object_start: AtomicIsize,
    closed: AtomicI8,
}

impl Store {
    fn new(part_size: isize, next_object_start: isize) -> Self {
        let (sender, receiver) = async_channel::bounded(calc_queue_size(part_size) as usize);
        Self {
            sender,
            receiver,
            part_size,
            next_part_number: AtomicIsize::new(1),
            next_object_start: AtomicIsize::new(next_object_start),
            closed: AtomicI8::new(0),
        }
    }

    fn new_store_item(&self, part: Part) -> StoreItem {
        let object_start = self.next_object_start.load(Ordering::Acquire);
        let object_end = object_start + part.size();
        StoreItem {
            part: Some(part),
            object_start,
            object_end,
            part_number: self.next_part_number.load(Ordering::Acquire),
        }
    }

    fn index(&self) -> isize {
        self.next_part_number.load(Ordering::Acquire) - 1
    }

    async fn push(&self, part: Part) -> (Option<Part>, bool) {
        let part_size = part.size();
        match self.sender.send(self.new_store_item(part)).await {
            Ok(_) => {
                self.next_object_start
                    .fetch_add(part_size, Ordering::Release);
                self.next_part_number.fetch_add(1, Ordering::Release);
                (None, true)
            }
            Err(ex) => (ex.0.part, false),
        }
    }

    async fn pull(&self) -> Option<StoreItem> {
        match self.receiver.recv().await {
            Ok(si) => Some(si),
            Err(_) => None,
        }
    }

    fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.sender.close();
        }
    }

    fn destroy(&self) {
        self.close();
        // do nothing
    }

    fn reopen(&mut self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(1, 0, Ordering::AcqRel, Ordering::Relaxed)
        {
            let (sender, receiver) =
                async_channel::bounded(calc_queue_size(self.part_size) as usize);
            self.sender = sender;
            self.receiver = receiver;
        }
    }
}

struct StoreItem {
    part: Option<Part>,
    object_start: isize,
    object_end: isize,
    part_number: isize,
}

impl StoreItem {
    fn part_number(&self) -> isize {
        self.part_number
    }

    fn object_start(&self) -> isize {
        self.object_start
    }

    fn object_end(&self) -> isize {
        self.object_end
    }

    fn take(&mut self) -> Option<Vec<u8>> {
        match self.part.take() {
            None => None,
            Some(part) => Some(part.buf),
        }
    }

    fn size(&self) -> isize {
        if let Some(part) = self.part.as_ref() {
            return part.size();
        }
        0
    }

    fn release(&mut self) {
        if let Some(part) = self.part.as_mut() {
            part.release();
        }
    }
}

struct TokenAcquirer {
    semaphore: Semaphore,
}

impl TokenAcquirer {
    fn new(max_tokens: isize) -> Self {
        Self {
            semaphore: Semaphore::new(max_tokens as usize),
        }
    }

    async fn acquire(&self) -> Result<SemaphorePermit, AcquireError> {
        self.semaphore.acquire().await
    }

    fn close(&self) {
        self.semaphore.close();
    }
}

struct MultipartUploadContext {
    kick_off_lock: RwLock<i8>,
    kick_off_notify: Notify,
    finished_lock: RwLock<bool>,
    finished_notify: Notify,
}

impl MultipartUploadContext {
    fn new() -> Self {
        Self {
            kick_off_lock: RwLock::new(0),
            kick_off_notify: Notify::new(),
            finished_lock: RwLock::new(false),
            finished_notify: Notify::new(),
        }
    }

    async fn kick_off(&self, flag: i8) {
        if flag <= 0 {
            return;
        }

        {
            let val = self.kick_off_lock.read().await;
            if *val > 0 {
                return;
            }
        }

        let mut val = self.kick_off_lock.write().await;
        if *val > 0 {
            return;
        }
        *val = flag;
        self.kick_off_notify.notify_waiters();
    }

    async fn wait_kick_off(&self) -> i8 {
        loop {
            {
                let val = self.kick_off_lock.read().await;
                if *val > 0 {
                    return *val;
                }
            }
            self.kick_off_notify.notified().await;
        }
    }

    async fn mark_finished(&self) {
        {
            let val = self.finished_lock.read().await;
            if *val {
                return;
            }
        }

        let mut val = self.finished_lock.write().await;
        if *val {
            return;
        }
        *val = true;
        self.finished_notify.notify_waiters();
    }

    async fn wait_finished(&self) {
        loop {
            {
                let val = self.finished_lock.read().await;
                if *val {
                    return;
                }
            }
            self.finished_notify.notified().await;
        }
    }
}

struct MultipartUploadMeta {
    upload_id: String,
    object_parts: Option<HashMap<isize, ObjectPart>>,
    cap: isize,
}

impl MultipartUploadMeta {
    fn new(upload_id: String, cap: isize) -> Self {
        Self {
            upload_id,
            object_parts: None,
            cap,
        }
    }

    fn add_object_part(&mut self, part_number: isize, op: ObjectPart) {
        if self.object_parts.is_none() {
            self.object_parts = Some(HashMap::with_capacity(self.cap as usize));
        }

        if let Some(object_parts) = self.object_parts.as_mut() {
            object_parts.insert(part_number, op);
        }
    }

    fn get_object_parts(&mut self) -> Vec<UploadedPart> {
        if let Some(object_parts) = self.object_parts.take() {
            let mut result = Vec::with_capacity(object_parts.len());
            for (_, op) in object_parts {
                result.push(op.uploaded_part);
            }
            return result;
        }
        Vec::new()
    }
}

struct ObjectPart {
    uploaded_part: UploadedPart,
    crc64: u64,
}

fn calc_queue_size(part_size: isize) -> isize {
    let mut queue_size = DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT / part_size;
    if DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT % part_size != 0 {
        queue_size += 1;
    }
    queue_size
}

fn trans_storage_class(value: impl AsRef<str>) -> Option<StorageClassType> {
    match value.as_ref() {
        "STANDARD" => Some(StorageClassType::StorageClassStandard),
        "IA" => Some(StorageClassType::StorageClassIa),
        "ARCHIVE_FR" => Some(StorageClassType::StorageClassArchiveFr),
        "INTELLIGENT_TIERING" => Some(StorageClassType::StorageClassIntelligentTiering),
        "COLD_ARCHIVE" => Some(StorageClassType::StorageClassColdArchive),
        "ARCHIVE" => Some(StorageClassType::StorageClassArchive),
        "DEEP_COLD_ARCHIVE" => Some(StorageClassType::StorageClassDeepColdArchive),
        _ => None,
    }
}
