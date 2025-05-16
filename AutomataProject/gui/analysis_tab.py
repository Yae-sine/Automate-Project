from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QGroupBox, QTextEdit, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

from automata.automaton import Automaton
from utils.visualization import visualize_automaton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AnalysisTab(QWidget):
    """Tab for analyzing automata and performing transformations."""
    
    # Signal emitted when an automaton is created through a transformation
    automaton_created = pyqtSignal(Automaton)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_automaton = None
        self.result_automaton = None
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Status group
        self.status_group = QGroupBox("Automaton Status")
        self.status_layout = QVBoxLayout(self.status_group)
        
        self.status_label = QLabel("No automaton loaded")
        self.status_layout.addWidget(self.status_label)
        
        self.status_checks = QHBoxLayout()
        
        self.is_deterministic_check = QCheckBox("Deterministic")
        self.is_deterministic_check.setEnabled(False)
        self.status_checks.addWidget(self.is_deterministic_check)
        
        self.is_complete_check = QCheckBox("Complete")
        self.is_complete_check.setEnabled(False)
        self.status_checks.addWidget(self.is_complete_check)
        
        self.is_minimal_check = QCheckBox("Minimal")
        self.is_minimal_check.setEnabled(False)
        self.status_checks.addWidget(self.is_minimal_check)
        
        self.status_layout.addLayout(self.status_checks)
        
        self.layout.addWidget(self.status_group)
        
        # Transformation group
        self.transform_group = QGroupBox("Transformations")
        self.transform_layout = QVBoxLayout(self.transform_group)
        
        self.transform_buttons = QHBoxLayout()
        
        self.to_dfa_button = QPushButton("Convert to DFA")
        self.to_dfa_button.clicked.connect(self.to_dfa)
        self.transform_buttons.addWidget(self.to_dfa_button)
        
        self.complete_button = QPushButton("Make Complete")
        self.complete_button.clicked.connect(self.make_complete)
        self.transform_buttons.addWidget(self.complete_button)
        
        self.minimize_button = QPushButton("Minimize")
        self.minimize_button.clicked.connect(self.minimize)
        self.transform_buttons.addWidget(self.minimize_button)
        
        self.complement_button = QPushButton("Complement")
        self.complement_button.clicked.connect(self.complement)
        self.transform_buttons.addWidget(self.complement_button)
        
        self.transform_layout.addLayout(self.transform_buttons)
        
        self.layout.addWidget(self.transform_group)
        
        # Operations group
        self.operations_group = QGroupBox("Operations with Another Automaton")
        self.operations_layout = QVBoxLayout(self.operations_group)
        
        self.operations_label = QLabel("No automaton loaded for operations")
        self.operations_layout.addWidget(self.operations_label)
        
        self.operations_buttons = QHBoxLayout()
        
        self.union_button = QPushButton("Union")
        self.union_button.clicked.connect(self.union)
        self.operations_buttons.addWidget(self.union_button)
        
        self.intersection_button = QPushButton("Intersection")
        self.intersection_button.clicked.connect(self.intersection)
        self.operations_buttons.addWidget(self.intersection_button)
        
        self.equivalence_button = QPushButton("Check Equivalence")
        self.equivalence_button.clicked.connect(self.check_equivalence)
        self.operations_buttons.addWidget(self.equivalence_button)
        
        self.operations_layout.addLayout(self.operations_buttons)
        
        self.layout.addWidget(self.operations_group)
        
        # Console/log
        self.log_group = QGroupBox("Operation Log")
        self.log_layout = QVBoxLayout(self.log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_layout.addWidget(self.log_text)
        
        self.layout.addWidget(self.log_group)
        
        # Result actions
        self.result_actions = QHBoxLayout()
        
        self.visualize_result_button = QPushButton("Visualize Result")
        self.visualize_result_button.clicked.connect(self.visualize_result)
        self.visualize_result_button.setEnabled(False)
        self.result_actions.addWidget(self.visualize_result_button)
        
        self.save_result_button = QPushButton("Save Result as New Automaton")
        self.save_result_button.clicked.connect(self.save_result)
        self.save_result_button.setEnabled(False)
        self.result_actions.addWidget(self.save_result_button)
        
        self.layout.addLayout(self.result_actions)
    
    def set_current_automaton(self, automaton):
        """Set the current automaton for analysis."""
        self.current_automaton = automaton
        self.update_status()
        
        self.log_text.clear()
        self.log("Loaded automaton: " + automaton.name)
        
        # Enable/disable buttons
        self.update_button_states()
    
    def set_operation_automaton(self, automaton):
        """Set the automaton for binary operations."""
        self.operation_automaton = automaton
        self.operations_label.setText(f"Operations with: {automaton.name}")
        
        # Enable operations buttons
        self.union_button.setEnabled(True)
        self.intersection_button.setEnabled(True)
        self.equivalence_button.setEnabled(True)
    
    def update_status(self):
        """Update status information about the current automaton."""
        if not self.current_automaton:
            self.status_label.setText("No automaton loaded")
            self.is_deterministic_check.setChecked(False)
            self.is_complete_check.setChecked(False)
            self.is_minimal_check.setChecked(False)
            return
        
        name = self.current_automaton.name
        states_count = len(self.current_automaton.states)
        transitions_count = len(self.current_automaton.transitions)
        
        self.status_label.setText(
            f"Automaton: {name}\n"
            f"States: {states_count}, Transitions: {transitions_count}"
        )
        
        # Check properties
        is_deterministic = self.current_automaton.is_deterministic()
        self.is_deterministic_check.setChecked(is_deterministic)
        
        is_complete = self.current_automaton.is_complete()
        self.is_complete_check.setChecked(is_complete)
        
        is_minimal = False
        if is_deterministic:
            is_minimal = self.current_automaton.is_minimal()
        self.is_minimal_check.setChecked(is_minimal)
    
    def update_button_states(self):
        """Update the enabled/disabled state of buttons based on the current automaton."""
        has_automaton = self.current_automaton is not None
        
        # Transform buttons
        self.to_dfa_button.setEnabled(has_automaton)
        self.complete_button.setEnabled(has_automaton and self.current_automaton.is_deterministic())
        self.minimize_button.setEnabled(has_automaton and self.current_automaton.is_deterministic())
        self.complement_button.setEnabled(has_automaton)
        
        # Result buttons
        self.visualize_result_button.setEnabled(self.result_automaton is not None)
        self.save_result_button.setEnabled(self.result_automaton is not None)
        
        # Operations buttons (need both automata)
        has_both = hasattr(self, 'operation_automaton') and self.operation_automaton is not None
        self.union_button.setEnabled(has_automaton and has_both)
        self.intersection_button.setEnabled(has_automaton and has_both)
        self.equivalence_button.setEnabled(has_automaton and has_both)
    
    def log(self, message):
        """Add a message to the log."""
        self.log_text.append(message)
    
    def to_dfa(self):
        """Convert the current automaton to a DFA."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            start_time = self.log(f"Converting {self.current_automaton.name} to DFA...")
            
            if self.current_automaton.is_deterministic():
                self.log("Automaton is already a DFA. No conversion needed.")
                return
            
            self.result_automaton = self.current_automaton.to_deterministic()
            
            self.log(f"Conversion complete. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, DFA states: {len(self.result_automaton.states)}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error converting to DFA: {str(e)}")
    
    def make_complete(self):
        """Make the current automaton complete."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log(f"Making {self.current_automaton.name} complete...")
            
            if self.current_automaton.is_complete():
                self.log("Automaton is already complete. No changes needed.")
                return
            
            self.result_automaton = self.current_automaton.complete()
            
            self.log(f"Completion successful. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, Complete automaton states: {len(self.result_automaton.states)}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error completing automaton: {str(e)}")
    
    def minimize(self):
        """Minimize the current automaton."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log(f"Minimizing {self.current_automaton.name}...")
            
            if not self.current_automaton.is_deterministic():
                self.log("Converting to DFA first...")
                automaton = self.current_automaton.to_deterministic()
                self.log("DFA conversion complete.")
            else:
                automaton = self.current_automaton
            
            if not automaton.is_complete():
                self.log("Making automaton complete first...")
                automaton = automaton.complete()
                self.log("Completion successful.")
            
            self.result_automaton = automaton.minimize()
            
            self.log(f"Minimization complete. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, Minimized states: {len(self.result_automaton.states)}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error minimizing automaton: {str(e)}")
    
    def complement(self):
        """Get the complement of the current automaton."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log(f"Computing complement of {self.current_automaton.name}...")
            
            self.result_automaton = self.current_automaton.get_complement()
            
            self.log(f"Complement computation complete. Result: {self.result_automaton.name}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error computing complement: {str(e)}")
    
    def union(self):
        """Compute the union of current and operation automata."""
        if not self.current_automaton or not hasattr(self, 'operation_automaton') or not self.operation_automaton:
            self.log("Need two automata for union operation")
            return
        
        try:
            self.log(f"Computing union of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            self.result_automaton = self.current_automaton.union(self.operation_automaton)
            
            self.log(f"Union computation complete. Result: {self.result_automaton.name}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error computing union: {str(e)}")
    
    def intersection(self):
        """Compute the intersection of current and operation automata."""
        if not self.current_automaton or not hasattr(self, 'operation_automaton') or not self.operation_automaton:
            self.log("Need two automata for intersection operation")
            return
        
        try:
            self.log(f"Computing intersection of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            self.result_automaton = self.current_automaton.intersection(self.operation_automaton)
            
            self.log(f"Intersection computation complete. Result: {self.result_automaton.name}")
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error computing intersection: {str(e)}")
    
    def check_equivalence(self):
        """Check if the current and operation automata are equivalent."""
        if not self.current_automaton or not hasattr(self, 'operation_automaton') or not self.operation_automaton:
            self.log("Need two automata to check equivalence")
            return
        
        try:
            self.log(f"Checking equivalence of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            are_equivalent = self.current_automaton.are_equivalent(self.operation_automaton)
            
            if are_equivalent:
                self.log("Automata are EQUIVALENT (they accept the same language)")
            else:
                self.log("Automata are NOT EQUIVALENT (they accept different languages)")
        except Exception as e:
            self.log(f"Error checking equivalence: {str(e)}")
    
    def visualize_result(self):
        """Visualize the result automaton."""
        if not self.result_automaton:
            self.log("No result automaton to visualize")
            return
        
        try:
            # Clear previous visualization
            for i in reversed(range(self.parent.visualization_layout.count())):
                widget = self.parent.visualization_layout.itemAt(i).widget()
                if widget != self.parent.visualization_label:
                    widget.setParent(None)
            
            # Create visualization
            fig = visualize_automaton(self.result_automaton)
            canvas = FigureCanvas(fig)
            
            # Add to the visualization panel
            self.parent.visualization_layout.addWidget(canvas)
            self.parent.visualization_label.setText(f"Result Automaton: {self.result_automaton.name}")
        except Exception as e:
            self.log(f"Error visualizing result: {str(e)}")
    
    def save_result(self):
        """Save the result automaton as a new automaton."""
        if not self.result_automaton:
            self.log("No result automaton to save")
            return
        
        try:
            file_path = self.result_automaton.save_to_file()
            self.log(f"Saved result automaton to {file_path}")
            
            self.automaton_created.emit(self.result_automaton)
            
            # Refresh automata list in the Automaton tab
            if hasattr(self.parent, 'automaton_tab'):
                self.parent.automaton_tab.refresh_automaton_list()
        except Exception as e:
            self.log(f"Error saving result: {str(e)}")
    
    def show_message(self, title, message):
        """Show a message dialog."""
        QMessageBox.information(self, title, message) 