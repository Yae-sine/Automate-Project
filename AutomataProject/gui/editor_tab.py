import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QLineEdit, QComboBox, QGroupBox, QTableWidget,
                          QTableWidgetItem, QCheckBox, QMessageBox, QHeaderView,
                          QInputDialog, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal

from AutomataProject.automata.automaton import Automaton
from AutomataProject.automata.state import State
from AutomataProject.automata.alphabet import Alphabet
from AutomataProject.automata.transition import Transition
from AutomataProject.utils.visualization import visualize_automaton, node_positions
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class EditorTab(QWidget):
    """Tab for creating and editing automata."""
    
    # Signal emitted when an automaton is created or modified
    automaton_changed = pyqtSignal(Automaton)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_automaton = None
        self.has_changes = False
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Automaton name section
        self.name_group = QGroupBox("Automaton Name")
        self.name_layout = QHBoxLayout(self.name_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter automaton name")
        self.name_input.textChanged.connect(self.on_automaton_modified)
        
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.create_new_automaton)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_current_automaton)
        
        self.name_layout.addWidget(self.name_input)
        self.name_layout.addWidget(self.new_button)
        self.name_layout.addWidget(self.save_button)
        
        self.layout.addWidget(self.name_group)
        
        # Alphabet section
        self.alphabet_group = QGroupBox("Alphabet")
        self.alphabet_layout = QVBoxLayout(self.alphabet_group)
        
        self.alphabet_input_layout = QHBoxLayout()
        self.alphabet_input = QLineEdit()
        self.alphabet_input.setPlaceholderText("Enter symbol to add")
        
        self.add_symbol_button = QPushButton("Add Symbol")
        self.add_symbol_button.clicked.connect(self.add_symbol)
        
        self.alphabet_input_layout.addWidget(self.alphabet_input)
        self.alphabet_input_layout.addWidget(self.add_symbol_button)
        
        self.alphabet_list = QComboBox()
        self.alphabet_list.setEditable(False)
        
        self.remove_symbol_button = QPushButton("Remove Symbol")
        self.remove_symbol_button.clicked.connect(self.remove_symbol)
        
        self.alphabet_layout.addLayout(self.alphabet_input_layout)
        self.alphabet_layout.addWidget(self.alphabet_list)
        self.alphabet_layout.addWidget(self.remove_symbol_button)
        
        self.layout.addWidget(self.alphabet_group)
        
        # States section
        self.states_group = QGroupBox("States")
        self.states_layout = QVBoxLayout(self.states_group)
        
        self.states_input_layout = QHBoxLayout()
        self.state_name_input = QLineEdit()
        self.state_name_input.setPlaceholderText("Enter state name")
        
        self.is_initial_check = QCheckBox("Initial")
        self.is_final_check = QCheckBox("Final")
        
        self.add_state_button = QPushButton("Add State")
        self.add_state_button.clicked.connect(self.add_state)
        
        self.states_input_layout.addWidget(self.state_name_input)
        self.states_input_layout.addWidget(self.is_initial_check)
        self.states_input_layout.addWidget(self.is_final_check)
        self.states_input_layout.addWidget(self.add_state_button)
        
        self.states_table = QTableWidget(0, 3)
        self.states_table.setHorizontalHeaderLabels(["Name", "Initial", "Final"])
        self.states_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.states_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.remove_state_button = QPushButton("Remove State")
        self.remove_state_button.clicked.connect(self.remove_state)
        
        self.states_layout.addLayout(self.states_input_layout)
        self.states_layout.addWidget(self.states_table)
        self.states_layout.addWidget(self.remove_state_button)
        
        self.layout.addWidget(self.states_group)
        
        # Transitions section
        self.transitions_group = QGroupBox("Transitions")
        self.transitions_layout = QVBoxLayout(self.transitions_group)
        
        self.transitions_input_layout = QHBoxLayout()
        
        self.from_state_combo = QComboBox()
        self.symbol_combo = QComboBox()
        self.to_state_combo = QComboBox()
        
        self.add_transition_button = QPushButton("Add Transition")
        self.add_transition_button.clicked.connect(self.add_transition)
        
        self.transitions_input_layout.addWidget(QLabel("From:"))
        self.transitions_input_layout.addWidget(self.from_state_combo)
        self.transitions_input_layout.addWidget(QLabel("Symbol:"))
        self.transitions_input_layout.addWidget(self.symbol_combo)
        self.transitions_input_layout.addWidget(QLabel("To:"))
        self.transitions_input_layout.addWidget(self.to_state_combo)
        self.transitions_input_layout.addWidget(self.add_transition_button)
        
        self.transitions_table = QTableWidget(0, 3)
        self.transitions_table.setHorizontalHeaderLabels(["From", "Symbol", "To"])
        self.transitions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transitions_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.remove_transition_button = QPushButton("Remove Transition")
        self.remove_transition_button.clicked.connect(self.remove_transition)
        
        self.transitions_layout.addLayout(self.transitions_input_layout)
        self.transitions_layout.addWidget(self.transitions_table)
        self.transitions_layout.addWidget(self.remove_transition_button)
        
        self.layout.addWidget(self.transitions_group)
        
        # Visualization button
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.clicked.connect(self.visualize_automaton)
        self.layout.addWidget(self.visualize_button)
        
        # Initialize with empty automaton
        self.create_new_automaton()
    
    def create_new_automaton(self):
        """Create a new empty automaton."""
        # Ask for confirmation if there are unsaved changes
        if self.has_changes:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                "You have unsaved changes. Do you want to continue and discard them?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        try:
            # Create a new automaton with a default name
            default_name = "NewAutomaton"
            self.current_automaton = Automaton(default_name)
            self.update_ui_from_automaton()
            self.has_changes = False
            self.parent.statusBar().showMessage(f"Created new automaton: {default_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create new automaton: {str(e)}")
            # If error occurred, create a default automaton
            self.current_automaton = Automaton("DefaultAutomaton")
            self.update_ui_from_automaton()
            self.has_changes = False
            self.parent.statusBar().showMessage("Created default automaton after error")
    
    def update_ui_from_automaton(self):
        """Update the UI to reflect the current automaton."""
        if not self.current_automaton:
            return
        
        # Update name
        self.name_input.setText(self.current_automaton.name)
        
        # Update alphabet
        self.alphabet_list.clear()
        for symbol in sorted(self.current_automaton.alphabet.symbols):
            self.alphabet_list.addItem(symbol)
        
        # Update symbol combo in transitions
        self.symbol_combo.clear()
        for symbol in sorted(self.current_automaton.alphabet.symbols):
            self.symbol_combo.addItem(symbol)
        # Add epsilon for NFAs
        self.symbol_combo.addItem(Transition.EPSILON)
        
        # Update states table
        self.states_table.setRowCount(0)
        for state in self.current_automaton.states:
            row = self.states_table.rowCount()
            self.states_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(state.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 0, name_item)
            
            # Initial
            initial_item = QTableWidgetItem("Yes" if state.is_initial else "No")
            initial_item.setFlags(initial_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 1, initial_item)
            
            # Final
            final_item = QTableWidgetItem("Yes" if state.is_final else "No")
            final_item.setFlags(final_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 2, final_item)
        
        # Update state combos in transitions
        self.from_state_combo.clear()
        self.to_state_combo.clear()
        for state in self.current_automaton.states:
            self.from_state_combo.addItem(state.name)
            self.to_state_combo.addItem(state.name)
        
        # Update transitions table
        self.transitions_table.setRowCount(0)
        for transition in self.current_automaton.transitions:
            row = self.transitions_table.rowCount()
            self.transitions_table.insertRow(row)
            
            # From state
            from_item = QTableWidgetItem(transition.from_state.name)
            from_item.setFlags(from_item.flags() & ~Qt.ItemIsEditable)
            self.transitions_table.setItem(row, 0, from_item)
            
            # Symbol
            symbol_item = QTableWidgetItem(transition.symbol)
            symbol_item.setFlags(symbol_item.flags() & ~Qt.ItemIsEditable)
            self.transitions_table.setItem(row, 1, symbol_item)
            
            # To state
            to_item = QTableWidgetItem(transition.to_state.name)
            to_item.setFlags(to_item.flags() & ~Qt.ItemIsEditable)
            self.transitions_table.setItem(row, 2, to_item)
    
    def add_symbol(self):
        """Add a symbol to the alphabet."""
        symbol = self.alphabet_input.text().strip()
        
        if not symbol:
            QMessageBox.warning(self, "Empty Input", "Please enter a symbol.")
            return
        
        if symbol in self.current_automaton.alphabet.symbols:
            QMessageBox.warning(self, "Duplicate Symbol", f"Symbol '{symbol}' is already in the alphabet.")
            return
        
        if symbol == Transition.EPSILON:
            QMessageBox.warning(self, "Reserved Symbol", f"Symbol '{Transition.EPSILON}' is reserved for epsilon transitions.")
            return
        
        self.current_automaton.alphabet.add_symbol(symbol)
        self.alphabet_input.clear()
        self.on_automaton_modified()
        self.update_ui_from_automaton()
    
    def remove_symbol(self):
        """Remove a symbol from the alphabet."""
        if self.alphabet_list.count() == 0:
            QMessageBox.warning(self, "No Symbols", "There are no symbols to remove.")
            return
        
        symbol = self.alphabet_list.currentText()
        
        # Check if any transitions use this symbol
        for transition in self.current_automaton.transitions:
            if transition.symbol == symbol:
                QMessageBox.warning(
                    self, "Symbol in Use", 
                    f"Cannot remove symbol '{symbol}' because it is used in transitions."
                )
                return
        
        self.current_automaton.alphabet.remove_symbol(symbol)
        self.on_automaton_modified()
        self.update_ui_from_automaton()
    
    def add_state(self):
        """Add a state to the automaton."""
        name = self.state_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Empty Input", "Please enter a state name.")
            return
        
        if self.current_automaton.get_state_by_name(name):
            QMessageBox.warning(self, "Duplicate State", f"State '{name}' already exists.")
            return
        
        is_initial = self.is_initial_check.isChecked()
        is_final = self.is_final_check.isChecked()
        
        state = State(name, is_initial, is_final)
        self.current_automaton.add_state(state)
        
        self.state_name_input.clear()
        self.is_initial_check.setChecked(False)
        self.is_final_check.setChecked(False)
        
        self.on_automaton_modified()
        self.update_ui_from_automaton()
    
    def remove_state(self):
        """Remove a state from the automaton."""
        selected_items = self.states_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a state to remove.")
            return
        
        state_name = self.states_table.item(selected_items[0].row(), 0).text()
        state = self.current_automaton.get_state_by_name(state_name)
        
        if state:
            self.current_automaton.remove_state(state)
            self.on_automaton_modified()
            self.update_ui_from_automaton()
    
    def add_transition(self):
        """Add a transition to the automaton."""
        if self.from_state_combo.count() == 0 or self.to_state_combo.count() == 0:
            QMessageBox.warning(self, "No States", "Please add states first.")
            return
        
        if self.symbol_combo.count() == 0:
            QMessageBox.warning(self, "No Symbols", "Please add symbols to the alphabet first.")
            return
        
        from_state_name = self.from_state_combo.currentText()
        symbol = self.symbol_combo.currentText()
        to_state_name = self.to_state_combo.currentText()
        
        from_state = self.current_automaton.get_state_by_name(from_state_name)
        to_state = self.current_automaton.get_state_by_name(to_state_name)
        
        # Check for duplicate transition
        for transition in self.current_automaton.transitions:
            if (transition.from_state == from_state and 
                transition.symbol == symbol and 
                transition.to_state == to_state):
                QMessageBox.warning(
                    self, "Duplicate Transition", 
                    f"Transition {from_state_name} --({symbol})--> {to_state_name} already exists."
                )
                return
        
        # Add the transition
        success = self.current_automaton.add_transition(from_state, to_state, symbol)
        
        if success:
            self.on_automaton_modified()
            self.update_ui_from_automaton()
        else:
            QMessageBox.warning(
                self, "Invalid Transition", 
                f"Could not add transition with symbol '{symbol}'."
            )
    
    def remove_transition(self):
        """Remove a transition from the automaton."""
        selected_items = self.transitions_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a transition to remove.")
            return
        
        row = selected_items[0].row()
        from_state_name = self.transitions_table.item(row, 0).text()
        symbol = self.transitions_table.item(row, 1).text()
        to_state_name = self.transitions_table.item(row, 2).text()
        
        from_state = self.current_automaton.get_state_by_name(from_state_name)
        to_state = self.current_automaton.get_state_by_name(to_state_name)
        
        # Find and remove the transition
        for transition in self.current_automaton.transitions:
            if (transition.from_state == from_state and 
                transition.symbol == symbol and 
                transition.to_state == to_state):
                self.current_automaton.remove_transition(transition)
                self.on_automaton_modified()
                self.update_ui_from_automaton()
                break
    
    def on_automaton_modified(self):
        """Handle modifications to the automaton."""
        if self.current_automaton:
            self.current_automaton.name = self.name_input.text().strip()
            self.has_changes = True
            self.automaton_changed.emit(self.current_automaton)
    
    def save_current_automaton(self):
        """Save the current automaton."""
        if not self.current_automaton:
            QMessageBox.warning(self, "No Automaton", "No automaton to save.")
            return
        
        if not self.current_automaton.name:
            QMessageBox.warning(self, "No Name", "Please enter a name for the automaton.")
            return
        
        try:
            # Check if an automaton with this name already exists
            existing_automata = Automaton.list_saved_automata()
            if self.current_automaton.name in existing_automata:
                reply = QMessageBox.question(
                    self, 'Overwrite Automaton',
                    f"An automaton named '{self.current_automaton.name}' already exists. Overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # Save the automaton
            file_path = self.current_automaton.save_to_file()
            self.has_changes = False
            self.parent.statusBar().showMessage(f"Saved automaton to {file_path}")
            
            # Refresh automata list in the Automaton tab
            if hasattr(self.parent, 'automaton_tab'):
                self.parent.automaton_tab.refresh_automaton_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save automaton: {str(e)}")
    
    def save_current_automaton_as(self):
        """Save the current automaton with a new name."""
        if not self.current_automaton:
            QMessageBox.warning(self, "No Automaton", "No automaton to save.")
            return
        
        new_name, ok = QInputDialog.getText(
            self, "Save As", "Enter new name for the automaton:", 
            text=self.current_automaton.name
        )
        
        if ok and new_name:
            original_name = self.current_automaton.name
            self.current_automaton.name = new_name
            try:
                self.save_current_automaton()
            except Exception as e:
                self.current_automaton.name = original_name
                QMessageBox.critical(self, "Error", f"Failed to save automaton: {str(e)}")
    
    def visualize_automaton(self):
        """Visualize the current automaton."""
        if not self.current_automaton:
            QMessageBox.warning(self, "No Automaton", "No automaton to visualize.")
            return
        
        try:
            # Clear previous visualization
            for i in reversed(range(self.parent.visualization_layout.count())):
                widget = self.parent.visualization_layout.itemAt(i).widget()
                if widget != self.parent.visualization_label:
                    widget.setParent(None)
            
            # Create visualization with consistent positioning
            # It will automatically reuse positions if available
            fig = visualize_automaton(self.current_automaton, reuse_positions=True)
            canvas = FigureCanvas(fig)
            
            # Add to the visualization panel
            self.parent.visualization_layout.addWidget(canvas)
            self.parent.visualization_label.setText(f"Automaton: {self.current_automaton.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to visualize automaton: {str(e)}")
    
    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        return self.has_changes 
        
    def set_current_automaton(self, automaton):
        """Set the current automaton for editing."""
        # Ask for confirmation if there are unsaved changes
        if self.has_changes:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                "You have unsaved changes. Do you want to discard them and load the selected automaton?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.current_automaton = automaton
        self.update_ui_from_automaton()
        self.has_changes = False 