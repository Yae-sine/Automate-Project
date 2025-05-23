import sys
import os

# Add the AutomataProject directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add current directory first

from PyQt5.QtWidgets import QApplication
from AutomataProject.gui import MainWindow

def main():
    """Main entry point for the application."""
    # Create the Automates directory if it doesn't exist
    os.makedirs("Automates", exist_ok=True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Automata Visualizer & Simulator")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Connect signals between tabs
    window.automaton_tab.automaton_selected.connect(window.editor_tab.set_current_automaton)
    window.automaton_tab.automaton_selected.connect(window.analysis_tab.set_current_automaton)
    window.automaton_tab.automaton_selected.connect(window.word_processing_tab.set_current_automaton)
    
    window.editor_tab.automaton_changed.connect(window.analysis_tab.set_current_automaton)
    window.editor_tab.automaton_changed.connect(window.word_processing_tab.set_current_automaton)
    
    # Connect the analysis tab's automaton_created signal to refresh automaton list
    window.analysis_tab.automaton_created.connect(window.automaton_tab.refresh_automaton_list)
    
    # Run application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 