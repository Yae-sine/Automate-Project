import sys
import os
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

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
    
    # Run application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 