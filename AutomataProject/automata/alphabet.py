from typing import Set, Dict, List, Any, Optional

class Alphabet:
    """
    Class representing the alphabet of an automaton.
    
    An alphabet is a set of symbols used for transitions.
    """
    
    def __init__(self, symbols: Optional[Set[str]] = None):
        """
        Initialize an alphabet with a set of symbols.
        
        Args:
            symbols: Set of symbols. Defaults to empty set.
        """
        self.symbols = set(symbols) if symbols else set()
        
    def add_symbol(self, symbol: str) -> None:
        """
        Add a symbol to the alphabet.
        
        Args:
            symbol: Symbol to add
        """
        self.symbols.add(symbol)
        
    def remove_symbol(self, symbol: str) -> None:
        """
        Remove a symbol from the alphabet.
        
        Args:
            symbol: Symbol to remove
        """
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            
    def contains(self, symbol: str) -> bool:
        """
        Check if a symbol is in the alphabet.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if the symbol is in the alphabet, False otherwise
        """
        return symbol in self.symbols
    
    def __str__(self) -> str:
        return f"Alphabet({', '.join(sorted(str(s) for s in self.symbols))})"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alphabet to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the alphabet
        """
        return {"symbols": list(self.symbols)}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alphabet':
        """
        Create an Alphabet object from a dictionary.
        
        Args:
            data: Dictionary with alphabet data
            
        Returns:
            New Alphabet object
        """
        return cls(symbols=set(data.get("symbols", []))) 