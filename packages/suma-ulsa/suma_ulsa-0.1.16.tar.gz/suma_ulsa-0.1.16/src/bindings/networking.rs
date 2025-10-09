use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use std::collections::HashMap;

use crate::core::networking::subnets::subnet_calculator::{SubnetCalculator, SubnetRow};

#[pyclass(name = "SubnetCalculator")]
pub struct PySubnetCalculator {
    inner: SubnetCalculator,
}

#[pymethods]
impl PySubnetCalculator {
    #[new]
    pub fn new(ip: &str, subnet_quantity: usize) -> Self {
        Self {
            inner: SubnetCalculator::new(ip, subnet_quantity),
        }
    }

    #[getter]
    pub fn original_ip(&self) -> String {
        self.inner.original_ip().to_string()
    }

    #[getter]
    pub fn net_class(&self) -> String {
        self.inner.net_class().to_string()
    }

    #[getter]
    pub fn subnet_mask(&self) -> String {
        self.inner.subnet_mask().to_string()
    }

    #[getter]
    pub fn new_subnet_mask(&self) -> String {
        self.inner.new_subnet_mask().to_string()
    }

    #[getter]
    pub fn net_jump(&self) -> u32 {
        self.inner.net_jump()
    }

    #[getter]
    pub fn hosts_quantity(&self) -> u32 {
        self.inner.hosts_quantity()
    }

    #[getter]
    pub fn binary_subnet_mask(&self) -> String {
        self.inner.binary_subnet_mask().to_string()
    }

    #[getter]
    pub fn binary_new_mask(&self) -> String {
        self.inner.binary_new_mask().to_string()
    }

    #[pyo3(text_signature = "($self)")]
    pub fn summary(&self) {
        println!("Subnet Calculator Summary:");
        println!("-----------------------------------");
        println!("Original IP: {}", self.original_ip());
        println!("Network Class: {}", self.net_class());
        println!("Subnet Mask: {}", self.subnet_mask());
        println!("New Subnet Mask: {}", self.new_subnet_mask());
        println!("Net Jump: {}", self.net_jump());
        println!("Hosts Quantity: {}", self.hosts_quantity());
        println!("Binary Subnet Mask: {}", self.binary_subnet_mask());
        println!("Binary New Mask: {}", self.binary_new_mask());
        println!("-----------------------------------");
    }

    #[pyo3(text_signature = "($self)")]
    pub fn generate_rows(&self) -> Vec<PySubnetRow> {
        self.inner
            .generate_rows()
            .into_iter()
            .map(PySubnetRow::from)
            .collect()
    }

    #[pyo3(text_signature = "($self)")]
    pub fn generate_hashmap(&self) -> Vec<HashMap<String, String>> {
        self.inner.generate_hashmap()
    }

    #[pyo3(text_signature = "($self)")]
    pub fn generate_dataframe(&self) -> PyResult<PyObject> {
        #[cfg(feature = "polars")]
        {
            use pyo3::Python;
            let py = unsafe { Python::assume_attached() };
            match self.inner.generate_dataframe() {
                Ok(df) => {
                    // Convertir el DataFrame de Polars a un objeto Python
                    // Esto requeriría tener bindings para polars en Rust o usar pyo3-polars
                    // Por ahora devolvemos un diccionario como fallback
                    let dict = PyDict::new(py);
                    dict.set_item("message", "Polars DataFrame generated (Rust side)")?;
                    dict.set_item("rows", self.generate_hashmap())?;
                    Ok(dict.into())
                }
                Err(e) => {
                    Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to generate DataFrame: {}",
                        e
                    )))
                }
            }
        }
        #[cfg(not(feature = "polars"))]
        {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Polars support not enabled. Compile with 'polars' feature.",
            ))
        }
    }

    // Método para compatibilidad con Python
    #[pyo3(text_signature = "($self)")]
    pub fn to_dict(&self) -> PyResult<Py<PyAny>> {
        use pyo3::Python;
        let py = unsafe { Python::assume_attached() };
        let dict = PyDict::new(py);

        dict.set_item("original_ip", self.original_ip())?;
        dict.set_item("net_class", self.net_class())?;
        dict.set_item("subnet_mask", self.subnet_mask())?;
        dict.set_item("new_subnet_mask", self.new_subnet_mask())?;
        dict.set_item("net_jump", self.net_jump())?;
        dict.set_item("hosts_quantity", self.hosts_quantity())?;
        dict.set_item("binary_subnet_mask", self.binary_subnet_mask())?;
        dict.set_item("binary_new_mask", self.binary_new_mask())?;

        Ok(dict.into())
    }

    // Método para generar tabla como lista de diccionarios (más amigable para Python)
    #[pyo3(text_signature = "($self)")]
    pub fn generate_table(&self) -> Vec<HashMap<String, String>> {
        self.generate_hashmap()
    }

    #[pyo3(text_signature = "($self, show_binary=False)")]
    pub fn pretty_print_table(&self, show_binary: bool) -> PyResult<()> {
        use pyo3::Python;
        let py = unsafe {
            Python::assume_attached()
        };
        
        // Importar la función de pretty print desde Python
        let pretty_print_func = py.import("suma_ulsa._internal.pretty_print")?
            .getattr("pretty_print_subnet_table")?;
        
        // Llamar a la función Python con nuestros datos
        let table_data = self.generate_table();
        let calculator_info = self.to_dict()?;
        
        pretty_print_func.call1((table_data, calculator_info, show_binary))?;
        
        Ok(())
    }

    pub fn __repr__(&self) -> String {
        format!(
            "SubnetCalculator(ip='{}', subnets={}, hosts_per_subnet={})",
            self.inner.original_ip(),
            self.inner.subnet_quantity(),
            self.inner.hosts_quantity()
        )
    }

    pub fn __str__(self_: PyRef<'_, Self>) -> PyResult<String> {
        let py = self_.py();
        let summary_func = py.import("suma_ulsa._internal.pretty_print")?
            .getattr("format_subnet_calculator_summary")?;
        
        let calculator_info = self_.to_dict()?;
        let result = summary_func.call1((calculator_info,))?;
        result.extract()
    }
}

// Wrapper para SubnetRow
#[pyclass(name = "SubnetRow")]
pub struct PySubnetRow {
    #[pyo3(get)]
    pub subred: u32,
    #[pyo3(get)]
    pub direccion_red: String,
    #[pyo3(get)]
    pub primera_ip: String,
    #[pyo3(get)]
    pub ultima_ip: String,
    #[pyo3(get)]
    pub broadcast: String,
}

impl From<SubnetRow> for PySubnetRow {
    fn from(row: SubnetRow) -> Self {
        Self {
            subred: row.subred,
            direccion_red: row.direccion_red,
            primera_ip: row.primera_ip,
            ultima_ip: row.ultima_ip,
            broadcast: row.broadcast,
        }
    }
}

#[pymethods]
impl PySubnetRow {
    #[pyo3(text_signature = "($self)")]
    pub fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);
        dict.set_item("subred", self.subred)?;
        dict.set_item("direccion_red", &self.direccion_red)?;
        dict.set_item("primera_ip", &self.primera_ip)?;
        dict.set_item("ultima_ip", &self.ultima_ip)?;
        dict.set_item("broadcast", &self.broadcast)?;
        Ok(dict.into())
    }

    fn __repr__(&self) -> String {
        format!(
            "SubnetRow(subred={}, red='{}', primera='{}', ultima='{}', broadcast='{}')",
            self.subred, self.direccion_red, self.primera_ip, self.ultima_ip, self.broadcast
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

// Función de utilidad para crear un calculador rápido
#[pyfunction]
#[pyo3(text_signature = "(ip, subnet_quantity)")]
pub fn create_subnet_calculator(ip: &str, subnet_quantity: usize) -> PySubnetCalculator {
    PySubnetCalculator::new(ip, subnet_quantity)
}

// Función de utilidad para cálculo rápido
#[pyfunction]
#[pyo3(text_signature = "(ip, subnet_quantity)")]
pub fn calculate_subnets(ip: &str, subnet_quantity: usize) -> PyResult<Vec<HashMap<String, String>>> {
    let calculator = PySubnetCalculator::new(ip, subnet_quantity);
    Ok(calculator.generate_table())
}


/// Registra el módulo de redes
pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let submodule = PyModule::new(parent.py(), "networking")?;
    submodule.add_class::<PySubnetCalculator>()?;
    submodule.add_class::<PySubnetRow>()?;
    submodule.add_function(wrap_pyfunction!(create_subnet_calculator, &submodule)?)?;
    submodule.add_function(wrap_pyfunction!(calculate_subnets, &submodule)?)?;

    parent.add_submodule(&submodule)?;
    parent.py().import("sys")?
    .getattr("modules")?
    .set_item(&format!("suma_ulsa.networking"), submodule)?;
    Ok(())
}

