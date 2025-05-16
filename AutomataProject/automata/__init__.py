"""
Automata package for defining and manipulating finite automata.

This package contains the core classes for automata representation:
- State: Represents a state in an automaton
- Alphabet: Represents the alphabet of an automaton
- Transition: Represents a transition between states
- Automaton: Represents a complete automaton (DFA or NFA)
"""

from .state import State
from .alphabet import Alphabet
from .transition import Transition
from .automaton import Automaton 