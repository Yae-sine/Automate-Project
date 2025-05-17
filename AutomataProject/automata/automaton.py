import json
import os
from collections import deque
from itertools import product
from typing import Set, Dict, List, Any, Optional, Tuple, FrozenSet

from .state import State
from .alphabet import Alphabet
from .transition import Transition



class Automaton:
    """
    Class representing a finite automaton (DFA or NFA).
    """
    
    def __init__(self, name: str, alphabet: Optional[Alphabet] = None, 
                 states: Optional[Set[State]] = None, 
                 transitions: Optional[Set[Transition]] = None):
        """
        Initialize an automaton.
        
        Args:
            name: Name of the automaton
            alphabet: Alphabet. Defaults to empty alphabet.
            states: Set of states. Defaults to empty set.
            transitions: Set of transitions. Defaults to empty set.
        """
        self.name = name
        self.alphabet = alphabet if alphabet else Alphabet()
        self.states = set(states) if states else set()
        self.transitions = set(transitions) if transitions else set()
    
    def add_state(self, state: State) -> None:
        """
        Add a state to the automaton.
        
        Args:
            state: State to add
        """
        self.states.add(state)
    
    def remove_state(self, state: State) -> None:
        """
        Remove a state and all its associated transitions.
        
        Args:
            state: State to remove
        """
        self.states.discard(state)
        # Remove all transitions involving this state
        self.transitions = {t for t in self.transitions 
                           if t.from_state != state and t.to_state != state}
    
    def add_transition(self, from_state: State, to_state: State, symbol: str) -> bool:
        """
        Add a transition to the automaton.
        
        Args:
            from_state: Source state
            to_state: Destination state
            symbol: Symbol for the transition
            
        Returns:
            True if added successfully, False if symbol not in alphabet (except epsilon)
        """
        # Make sure states are in the automaton
        if from_state not in self.states:
            self.add_state(from_state)
        if to_state not in self.states:
            self.add_state(to_state)
        
        # For epsilon transitions or if symbol is in alphabet
        if symbol == Transition.EPSILON or symbol in self.alphabet.symbols:
            self.transitions.add(Transition(from_state, to_state, symbol))
            return True
        return False
    
    def remove_transition(self, transition: Transition) -> None:
        """
        Remove a transition.
        
        Args:
            transition: Transition to remove
        """
        self.transitions.discard(transition)
    
    def get_initial_states(self) -> Set[State]:
        """
        Get all initial states.
        
        Returns:
            Set of initial states
        """
        return {state for state in self.states if state.is_initial}
    
    def get_final_states(self) -> Set[State]:
        """
        Get all final states.
        
        Returns:
            Set of final states
        """
        return {state for state in self.states if state.is_final}
    
    def get_transitions_from(self, state: State, symbol: Optional[str] = None) -> Set[Transition]:
        """
        Get all transitions from a state, optionally filtered by symbol.
        
        Args:
            state: The source state
            symbol: If provided, only transitions with this symbol are returned
            
        Returns:
            Set of matching transitions
        """
        if symbol is not None:
            return {t for t in self.transitions 
                   if t.from_state == state and t.symbol == symbol}
        return {t for t in self.transitions if t.from_state == state}
    
    def get_next_states(self, state: State, symbol: str) -> Set[State]:
        """
        Get all states that can be reached from the given state with the given symbol.
        
        Args:
            state: The source state
            symbol: The transition symbol
            
        Returns:
            Set of states that can be reached
        """
        transitions = self.get_transitions_from(state, symbol)
        return {t.to_state for t in transitions}
    
    def get_state_by_name(self, name: str) -> Optional[State]:
        """
        Find a state by its name.
        
        Args:
            name: The name of the state to find
            
        Returns:
            The state if found, None otherwise
        """
        for state in self.states:
            if state.name == name:
                return state
        return None
    
    def is_deterministic(self) -> bool:
        """
        Check if the automaton is deterministic.
        
        Returns:
            True if deterministic, False otherwise
        """
        # Must have exactly one initial state
        if len(self.get_initial_states()) != 1:
            return False
        
        # No epsilon transitions allowed
        if any(t.is_epsilon() for t in self.transitions):
            return False
        
        # For each state and symbol, there must be at most one transition
        for state in self.states:
            for symbol in self.alphabet.symbols:
                if len(self.get_next_states(state, symbol)) > 1:
                    return False
        
        return True
    
    def is_complete(self) -> bool:
        """
        Check if the automaton is complete (has a transition for each state and symbol).
        
        Returns:
            True if complete, False otherwise
        """
        if not self.is_deterministic():
            return False
        
        for state in self.states:
            for symbol in self.alphabet.symbols:
                if not self.get_next_states(state, symbol):
                    return False
        
        return True
    
    def is_minimal(self) -> bool:
        """
        Check if the automaton is minimal.
        
        Returns:
            True if minimal, False otherwise
        """
        # Only applicable to DFAs
        if not self.is_deterministic():
            return False
            
        # A minimal DFA can't be further minimized
        minimized = self.minimize()
        return len(minimized.states) == len(self.states)
    
    def accepts_word(self, word: str) -> bool:
        """
        Check if the automaton accepts a word.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is accepted, False otherwise
        """
        if self.is_deterministic():
            return self._accepts_word_dfa(word)
        else:
            return self._accepts_word_nfa(word)
    
    def _accepts_word_dfa(self, word: str) -> bool:
        """
        Check if the DFA accepts a word.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is accepted, False otherwise
        """
        current_state = next(iter(self.get_initial_states()))
        
        for symbol in word:
            if symbol not in self.alphabet.symbols:
                return False
            
            next_states = self.get_next_states(current_state, symbol)
            if not next_states:
                return False
            
            current_state = next(iter(next_states))
        
        return current_state.is_final
    
    def _accepts_word_nfa(self, word: str) -> bool:
        """
        Check if the NFA accepts a word using breadth-first search.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is accepted, False otherwise
        """
        # Get epsilon closure of initial states
        current_states = self._epsilon_closure(self.get_initial_states())
        
        for symbol in word:
            if symbol not in self.alphabet.symbols:
                return False
            
            # Get all possible next states after this symbol
            next_states = set()
            for state in current_states:
                transitions = self.get_transitions_from(state, symbol)
                next_states.update(t.to_state for t in transitions)
            
            # Include epsilon transitions from these states
            current_states = self._epsilon_closure(next_states)
            
            if not current_states:
                return False
        
        # Check if any current state is final
        return any(state.is_final for state in current_states)
    
    def _epsilon_closure(self, states: Set[State]) -> Set[State]:
        """
        Get the epsilon closure of a set of states.
        
        Args:
            states: Set of states to get epsilon closure for
            
        Returns:
            Epsilon closure of the states
        """
        closure = set(states)
        queue = deque(states)
        
        while queue:
            state = queue.popleft()
            epsilon_transitions = self.get_transitions_from(state, Transition.EPSILON)
            
            for transition in epsilon_transitions:
                if transition.to_state not in closure:
                    closure.add(transition.to_state)
                    queue.append(transition.to_state)
        
        return closure
    
    def to_deterministic(self) -> 'Automaton':
        """
        Convert the NFA to a DFA using the subset construction algorithm.
        
        Returns:
            A new DFA equivalent to this NFA
        """
        if self.is_deterministic():
            return self  # Already a DFA
        
        dfa = Automaton(f"{self.name}_DFA", Alphabet(self.alphabet.symbols))
        
        # Map sets of NFA states to DFA states
        state_map: Dict[FrozenSet[State], State] = {}
        
        # Initialize with epsilon closure of initial states
        initial_closure = frozenset(self._epsilon_closure(self.get_initial_states()))
        initial_name = self._state_set_name(initial_closure)
        initial_is_final = any(state.is_final for state in initial_closure)
        
        initial_dfa_state = State(initial_name, is_initial=True, is_final=initial_is_final)
        dfa.add_state(initial_dfa_state)
        state_map[initial_closure] = initial_dfa_state
        
        # Process states until no new states are found
        unprocessed = [initial_closure]
        
        while unprocessed:
            current_states = unprocessed.pop(0)
            current_dfa_state = state_map[current_states]
            
            for symbol in self.alphabet.symbols:
                # Get all states reachable from current_states via symbol
                next_states = set()
                for state in current_states:
                    for transition in self.get_transitions_from(state, symbol):
                        next_states.add(transition.to_state)
                
                # Apply epsilon closure
                next_closure = frozenset(self._epsilon_closure(next_states))
                
                if not next_closure:
                    continue
                
                # Create new DFA state if needed
                if next_closure not in state_map:
                    next_name = self._state_set_name(next_closure)
                    next_is_final = any(state.is_final for state in next_closure)
                    
                    next_dfa_state = State(next_name, is_final=next_is_final)
                    dfa.add_state(next_dfa_state)
                    state_map[next_closure] = next_dfa_state
                    unprocessed.append(next_closure)
                else:
                    next_dfa_state = state_map[next_closure]
                
                # Add transition
                dfa.add_transition(current_dfa_state, next_dfa_state, symbol)
        
        return dfa
    
    def _state_set_name(self, states: Set[State]) -> str:
        """
        Generate a name for a set of states.
        
        Args:
            states: Set of states
            
        Returns:
            A name representing the set of states
        """
        if not states:
            return "∅"
        return "{" + ",".join(sorted(state.name for state in states)) + "}"
    
    def get_complement(self) -> 'Automaton':
        """
        Get the complement of this automaton (accepting the complement language).
        First ensures the automaton is a complete DFA.
        
        Returns:
            The complement automaton
        """
        # First, ensure we have a complete DFA
        dfa = self.to_deterministic()
        if not dfa.is_complete():
            dfa = dfa.complete()
        
        # Create a new automaton with inverted final states
        complement = Automaton(f"{dfa.name}_complement", Alphabet(dfa.alphabet.symbols))
        
        for state in dfa.states:
            complement_state = State(
                state.name,
                is_initial=state.is_initial,
                is_final=not state.is_final  # Invert final/non-final
            )
            complement.add_state(complement_state)
        
        # Add the same transitions
        for transition in dfa.transitions:
            from_state = complement.get_state_by_name(transition.from_state.name)
            to_state = complement.get_state_by_name(transition.to_state.name)
            complement.add_transition(from_state, to_state, transition.symbol)
        
        return complement
    
    def complete(self) -> 'Automaton':
        """
        Make the automaton complete by adding a sink state and missing transitions.
        
        Returns:
            A new complete automaton
        """
        if not self.is_deterministic():
            return self.to_deterministic().complete()
        
        if self.is_complete():
            return self
        
        # Create a new automaton
        complete_automaton = Automaton(f"{self.name}_complete", Alphabet(self.alphabet.symbols))
        
        # Copy all states
        for state in self.states:
            complete_automaton.add_state(State(
                state.name,
                is_initial=state.is_initial,
                is_final=state.is_final
            ))
        
        # Add a sink state for missing transitions
        sink_state = State("sink", is_initial=False, is_final=False)
        complete_automaton.add_state(sink_state)
        
        # Make sure sink has transitions for all symbols (to itself)
        for symbol in self.alphabet.symbols:
            complete_automaton.add_transition(sink_state, sink_state, symbol)
        
        # Copy all transitions and add missing ones to sink
        for state in self.states:
            complete_state = complete_automaton.get_state_by_name(state.name)
            
            for symbol in self.alphabet.symbols:
                next_states = self.get_next_states(state, symbol)
                
                if next_states:
                    # Copy existing transitions
                    for next_state in next_states:
                        complete_next = complete_automaton.get_state_by_name(next_state.name)
                        complete_automaton.add_transition(complete_state, complete_next, symbol)
                else:
                    # Add missing transition to sink
                    complete_automaton.add_transition(complete_state, sink_state, symbol)
        
        return complete_automaton
    
    def minimize(self) -> 'Automaton':
        """
        Minimize the automaton using Hopcroft's algorithm.
        First ensures the automaton is a complete DFA.
        
        Returns:
            The minimized automaton
        """
        # First, ensure we have a complete DFA
        dfa = self.to_deterministic()
        if not dfa.is_complete():
            dfa = dfa.complete()
        
        # Step 1: Create initial partition (final and non-final states)
        final_states = dfa.get_final_states()
        non_final_states = dfa.states - final_states
        
        # Initial partition of states
        partitions = []
        if final_states:
            partitions.append(final_states)
        if non_final_states:
            partitions.append(non_final_states)
        
        # Step 2: Refine partitions until no more refinement is possible
        work_list = list(partitions)  # Copy the initial partitions
        
        while work_list:
            partition = work_list.pop(0)
            
            for symbol in dfa.alphabet.symbols:
                # Find states that lead to the current partition on symbol
                predecessors = {}
                
                for state in dfa.states:
                    next_states = dfa.get_next_states(state, symbol)
                    if next_states and any(next_state in partition for next_state in next_states):
                        # This state leads to the partition
                        predecessors[state] = True
                    else:
                        # This state doesn't lead to the partition
                        predecessors[state] = False
                
                # Refine existing partitions based on predecessors
                new_partitions = []
                for p in partitions:
                    # Split each partition based on whether states lead to 'partition'
                    leading = {s for s in p if predecessors.get(s, False)}
                    not_leading = p - leading
                    
                    if leading and not_leading:  # If the partition is actually split
                        new_partitions.append(leading)
                        new_partitions.append(not_leading)
                        
                        # Add the smaller split to the work list
                        smaller = leading if len(leading) <= len(not_leading) else not_leading
                        work_list.append(smaller)
                    else:
                        new_partitions.append(p)  # Keep the partition as is
                
                partitions = new_partitions
        
        # Step 3: Create the minimized automaton
        minimized = Automaton(f"{dfa.name}_minimized", Alphabet(dfa.alphabet.symbols))
        
        # Create a state for each partition
        partition_to_state = {}
        for i, partition in enumerate(partitions):
            # Check if the partition contains an initial state
            is_initial = any(state.is_initial for state in partition)
            # Check if the partition contains a final state
            is_final = any(state.is_final for state in partition)
            
            # Get a representative name from the partition
            name = f"q{i}_" + ",".join(sorted(state.name for state in partition))
            
            state = State(name, is_initial=is_initial, is_final=is_final)
            minimized.add_state(state)
            partition_to_state[frozenset(partition)] = state
        
        # Create transitions between the new states
        for partition, state in partition_to_state.items():
            # Take any representative from the partition (they're equivalent)
            representative = next(iter(partition))
            
            for symbol in dfa.alphabet.symbols:
                next_states = dfa.get_next_states(representative, symbol)
                if next_states:
                    next_state = next(iter(next_states))  # For a DFA, there is only one
                    
                    # Find which partition contains the next state
                    for p, s in partition_to_state.items():
                        if next_state in p:
                            minimized.add_transition(state, s, symbol)
                            break
        
        return minimized
    
    def union(self, other: 'Automaton') -> 'Automaton':
        """
        Create a new automaton that accepts the union of the languages of this automaton and another.
        
        Args:
            other: The other automaton
            
        Returns:
            A new automaton accepting the union
        """
        # Convert both to DFAs and make sure they are complete
        self_dfa = self.to_deterministic().complete()
        other_dfa = other.to_deterministic().complete()
        
        # Create a new alphabet as the union of both alphabets
        combined_alphabet = Alphabet(self_dfa.alphabet.symbols.union(other_dfa.alphabet.symbols))
        union_name = f"{self_dfa.name}|{other_dfa.name}"
        
        # Create a new automaton for the union
        union = Automaton(union_name, combined_alphabet)
        
        # Create state pairs mapping
        state_pairs = {}
        
        # Create combined states
        for self_state in self_dfa.states:
            for other_state in other_dfa.states:
                name = f"({self_state.name},{other_state.name})"
                is_initial = self_state.is_initial and other_state.is_initial
                is_final = self_state.is_final or other_state.is_final  # Union: either is final
                
                combined_state = State(name, is_initial=is_initial, is_final=is_final)
                union.add_state(combined_state)
                state_pairs[(self_state, other_state)] = combined_state
        
        # Add transitions - with both automata complete, there should be a valid transition for every symbol
        for (self_state, other_state), combined_state in state_pairs.items():
            for symbol in combined_alphabet.symbols:
                # Get next states in both automata - since automata are complete, these should never be empty
                self_next_states = self_dfa.get_next_states(self_state, symbol)
                other_next_states = other_dfa.get_next_states(other_state, symbol)
                
                if not self_next_states or not other_next_states:
                    continue  # Skip if somehow there's no transition (shouldn't happen with complete DFAs)
                
                # Since we're dealing with DFAs, there should be exactly one next state for each symbol
                self_next = next(iter(self_next_states))
                other_next = next(iter(other_next_states))
                
                # Add transition to the combined next state
                next_combined = state_pairs.get((self_next, other_next))
                if next_combined:
                    union.add_transition(combined_state, next_combined, symbol)
        
        # Simplify the result by removing unreachable states
        return self._remove_unreachable_states(union)
    
    def intersection(self, other: 'Automaton') -> 'Automaton':
        """
        Create a new automaton that accepts the intersection of the languages of this automaton and another.
        
        Args:
            other: The other automaton
            
        Returns:
            A new automaton accepting the intersection
        """
        # Convert both to DFAs and make sure they are complete
        self_dfa = self.to_deterministic().complete()
        other_dfa = other.to_deterministic().complete()
        
        # Create a new alphabet as the union of both alphabets
        combined_alphabet = Alphabet(self_dfa.alphabet.symbols.union(other_dfa.alphabet.symbols))
        intersection_name = f"{self_dfa.name}&{other_dfa.name}"
        
        # Create a new automaton for the intersection
        intersection = Automaton(intersection_name, combined_alphabet)
        
        # Create state pairs mapping
        state_pairs = {}
        
        # Create combined states
        for self_state in self_dfa.states:
            for other_state in other_dfa.states:
                name = f"({self_state.name},{other_state.name})"
                is_initial = self_state.is_initial and other_state.is_initial
                is_final = self_state.is_final and other_state.is_final  # Intersection: both are final
                
                combined_state = State(name, is_initial=is_initial, is_final=is_final)
                intersection.add_state(combined_state)
                state_pairs[(self_state, other_state)] = combined_state
        
        # Add transitions - with both automata complete, there should be a valid transition for every symbol
        for (self_state, other_state), combined_state in state_pairs.items():
            for symbol in combined_alphabet.symbols:
                # Get next states in both automata - since automata are complete, these should never be empty
                self_next_states = self_dfa.get_next_states(self_state, symbol)
                other_next_states = other_dfa.get_next_states(other_state, symbol)
                
                if not self_next_states or not other_next_states:
                    continue  # Skip if somehow there's no transition (shouldn't happen with complete DFAs)
                
                # Since we're dealing with DFAs, there should be exactly one next state for each symbol
                self_next = next(iter(self_next_states))
                other_next = next(iter(other_next_states))
                
                # Add transition to the combined next state
                next_combined = state_pairs.get((self_next, other_next))
                if next_combined:
                    intersection.add_transition(combined_state, next_combined, symbol)
        
        # Simplify the result by removing unreachable states
        return self._remove_unreachable_states(intersection)
    
    def _remove_unreachable_states(self, automaton: 'Automaton') -> 'Automaton':
        """
        Remove unreachable states from an automaton.
        
        Args:
            automaton: The automaton to simplify
            
        Returns:
            A new automaton with unreachable states removed
        """
        # Find all reachable states using BFS
        reachable = set()
        queue = deque(automaton.get_initial_states())
        
        while queue:
            state = queue.popleft()
            if state in reachable:
                continue
                
            reachable.add(state)
            
            # Add all states reachable via transitions
            for transition in automaton.get_transitions_from(state):
                if transition.to_state not in reachable:
                    queue.append(transition.to_state)
        
        # Create a new automaton with only reachable states
        simplified_name = automaton.name + "_simplified"
        simplified = Automaton(simplified_name, automaton.alphabet)
        
        # First add all reachable states
        for state in reachable:
            simplified.add_state(state)
        
        # Then add transitions between them
        for state in reachable:
            for transition in automaton.get_transitions_from(state):
                if transition.to_state in reachable:
                    simplified.add_transition(transition.from_state, transition.to_state, transition.symbol)
        
        return simplified
    
    def are_equivalent(self, other: 'Automaton') -> bool:
        """
        Check if this automaton is equivalent to another (they accept the same language).
        
        Args:
            other: The other automaton
            
        Returns:
            True if the automata are equivalent, False otherwise
        """
        # Convert both to minimal DFAs
        self_min = self.to_deterministic().minimize()
        other_min = other.to_deterministic().minimize()
        
        # If both DFAs have different number of states after minimization, they are not equivalent
        if len(self_min.states) != len(other_min.states):
            return False
            
        # If both minimal DFAs have different number of transitions, they are not equivalent
        if len(self_min.transitions) != len(other_min.transitions):
            return False
            
        # If they have different alphabets, they are not equivalent
        if self_min.alphabet.symbols != other_min.alphabet.symbols:
            return False
            
        # Check more precisely by computing symmetric difference
        # Two automata are equivalent if their symmetric difference is empty
        # L(A) = L(B) iff (L(A) ∩ L(B)^c) ∪ (L(A)^c ∩ L(B)) = ∅
        
        # Get complements
        self_complement = self_min.get_complement()
        other_complement = other_min.get_complement()
        
        # Check L(A) ∩ L(B)^c = ∅
        intersection1 = self_min.intersection(other_complement)
        
        # Check if the intersection has an accepting path
        if self._has_accepting_path(intersection1):
            return False
            
        # Check L(A)^c ∩ L(B) = ∅
        intersection2 = self_complement.intersection(other_min)
        
        # Check if the intersection has an accepting path
        return not self._has_accepting_path(intersection2)
    
    def _has_accepting_path(self, automaton: 'Automaton') -> bool:
        """
        Check if the automaton has any accepting path.
        
        Args:
            automaton: The automaton to check
            
        Returns:
            True if there is an accepting path, False otherwise
        """
        # Get initial states
        initial_states = automaton.get_initial_states()
        if not initial_states:
            return False
        
        # If any initial state is final, there is an accepting path
        if any(state.is_final for state in initial_states):
            return True
        
        # Use BFS to find an accepting path
        visited = set()
        queue = deque(initial_states)
        
        while queue:
            state = queue.popleft()
            if state in visited:
                continue
            
            visited.add(state)
            
            # Check all transitions from this state
            for transition in automaton.get_transitions_from(state):
                if transition.to_state.is_final:
                    return True
                
                if transition.to_state not in visited:
                    queue.append(transition.to_state)
        
        return False
    
    def generate_words(self, max_length: int) -> List[str]:
        """
        Generate all accepted words up to a given length.
        
        Args:
            max_length: Maximum length of words to generate
            
        Returns:
            List of accepted words
        """
        accepted_words = []
        
        # Use BFS to generate words
        queue = deque([("", next(iter(self.get_initial_states())))] if self.is_deterministic() 
                     else [("", state) for state in self.get_initial_states()])
        
        while queue:
            word, state = queue.popleft()
            
            # If we're in a final state, add the word to the list
            if state.is_final:
                accepted_words.append(word)
            
            # If we've reached max length, don't add more symbols
            if len(word) >= max_length:
                continue
            
            # For each symbol in alphabet, explore the next states
            for symbol in self.alphabet.symbols:
                for next_state in self.get_next_states(state, symbol):
                    queue.append((word + symbol, next_state))
            
            # For NFAs, also follow epsilon transitions
            if not self.is_deterministic():
                for next_state in self.get_next_states(state, Transition.EPSILON):
                    queue.append((word, next_state))
        
        return accepted_words
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert automaton to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the automaton
        """
        return {
            "name": self.name,
            "alphabet": self.alphabet.to_dict(),
            "states": [state.to_dict() for state in self.states],
            "transitions": [transition.to_dict() for transition in self.transitions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Automaton':
        """
        Create an Automaton object from a dictionary.
        
        Args:
            data: Dictionary with automaton data
            
        Returns:
            New Automaton object
        """
        name = data.get("name", "unnamed")
        alphabet = Alphabet.from_dict(data.get("alphabet", {}))
        
        # Create states first
        states = []
        states_dict = {}
        for state_data in data.get("states", []):
            state = State.from_dict(state_data)
            states.append(state)
            states_dict[state.name] = state
        
        # Then create transitions
        transitions = []
        for transition_data in data.get("transitions", []):
            transition = Transition.from_dict(transition_data, states_dict)
            if transition:
                transitions.append(transition)
        
        return cls(name, alphabet, set(states), set(transitions))
    
    def save_to_file(self, directory: str = "Automates") -> str:
        """
        Save the automaton to a JSON file.
        
        Args:
            directory: Directory to save the file. Defaults to "Automates".
            
        Returns:
            Path to the saved file
        """
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(directory, f"{self.name}.json")
        
        # Convert to JSON and save
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
        
        return file_path
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Automaton':
        """
        Load an automaton from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded Automaton object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def list_saved_automata(cls, directory: str = "Automates") -> List[str]:
        """
        List all saved automata in the specified directory.
        
        Args:
            directory: Directory to look for automata files. Defaults to "Automates".
            
        Returns:
            List of automaton names (without .json extension)
        """
        if not os.path.exists(directory):
            return []
        
        automata_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        return [os.path.splitext(f)[0] for f in automata_files] 