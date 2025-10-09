use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_client::TosClient;
use crate::tos_error::{TosError, TosException};
use crate::tos_model::{ListObjectsResult, TosObject};
use crate::tos_raw_client::{
    DeleteObjectInput, DeleteObjectOutput, GetObjectInput, GetObjectOutput, HeadObjectInput,
    HeadObjectOutput, PutObjectFromBufferInput, PutObjectFromFileInput, PutObjectOutput,
    TosRawClient,
};
use crate::write_stream::WriteStream;
use pyo3::prelude::*;

mod list_stream;
mod read_stream;
mod tos_client;
mod tos_error;
mod tos_model;
mod tos_raw_client;
mod write_stream;

#[pymodule]
#[pyo3(name = "tosnativeclient")]
fn main(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TosRawClient>()?;
    m.add_class::<HeadObjectInput>()?;
    m.add_class::<HeadObjectOutput>()?;
    m.add_class::<DeleteObjectInput>()?;
    m.add_class::<DeleteObjectOutput>()?;
    m.add_class::<GetObjectInput>()?;
    m.add_class::<GetObjectOutput>()?;
    m.add_class::<PutObjectFromBufferInput>()?;
    m.add_class::<PutObjectFromFileInput>()?;
    m.add_class::<PutObjectOutput>()?;
    m.add_class::<TosClient>()?;
    m.add_class::<ListStream>()?;
    m.add_class::<ListObjectsResult>()?;
    m.add_class::<TosObject>()?;
    m.add_class::<WriteStream>()?;
    m.add_class::<ReadStream>()?;
    m.add_class::<TosError>()?;
    m.add("TosException", m.py().get_type::<TosException>())?;
    Ok(())
}
