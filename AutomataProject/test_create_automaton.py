import os
import sys

# Add the project directory to the path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

from automata.automaton import Automaton
from automata.state import State
from automata.alphabet import Alphabet

def create_test_automaton():
    """Create a test automaton and save it to the Automates directory."""
    # Create an automaton named 'Yassine'
    automaton = Automaton("Yassine")
    
    # Add symbols to the alphabet
    alphabet = Alphabet({"a", "b", "c"})
    automaton.alphabet = alphabet
    
    # Create states
    q0 = State("q0", is_initial=True)
    q1 = State("q1")
    q2 = State("q2", is_final=True)
    
    # Add states to the automaton
    automaton.add_state(q0)
    automaton.add_state(q1)
    automaton.add_state(q2)
    
    # Add transitions
    automaton.add_transition(q0, q1, "a")
    automaton.add_transition(q1, q1, "b")
    automaton.add_transition(q1, q2, "c")
    automaton.add_transition(q2, q0, "a")
    
    # Ensure directory exists
    os.makedirs("Automates", exist_ok=True)
    
    # Save the automaton
    file_path = automaton.save_to_file()
    print(f"Automaton saved to {file_path}")
    
    return file_path

if __name__ == "__main__":
    create_test_automaton() 