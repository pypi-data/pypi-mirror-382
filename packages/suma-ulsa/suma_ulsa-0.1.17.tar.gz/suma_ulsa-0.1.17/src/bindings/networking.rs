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

    /// Returns a summary string of the subnet calculation.
    #[pyo3(name = "summary")]
    pub fn summary(&self) -> String {
        format!(
            "SubnetCalculator Summary\n\
            IP: {}\n\
            Class: {}\n\
            Subnet Mask: {}\n\
            New Mask: {}\n\
            Net Jump: {}\n\
            Hosts/Subnet: {}\n",
            self.inner.original_ip(),
            self.inner.net_class(),
            self.inner.subnet_mask(),
            self.inner.new_subnet_mask(),
            self.inner.net_jump(),
            self.inner.hosts_quantity()
        )
    }

    /// Prints the summary to stdout.
    #[pyo3(name = "print_summary")]
    pub fn print_summary(&self) {
        println!("{}", self.summary());
    }

    /// Returns the subnet table as a formatted string.
    #[pyo3(name = "table")]
    pub fn table(&self, show_binary: bool) -> String {
        let rows = self.inner.generate_rows();
        let mut output = String::new();
        output.push_str("Subnet Table\n");
        output.push_str("--------------------------------------------------\n");
        for row in rows {
            output.push_str(&format!(
                "Subnet: {} | Network: {} | First IP: {} | Last IP: {} | Broadcast: {}\n",
                row.subred,
                row.direccion_red,
                row.primera_ip,
                row.ultima_ip,
                row.broadcast,
            ));
            if show_binary {
                // Puedes agregar aquí la representación binaria si lo deseas
            }
        }
        output
    }

    /// Prints the subnet table to stdout.
    #[pyo3(name = "print_table")]
    pub fn print_table(&self, show_binary: bool) {
        println!("{}", self.table(show_binary));
    }

    /// Mejor __str__ para mostrar resumen por defecto
    fn __str__(&self) -> String {
        self.summary()
    }

    /// Mejor __repr__ para debugging
    fn __repr__(&self) -> String {
        format!(
            "SubnetCalculator(ip='{}', subnets={}, hosts_per_subnet={})",
            self.inner.original_ip(),
            self.inner.subnet_quantity(),
            self.inner.hosts_quantity()
        )
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
    let rows = calculator.inner.generate_rows();
    let result = rows
        .into_iter()
        .map(|row| {
            let mut map = HashMap::new();
            map.insert("subred".to_string(), row.subred.to_string());
            map.insert("direccion_red".to_string(), row.direccion_red);
            map.insert("primera_ip".to_string(), row.primera_ip);
            map.insert("ultima_ip".to_string(), row.ultima_ip);
            map.insert("broadcast".to_string(), row.broadcast);
            map
        })
        .collect();
    Ok(result)
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

