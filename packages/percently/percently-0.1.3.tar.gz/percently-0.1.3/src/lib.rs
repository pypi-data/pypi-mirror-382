mod macros;
mod models;

use kolmogorov_smirnov as ks;
use models::{OrdF32, OrdF64};
use pyo3::prelude::*;

percentile_factory!(percentile_f32, f32, OrdF32);
percentile_factory!(percentile_f64, f64, OrdF64);

/// A Python module implemented in Rust.
#[pymodule]
fn percently(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(percentile_f32, m)?)?;
    m.add_function(wrap_pyfunction!(percentile_f64, m)?)?;
    Ok(())
}
