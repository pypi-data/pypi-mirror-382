use pyo3::pyclass;
use ve_tos_rust_sdk::object::{HeadObjectOutput, ListObjectsType2Output};

#[pyclass(name = "ListObjectsResult")]
pub struct ListObjectsResult {
    #[pyo3(get)]
    contents: Vec<TosObject>,
    #[pyo3(get)]
    common_prefixes: Vec<String>,
}

impl ListObjectsResult {
    pub(crate) fn new(output: ListObjectsType2Output) -> Self {
        let mut contents = Vec::with_capacity(output.contents().len());
        for content in output.contents() {
            contents.push(TosObject {
                bucket: output.name().to_string(),
                key: content.key().to_string(),
                size: content.size() as isize,
                etag: content.etag().to_string(),
            });
        }

        let mut common_prefixes = Vec::with_capacity(output.common_prefixes().len());
        for common_prefix in output.common_prefixes() {
            common_prefixes.push(common_prefix.prefix().to_string());
        }
        Self {
            contents,
            common_prefixes,
        }
    }
}

#[derive(Clone)]
#[pyclass(name = "TosObject")]
pub struct TosObject {
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) size: isize,
    #[pyo3(get)]
    pub(crate) etag: String,
}

impl TosObject {
    pub(crate) fn new(bucket: &str, key: &str, output: HeadObjectOutput) -> Self {
        Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            size: output.content_length() as isize,
            etag: output.etag().to_string(),
        }
    }
}
