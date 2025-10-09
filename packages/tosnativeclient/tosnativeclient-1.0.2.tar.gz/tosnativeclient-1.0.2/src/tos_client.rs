use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_error::map_tos_error;
use crate::tos_model::TosObject;
use crate::write_stream::WriteStream;
use async_trait::async_trait;
use futures_util::future::BoxFuture;
use pyo3::{pyclass, pymethods, PyRef, PyResult};
use std::future::Future;
use std::sync::atomic::{AtomicIsize, Ordering};
use std::sync::Arc;
use std::time::Duration;
use tokio::runtime::{Builder, Handle, Runtime};
use tracing_appender::non_blocking::WorkerGuard;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::asynchronous::tos;
use ve_tos_rust_sdk::asynchronous::tos::{AsyncRuntime, TosClientImpl};
use ve_tos_rust_sdk::common::init_tracing_log;
use ve_tos_rust_sdk::credential::{CommonCredentials, CommonCredentialsProvider};
use ve_tos_rust_sdk::object::HeadObjectInput;

#[derive(Debug, Default)]
pub(crate) struct TokioRuntime {
    pub(crate) runtime: Option<Arc<Runtime>>,
}

#[async_trait]
impl AsyncRuntime for TokioRuntime {
    type JoinError = tokio::task::JoinError;
    async fn sleep(&self, duration: Duration) {
        tokio::time::sleep(duration).await;
    }

    fn spawn<'a, F>(&self, future: F) -> BoxFuture<'a, Result<F::Output, Self::JoinError>>
    where
        F: Future + Send + 'static,
        F::Output: Send + 'static,
    {
        match self.runtime.as_ref() {
            None => Box::pin(Handle::current().spawn(future)),
            Some(r) => Box::pin(r.spawn(future)),
        }
    }

    fn block_on<F: Future>(&self, future: F) -> F::Output {
        match self.runtime.as_ref() {
            None => Handle::current().block_on(future),
            Some(r) => r.block_on(future),
        }
    }
}

pub(crate) type InnerTosClient =
    TosClientImpl<CommonCredentialsProvider<CommonCredentials>, CommonCredentials, TokioRuntime>;

#[pyclass(name = "TosClient")]
pub struct TosClient {
    rclient: Arc<InnerTosClient>,
    wclient: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    _guard: Option<WorkerGuard>,
    pcontext: Arc<SharedPrefetchContext>,

    #[pyo3(get)]
    region: String,
    #[pyo3(get)]
    endpoint: String,
    #[pyo3(get)]
    ak: String,
    #[pyo3(get)]
    sk: String,
    #[pyo3(get)]
    part_size: isize,
    #[pyo3(get)]
    max_retry_count: isize,
    #[pyo3(get)]
    max_prefetch_tasks: isize,
}

#[pymethods]
impl TosClient {
    #[new]
    #[pyo3(signature = (region, endpoint, ak=String::from(""), sk=String::from(""), part_size=8388608, max_retry_count=3, max_prefetch_tasks=3,
    directives=String::from(""), directory=String::from(""), file_name_prefix=String::from(""), shared_prefetch_tasks=20))]
    pub fn new(
        region: String,
        endpoint: String,
        ak: String,
        sk: String,
        part_size: isize,
        max_retry_count: isize,
        max_prefetch_tasks: isize,
        directives: String,
        directory: String,
        file_name_prefix: String,
        shared_prefetch_tasks: isize,
    ) -> PyResult<Self> {
        let mut _guard = None;
        if directives != "" {
            _guard = Some(init_tracing_log(directives, directory, file_name_prefix));
        }

        let logical_cores = num_cpus::get();
        let mut builder = Builder::new_multi_thread();
        if logical_cores > 0 {
            builder.worker_threads(logical_cores);
        }
        let runtime = Arc::new(builder.enable_all().build()?);
        let mut clients = Vec::with_capacity(2);
        for _ in 0..2 {
            match tos::builder()
                .connection_timeout(3000)
                .request_timeout(120000)
                .max_connections(10000)
                .max_retry_count(max_retry_count)
                .ak(ak.clone())
                .sk(sk.clone())
                .region(region.clone())
                .endpoint(endpoint.clone())
                .async_sleeper(TokioRuntime {
                    runtime: Some(runtime.clone()),
                })
                .build()
            {
                Err(ex) => return Err(map_tos_error(ex)),
                Ok(client) => {
                    clients.push(client);
                }
            }
        }

        Ok(Self {
            rclient: Arc::new(clients.pop().unwrap()),
            wclient: Arc::new(clients.pop().unwrap()),
            runtime,
            _guard,
            pcontext: Arc::new(SharedPrefetchContext::new(shared_prefetch_tasks)),
            region,
            endpoint,
            ak,
            sk,
            part_size,
            max_retry_count,
            max_prefetch_tasks,
        })
    }

    #[pyo3(signature = (bucket, prefix=String::from(""), max_keys=1000, delimiter=String::from("")))]
    pub fn list_objects(
        &self,
        bucket: String,
        prefix: String,
        max_keys: isize,
        delimiter: String,
    ) -> ListStream {
        ListStream::new(
            self.rclient.clone(),
            self.runtime.clone(),
            bucket,
            prefix,
            delimiter,
            max_keys,
        )
    }
    pub fn head_object(slf: PyRef<'_, Self>, bucket: String, key: String) -> PyResult<TosObject> {
        let input = HeadObjectInput::new(bucket, key);
        let client = slf.rclient.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.block_on(async move {
                match client.head_object(&input).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(TosObject::new(input.bucket(), input.key(), output)),
                }
            })
        })
    }
    #[pyo3(signature = (bucket, key, etag, size))]
    pub fn get_object(&self, bucket: String, key: String, etag: String, size: isize) -> ReadStream {
        ReadStream::new(
            self.rclient.clone(),
            self.runtime.clone(),
            self.pcontext.clone(),
            bucket,
            key,
            etag,
            size,
            self.part_size,
            self.max_prefetch_tasks,
        )
    }

    #[pyo3(signature = (bucket, key, storage_class=None))]
    pub fn put_object(
        slf: PyRef<'_, Self>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> PyResult<WriteStream> {
        let client = slf.wclient.clone();
        let runtime = slf.runtime.clone();
        let part_size = slf.part_size;
        slf.py().allow_threads(|| {
            runtime.clone().block_on(async move {
                match WriteStream::new(client, runtime, bucket, key, storage_class, part_size).await
                {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(ws) => Ok(ws),
                }
            })
        })
    }
}

pub(crate) struct SharedPrefetchContext {
    stolen_shared_prefetch_tasks: AtomicIsize,
    shared_prefetch_tasks: isize,
}

impl SharedPrefetchContext {
    pub(crate) fn new(shared_prefetch_tasks: isize) -> Self {
        Self {
            stolen_shared_prefetch_tasks: AtomicIsize::new(0),
            shared_prefetch_tasks,
        }
    }

    pub(crate) fn try_steal_shared_prefetch_task(&self) -> bool {
        loop {
            let current = self.stolen_shared_prefetch_tasks.load(Ordering::Acquire);
            if current >= self.shared_prefetch_tasks {
                return false;
            }
            if let Ok(_) = self.stolen_shared_prefetch_tasks.compare_exchange(
                current,
                current + 1,
                Ordering::AcqRel,
                Ordering::Relaxed,
            ) {
                return true;
            }
        }
    }

    pub(crate) fn release_shared_prefetch_task(&self) {
        self.stolen_shared_prefetch_tasks
            .fetch_add(-1, Ordering::Release);
    }
}
