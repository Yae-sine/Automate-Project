from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QGroupBox, QTextEdit, QMessageBox, QCheckBox,
                          QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os

from automata.automaton import Automaton
from utils.visualization import visualize_automaton, node_positions
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
        self.operation_automaton = None
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Status group
        self.status_group = QGroupBox("Automaton Status")
        self.status_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.status_layout = QVBoxLayout(self.status_group)
        self.status_layout.setContentsMargins(10, 15, 10, 10)
        
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
        self.transform_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.transform_layout = QVBoxLayout(self.transform_group)
        self.transform_layout.setContentsMargins(10, 15, 10, 10)
        
        self.transform_buttons = QHBoxLayout()
        
        # Style all buttons
        button_style = "QPushButton { padding: 4px 8px; }"
        
        self.to_dfa_button = QPushButton("Convert to DFA")
        self.to_dfa_button.clicked.connect(self.to_dfa)
        self.to_dfa_button.setStyleSheet(button_style)
        self.transform_buttons.addWidget(self.to_dfa_button)
        
        self.complete_button = QPushButton("Make Complete")
        self.complete_button.clicked.connect(self.make_complete)
        self.complete_button.setStyleSheet(button_style)
        self.transform_buttons.addWidget(self.complete_button)
        
        self.minimize_button = QPushButton("Minimize")
        self.minimize_button.clicked.connect(self.minimize)
        self.minimize_button.setStyleSheet(button_style)
        self.transform_buttons.addWidget(self.minimize_button)
        
        self.complement_button = QPushButton("Complement")
        self.complement_button.clicked.connect(self.complement)
        self.complement_button.setStyleSheet(button_style)
        self.transform_buttons.addWidget(self.complement_button)
        
        self.transform_layout.addLayout(self.transform_buttons)
        
        self.layout.addWidget(self.transform_group)
        
        # Operations group
        self.operations_group = QGroupBox("Operations with Another Automaton")
        self.operations_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.operations_layout = QVBoxLayout(self.operations_group)
        self.operations_layout.setContentsMargins(10, 15, 10, 10)
        
        # Add selector for second automaton
        self.selector_layout = QHBoxLayout()
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        self.second_automaton_label = QLabel("Select second automaton:")
        self.second_automaton_label.setFont(bold_font)
        self.selector_layout.addWidget(self.second_automaton_label)
        
        self.second_automaton_combo = QComboBox()
        self.second_automaton_combo.setStyleSheet("QComboBox { padding: 4px; border: 1px solid #ccc; border-radius: 3px; }")
        self.second_automaton_combo.currentIndexChanged.connect(self.on_second_automaton_selected)
        self.selector_layout.addWidget(self.second_automaton_combo, 1)
        
        self.refresh_automata_button = QPushButton("Refresh List")
        self.refresh_automata_button.setStyleSheet(button_style)
        self.refresh_automata_button.clicked.connect(self.refresh_automata_list)
        self.selector_layout.addWidget(self.refresh_automata_button)
        
        self.operations_layout.addLayout(self.selector_layout)
        
        self.operations_label = QLabel("No automaton selected for operations")
        self.operations_label.setAlignment(Qt.AlignCenter)
        self.operations_label.setStyleSheet("QLabel { background-color: #f5f5f5; padding: 5px; border-radius: 3px; }")
        self.operations_layout.addWidget(self.operations_label)
        
        self.operations_buttons = QHBoxLayout()
        
        self.union_button = QPushButton("Union")
        self.union_button.clicked.connect(self.union)
        self.union_button.setStyleSheet(button_style)
        self.operations_buttons.addWidget(self.union_button)
        
        self.intersection_button = QPushButton("Intersection")
        self.intersection_button.clicked.connect(self.intersection)
        self.intersection_button.setStyleSheet(button_style)
        self.operations_buttons.addWidget(self.intersection_button)
        
        self.equivalence_button = QPushButton("Check Equivalence")
        self.equivalence_button.clicked.connect(self.check_equivalence)
        self.equivalence_button.setStyleSheet(button_style)
        self.operations_buttons.addWidget(self.equivalence_button)
        
        self.operations_layout.addLayout(self.operations_buttons)
        
        self.layout.addWidget(self.operations_group)
        
        # Console/log
        self.log_group = QGroupBox("Operation Log")
        self.log_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.log_layout = QVBoxLayout(self.log_group)
        self.log_layout.setContentsMargins(10, 15, 10, 10)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QTextEdit { border: 1px solid #ddd; font-family: Consolas, Monaco, monospace; }")
        self.log_layout.addWidget(self.log_text)
        
        self.layout.addWidget(self.log_group)
        
        # Result actions
        self.result_actions = QHBoxLayout()
        
        self.visualize_result_button = QPushButton("Visualize Result")
        self.visualize_result_button.clicked.connect(self.visualize_result)
        self.visualize_result_button.setEnabled(False)
        self.visualize_result_button.setStyleSheet(button_style)
        self.result_actions.addWidget(self.visualize_result_button)
        
        self.save_result_button = QPushButton("Save Result as New Automaton")
        self.save_result_button.clicked.connect(self.save_result)
        self.save_result_button.setEnabled(False)
        self.save_result_button.setStyleSheet(button_style)
        self.result_actions.addWidget(self.save_result_button)
        
        self.layout.addLayout(self.result_actions)
        
        # Initialize the automata list
        self.refresh_automata_list()
    
    def refresh_automata_list(self):
        """Refresh the list of available automata for operations."""
        current_selection = self.second_automaton_combo.currentText()
        
        self.second_automaton_combo.clear()
        self.second_automaton_combo.addItem("-- Select Automaton --")
        
        try:
            # Get all saved automaton names
            automata_names = Automaton.list_saved_automata()
            
            # Filter out empty or invalid names
            valid_automata = []
            for name in automata_names:
                if not name or not name.strip():
                    continue
                    
                # Verify the file actually exists
                file_path = os.path.join("Automates", f"{name}.json")
                if not os.path.exists(file_path):
                    self.log(f"Warning: Listed automaton '{name}' has no file at {file_path}")
                    continue
                    
                valid_automata.append(name)
            
            # Sort alphabetically for better user experience
            for name in sorted(valid_automata):
                # Skip the current automaton (can't perform operations with itself)
                if self.current_automaton is None or name != self.current_automaton.name:
                    self.second_automaton_combo.addItem(name)
                    
            # If no automata available besides the current one, inform the user
            if self.second_automaton_combo.count() <= 1:
                self.log("No other automata available for operations. Create or load more automata.")
        except Exception as e:
            self.log(f"Error refreshing automata list: {str(e)}")
        
        # Restore previous selection if possible
        if current_selection:
            index = self.second_automaton_combo.findText(current_selection)
            if index >= 0:
                self.second_automaton_combo.setCurrentIndex(index)
    
    def on_second_automaton_selected(self):
        """Handle selection of second automaton from dropdown."""
        selected_name = self.second_automaton_combo.currentText()
        if selected_name == "-- Select Automaton --" or not selected_name or selected_name.strip() == "":
            self.operation_automaton = None
            self.operations_label.setText("No automaton selected for operations")
            self.operations_label.setStyleSheet("QLabel { background-color: #f5f5f5; padding: 5px; border-radius: 3px; }")
            self.update_button_states()
            return
            
        try:
            # Validate that we have a proper name and file exists
            file_path = os.path.join("Automates", f"{selected_name}.json")
            if not os.path.exists(file_path):
                self.log(f"Error: Automaton file for '{selected_name}' does not exist at path: {file_path}")
                self.operations_label.setText(f"Error: File not found for {selected_name}")
                self.operations_label.setStyleSheet("QLabel { background-color: #ffebee; padding: 5px; border-radius: 3px; color: red; }")
                self.operation_automaton = None
                self.update_button_states()
                return
            
            # Attempt to load the automaton
            try:
                self.operation_automaton = Automaton.load_from_file(file_path)
                self.operations_label.setText(f"Operations with: {selected_name}")
                self.operations_label.setStyleSheet("QLabel { background-color: #e8f0fe; padding: 5px; border-radius: 3px; font-weight: bold; }")
                self.log(f"Selected second automaton: {selected_name}")
            except Exception as load_error:
                self.log(f"Error loading automaton '{selected_name}': {str(load_error)}")
                self.operations_label.setText(f"Error loading: {selected_name}")
                self.operations_label.setStyleSheet("QLabel { background-color: #ffebee; padding: 5px; border-radius: 3px; color: red; }")
                self.operation_automaton = None
        except Exception as e:
            self.log(f"Unexpected error with automaton '{selected_name}': {str(e)}")
            self.operations_label.setText(f"Error with: {selected_name}")
            self.operations_label.setStyleSheet("QLabel { background-color: #ffebee; padding: 5px; border-radius: 3px; color: red; }")
            self.operation_automaton = None
        
        self.update_button_states()
    
    def set_current_automaton(self, automaton):
        """Set the current automaton for analysis."""
        self.current_automaton = automaton
        self.update_status()
        
        self.log_text.clear()
        self.log(f"Loaded automaton: {automaton.name}")
        
        # Refresh second automaton dropdown to exclude current automaton
        self.refresh_automata_list()
        
        # Enable/disable buttons
        self.update_button_states()
    
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
        has_both = self.operation_automaton is not None
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
            self.log("\n" + "-"*50)
            self.log(f"Converting {self.current_automaton.name} to DFA...")
            
            if self.current_automaton.is_deterministic():
                self.log("Automaton is already a DFA. No conversion needed.")
                return
            
            self.result_automaton = self.current_automaton.to_deterministic()
            
            self.log(f"Conversion complete. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, DFA states: {len(self.result_automaton.states)}")
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error converting to DFA: {str(e)}")
    
    def make_complete(self):
        """Make the current automaton complete."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Making {self.current_automaton.name} complete...")
            
            if self.current_automaton.is_complete():
                self.log("Automaton is already complete. No changes needed.")
                return
            
            self.result_automaton = self.current_automaton.complete()
            
            self.log(f"Completion successful. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, Complete automaton states: {len(self.result_automaton.states)}")
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error completing automaton: {str(e)}")
    
    def minimize(self):
        """Minimize the current automaton."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Minimizing {self.current_automaton.name}...")
            
            if not self.current_automaton.is_deterministic():
                self.log("Cannot minimize non-deterministic automaton. Convert to DFA first.")
                return
            
            if self.current_automaton.is_minimal():
                self.log("Automaton is already minimal. No changes needed.")
                return
            
            self.result_automaton = self.current_automaton.minimize()
            
            self.log(f"Minimization successful. Result: {self.result_automaton.name}")
            self.log(f"Original states: {len(self.current_automaton.states)}, Minimized states: {len(self.result_automaton.states)}")
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error minimizing automaton: {str(e)}")
    
    def complement(self):
        """Compute the complement of the current automaton."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Computing complement of {self.current_automaton.name}...")
            
            self.result_automaton = self.current_automaton.get_complement()
            
            self.log(f"Complement computed. Result: {self.result_automaton.name}")
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            self.log(f"Error computing complement: {str(e)}")
    
    def union(self):
        """Compute the union of the current automaton with another one."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
            
        if not self.operation_automaton:
            self.log("No second automaton selected for union operation")
            self.show_message("Missing Automaton", "Please select a second automaton for the union operation")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Computing union of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            # Validate both automata
            if not self.current_automaton.states:
                self.log(f"Error: The current automaton '{self.current_automaton.name}' has no states")
                return
                
            if not self.operation_automaton.states:
                self.log(f"Error: The second automaton '{self.operation_automaton.name}' has no states")
                return
                
            # Check for compatible alphabets
            alphabet1 = self.current_automaton.alphabet.symbols
            alphabet2 = self.operation_automaton.alphabet.symbols
            combined_alphabet = alphabet1.union(alphabet2)
            
            self.log(f"Combined alphabet symbols: {', '.join(sorted(combined_alphabet))}")
            
            # Perform the union operation
            self.result_automaton = self.current_automaton.union(self.operation_automaton)
            
            # Log success and details
            self.log(f"Union computed. Result: {self.result_automaton.name}")
            self.log(f"Result has {len(self.result_automaton.states)} states and {len(self.result_automaton.transitions)} transitions")
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error computing union: {str(e)}")
            self.log(f"Error details: {error_details}")
            self.show_message("Error", f"Failed to compute union: {str(e)}")
    
    def intersection(self):
        """Compute the intersection of the current automaton with another one."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
            
        if not self.operation_automaton:
            self.log("No second automaton selected for intersection operation")
            self.show_message("Missing Automaton", "Please select a second automaton for the intersection operation")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Computing intersection of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            # Validate both automata
            if not self.current_automaton.states:
                self.log(f"Error: The current automaton '{self.current_automaton.name}' has no states")
                return
                
            if not self.operation_automaton.states:
                self.log(f"Error: The second automaton '{self.operation_automaton.name}' has no states")
                return
            
            # Check for compatible alphabets
            alphabet1 = self.current_automaton.alphabet.symbols
            alphabet2 = self.operation_automaton.alphabet.symbols
            shared_symbols = alphabet1.intersection(alphabet2)
            
            if not shared_symbols:
                self.log(f"Warning: The automata have no common alphabet symbols. Intersection might be empty.")
            else:
                self.log(f"Common alphabet symbols: {', '.join(sorted(shared_symbols))}")
            
            # Perform the intersection operation
            self.result_automaton = self.current_automaton.intersection(self.operation_automaton)
            
            # Log success and details
            self.log(f"Intersection computed. Result: {self.result_automaton.name}")
            self.log(f"Result has {len(self.result_automaton.states)} states and {len(self.result_automaton.transitions)} transitions")
            
            if len(self.result_automaton.states) == 0 or len(self.result_automaton.get_final_states()) == 0:
                self.log("The intersection appears to be empty (no states or no final states).")
            
            self.log("-"*50)
            
            self.update_button_states()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error computing intersection: {str(e)}")
            self.log(f"Error details: {error_details}")
            self.show_message("Error", f"Failed to compute intersection: {str(e)}")
    
    def check_equivalence(self):
        """Check if the current automaton is equivalent to another one."""
        if not self.current_automaton:
            self.log("No automaton loaded")
            return
            
        if not self.operation_automaton:
            self.log("No second automaton selected for equivalence check")
            self.show_message("Missing Automaton", "Please select a second automaton for the equivalence check")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Checking equivalence of {self.current_automaton.name} and {self.operation_automaton.name}...")
            
            # Validate both automata
            if not self.current_automaton.states:
                self.log(f"Error: The current automaton '{self.current_automaton.name}' has no states")
                return
                
            if not self.operation_automaton.states:
                self.log(f"Error: The second automaton '{self.operation_automaton.name}' has no states")
                return
                
            # Check alphabets
            alphabet1 = self.current_automaton.alphabet.symbols
            alphabet2 = self.operation_automaton.alphabet.symbols
            
            if alphabet1 != alphabet2:
                self.log(f"Warning: Automata have different alphabets.")
                self.log(f"A: {', '.join(sorted(alphabet1))}")
                self.log(f"B: {', '.join(sorted(alphabet2))}")
                self.log("Alphabets will be unified for equivalence check.")
            
            # Perform the equivalence check
            are_equivalent = self.current_automaton.are_equivalent(self.operation_automaton)
            
            if are_equivalent:
                self.log(f"The automata are EQUIVALENT")
                self.show_message("Equivalence Check", f"The automata {self.current_automaton.name} and {self.operation_automaton.name} are EQUIVALENT.")
            else:
                self.log(f"The automata are NOT equivalent")
                self.show_message("Equivalence Check", f"The automata {self.current_automaton.name} and {self.operation_automaton.name} are NOT equivalent.")
            
            self.log("-"*50)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error checking equivalence: {str(e)}")
            self.log(f"Error details: {error_details}")
            self.show_message("Error", f"Failed to check equivalence: {str(e)}")
    
    def visualize_result(self):
        """Visualize the result automaton."""
        if not self.result_automaton:
            self.log("No result automaton to visualize")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Visualizing result automaton: {self.result_automaton.name}")
            
            # Clear previous visualization
            for i in reversed(range(self.parent.visualization_layout.count())):
                widget = self.parent.visualization_layout.itemAt(i).widget()
                if widget != self.parent.visualization_label:
                    widget.setParent(None)
            
            # Create visualization with consistent positioning
            fig = visualize_automaton(self.result_automaton, reuse_positions=True)
            canvas = FigureCanvas(fig)
            
            # Add to the visualization panel
            self.parent.visualization_layout.addWidget(canvas)
            self.parent.visualization_label.setText(f"Result: {self.result_automaton.name}")
            
            self.log("Visualization complete")
            self.log("-"*50)
        except Exception as e:
            self.log(f"Error visualizing result: {str(e)}")
    
    def save_result(self):
        """Save the result automaton."""
        if not self.result_automaton:
            self.log("No result automaton to save")
            return
        
        try:
            self.log("\n" + "-"*50)
            self.log(f"Saving result automaton: {self.result_automaton.name}")
            
            # Save the automaton
            file_path = self.result_automaton.save_to_file()
            self.log(f"Result saved as: {self.result_automaton.name}")
            self.log(f"File: {file_path}")
            self.log("-"*50)
            
            # Emit signal to refresh list in automaton tab
            self.automaton_created.emit(self.result_automaton)
            
            # Refresh the second automaton dropdown
            self.refresh_automata_list()
        except Exception as e:
            self.log(f"Error saving result: {str(e)}")
    
    def show_message(self, title, message):
        """Show a message dialog."""
        QMessageBox.information(self, title, message) 