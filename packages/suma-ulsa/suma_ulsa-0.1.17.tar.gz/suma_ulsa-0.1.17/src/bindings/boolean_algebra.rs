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
            "┌──────────────────────────────────────────┐\n\
             │           SUBNET CALCULATOR SUMMARY      │\n\
             ├──────────────────────────────────────────┤\n\
             │ IP:            {:25} │\n\
             │ Class:         {:25} │\n\
             │ Subnet Mask:   {:25} │\n\
             │ New Mask:      {:25} │\n\
             │ Net Jump:      {:25} │\n\
             │ Hosts/Subnet:  {:25} │\n\
             │ Total Subnets: {:25} │\n\
             └──────────────────────────────────────────┘",
            self.inner.original_ip(),
            self.inner.net_class(),
            self.inner.subnet_mask(),
            self.inner.new_subnet_mask(),
            self.inner.net_jump(),
            format_hosts_quantity(self.inner.hosts_quantity().try_into().unwrap()),
            self.inner.subnet_quantity()
        )
    }

    /// Prints the summary to stdout.
    #[pyo3(name = "print_summary")]
    pub fn print_summary(&self) {
        println!("{}", self.summary());
    }

    /// Returns the subnet table as a formatted string.
    #[pyo3(name = "table")]
    pub fn table(&self, show_binary: Option<bool>) -> String {
        let show_binary = show_binary.unwrap_or(false);
        let rows = self.inner.generate_rows();
        
        if rows.is_empty() {
            return "┌──────────────────┐\n│ No subnets found │\n└──────────────────┘".to_string();
        }

        // Calcular anchos de columna
        let subnet_width = 8;
        let network_width = rows.iter().map(|r| r.direccion_red.len()).max().unwrap_or(15).max(15);
        let first_ip_width = rows.iter().map(|r| r.primera_ip.len()).max().unwrap_or(12).max(12);
        let last_ip_width = rows.iter().map(|r| r.ultima_ip.len()).max().unwrap_or(11).max(11);
        let broadcast_width = rows.iter().map(|r| r.broadcast.len()).max().unwrap_or(15).max(15);

        let total_width = subnet_width + network_width + first_ip_width + last_ip_width + broadcast_width + 14;

        let mut output = String::new();
        
        // Encabezado de la tabla
        output.push_str(&format!("┌{:─<width$}┐\n", "", width = total_width - 2));
        output.push_str(&format!("│{:^width$}│\n", "SUBNET TABLE", width = total_width - 2));
        output.push_str(&format!("├{:─<width$}┤\n", "", width = total_width - 2));
        
        // Nombres de columnas
        output.push_str(&format!(
            "│ {:^subnet$} │ {:^network$} │ {:^first$} │ {:^last$} │ {:^broadcast$} │\n",
            "Subnet",
            "Network",
            "First Host",
            "Last Host",
            "Broadcast",
            subnet = subnet_width,
            network = network_width,
            first = first_ip_width,
            last = last_ip_width,
            broadcast = broadcast_width
        ));
        
        // Separador
        output.push_str(&format!(
            "├{:─<subnet$}┼{:─<network$}┼{:─<first$}┼{:─<last$}┼{:─<broadcast$}┤\n",
            "",
            "",
            "",
            "",
            "",
            subnet = subnet_width + 2,
            network = network_width + 2,
            first = first_ip_width + 2,
            last = last_ip_width + 2,
            broadcast = broadcast_width + 2
        ));
        
        // Filas de datos
        for row in rows {
            output.push_str(&format!(
                "│ {:^subnet$} │ {:<network$} │ {:<first$} │ {:<last$} │ {:<broadcast$} │\n",
                row.subred,
                row.direccion_red,
                row.primera_ip,
                row.ultima_ip,
                row.broadcast,
                subnet = subnet_width,
                network = network_width,
                first = first_ip_width,
                last = last_ip_width,
                broadcast = broadcast_width
            ));

            // Opcional: mostrar representación binaria
            if show_binary {
                output.push_str(&format!(
                    "│ {:^subnet$} │ {:^network$} │ {:^first$} │ {:^last$} │ {:^broadcast$} │\n",
                    "bin",
                    ip_to_binary(&row.direccion_red),
                    ip_to_binary(&row.primera_ip),
                    ip_to_binary(&row.ultima_ip),
                    ip_to_binary(&row.broadcast),
                    subnet = subnet_width,
                    network = network_width,
                    first = first_ip_width,
                    last = last_ip_width,
                    broadcast = broadcast_width
                ));
                
                // Separador entre filas binarias
                if row.subred < self.inner.subnet_quantity() as u32 {
                    output.push_str(&format!(
                        "├{:─<subnet$}┼{:─<network$}┼{:─<first$}┼{:─<last$}┼{:─<broadcast$}┤\n",
                        "",
                        "",
                        "",
                        "",
                        "",
                        subnet = subnet_width + 2,
                        network = network_width + 2,
                        first = first_ip_width + 2,
                        last = last_ip_width + 2,
                        broadcast = broadcast_width + 2
                    ));
                }
            }
            
            // Separador entre subredes (excepto la última)
            if row.subred < self.inner.subnet_quantity() as u32 && !show_binary {
                output.push_str(&format!(
                    "├{:─<subnet$}┼{:─<network$}┼{:─<first$}┼{:─<last$}┼{:─<broadcast$}┤\n",
                    "",
                    "",
                    "",
                    "",
                    "",
                    subnet = subnet_width + 2,
                    network = network_width + 2,
                    first = first_ip_width + 2,
                    last = last_ip_width + 2,
                    broadcast = broadcast_width + 2
                ));
            }
        }
        
        // Línea final
        output.push_str(&format!("└{:─<subnet$}┴{:─<network$}┴{:─<first$}┴{:─<last$}┴{:─<broadcast$}┘\n",
            "",
            "",
            "",
            "",
            "",
            subnet = subnet_width + 2,
            network = network_width + 2,
            first = first_ip_width + 2,
            last = last_ip_width + 2,
            broadcast = broadcast_width + 2
        ));
        
        output
    }

    /// Prints the subnet table to stdout.
    #[pyo3(name = "print_table")]
    pub fn print_table(&self, show_binary: Option<bool>) {
        println!("{}", self.table(show_binary));
    }

    /// Versión compacta de la tabla
    #[pyo3(name = "compact_table")]
    pub fn compact_table(&self) -> String {
        let rows = self.inner.generate_rows();
        
        if rows.is_empty() {
            return "No subnets".to_string();
        }

        let mut output = String::new();
        output.push_str("Subnet │ Network       │ First Host    │ Last Host     │ Broadcast\n");
        output.push_str("───────┼───────────────┼───────────────┼───────────────┼───────────────\n");
        
        for row in rows {
            output.push_str(&format!(
                "{:6} │ {:13} │ {:13} │ {:13} │ {:13}\n",
                row.subred,
                truncate_string(&row.direccion_red, 13),
                truncate_string(&row.primera_ip, 13),
                truncate_string(&row.ultima_ip, 13),
                truncate_string(&row.broadcast, 13)
            ));
        }
        
        output
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

// Funciones auxiliares
fn format_hosts_quantity(hosts: usize) -> String {
    if hosts >= 1_000_000 {
        format!("{:.1}M", hosts as f64 / 1_000_000.0)
    } else if hosts >= 1_000 {
        format!("{:.1}K", hosts as f64 / 1_000.0)
    } else {
        hosts.to_string()
    }
}

fn truncate_string(s: &str, max_len: usize) -> String {
    if s.len() > max_len {
        format!("{}...", &s[..max_len.saturating_sub(3)])
    } else {
        s.to_string()
    }
}

fn ip_to_binary(ip: &str) -> String {
    // Implementación simplificada - puedes expandir esto
    if ip.len() > 15 {
        "binary...".to_string()
    } else {
        ip.chars().take(8).collect()
    }
}

// Wrapper para SubnetRow (mantener igual)
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

    /// Versión bonita para print
    fn to_pretty_string(&self) -> String {
        format!(
            "┌─────────────┐\n\
             │ Subnet {:3}  │\n\
             ├─────────────┤\n\
             │ Network:   {} │\n\
             │ First:     {} │\n\
             │ Last:      {} │\n\
             │ Broadcast: {} │\n\
             └─────────────┘",
            self.subred,
            pad_right(&self.direccion_red, 11),
            pad_right(&self.primera_ip, 11),
            pad_right(&self.ultima_ip, 11),
            pad_right(&self.broadcast, 11)
        )
    }
}

fn pad_right(s: &str, width: usize) -> String {
    if s.len() >= width {
        s.to_string()
    } else {
        format!("{}{}", s, " ".repeat(width - s.len()))
    }
}

// Resto del código permanece igual...
#[pyfunction]
#[pyo3(text_signature = "(ip, subnet_quantity)")]
pub fn create_subnet_calculator(ip: &str, subnet_quantity: usize) -> PySubnetCalculator {
    PySubnetCalculator::new(ip, subnet_quantity)
}

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