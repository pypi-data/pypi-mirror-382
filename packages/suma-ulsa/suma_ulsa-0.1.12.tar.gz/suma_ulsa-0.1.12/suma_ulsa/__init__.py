"""
SUMA ULSA - Sistema Unificado de Métodos Avanzados
"""
from . import suma_ulsa  # Rust

# Importa explícitamente desde submódulos para linters
from .conversions import (
    NumberConverter,
    binary_to_decimal,
    decimal_to_binary,
    decimal_to_hex,
    decimal_to_letters, 
    binary_to_hex,
    hex_to_decimal,
    hex_to_binary,
    letters_to_decimal,
    convert_number,
    SUPPORTED_FORMATS
)

from .boolean_algebra import (
    BooleanExpr,
    TruthTable,
    parse_expression_debug,
    truth_table_from_expr
)

__version__ = "0.1.0"

__all__ = [
    # Conversions
    "NumberConverter",
    "binary_to_decimal", 
    "decimal_to_binary",
    "decimal_to_hex",
    "decimal_to_letters",
    "binary_to_hex",
    "hex_to_decimal", 
    "hex_to_binary",
    "letters_to_decimal",
    "convert_number", 
    "SUPPORTED_FORMATS",
    
    # Boolean Algebra
    "BooleanExpr",
    "TruthTable",
    "parse_expression_debug",
    "truth_table_from_expr",
]