from automata.automaton import Automaton
from automata.state import State
from automata.alphabet import Alphabet

def main():
    # Load existing automata or create test ones
    try:
        # Try to load existing automata
        automata_list = Automaton.list_saved_automata()
        if len(automata_list) >= 2:
            # Use the first two automata in the list
            automaton1_name = automata_list[0]
            automaton2_name = automata_list[1]
            
            print(f"Loading automata '{automaton1_name}' and '{automaton2_name}'...")
            automaton1 = Automaton.load_from_file(f"Automates/{automaton1_name}.json")
            automaton2 = Automaton.load_from_file(f"Automates/{automaton2_name}.json")
        else:
            # Create simple test automata
            print("Not enough saved automata, creating test ones...")
            automaton1 = create_test_automaton1()
            automaton2 = create_test_automaton2()
    except Exception as e:
        print(f"Error loading automata: {e}")
        print("Creating test automata instead...")
        automaton1 = create_test_automaton1()
        automaton2 = create_test_automaton2()
    
    # Test union
    print(f"Computing union of {automaton1.name} and {automaton2.name}...")
    try:
        union = automaton1.union(automaton2)
        print(f"Union successful! Result has {len(union.states)} states and {len(union.transitions)} transitions.")
    except Exception as e:
        print(f"Error computing union: {e}")
    
    # Test intersection
    print(f"Computing intersection of {automaton1.name} and {automaton2.name}...")
    try:
        intersection = automaton1.intersection(automaton2)
        print(f"Intersection successful! Result has {len(intersection.states)} states and {len(intersection.transitions)} transitions.")
    except Exception as e:
        print(f"Error computing intersection: {e}")
    
    # Test equivalence
    print(f"Checking equivalence of {automaton1.name} and {automaton2.name}...")
    try:
        are_equivalent = automaton1.are_equivalent(automaton2)
        print(f"Equivalence check successful! Automata are {'equivalent' if are_equivalent else 'not equivalent'}.")
    except Exception as e:
        print(f"Error checking equivalence: {e}")

def create_test_automaton1():
    """Create a simple test automaton that accepts strings ending with 'a'"""
    automaton = Automaton("TestA")
    
    # Add alphabet
    automaton.alphabet.add_symbol("a")
    automaton.alphabet.add_symbol("b")
    
    # Add states
    q0 = State("q0", is_initial=True, is_final=False)
    q1 = State("q1", is_initial=False, is_final=True)
    
    automaton.add_state(q0)
    automaton.add_state(q1)
    
    # Add transitions
    automaton.add_transition(q0, q0, "b")
    automaton.add_transition(q0, q1, "a")
    automaton.add_transition(q1, q0, "b")
    automaton.add_transition(q1, q1, "a")
    
    return automaton

def create_test_automaton2():
    """Create a simple test automaton that accepts strings with at least one 'a'"""
    automaton = Automaton("TestB")
    
    # Add alphabet
    automaton.alphabet.add_symbol("a")
    automaton.alphabet.add_symbol("b")
    
    # Add states
    q0 = State("q0", is_initial=True, is_final=False)
    q1 = State("q1", is_initial=False, is_final=True)
    
    automaton.add_state(q0)
    automaton.add_state(q1)
    
    # Add transitions
    automaton.add_transition(q0, q0, "b")
    automaton.add_transition(q0, q1, "a")
    automaton.add_transition(q1, q1, "a")
    automaton.add_transition(q1, q1, "b")
    
    return automaton

if __name__ == "__main__":
    main() 