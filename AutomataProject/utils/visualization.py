import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, Set, Optional, Tuple, List, Any

# Use absolute imports instead of relative imports
from automata.automaton import Automaton
from automata.state import State
from automata.transition import Transition

# Global dictionary to store node positions for each automaton
# Key: automaton name, Value: dictionary of node positions
node_positions = {}

def create_automaton_graph(automaton: Automaton) -> nx.DiGraph:
    """
    Create a networkx graph from an automaton.
    
    Args:
        automaton: The automaton to visualize
        
    Returns:
        A networkx DiGraph representing the automaton
    """
    G = nx.DiGraph()
    
    # Add states as nodes
    for state in automaton.states:
        G.add_node(state.name, 
                  is_initial=state.is_initial, 
                  is_final=state.is_final,
                  label=state.name)
    
    # Add transitions as edges
    for transition in automaton.transitions:
        # Check if an edge already exists
        if G.has_edge(transition.from_state.name, transition.to_state.name):
            # Append to the existing label
            existing_label = G.edges[transition.from_state.name, transition.to_state.name]['label']
            G.edges[transition.from_state.name, transition.to_state.name]['label'] = f"{existing_label}, {transition.symbol}"
        else:
            # Create a new edge
            G.add_edge(transition.from_state.name, transition.to_state.name, 
                      label=transition.symbol)
    
    return G

def visualize_automaton(automaton: Automaton, highlight_path: Optional[List[Tuple[str, str, str]]] = None,
                       ax: Optional[plt.Axes] = None, figsize: Tuple[int, int] = (10, 8),
                       reuse_positions: bool = True) -> Figure:
    """
    Visualize an automaton using networkx and matplotlib.
    
    Args:
        automaton: The automaton to visualize
        highlight_path: Optional list of transitions to highlight (from_state, to_state, symbol)
        ax: Optional matplotlib axis to draw on
        figsize: Size of the figure
        reuse_positions: Whether to reuse previously calculated node positions
        
    Returns:
        Matplotlib figure object
    """
    G = create_automaton_graph(automaton)
    
    # Create a new figure if ax is not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    # Generate or reuse node positions
    global node_positions
    if reuse_positions and automaton.name in node_positions:
        # Check if all current nodes are in the saved positions
        stored_positions = node_positions[automaton.name]
        missing_nodes = [node for node in G.nodes() if node not in stored_positions]
        
        if missing_nodes:
            # If there are new nodes, start with existing positions and let networkx position the new ones
            pos = nx.spring_layout(G, pos=stored_positions, fixed=list(stored_positions.keys()),
                                 k=0.5, iterations=50)
            # Update stored positions
            node_positions[automaton.name] = pos
        else:
            # Use stored positions directly
            pos = stored_positions
    else:
        # Calculate new positions
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        # Store for future use
        node_positions[automaton.name] = pos
    
    # Draw nodes
    node_colors = []
    node_shapes = []
    for node in G.nodes():
        # Initial and final states are green, initial-only states are blue, 
        # final-only states are orange, regular states are gray
        if G.nodes[node]['is_initial'] and G.nodes[node]['is_final']:
            node_colors.append('green')
            node_shapes.append('doublecircle')
        elif G.nodes[node]['is_initial']:
            node_colors.append('blue')
            node_shapes.append('circle')
        elif G.nodes[node]['is_final']:
            node_colors.append('orange')
            node_shapes.append('doublecircle')
        else:
            node_colors.append('lightgray')
            node_shapes.append('circle')
    
    # Draw normal nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=700)
    
    # Draw double circles for final states
    final_states = [node for node in G.nodes() if G.nodes[node]['is_final']]
    if final_states:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=final_states, 
                               node_color='none', node_size=800, 
                               node_shape='o', edgecolors='black', linewidths=2)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)
    
    # Draw edges
    edge_colors = ['black'] * len(G.edges())
    
    # Highlight path if provided
    if highlight_path:
        for i, (u, v, data) in enumerate(G.edges(data=True)):
            for from_state, to_state, symbol in highlight_path:
                if u == from_state and v == to_state and symbol in data['label']:
                    edge_colors[i] = 'red'
                    break
    
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.0, arrowsize=20, edge_color=edge_colors)
    
    # Draw edge labels
    edge_labels = {(u, v): data['label'] for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8)
    
    # Draw initial state markers (arrows pointing to initial states)
    for node in G.nodes():
        if G.nodes[node]['is_initial']:
            # Draw an arrow pointing to the initial state
            node_pos = pos[node]
            ax.annotate('', xy=node_pos, xytext=(node_pos[0] - 0.1, node_pos[1]),
                       arrowprops=dict(arrowstyle="->", lw=1.5))
    
    # Set title and remove axes
    ax.set_title(f"Automaton: {automaton.name}")
    ax.axis('off')
    
    return fig

def save_automaton_image(automaton: Automaton, filename: str, directory: str = "Automates", 
                         format: str = "png", **kwargs) -> str:
    """
    Save an automaton visualization to a file.
    
    Args:
        automaton: The automaton to visualize
        filename: Name of the file to save
        directory: Directory to save the file
        format: File format (png, svg, etc.)
        **kwargs: Additional arguments for visualize_automaton
        
    Returns:
        Path to the saved file
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Create file path
    if not filename.endswith(f".{format}"):
        filename = f"{filename}.{format}"
    file_path = os.path.join(directory, filename)
    
    # Create visualization
    fig = visualize_automaton(automaton, **kwargs)
    
    # Save figure
    fig.savefig(file_path, format=format, bbox_inches='tight')
    plt.close(fig)
    
    return file_path

def animate_word_processing(automaton: Automaton, word: str, 
                          save_path: Optional[str] = None) -> List[Figure]:
    """
    Create a series of visualizations showing the processing of a word by an automaton.
    
    Args:
        automaton: The automaton
        word: The word to process
        save_path: Optional path to save the animation frames
        
    Returns:
        List of figures representing the animation frames
    """
    frames = []
    
    # Create a copy of the automaton to track state
    current_state = next(iter(automaton.get_initial_states())) if automaton.is_deterministic() else None
    current_states = automaton._epsilon_closure(automaton.get_initial_states()) if not automaton.is_deterministic() else None
    
    # Initial state
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    visualize_automaton(automaton, ax=ax)
    ax.set_title(f"Initial state: Processing word '{word}'")
    frames.append(fig)
    
    # Process each symbol
    path_so_far = []
    processed_word = ""
    
    for i, symbol in enumerate(word):
        processed_word += symbol
        
        if automaton.is_deterministic():
            # For DFA
            next_states = automaton.get_next_states(current_state, symbol)
            if not next_states:
                # No transition
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)
                visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
                ax.set_title(f"No transition for symbol '{symbol}' from state {current_state.name}. Word rejected.")
                frames.append(fig)
                break
            
            next_state = next(iter(next_states))
            
            # Record this transition for highlighting
            path_so_far.append((current_state.name, next_state.name, symbol))
            
            # Visualize current step
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111)
            visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
            ax.set_title(f"Processed: '{processed_word}', Current state: {next_state.name}")
            frames.append(fig)
            
            current_state = next_state
        else:
            # For NFA
            next_states_set = set()
            transitions_to_highlight = []
            
            for state in current_states:
                for next_state in automaton.get_next_states(state, symbol):
                    next_states_set.add(next_state)
                    transitions_to_highlight.append((state.name, next_state.name, symbol))
            
            # Apply epsilon closure
            next_states_set = automaton._epsilon_closure(next_states_set)
            
            # Add epsilon transitions to highlight
            for state in next_states_set:
                for t in automaton.get_transitions_from(state, Transition.EPSILON):
                    transitions_to_highlight.append((t.from_state.name, t.to_state.name, Transition.EPSILON))
            
            # Update path for highlighting
            path_so_far.extend(transitions_to_highlight)
            
            if not next_states_set:
                # No valid transitions
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)
                visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
                ax.set_title(f"No transitions for symbol '{symbol}'. Word rejected.")
                frames.append(fig)
                break
            
            # Visualize current step
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111)
            visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
            current_states_names = ", ".join(s.name for s in next_states_set)
            ax.set_title(f"Processed: '{processed_word}', Current states: {current_states_names}")
            frames.append(fig)
            
            current_states = next_states_set
    
    # Final state
    if automaton.is_deterministic():
        if current_state.is_final:
            accepted = True
            message = f"Word '{word}' is ACCEPTED. Ended in final state {current_state.name}."
        else:
            accepted = False
            message = f"Word '{word}' is REJECTED. Ended in non-final state {current_state.name}."
    else:
        if any(state.is_final for state in current_states):
            accepted = True
            final_states = [s.name for s in current_states if s.is_final]
            message = f"Word '{word}' is ACCEPTED. Ended in final states: {', '.join(final_states)}."
        else:
            accepted = False
            message = f"Word '{word}' is REJECTED. No final states reached."
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
    ax.set_title(message, color='green' if accepted else 'red')
    frames.append(fig)
    
    # Save frames if requested
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        for i, fig in enumerate(frames):
            fig.savefig(f"{save_path}_{i}.png", bbox_inches='tight')
    
    return frames 