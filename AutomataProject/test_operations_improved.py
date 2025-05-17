from automata.automaton import Automaton
from automata.state import State
from automata.alphabet import Alphabet

def create_test_automaton1():
    """Create a simple test automaton that accepts strings ending with 'a'"""
    alphabet = Alphabet(['a', 'b'])
    automaton = Automaton("EndsWithA", alphabet)
    
    # Create states
    q0 = State("q0", is_initial=True, is_final=False)
    q1 = State("q1", is_initial=False, is_final=True)
    
    automaton.add_state(q0)
    automaton.add_state(q1)
    
    # Create transitions
    automaton.add_transition(q0, q0, 'b')  # Stay in q0 on 'b'
    automaton.add_transition(q0, q1, 'a')  # Go to q1 on 'a'
    automaton.add_transition(q1, q0, 'b')  # Go back to q0 on 'b'
    automaton.add_transition(q1, q1, 'a')  # Stay in q1 on 'a'
    
    return automaton

def create_test_automaton2():
    """Create a simple test automaton that accepts strings with an odd number of 'a's"""
    alphabet = Alphabet(['a', 'b'])
    automaton = Automaton("OddNumberOfA", alphabet)
    
    # Create states
    even = State("even", is_initial=True, is_final=False)
    odd = State("odd", is_initial=False, is_final=True)
    
    automaton.add_state(even)
    automaton.add_state(odd)
    
    # Create transitions
    automaton.add_transition(even, odd, 'a')   # Even to odd on 'a'
    automaton.add_transition(even, even, 'b')  # Stay in even on 'b'
    automaton.add_transition(odd, even, 'a')   # Odd to even on 'a'
    automaton.add_transition(odd, odd, 'b')    # Stay in odd on 'b'
    
    return automaton

def test_intersection():
    """Test the intersection operation"""
    print("\n=== Testing Intersection Operation ===")
    automaton1 = create_test_automaton1()
    automaton2 = create_test_automaton2()
    
    print(f"Automaton 1: {automaton1.name}")
    print(f"States: {[s.name for s in automaton1.states]}")
    print(f"Initial states: {[s.name for s in automaton1.get_initial_states()]}")
    print(f"Final states: {[s.name for s in automaton1.get_final_states()]}")
    
    print(f"\nAutomaton 2: {automaton2.name}")
    print(f"States: {[s.name for s in automaton2.states]}")
    print(f"Initial states: {[s.name for s in automaton2.get_initial_states()]}")
    print(f"Final states: {[s.name for s in automaton2.get_final_states()]}")
    
    try:
        intersection = automaton1.intersection(automaton2)
        print(f"\nIntersection successful!")
        print(f"Result name: {intersection.name}")
        print(f"Result states: {len(intersection.states)}")
        print(f"Result transitions: {len(intersection.transitions)}")
        
        # Test some words that should be in the intersection
        test_words = ["a", "aaa", "ba", "baa", "aba", "ababa", "ababaa"]
        print("\nTesting words:")
        
        for word in test_words:
            in_a1 = automaton1.accepts_word(word)
            in_a2 = automaton2.accepts_word(word)
            in_intersection = intersection.accepts_word(word)
            expected = in_a1 and in_a2
            
            print(f"Word '{word}': A1={in_a1}, A2={in_a2}, Intersection={in_intersection}, Expected={expected}, Correct={in_intersection == expected}")
        
        return True
    except Exception as e:
        print(f"Error in intersection test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_union():
    """Test the union operation"""
    print("\n=== Testing Union Operation ===")
    automaton1 = create_test_automaton1()
    automaton2 = create_test_automaton2()
    
    try:
        union = automaton1.union(automaton2)
        print(f"Union successful!")
        print(f"Result name: {union.name}")
        print(f"Result states: {len(union.states)}")
        print(f"Result transitions: {len(union.transitions)}")
        
        # Test some words
        test_words = ["a", "b", "aa", "ab", "ba", "bb", "aaa", "aba"]
        print("\nTesting words:")
        
        for word in test_words:
            in_a1 = automaton1.accepts_word(word)
            in_a2 = automaton2.accepts_word(word)
            in_union = union.accepts_word(word)
            expected = in_a1 or in_a2
            
            print(f"Word '{word}': A1={in_a1}, A2={in_a2}, Union={in_union}, Expected={expected}, Correct={in_union == expected}")
        
        return True
    except Exception as e:
        print(f"Error in union test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_equivalence():
    """Test the equivalence check"""
    print("\n=== Testing Equivalence Check ===")
    
    # Create two equivalent automata with different structure
    automaton1 = create_test_automaton1()
    
    # Create a slightly modified version of automaton1
    automaton2 = create_test_automaton1()
    automaton2.name = "EndsWithA_Copy"
    
    # Create a different automaton
    automaton3 = create_test_automaton2()
    
    try:
        # Test equivalent automata
        are_equivalent1 = automaton1.are_equivalent(automaton2)
        print(f"Automaton1 equivalent to Automaton2: {are_equivalent1} (Expected: True)")
        
        # Test non-equivalent automata
        are_equivalent2 = automaton1.are_equivalent(automaton3)
        print(f"Automaton1 equivalent to Automaton3: {are_equivalent2} (Expected: False)")
        
        return are_equivalent1 and not are_equivalent2
    except Exception as e:
        print(f"Error in equivalence test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== Running Automaton Operations Tests ===")
    
    tests = [
        ("Intersection", test_intersection),
        ("Union", test_union),
        ("Equivalence", test_equivalence)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\nRunning {name} test...")
        try:
            result = test_func()
            results[name] = result
            print(f"{name} test {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results[name] = False
            print(f"{name} test ERROR: {e}")
    
    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    for name, result in results.items():
        print(f"{name}: {'PASSED' if result else 'FAILED'}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\nAll tests PASSED!")
    else:
        print("\nSome tests FAILED!")

if __name__ == "__main__":
    main() 