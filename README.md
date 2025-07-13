# Automata Visualizer & Simulator

A Python GUI application to design, analyze, and simulate finite automata (DFA/NFA).

## Preview
<img width="600" height="700" alt="Screenshot 2025-07-13 220317" src="https://github.com/user-attachments/assets/25d71aaa-6470-458b-8e8e-3b3144911290" /> <br>
<img width="600" height="700" alt="Screenshot 2025-07-13 220349" src="https://github.com/user-attachments/assets/af868e00-95ba-4c83-a83d-8041b6aaf204" /> <br>
<img width="600" height="700" alt="Screenshot 2025-07-13 220416" src="https://github.com/user-attachments/assets/dc75cb3f-b1fe-4c64-889b-d1ed08fd4e77" /> <br>

## Main Features

### Automata Management
- Object-oriented model with classes for State, Transition, Alphabet, and Automaton
- Visual creation and editing of automata with support for initial and final states
- Full automata management (save, load, delete, rename)
- User-friendly interface to manipulate all aspects of automata

### Visualization
- Interactive visualization of automata as graphs
- Step-by-step animation of word processing
- Export visualizations as PNG/SVG images for documentation or presentations

### Analysis and Transformations
- Check if an automaton is deterministic, complete, or minimal
- Analyze fundamental properties of automata
- Automatic transformation of automata (determinization, completion, minimization)
- Operations between automata (union, intersection, equivalence checking)

### Word and Language Processing
- Test if a word is accepted by an automaton
- Animate the automaton's traversal with the option to save animations
- Process words with step-by-step visualization of transitions
- Generate all accepted words up to a given length
- Statistics on recognized languages (number of words accepted by length)


## Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5
- NetworkX
- Matplotlib

### Installing Dependencies
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

## User Guide

### Creating a New Automaton
1. Click on the "Editor" tab
2. Click the "New" button
3. Enter a name for the automaton
4. Add symbols to the alphabet using the "Add Symbol" button
5. Add states using the "Add State" section (check "Initial" or "Final" as needed)
6. Add transitions by selecting the source state, symbol, and target state
7. Click "Save" to save the automaton in the "Automates" directory that will be created

### Loading an Automaton
1. Go to the "Automata" tab
2. Select an automaton from the list or use the "Load" button to load from a file
3. The automaton will be displayed in the visualization panel

### Analyzing an Automaton
1. Load an automaton
2. Go to the "Analysis" tab
3. The automaton's properties will be displayed at the top
4. Use the transformation buttons to convert to DFA, minimize, etc.
5. Use the "Visualize Result" button to see the transformed automaton
6. Use "Save Result as New Automaton" to save the result

### Word Recognition Test
1. Load an automaton
2. Go to the "Word Processing" tab
3. Enter a word in the input field
4. Click "Test Word" to check if the word is accepted
5. Click "Animate Processing" to see the step-by-step visualization

### Word Generation
1. Load an automaton
2. Go to the "Word Processing" tab
3. Set the maximum length for generated words
4. Click "Generate Words" to list all accepted words up to that length

## Project Structure

- `automata/`: Base classes for automata representation
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
- `Automates/`: Directory to store automata JSON files
- `main.py`: Application entry point
