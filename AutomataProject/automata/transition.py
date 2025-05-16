from typing import Dict, Any, Optional
from .state import State

class Transition:
    """
    Class representing a transition in an automaton.
    
    A transition connects two states with a symbol (or epsilon for NFA).
    """
    
    # Epsilon symbol for epsilon-transitions in NFAs
    EPSILON = "ε"
    
    def __init__(self, from_state: State, to_state: State, symbol: str):
        """
        Initialize a transition.
        
        Args:
            from_state: Source state
            to_state: Destination state
            symbol: Symbol that triggers the transition, use EPSILON for epsilon transitions
        """
        self.from_state = from_state
        self.to_state = to_state
        self.symbol = symbol
    
    def __eq__(self, other):
        if not isinstance(other, Transition):
            return False
        return (self.from_state == other.from_state and
                self.to_state == other.to_state and
                self.symbol == other.symbol)
    
    def __hash__(self):
        return hash((self.from_state, self.to_state, self.symbol))
    
    def __str__(self) -> str:
        return f"{self.from_state.name} --({self.symbol})--> {self.to_state.name}"
    
    def is_epsilon(self) -> bool:
        """
        Check if this is an epsilon transition.
        
        Returns:
            True if this is an epsilon transition, False otherwise
        """
        return self.symbol == self.EPSILON
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transition to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the transition
        """
        return {
            "from_state": self.from_state.name,
            "to_state": self.to_state.name,
            "symbol": self.symbol
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], states_dict: Dict[str, State]) -> Optional['Transition']:
        """
        Create a Transition object from a dictionary.
        
        Args:
            data: Dictionary with transition data
            states_dict: Dictionary mapping state names to State objects
            
        Returns:
            New Transition object or None if states not found
        """
        from_state = states_dict.get(data.get("from_state"))
        to_state = states_dict.get(data.get("to_state"))
        symbol = data.get("symbol")
        
        if from_state and to_state:
            return cls(from_state, to_state, symbol)
        return None 