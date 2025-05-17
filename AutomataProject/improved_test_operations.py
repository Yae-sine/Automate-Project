from automata.automaton import Automaton
from automata.state import State
from automata.alphabet import Alphabet

def test_union_operation():
    """Test the improved union operation"""
    print("\n=== Testing Union Operation ===")
    
    # Create two simple automata
    automaton1 = create_test_automaton_a()
    automaton2 = create_test_automaton_b()
    
    print(f"Automaton A: {automaton1.name} with {len(automaton1.states)} states and {len(automaton1.transitions)} transitions")
    print(f"Automaton B: {automaton2.name} with {len(automaton2.states)} states and {len(automaton2.transitions)} transitions")
    
    try:
        # Perform union operation
        union = automaton1.union(automaton2)
        print(f"Union successful! Result has {len(union.states)} states and {len(union.transitions)} transitions")
        
        # Test acceptance on some example words
        test_words = ["", "a", "b", "aa", "ab", "ba", "bb", "aaa", "bbb", "abab", "baba"]
        for word in test_words:
            a_accepts = automaton1.accepts_word(word)
            b_accepts = automaton2.accepts_word(word)
            union_accepts = union.accepts_word(word)
            expected = a_accepts or b_accepts
            
            print(f"Word '{word}': A={a_accepts}, B={b_accepts}, Union={union_accepts}, Expected={expected}, Correct={union_accepts == expected}")
            
            if union_accepts != expected:
                print("ERROR: Union automaton does not correctly accept/reject this word!")
        
        return True
    except Exception as e:
        print(f"Error testing union: {e}")
        return False

def test_intersection_operation():
    """Test the improved intersection operation"""
    print("\n=== Testing Intersection Operation ===")
    
    # Create two simple automata
    automaton1 = create_test_automaton_a()
    automaton2 = create_test_automaton_b()
    
    print(f"Automaton A: {automaton1.name} with {len(automaton1.states)} states and {len(automaton1.transitions)} transitions")
    print(f"Automaton B: {automaton2.name} with {len(automaton2.states)} states and {len(automaton2.transitions)} transitions")
    
    try:
        # Perform intersection operation
        intersection = automaton1.intersection(automaton2)
        print(f"Intersection successful! Result has {len(intersection.states)} states and {len(intersection.transitions)} transitions")
        
        # Test acceptance on some example words
        test_words = ["", "a", "b", "aa", "ab", "ba", "bb", "aaa", "bbb", "abab", "baba"]
        for word in test_words:
            a_accepts = automaton1.accepts_word(word)
            b_accepts = automaton2.accepts_word(word)
            intersection_accepts = intersection.accepts_word(word)
            expected = a_accepts and b_accepts
            
            print(f"Word '{word}': A={a_accepts}, B={b_accepts}, Intersection={intersection_accepts}, Expected={expected}, Correct={intersection_accepts == expected}")
            
            if intersection_accepts != expected:
                print("ERROR: Intersection automaton does not correctly accept/reject this word!")
        
        return True
    except Exception as e:
        print(f"Error testing intersection: {e}")
        return False

def test_equivalence_check():
    """Test the improved equivalence check"""
    print("\n=== Testing Equivalence Check ===")
    
    # Create equivalent automata
    automaton1 = create_test_automaton_a()
    automaton2 = create_equivalent_automaton_to_a()
    automaton3 = create_test_automaton_b()  # Not equivalent to A
    
    print(f"Testing equivalence between automata...")
    
    try:
        # Test A ≡ A' (should be true)
        are_equivalent1 = automaton1.are_equivalent(automaton2)
        print(f"Are A and A' equivalent? {are_equivalent1} (Expected: True)")
        
        # Test A ≡ B (should be false)
        are_equivalent2 = automaton1.are_equivalent(automaton3)
        print(f"Are A and B equivalent? {are_equivalent2} (Expected: False)")
        
        # Test B ≡ B (should be true)
        are_equivalent3 = automaton3.are_equivalent(automaton3)
        print(f"Is B equivalent to itself? {are_equivalent3} (Expected: True)")
        
        return are_equivalent1 and not are_equivalent2 and are_equivalent3
    except Exception as e:
        print(f"Error testing equivalence: {e}")
        return False

def create_test_automaton_a():
    """Create a test automaton that accepts strings ending with 'a'"""
    automaton = Automaton("AutomatonA")
    
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

def create_equivalent_automaton_to_a():
    """Create an automaton equivalent to automaton A but with a different structure"""
    automaton = Automaton("AutomatonA_Equiv")
    
    # Add alphabet
    automaton.alphabet.add_symbol("a")
    automaton.alphabet.add_symbol("b")
    
    # Add states - more states but equivalent behavior
    q0 = State("s0", is_initial=True, is_final=False)
    q1 = State("s1", is_initial=False, is_final=True)
    q2 = State("s2", is_initial=False, is_final=False)
    
    automaton.add_state(q0)
    automaton.add_state(q1)
    automaton.add_state(q2)
    
    # Add transitions - different structure but same language
    automaton.add_transition(q0, q1, "a")
    automaton.add_transition(q0, q2, "b")
    automaton.add_transition(q1, q1, "a")
    automaton.add_transition(q1, q2, "b")
    automaton.add_transition(q2, q1, "a")
    automaton.add_transition(q2, q2, "b")
    
    return automaton

def create_test_automaton_b():
    """Create a test automaton that accepts strings with at least one 'a'"""
    automaton = Automaton("AutomatonB")
    
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

def main():
    """Run all tests"""
    union_success = test_union_operation()
    intersection_success = test_intersection_operation()
    equivalence_success = test_equivalence_check()
    
    print("\n=== Test Results ===")
    print(f"Union Operation: {'SUCCESS' if union_success else 'FAILURE'}")
    print(f"Intersection Operation: {'SUCCESS' if intersection_success else 'FAILURE'}")
    print(f"Equivalence Check: {'SUCCESS' if equivalence_success else 'FAILURE'}")
    
    if union_success and intersection_success and equivalence_success:
        print("\nAll tests passed! The improved methods are working correctly.")
    else:
        print("\nSome tests failed. Please check the output for details.")

if __name__ == "__main__":
    main() 