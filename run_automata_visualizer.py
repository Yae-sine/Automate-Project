"""
Automata Visualizer & Simulator

A GUI application for designing, analyzing, and simulating finite automata (DFA/NFA).
"""

import os
import sys

def main():
    """Run the Automata Visualizer application."""
    # Add the project directory to the path
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AutomataProject")
    sys.path.insert(0, project_path)
    
    # Import and run the application
    from AutomataProject.main import main as run_app
    run_app()

if __name__ == "__main__":
    main() 