import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                          QPushButton, QLabel, QMessageBox, QFileDialog,
                          QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt

from automata.automaton import Automaton
from utils.visualization import visualize_automaton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AutomatonTab(QWidget):
    """Tab for listing and managing saved automata."""
    
    # Signal emitted when an automaton is selected
    automaton_selected = pyqtSignal(Automaton)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_automaton = None
        self.setup_ui()
        self.refresh_automaton_list()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Automata list
        self.list_label = QLabel("Saved Automata:")
        self.layout.addWidget(self.list_label)
        
        self.automata_list = QListWidget()
        self.automata_list.itemSelectionChanged.connect(self.on_automaton_selected)
        self.layout.addWidget(self.automata_list)
        
        # Buttons layout
        self.buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_automaton)
        self.buttons_layout.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_automaton)
        self.buttons_layout.addWidget(self.delete_button)
        
        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_automaton)
        self.buttons_layout.addWidget(self.rename_button)
        
        self.layout.addLayout(self.buttons_layout)
    
    def refresh_automaton_list(self):
        """Refresh the list of saved automata."""
        self.automata_list.clear()
        automata_names = Automaton.list_saved_automata()
        for name in sorted(automata_names):
            self.automata_list.addItem(name)
    
    def on_automaton_selected(self):
        """Handle selection of an automaton from the list."""
        selected_items = self.automata_list.selectedItems()
        if not selected_items:
            return
        
        automaton_name = selected_items[0].text()
        self.load_automaton_by_name(automaton_name)
    
    def load_automaton_by_name(self, name):
        """Load an automaton by its name."""
        try:
            file_path = os.path.join("Automates", f"{name}.json")
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Not Found", f"Automaton file {file_path} not found.")
                return
            
            automaton = Automaton.load_from_file(file_path)
            self.current_automaton = automaton
            self.automaton_selected.emit(automaton)
            self.display_automaton()
            self.parent.statusBar().showMessage(f"Loaded automaton: {name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load automaton: {str(e)}")
    
    def load_automaton(self):
        """Load an automaton from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Automaton", "Automates", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                automaton = Automaton.load_from_file(file_path)
                self.current_automaton = automaton
                self.automaton_selected.emit(automaton)
                self.display_automaton()
                self.parent.statusBar().showMessage(f"Loaded automaton: {automaton.name}")
                self.refresh_automaton_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load automaton: {str(e)}")
    
    def delete_automaton(self):
        """Delete the selected automaton."""
        selected_items = self.automata_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an automaton to delete.")
            return
        
        automaton_name = selected_items[0].text()
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the automaton '{automaton_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                file_path = os.path.join("Automates", f"{automaton_name}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.refresh_automaton_list()
                    self.parent.statusBar().showMessage(f"Deleted automaton: {automaton_name}")
                    
                    # Clear visualization if the deleted automaton was being displayed
                    if self.current_automaton and self.current_automaton.name == automaton_name:
                        self.current_automaton = None
                        self.clear_display()
                else:
                    QMessageBox.warning(self, "File Not Found", f"Automaton file {file_path} not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete automaton: {str(e)}")
    
    def rename_automaton(self):
        """Rename the selected automaton."""
        selected_items = self.automata_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an automaton to rename.")
            return
        
        old_name = selected_items[0].text()
        new_name, ok = QInputDialog.getText(
            self, "Rename Automaton", "New name:", text=old_name
        )
        
        if ok and new_name:
            if new_name == old_name:
                return  # No change
            
            if new_name in Automaton.list_saved_automata():
                QMessageBox.warning(
                    self, "Name Exists", 
                    f"An automaton named '{new_name}' already exists. Please choose a different name."
                )
                return
            
            try:
                old_path = os.path.join("Automates", f"{old_name}.json")
                new_path = os.path.join("Automates", f"{new_name}.json")
                
                if os.path.exists(old_path):
                    # Load, rename, and save with new name
                    automaton = Automaton.load_from_file(old_path)
                    automaton.name = new_name
                    automaton.save_to_file()
                    os.remove(old_path)
                    
                    self.refresh_automaton_list()
                    self.parent.statusBar().showMessage(f"Renamed automaton: {old_name} to {new_name}")
                    
                    # Update current automaton if it was renamed
                    if self.current_automaton and self.current_automaton.name == old_name:
                        self.current_automaton.name = new_name
                        self.display_automaton()
                else:
                    QMessageBox.warning(self, "File Not Found", f"Automaton file {old_path} not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename automaton: {str(e)}")
    
    def display_automaton(self):
        """Display the current automaton in the visualization panel."""
        if not self.current_automaton:
            self.clear_display()
            return
        
        try:
            # Clear previous visualization
            self.clear_display()
            
            # Create visualization
            fig = visualize_automaton(self.current_automaton)
            canvas = FigureCanvas(fig)
            
            # Add to the visualization panel
            self.parent.visualization_layout.addWidget(canvas)
            self.parent.visualization_label.setText(f"Automaton: {self.current_automaton.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display automaton: {str(e)}")
    
    def clear_display(self):
        """Clear the visualization panel."""
        # Remove all widgets except the label
        for i in reversed(range(self.parent.visualization_layout.count())):
            widget = self.parent.visualization_layout.itemAt(i).widget()
            if widget != self.parent.visualization_label:
                widget.setParent(None)
        
        self.parent.visualization_label.setText("Automaton Visualization")
    
    def get_current_automaton(self):
        """Get the currently selected automaton."""
        return self.current_automaton 