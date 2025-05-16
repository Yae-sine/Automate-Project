from typing import Dict, Any

class State:
    """
    Class representing a state in an automaton.
    
    A state can be initial, final, or both. Each state has a unique name.
    """
    
    def __init__(self, name: str, is_initial: bool = False, is_final: bool = False):
        """
        Initialize a state.
        
        Args:
            name: Name or identifier of the state
            is_initial: Whether the state is initial. Defaults to False.
            is_final: Whether the state is final. Defaults to False.
        """
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
    
    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self) -> str:
        attributes = []
        if self.is_initial:
            attributes.append("initial")
        if self.is_final:
            attributes.append("final")
        
        attrs_str = ", ".join(attributes)
        if attrs_str:
            return f"State({self.name}, {attrs_str})"
        return f"State({self.name})"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "name": self.name,
            "is_initial": self.is_initial,
            "is_final": self.is_final
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        """
        Create a State object from a dictionary.
        
        Args:
            data: Dictionary with state data
            
        Returns:
            New State object
        """
        return cls(
            name=data.get("name", ""),
            is_initial=data.get("is_initial", False),
            is_final=data.get("is_final", False)
        ) 