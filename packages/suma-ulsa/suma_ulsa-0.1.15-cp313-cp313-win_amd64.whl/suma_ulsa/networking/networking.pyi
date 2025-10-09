"""
Subnet calculator module interface.
"""

from typing import List, Dict, Any, Optional

class SubnetRow:
    """Represents a single subnet row in the results."""
    
    subred: int
    direccion_red: str
    primera_ip: str
    ultima_ip: str
    broadcast: str
    
    def __init__(self) -> None: ...
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert row to dictionary."""
        ...
    
    def __repr__(self) -> str:
        ...
    
    def __str__(self) -> str:
        ...

class SubnetCalculator:
    """Calculate subnets for IP networks."""
    
    @property
    def original_ip(self) -> str:
        """Original IP address with optional CIDR."""
        ...
    
    @property
    def net_class(self) -> str:
        """Network class (A, B, C) or CIDR information."""
        ...
    
    @property
    def subnet_mask(self) -> str:
        """Base subnet mask."""
        ...
    
    @property
    def new_subnet_mask(self) -> str:
        """New subnet mask after subnetting."""
        ...
    
    @property
    def net_jump(self) -> int:
        """Jump size between subnets."""
        ...
    
    @property
    def hosts_quantity(self) -> int:
        """Number of hosts per subnet."""
        ...
    
    @property
    def binary_subnet_mask(self) -> str:
        """Binary representation of base subnet mask."""
        ...
    
    @property
    def binary_new_mask(self) -> str:
        """Binary representation of new subnet mask."""
        ...
    
    def __init__(self, ip: str, subnet_quantity: int) -> None:
        """
        Initialize subnet calculator.
        
        Args:
            ip: IP address with optional CIDR (e.g., "192.168.1.0/24")
            subnet_quantity: Number of subnets to create
        """
        ...
    
    def summary(self) -> None:
        """Print summary of subnet calculation."""
        ...
    
    def generate_rows(self) -> List[SubnetRow]:
        """
        Generate subnet information as structured rows.
        
        Returns:
            List of SubnetRow objects
        """
        ...
    
    def generate_hashmap(self) -> List[Dict[str, str]]:
        """
        Generate subnet information as list of dictionaries.
        
        Returns:
            List of dictionaries with subnet information
        """
        ...
    
    def generate_table(self) -> List[Dict[str, str]]:
        """
        Generate subnet information as list of dictionaries.
        Alias for generate_hashmap().
        
        Returns:
            List of dictionaries with subnet information
        """
        ...
    
    def generate_dataframe(self) -> Any:
        """
        Generate subnet information as Polars DataFrame.
        
        Returns:
            Polars DataFrame if polars feature is enabled
            
        Raises:
            RuntimeError: If polars feature is not enabled
        """
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert calculator properties to dictionary.
        
        Returns:
            Dictionary with calculator properties
        """
        ...
    
    def pretty_print_table(self, show_binary: bool = False) -> None:
        """
        Pretty print the subnet table.
        
        Args:
            show_binary: Whether to show binary representations
        """
        ...

# Module-level functions
def create_subnet_calculator(ip: str, subnet_quantity: int) -> SubnetCalculator:
    """
    Create a subnet calculator instance.
    
    Args:
        ip: IP address with optional CIDR
        subnet_quantity: Number of subnets to create
        
    Returns:
        SubnetCalculator instance
    """
    ...

def calculate_subnets(ip: str, subnet_quantity: int) -> List[Dict[str, str]]:
    """
    Quick function to calculate subnets.
    
    Args:
        ip: IP address with optional CIDR
        subnet_quantity: Number of subnets to create
        
    Returns:
        List of dictionaries with subnet information
    """
    ...

def pretty_print_subnets(ip: str, subnet_quantity: int, show_binary: bool = False) -> None:
    """
    Quick function to calculate and pretty print subnets.
    
    Args:
        ip: IP address with optional CIDR
        subnet_quantity: Number of subnets to create
        show_binary: Whether to show binary representations
    """
    ...