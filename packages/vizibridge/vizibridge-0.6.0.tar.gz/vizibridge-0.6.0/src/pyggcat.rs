use vizitig_lib::ggcat_integration::{build_gcalm};
use std::path::PathBuf;
use pyo3::pyfunction;

#[pyfunction]
pub fn build_graph(
    input_files: Vec<PathBuf>,
    memory: f64,
    thread_count: usize,
    output: PathBuf,
    k: usize,
    min_multiplicity: usize,
) {
    build_gcalm(input_files, memory, thread_count, output, k, min_multiplicity)
}
