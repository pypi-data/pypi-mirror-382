use pyo3::exceptions::PyException;
use pyo3::{create_exception, pyclass, pymethods, PyErr};
use std::error::Error;

#[pyclass]
#[derive(Clone)]
pub struct TosError {
    #[pyo3(get)]
    message: String,
    #[pyo3(get)]
    status_code: Option<isize>,
    #[pyo3(get)]
    ec: String,
    #[pyo3(get)]
    request_id: String,
}

impl TosError {
    pub(crate) fn message(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
            status_code: None,
            ec: "".to_string(),
            request_id: "".to_string(),
        }
    }
}

#[pymethods]
impl TosError {
    #[new]
    #[pyo3(signature = (message, status_code=None, ec=String::from(""), request_id=String::from("")))]
    pub fn new(
        message: String,
        status_code: Option<isize>,
        ec: String,
        request_id: String,
    ) -> Self {
        Self {
            message,
            status_code,
            ec,
            request_id,
        }
    }
}

create_exception!(tosnativeclient, TosException, PyException);

pub(crate) fn map_error_from_string(message: impl Into<String>) -> PyErr {
    PyErr::new::<TosException, _>(TosError::new(
        message.into(),
        None,
        "".to_string(),
        "".to_string(),
    ))
}

pub(crate) fn map_error(err: impl Error) -> PyErr {
    PyErr::new::<TosException, _>(TosError::message(err.to_string()))
}

pub(crate) fn map_tos_error(err: ve_tos_rust_sdk::error::TosError) -> PyErr {
    match err {
        ve_tos_rust_sdk::error::TosError::TosClientError { message, .. } => {
            PyErr::new::<TosException, _>(TosError::message(message))
        }
        ve_tos_rust_sdk::error::TosError::TosServerError {
            message,
            status_code,
            ec,
            request_id,
            ..
        } => {
            PyErr::new::<TosException, _>(TosError::new(message, Some(status_code), ec, request_id))
        }
    }
}
