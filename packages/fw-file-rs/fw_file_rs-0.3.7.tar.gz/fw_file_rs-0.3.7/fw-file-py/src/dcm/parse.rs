use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::collections::HashMap;

use fw_file::dcm;
use fw_file::dcm::parse;

#[derive(Debug, IntoPyObject, FromPyObject)]
pub enum DicomValue {
    Int(i64),
    Float(f64),
    Str(String),
    Strings(Vec<String>),
    Ints(Vec<i64>),
    Floats(Vec<f64>),
    Unsupported(String),
}

impl From<dcm::DicomValue> for DicomValue {
    fn from(v: dcm::DicomValue) -> Self {
        match v {
            dcm::DicomValue::Int(i) => Self::Int(i),
            dcm::DicomValue::Float(f) => Self::Float(f),
            dcm::DicomValue::Str(s) => Self::Str(s),
            dcm::DicomValue::Strings(v) => Self::Strings(v),
            dcm::DicomValue::Ints(v) => Self::Ints(v),
            dcm::DicomValue::Floats(v) => Self::Floats(v),
            dcm::DicomValue::Unsupported(s) => Self::Unsupported(s),
        }
    }
}

impl From<DicomValue> for dcm::DicomValue {
    fn from(v: DicomValue) -> Self {
        match v {
            DicomValue::Int(i) => dcm::DicomValue::Int(i),
            DicomValue::Float(f) => dcm::DicomValue::Float(f),
            DicomValue::Str(s) => dcm::DicomValue::Str(s),
            DicomValue::Strings(v) => dcm::DicomValue::Strings(v),
            DicomValue::Ints(v) => dcm::DicomValue::Ints(v),
            DicomValue::Floats(v) => dcm::DicomValue::Floats(v),
            _ => dcm::DicomValue::Unsupported("".to_string()),
        }
    }
}

#[pyfunction]
#[pyo3(signature = (bytes, include_tags=None))]
pub fn parse_header(
    _py: Python,
    bytes: &[u8],
    include_tags: Option<Vec<String>>,
) -> PyResult<HashMap<String, DicomValue>> {
    let tag_refs: Vec<&str> = include_tags
        .as_ref()
        .map(|v| v.iter().map(String::as_str).collect())
        .unwrap_or_default();
    let result = parse::parse_header(bytes, &tag_refs)
        .map_err(|e| PyValueError::new_err(format!("get_dcm_meta failed: {}", e)))?;
    let py_map: HashMap<String, DicomValue> = result
        .into_iter()
        .map(|(k, v)| (k, DicomValue::from(v)))
        .collect();

    Ok(py_map)
}
