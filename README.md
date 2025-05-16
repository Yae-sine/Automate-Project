# Automata Visualizer & Simulator

A Python GUI application to design, analyze, and simulate finite automata (DFA/NFA).

## Features

### Core Automata Management
- Object-oriented model with classes for State, Transition, Alphabet, and Automaton
- Save/load automata to/from JSON files
- Create, edit, and delete automata with a user-friendly interface

### Visualization
- Interactive graph visualization of automata
- Step-by-step animation of word processing
- Export visualizations as PNG/SVG images

### Analysis & Transformations
- Check if an automaton is deterministic, complete, or minimal
- Convert NFA to DFA (subset construction)
- Minimize automata (Hopcroft's algorithm)
- Complete incomplete automata
- Verify equivalence between automata

### Word & Language Processing
- Test if a word is accepted by an automaton
- Animate word recognition steps
- Generate all accepted words up to a given length
- Perform language operations: union, intersection, and complement

## Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5
- NetworkX
- Matplotlib

### Dependencies Installation
```bash
pip install PyQt5 networkx matplotlib
```

### Running the Application
1. Clone or download this repository
2. Navigate to the project directory
3. Run the application:

```bash
python main.py
```

## Usage Guide

### Creating a New Automaton
1. Click on the "Editor" tab
2. Click "New" button
3. Enter a name for the automaton
4. Add symbols to the alphabet using the "Add Symbol" button
5. Add states using the "Add State" section (check "Initial" or "Final" as needed)
6. Add transitions by selecting source state, symbol, and target state
7. Click "Save" to save the automaton

### Loading an Automaton
1. Navigate to the "Automata" tab
2. Select an automaton from the list or use the "Load" button to load from a file
3. The automaton will be displayed in the visualization panel

### Analyzing an Automaton
1. Load an automaton
2. Go to the "Analysis" tab
3. The automaton's properties will be displayed at the top
4. Use the transformation buttons to convert to DFA, minimize, etc.
5. Use the "Visualize Result" button to view the transformed automaton
6. Use the "Save Result as New Automaton" to save the result

### Testing Word Recognition
1. Load an automaton
2. Go to the "Word Processing" tab
3. Enter a word in the input field
4. Click "Test Word" to check if the word is accepted
5. Click "Animate Processing" to see step-by-step visualization

### Generating Words
1. Load an automaton
2. Go to the "Word Processing" tab
3. Set the maximum length for generated words
4. Click "Generate Words" to list all accepted words up to that length

## Project Structure

- `automata/`: Core classes for automata representation
  - `state.py`: State class
  - `alphabet.py`: Alphabet class
  - `transition.py`: Transition class
  - `automaton.py`: Automaton class with algorithms
- `gui/`: GUI components
  - `main_window.py`: Main application window
  - `automaton_tab.py`: Tab for listing and loading automata
  - `editor_tab.py`: Tab for creating and editing automata
  - `analysis_tab.py`: Tab for analyzing and transforming automata
  - `word_processing_tab.py`: Tab for word processing and language operations
- `utils/`: Utility functions
  - `visualization.py`: Functions for visualizing automata
- `Automates/`: Directory for storing automata JSON files
- `main.py`: Application entry point 