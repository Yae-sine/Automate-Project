import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
import matplotlib.colors as mcolors
from typing import Dict, Set, Optional, Tuple, List, Any
import colorsys

# Use absolute imports instead of relative imports
from automata.automaton import Automaton
from automata.state import State
from automata.transition import Transition

# Global dictionary to store node positions for each automaton
# Key: automaton name, Value: dictionary of node positions
node_positions = {}

# Enhanced color palette - modern, visually appealing colors
COLOR_PALETTE = {
    'regular': '#E0E0E0',       # Light gray for regular states
    'initial': '#6495ED',       # Cornflower blue for initial states
    'final': '#FF8C00',         # Dark orange for final states
    'initial_final': '#20B2AA', # Light sea green for states that are both initial and final
    'edge': '#2F4F4F',          # Dark slate gray for edges
    'text': '#000000',          # Black for text
    'highlight': '#FF4500',     # Orange-red for highlighting
    'background': '#FFFFFF',    # White background
}

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
    Visualize an automaton using networkx and matplotlib with enhanced visuals.
    
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
        fig, ax = plt.subplots(figsize=figsize, facecolor=COLOR_PALETTE['background'])
    else:
        fig = ax.figure
        fig.set_facecolor(COLOR_PALETTE['background'])
    
    # Set axis background color
    ax.set_facecolor(COLOR_PALETTE['background'])
    
    # Generate or reuse node positions
    global node_positions
    if reuse_positions and automaton.name in node_positions:
        # Check if all current nodes are in the saved positions
        stored_positions = node_positions[automaton.name]
        missing_nodes = [node for node in G.nodes() if node not in stored_positions]
        
        if missing_nodes:
            # If there are new nodes, start with existing positions and let networkx position the new ones
            pos = nx.spring_layout(G, pos=stored_positions, fixed=list(stored_positions.keys()),
                                 k=0.5, iterations=100)
            # Update stored positions
            node_positions[automaton.name] = pos
        else:
            # Use stored positions directly
            pos = stored_positions
    else:
        # Calculate new positions with better spacing and prevent overlaps
        # Using a larger k value and more iterations for better separation
        pos = nx.spring_layout(G, k=1.5, iterations=200, seed=42)
        
        # Post-process positions to ensure minimum distance between nodes
        min_distance = 0.3  # Minimum distance between nodes
        
        # Iteratively adjust positions to ensure minimum distance
        for _ in range(10):  # Try to adjust up to 10 times
            overlaps = False
            for n1 in G.nodes():
                for n2 in G.nodes():
                    if n1 != n2:
                        # Calculate distance between nodes
                        dx = pos[n1][0] - pos[n2][0]
                        dy = pos[n1][1] - pos[n2][1]
                        dist = (dx**2 + dy**2)**0.5
                        
                        # If nodes are too close, push them apart
                        if dist < min_distance:
                            overlaps = True
                            # Push direction
                            push_x = dx / dist if dist > 0 else 0
                            push_y = dy / dist if dist > 0 else 0
                            
                            # Adjust positions (move both nodes slightly)
                            adjustment = 0.05 * (min_distance - dist)
                            pos[n1] = (pos[n1][0] + push_x * adjustment, 
                                      pos[n1][1] + push_y * adjustment)
                            pos[n2] = (pos[n2][0] - push_x * adjustment, 
                                      pos[n2][1] - push_y * adjustment)
            
            if not overlaps:
                break
        
        # Store for future use
        node_positions[automaton.name] = pos
    
    # Draw nodes with enhanced visuals
    node_colors = []
    node_sizes = []
    node_borders = []
    border_widths = []
    
    for node in G.nodes():
        # Set node properties based on state type
        if G.nodes[node]['is_initial'] and G.nodes[node]['is_final']:
            node_colors.append(COLOR_PALETTE['initial_final'])
            node_borders.append('black')
            border_widths.append(2.0)
            node_sizes.append(800)
        elif G.nodes[node]['is_initial']:
            node_colors.append(COLOR_PALETTE['initial'])
            node_borders.append('black')
            border_widths.append(1.5)
            node_sizes.append(700)
        elif G.nodes[node]['is_final']:
            node_colors.append(COLOR_PALETTE['final'])
            node_borders.append('black')
            border_widths.append(2.0)
            node_sizes.append(750)
        else:
            node_colors.append(COLOR_PALETTE['regular'])
            node_borders.append('gray')
            border_widths.append(1.0)
            node_sizes.append(650)
    
    # Draw all nodes with a subtle shadow effect
    for i, (node, color) in enumerate(zip(G.nodes(), node_colors)):
        # Draw a slightly larger shadow node
        ax.scatter(pos[node][0], pos[node][1], s=node_sizes[i]+20, 
                  color=(0,0,0,0.2), zorder=1)
    
    # Draw nodes with gradients and shadows
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax, 
                                   node_color=node_colors,
                                   node_size=node_sizes,
                                   edgecolors=node_borders,
                                   linewidths=border_widths,
                                   alpha=1.0)
    
    # Draw double circles for final states
    final_states = [node for node in G.nodes() if G.nodes[node]['is_final']]
    if final_states:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=final_states, 
                               node_color='none', node_size=[650 + 100 for _ in final_states], 
                               node_shape='o', edgecolors='black', linewidths=1.5,
                               alpha=0.7)
    
    # Draw node labels with better font
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_family='sans-serif', 
                           font_weight='bold', font_color=COLOR_PALETTE['text'])
    
    # Draw edges with curved style for better visibility
    # Prepare edge colors and styles
    edge_colors = []
    edge_widths = []
    edge_styles = []
    edge_alphas = []
    
    highlight_edges = []
    if highlight_path:
        highlight_edges = [(from_state, to_state) for from_state, to_state, _ in highlight_path]
    
    for u, v in G.edges():
        if (u, v) in highlight_edges:
            edge_colors.append(COLOR_PALETTE['highlight'])
            edge_widths.append(2.0)
            edge_styles.append('solid')
            edge_alphas.append(1.0)
        else:
            edge_colors.append(COLOR_PALETTE['edge'])
            edge_widths.append(1.0)
            edge_styles.append('solid')
            edge_alphas.append(0.8)
    
    # Draw curved edges between nodes
    curved_edges = []
    for i, (u, v) in enumerate(G.edges()):
        # Self-loops need special handling
        if u == v:
            rad = 0.3
            center = pos[u]
            theta = np.linspace(0, 2*np.pi, 100)
            circle_radius = 0.05
            circle_x = center[0] + circle_radius * np.cos(theta)
            circle_y = center[1] + circle_radius * np.sin(theta)
            ax.plot(circle_x, circle_y, color=edge_colors[i], linewidth=edge_widths[i], 
                    linestyle=edge_styles[i], alpha=edge_alphas[i], zorder=1)
            
            # Add more prominent arrowhead
            arrow_idx = len(theta) * 3 // 4
            dx = circle_x[arrow_idx] - circle_x[arrow_idx-5]
            dy = circle_y[arrow_idx] - circle_y[arrow_idx-5]
            arrow = FancyArrowPatch((circle_x[arrow_idx-5], circle_y[arrow_idx-5]),
                                  (circle_x[arrow_idx], circle_y[arrow_idx]),
                                  arrowstyle='->', color=edge_colors[i],
                                  linewidth=edge_widths[i]*1.5, alpha=edge_alphas[i], 
                                  mutation_scale=15, zorder=3)
            ax.add_patch(arrow)
        else:
            # Create the curved edge with more prominent arrow and better routing
            # Calculate appropriate curve based on node positions to avoid overlapping with other nodes
            rad = 0.15  # Default curve
            
            # Draw separate curves for bidirectional edges instead of increasing the curve
            has_reverse = G.has_edge(v, u)
            if has_reverse:
                # For bidirectional edges, draw two separate curves
                # First edge curves upward
                rad1 = 0.25  # Curve one way
                arrow1 = FancyArrowPatch(pos[u], pos[v], 
                                      connectionstyle=f'arc3,rad={rad1}',
                                      arrowstyle='->', color=edge_colors[i],
                                      linewidth=edge_widths[i], alpha=edge_alphas[i],
                                      mutation_scale=25, shrinkA=15, shrinkB=15,
                                      lw=2.0, zorder=1)
                curved_edges.append(arrow1)
                
                # Don't add the second arrow here - it will be added when we iterate to the reverse edge
                continue
            
            # Compute angle between nodes to determine best curve direction
            angle = np.arctan2(pos[v][1] - pos[u][1], pos[v][0] - pos[u][0])
            if -np.pi/2 <= angle <= np.pi/2:
                # For edges going generally rightward, curve upward
                rad = abs(rad)
            else:
                # For edges going generally leftward, curve downward
                rad = -abs(rad)
            
            # Create curved edge with adjusted parameters
            arrow = FancyArrowPatch(pos[u], pos[v], 
                                  connectionstyle=f'arc3,rad={rad}',
                                  arrowstyle='->', color=edge_colors[i],
                                  linewidth=edge_widths[i], alpha=edge_alphas[i],
                                  mutation_scale=25, shrinkA=15, shrinkB=15,  # Increase shrink to avoid nodes
                                  lw=2.0, zorder=1)
            curved_edges.append(arrow)
    
    # Add all curved edges to the plot
    for arrow in curved_edges:
        ax.add_patch(arrow)
    
    # Draw edge labels with better positioning
    edge_labels = {(u, v): data['label'] for u, v, data in G.edges(data=True)}
    for (u, v), label in edge_labels.items():
        # Calculate position for the label
        if u == v:
            # Self-loop
            x, y = pos[u]
            label_pos = (x, y + 0.15)
        else:
            # Standard edge
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Check if bidirectional
            has_reverse = G.has_edge(v, u)
            if has_reverse:
                # For bidirectional edges with separate arrows, position label above the upward curve
                rad = 0.25  # Match the curve value used above
                # Position the label above the curved line
                label_pos = ((x1 + x2) / 2 + rad * (y2 - y1), 
                            (y1 + y2) / 2 + rad * (x1 - x2))
            else:
                # Standard curve
                rad = 0.15
                # Compute angle to determine curve direction
                angle = np.arctan2(y2 - y1, x2 - x1)
                if -np.pi/2 <= angle <= np.pi/2:
                    rad = abs(rad)
                else:
                    rad = -abs(rad)
                
                # Middle position with offset based on curve
                label_pos = ((x1 + x2) / 2 + rad * (y2 - y1), 
                            (y1 + y2) / 2 + rad * (x1 - x2))
        
        # Create background for better visibility
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
        
        # Draw the label
        ax.text(label_pos[0], label_pos[1], label, size=9, ha='center', va='center',
               bbox=bbox_props, color='black', zorder=5, fontweight='bold')
    
    # Draw initial state markers
    for node in G.nodes():
        if G.nodes[node]['is_initial']:
            # Draw a nicer arrow pointing to the initial state
            node_pos = pos[node]
            offset = 0.15  # Arrow starting point offset
            dx, dy = -offset, 0  # Direction for the arrow (from left to right)
            
            # Create a fancy arrow
            start_point = (node_pos[0] + dx - 0.1, node_pos[1] + dy)
            end_point = (node_pos[0] - 0.02, node_pos[1])
            
            # Add a fancy arrow with gradient
            arrow = FancyArrowPatch(start_point, end_point,
                                 arrowstyle='->',
                                 mutation_scale=20,
                                 linewidth=2,
                                 color='black',
                                 zorder=3)
            ax.add_patch(arrow)
    
    # Set title with nice styling
    ax.set_title(f"Automaton: {automaton.name}", fontsize=14, fontweight='bold', 
                pad=20, color='#2F4F4F')
    
    # Remove axes
    ax.axis('off')
    
    # Add a subtle grid in the background
    ax.grid(False)
    
    # Add a light border around the plot area
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#DDDDDD')
        spine.set_linewidth(1)
    
    # Ensure proper spacing
    plt.tight_layout()
    
    return fig

def save_automaton_image(automaton: Automaton, filename: str, directory: str = "Automates", 
                         format: str = "png", **kwargs) -> str:
    """
    Save an automaton visualization to a file with enhanced quality.
    
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
    
    # Save figure with high DPI for better quality
    dpi = 300 if format == 'png' else 100
    fig.savefig(file_path, format=format, bbox_inches='tight', dpi=dpi, facecolor=fig.get_facecolor())
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
    fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
    ax = fig.add_subplot(111)
    ax.set_facecolor(COLOR_PALETTE['background'])
    visualize_automaton(automaton, ax=ax)
    
    # Improved title with better styling
    title = f"Initial state: Processing word '{word}'"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#2F4F4F')
    
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
                fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
                ax = fig.add_subplot(111)
                ax.set_facecolor(COLOR_PALETTE['background'])
                visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
                
                title = f"No transition for symbol '{symbol}' from state {current_state.name}. Word rejected."
                ax.set_title(title, fontsize=14, fontweight='bold', color='#FF0000')
                
                frames.append(fig)
                break
            
            next_state = next(iter(next_states))
            
            # Record this transition for highlighting
            path_so_far.append((current_state.name, next_state.name, symbol))
            
            # Visualize current step
            fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
            ax = fig.add_subplot(111)
            ax.set_facecolor(COLOR_PALETTE['background'])
            visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
            
            title = f"Processed: '{processed_word}', Current state: {next_state.name}"
            ax.set_title(title, fontsize=14, fontweight='bold', color='#2F4F4F')
            
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
                fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
                ax = fig.add_subplot(111)
                ax.set_facecolor(COLOR_PALETTE['background'])
                visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
                
                title = f"No transitions for symbol '{symbol}'. Word rejected."
                ax.set_title(title, fontsize=14, fontweight='bold', color='#FF0000')
                
                frames.append(fig)
                break
            
            # Visualize current step
            fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
            ax = fig.add_subplot(111)
            ax.set_facecolor(COLOR_PALETTE['background'])
            visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
            
            current_states_names = ", ".join(s.name for s in next_states_set)
            title = f"Processed: '{processed_word}', Current states: {current_states_names}"
            ax.set_title(title, fontsize=14, fontweight='bold', color='#2F4F4F')
            
            frames.append(fig)
            
            current_states = next_states_set
    
    # Final state with enhanced styling
    if automaton.is_deterministic():
        if current_state.is_final:
            accepted = True
            message = f"Word '{word}' is ACCEPTED. Ended in final state {current_state.name}."
            title_color = '#008000'  # Green for accepted
        else:
            accepted = False
            message = f"Word '{word}' is REJECTED. Ended in non-final state {current_state.name}."
            title_color = '#FF0000'  # Red for rejected
    else:
        if any(state.is_final for state in current_states):
            accepted = True
            final_states = [s.name for s in current_states if s.is_final]
            message = f"Word '{word}' is ACCEPTED. Ended in final states: {', '.join(final_states)}."
            title_color = '#008000'  # Green for accepted
        else:
            accepted = False
            message = f"Word '{word}' is REJECTED. No final states reached."
            title_color = '#FF0000'  # Red for rejected
    
    fig = plt.figure(figsize=(10, 8), facecolor=COLOR_PALETTE['background'])
    ax = fig.add_subplot(111)
    ax.set_facecolor(COLOR_PALETTE['background'])
    visualize_automaton(automaton, highlight_path=path_so_far, ax=ax)
    
    # Add a background box to the title for emphasis
    title_bbox = dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8, edgecolor=title_color)
    ax.set_title(message, fontsize=14, fontweight='bold', color=title_color, bbox=title_bbox)
    
    frames.append(fig)
    
    # Save frames with improved quality if requested
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        for i, fig in enumerate(frames):
            fig.savefig(f"{save_path}_{i}.png", bbox_inches='tight', dpi=200, facecolor=fig.get_facecolor())
    
    return frames 