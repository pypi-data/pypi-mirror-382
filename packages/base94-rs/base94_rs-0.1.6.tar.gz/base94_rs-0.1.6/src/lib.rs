// lib.rs
// Implementation of Base94 encode and decode in Rust for Python 3.
//
// THE GPLv3 LICENSE
// Copyleft (©) 2025 hibays
//

use pyo3::prelude::*;

mod base94;
use base94::{b94_decode_rust, b94_encode_rust};

mod base72;
use base72::{b72_decode_rust, b72_encode_rust};

// PyO3 绑定
#[pyfunction]
fn b94encode(data: &[u8]) -> PyResult<Vec<u8>> {
    Ok(b94_encode_rust(data))
}

#[pyfunction]
fn b94decode(data: &[u8]) -> PyResult<Vec<u8>> {
    b94_decode_rust(data).map_err(PyErr::new::<pyo3::exceptions::PyValueError, _>)
}

#[pyfunction]
fn b72encode(data: &[u8]) -> PyResult<Vec<u8>> {
    Ok(b72_encode_rust(data))
}

#[pyfunction]
fn b72decode(data: &[u8]) -> PyResult<Vec<u8>> {
    b72_decode_rust(data).map_err(PyErr::new::<pyo3::exceptions::PyValueError, _>)
}

#[pymodule]
fn _base94(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(b94encode, module)?)?;
    module.add_function(wrap_pyfunction!(b94decode, module)?)?;
    module.add_function(wrap_pyfunction!(b72encode, module)?)?;
    module.add_function(wrap_pyfunction!(b72decode, module)?)?;
    Ok(())
}
