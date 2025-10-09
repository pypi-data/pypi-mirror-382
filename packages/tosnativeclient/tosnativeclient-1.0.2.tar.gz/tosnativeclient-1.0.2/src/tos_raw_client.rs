use crate::tos_client::{InnerTosClient, TokioRuntime};
use crate::tos_error::{map_error, map_tos_error};
use bytes::Buf;
use futures_util::StreamExt;
use pyo3::{pyclass, pymethods, PyRef, PyRefMut, PyResult};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::runtime;
use tokio::runtime::Runtime;
use tokio::sync::Mutex;
use ve_tos_rust_sdk::asynchronous::object::{ObjectAPI, ObjectContent};
use ve_tos_rust_sdk::asynchronous::tos;

#[pyclass(name = "TosRawClient")]
pub struct TosRawClient {
    client: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    #[pyo3(get)]
    region: String,
    #[pyo3(get)]
    endpoint: String,
    #[pyo3(get)]
    ak: String,
    #[pyo3(get)]
    sk: String,
    #[pyo3(get)]
    connection_timeout: isize,
    #[pyo3(get)]
    request_timeout: isize,
    #[pyo3(get)]
    max_connections: isize,
    #[pyo3(get)]
    max_retry_count: isize,
}

#[pymethods]
impl TosRawClient {
    #[new]
    #[pyo3(signature = (region, endpoint, ak="", sk="", connection_timeout=10000, request_timeout=120000, max_connections=1024, max_retry_count=3)
    )]
    pub fn new(
        region: &str,
        endpoint: &str,
        ak: &str,
        sk: &str,
        connection_timeout: isize,
        request_timeout: isize,
        max_connections: isize,
        max_retry_count: isize,
    ) -> PyResult<Self> {
        let runtime = Arc::new(runtime::Builder::new_multi_thread().enable_all().build()?);
        match tos::builder()
            .connection_timeout(connection_timeout)
            .request_timeout(request_timeout)
            .max_connections(max_connections)
            .max_retry_count(max_retry_count)
            .ak(ak)
            .sk(sk)
            .region(region)
            .endpoint(endpoint)
            .async_sleeper(TokioRuntime {
                runtime: Some(runtime.clone()),
            })
            .build()
        {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(client) => Ok(Self {
                client: Arc::new(client),
                runtime,
                region: region.to_string(),
                endpoint: endpoint.to_string(),
                ak: ak.to_string(),
                sk: sk.to_string(),
                connection_timeout,
                request_timeout,
                max_connections,
                max_retry_count,
            }),
        }
    }
    pub fn head_object<'py>(
        slf: PyRef<'_, Self>,
        input: &HeadObjectInput,
    ) -> PyResult<HeadObjectOutput> {
        let input = ve_tos_rust_sdk::object::HeadObjectInput::new_with_version_id(
            &input.bucket,
            &input.key,
            &input.version_id,
        );
        let client = slf.client.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.block_on(async move {
                match client.head_object(&input).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(HeadObjectOutput {
                        request_id: output.request_id().to_string(),
                        status_code: output.status_code(),
                        header: output.header().clone(),
                        content_length: output.content_length(),
                        etag: output.etag().to_string(),
                        version_id: output.version_id().to_string(),
                        hash_crc64ecma: output.hash_crc64ecma(),
                    }),
                }
            })
        })
    }

    pub fn delete_object(
        slf: PyRef<'_, Self>,
        input: &DeleteObjectInput,
    ) -> PyResult<DeleteObjectOutput> {
        let input = ve_tos_rust_sdk::object::DeleteObjectInput::new_with_version_id(
            &input.bucket,
            &input.key,
            &input.version_id,
        );
        let client = slf.client.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.block_on(async move {
                match client.delete_object(&input).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(DeleteObjectOutput {
                        request_id: output.request_id().to_string(),
                        status_code: output.status_code(),
                        header: output.header().clone(),
                        delete_marker: output.delete_marker(),
                        version_id: output.version_id().to_string(),
                    }),
                }
            })
        })
    }

    pub fn get_object(slf: PyRef<'_, Self>, input: &GetObjectInput) -> PyResult<GetObjectOutput> {
        let mut rinput = ve_tos_rust_sdk::object::GetObjectInput::new_with_version_id(
            &input.bucket,
            &input.key,
            &input.version_id,
        );
        rinput.set_range(&input.range);

        let client = slf.client.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.clone().block_on(async move {
                match client.get_object(&rinput).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(GetObjectOutput {
                        request_id: output.request_id().to_string(),
                        status_code: output.status_code(),
                        header: output.header().clone(),
                        content_length: output.content_length(),
                        etag: output.etag().to_string(),
                        version_id: output.version_id().to_string(),
                        content_range: output.content_range().to_string(),
                        hash_crc64ecma: output.hash_crc64ecma(),
                        output: Arc::new(Mutex::new(output)),
                        runtime: runtime.clone(),
                    }),
                }
            })
        })
    }

    pub fn put_object_from_buffer(
        slf: PyRef<'_, Self>,
        input: &PutObjectFromBufferInput,
    ) -> PyResult<PutObjectOutput> {
        let mut rinput =
            ve_tos_rust_sdk::object::PutObjectFromBufferInput::new(&input.bucket, &input.key);
        if input.content.len() > 0 {
            rinput.set_content(input.content.as_slice());
        }
        let client = slf.client.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.clone().block_on(async move {
                match client.put_object_from_buffer(&rinput).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(PutObjectOutput {
                        request_id: output.request_id().to_string(),
                        status_code: output.status_code(),
                        header: output.header().clone(),
                        etag: output.etag().to_string(),
                        version_id: output.version_id().to_string(),
                        hash_crc64ecma: output.hash_crc64ecma(),
                    }),
                }
            })
        })
    }

    pub fn put_object_from_file(
        slf: PyRef<'_, Self>,
        input: &PutObjectFromFileInput,
    ) -> PyResult<PutObjectOutput> {
        let mut rinput =
            ve_tos_rust_sdk::object::PutObjectFromFileInput::new(&input.bucket, &input.key);
        rinput.set_file_path(&input.file_path);
        let client = slf.client.clone();
        let runtime = slf.runtime.clone();
        slf.py().allow_threads(|| {
            runtime.clone().block_on(async move {
                match client.put_object_from_file(&rinput).await {
                    Err(ex) => Err(map_tos_error(ex)),
                    Ok(output) => Ok(PutObjectOutput {
                        request_id: output.request_id().to_string(),
                        status_code: output.status_code(),
                        header: output.header().clone(),
                        etag: output.etag().to_string(),
                        version_id: output.version_id().to_string(),
                        hash_crc64ecma: output.hash_crc64ecma(),
                    }),
                }
            })
        })
    }
}

#[pyclass(name = "HeadObjectInput")]
pub struct HeadObjectInput {
    #[pyo3(get, set)]
    pub(crate) bucket: String,
    #[pyo3(get, set)]
    pub(crate) key: String,
    #[pyo3(get, set)]
    pub(crate) version_id: String,
}

#[pymethods]
impl HeadObjectInput {
    #[new]
    #[pyo3(signature = (bucket, key, version_id = ""))]
    pub fn new(bucket: &str, key: &str, version_id: &str) -> PyResult<Self> {
        Ok(Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            version_id: version_id.to_string(),
        })
    }
}

#[pyclass(name = "HeadObjectOutput")]
pub struct HeadObjectOutput {
    #[pyo3(get)]
    pub(crate) request_id: String,
    #[pyo3(get)]
    pub(crate) status_code: isize,
    #[pyo3(get)]
    pub(crate) header: HashMap<String, String>,
    #[pyo3(get)]
    pub(crate) content_length: i64,
    #[pyo3(get)]
    pub(crate) etag: String,
    #[pyo3(get)]
    pub(crate) version_id: String,
    #[pyo3(get)]
    pub(crate) hash_crc64ecma: u64,
}

#[pyclass(name = "DeleteObjectInput")]
pub struct DeleteObjectInput {
    #[pyo3(get, set)]
    pub(crate) bucket: String,
    #[pyo3(get, set)]
    pub(crate) key: String,
    #[pyo3(get, set)]
    pub(crate) version_id: String,
}

#[pymethods]
impl DeleteObjectInput {
    #[new]
    #[pyo3(signature = (bucket, key, version_id = ""))]
    pub fn new(bucket: &str, key: &str, version_id: &str) -> PyResult<Self> {
        Ok(Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            version_id: version_id.to_string(),
        })
    }
}

#[pyclass(name = "DeleteObjectOutput")]
pub struct DeleteObjectOutput {
    #[pyo3(get)]
    pub(crate) request_id: String,
    #[pyo3(get)]
    pub(crate) status_code: isize,
    #[pyo3(get)]
    pub(crate) header: HashMap<String, String>,
    #[pyo3(get)]
    pub(crate) delete_marker: bool,
    #[pyo3(get)]
    pub(crate) version_id: String,
}
#[pyclass(name = "GetObjectInput")]
pub struct GetObjectInput {
    #[pyo3(get, set)]
    pub(crate) bucket: String,
    #[pyo3(get, set)]
    pub(crate) key: String,
    #[pyo3(get, set)]
    pub(crate) version_id: String,
    #[pyo3(get, set)]
    pub(crate) range: String,
}

#[pymethods]
impl GetObjectInput {
    #[new]
    #[pyo3(signature = (bucket, key, version_id = "", range = ""))]
    pub fn new(bucket: &str, key: &str, version_id: &str, range: &str) -> PyResult<Self> {
        Ok(Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            version_id: version_id.to_string(),
            range: range.to_string(),
        })
    }
}

#[pyclass(name = "GetObjectOutput")]
pub struct GetObjectOutput {
    #[pyo3(get)]
    pub(crate) request_id: String,
    #[pyo3(get)]
    pub(crate) status_code: isize,
    #[pyo3(get)]
    pub(crate) header: HashMap<String, String>,
    #[pyo3(get)]
    pub(crate) content_length: i64,
    #[pyo3(get)]
    pub(crate) etag: String,
    #[pyo3(get)]
    pub(crate) version_id: String,
    #[pyo3(get)]
    pub(crate) content_range: String,
    #[pyo3(get)]
    pub(crate) hash_crc64ecma: u64,
    output: Arc<Mutex<ve_tos_rust_sdk::object::GetObjectOutput>>,
    runtime: Arc<Runtime>,
}

#[pymethods]
impl GetObjectOutput {
    pub fn read_all(slf: PyRefMut<'_, Self>) -> PyResult<Option<Vec<u8>>> {
        let runtime = slf.runtime.clone();
        let output = slf.output.clone();
        runtime.block_on(async move {
            match output.lock().await.read_all().await {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(buf) => Ok(Some(buf)),
            }
        })
    }

    pub fn read(slf: PyRefMut<'_, Self>) -> PyResult<Option<Vec<u8>>> {
        let runtime = slf.runtime.clone();
        let output = slf.output.clone();
        runtime.block_on(async move {
            match output.lock().await.next().await {
                None => Ok(None),
                Some(result) => match result {
                    Err(ex) => Err(map_error(ex)),
                    Ok(buf) => Ok(Some(buf.chunk().to_vec())),
                },
            }
        })
    }
}

#[pyclass(name = "PutObjectFromBufferInput")]
pub struct PutObjectFromBufferInput {
    #[pyo3(get, set)]
    pub(crate) bucket: String,
    #[pyo3(get, set)]
    pub(crate) key: String,
    #[pyo3(get, set)]
    pub(crate) content: Vec<u8>,
}

#[pymethods]
impl PutObjectFromBufferInput {
    #[new]
    #[pyo3(signature = (bucket, key, content))]
    pub fn new(bucket: &str, key: &str, content: &[u8]) -> PyResult<Self> {
        Ok(Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            content: content.to_vec(),
        })
    }
}

#[pyclass(name = "PutObjectFromFileInput")]
pub struct PutObjectFromFileInput {
    #[pyo3(get, set)]
    pub(crate) bucket: String,
    #[pyo3(get, set)]
    pub(crate) key: String,
    #[pyo3(get, set)]
    pub(crate) file_path: String,
}

#[pymethods]
impl PutObjectFromFileInput {
    #[new]
    #[pyo3(signature = (bucket, key, file_path))]
    pub fn new(bucket: &str, key: &str, file_path: &str) -> PyResult<Self> {
        Ok(Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            file_path: file_path.to_string(),
        })
    }
}

#[pyclass(name = "PutObjectOutput")]
pub struct PutObjectOutput {
    #[pyo3(get)]
    pub(crate) request_id: String,
    #[pyo3(get)]
    pub(crate) status_code: isize,
    #[pyo3(get)]
    pub(crate) header: HashMap<String, String>,
    #[pyo3(get)]
    pub(crate) etag: String,
    #[pyo3(get)]
    pub(crate) version_id: String,
    #[pyo3(get)]
    pub(crate) hash_crc64ecma: u64,
}
