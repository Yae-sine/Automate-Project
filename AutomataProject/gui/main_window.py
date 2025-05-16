import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTabWidget, 
                          QVBoxLayout, QHBoxLayout, QSplitter, QLabel, 
                          QStatusBar, QAction, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

from .automaton_tab import AutomatonTab
from .editor_tab import EditorTab
from .analysis_tab import AnalysisTab
from .word_processing_tab import WordProcessingTab

class MainWindow(QMainWindow):
    """Main window for the automata application."""
    
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("AutomataProject", "Automata Visualizer")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Automata Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Restore window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            self.center_window()
        
        # Setup central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create the main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Create the visualization panel
        self.visualization_panel = QWidget()
        self.visualization_layout = QVBoxLayout(self.visualization_panel)
        self.visualization_label = QLabel("Automaton Visualization")
        self.visualization_label.setAlignment(Qt.AlignCenter)
        self.visualization_layout.addWidget(self.visualization_label)
        
        # Create the right panel with tabs
        self.right_panel = QTabWidget()
        
        # Create tabs
        self.automaton_tab = AutomatonTab(self)
        self.editor_tab = EditorTab(self)
        self.analysis_tab = AnalysisTab(self)
        self.word_processing_tab = WordProcessingTab(self)
        
        # Add tabs to the right panel
        self.right_panel.addTab(self.automaton_tab, "Automata")
        self.right_panel.addTab(self.editor_tab, "Editor")
        self.right_panel.addTab(self.analysis_tab, "Analysis")
        self.right_panel.addTab(self.word_processing_tab, "Word Processing")
        
        # Add panels to the splitter
        self.main_splitter.addWidget(self.visualization_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([600, 600])  # Initial sizes
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Restore splitter state
        if self.settings.contains("splitter"):
            self.main_splitter.restoreState(self.settings.value("splitter"))
    
    def create_menu_bar(self):
        """Create the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_action = QAction("&New Automaton", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_automaton)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Automaton", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_automaton)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Automaton", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_automaton)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Automaton &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_automaton_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("E&xport Image", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        toggle_theme_action = QAction("Toggle &Dark Mode", self)
        toggle_theme_action.setShortcut("Ctrl+D")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_automaton(self):
        """Create a new automaton."""
        self.editor_tab.create_new_automaton()
        self.right_panel.setCurrentIndex(1)  # Switch to editor tab
    
    def open_automaton(self):
        """Open an existing automaton."""
        self.automaton_tab.load_automaton()
    
    def save_automaton(self):
        """Save the current automaton."""
        self.editor_tab.save_current_automaton()
    
    def save_automaton_as(self):
        """Save the current automaton with a new name."""
        self.editor_tab.save_current_automaton_as()
    
    def export_image(self):
        """Export the current automaton visualization as an image."""
        current_automaton = self.automaton_tab.get_current_automaton()
        if not current_automaton:
            QMessageBox.warning(self, "No Automaton", "No automaton to export.")
            return
        
        formats = "PNG (*.png);;SVG (*.svg)"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Image", os.path.join("Automates", f"{current_automaton.name}"), formats
        )
        
        if file_path:
            format_type = "png" if selected_filter == "PNG (*.png)" else "svg"
            from ..utils.visualization import save_automaton_image
            save_automaton_image(current_automaton, file_path, format=format_type)
            self.statusBar().showMessage(f"Image exported to {file_path}")
    
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        # Implementation depends on styling framework used
        # This is a placeholder for future implementation
        QMessageBox.information(self, "Theme Toggle", "Theme toggle feature will be implemented in a future update.")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, 
            "About Automata Visualizer",
            "<h3>Automata Visualizer</h3>"
            "<p>A tool for visualizing and analyzing finite automata.</p>"
            "<p>Created for educational purposes.</p>"
            "<p>Version 1.0</p>"
        )
    
    def center_window(self):
        """Center the window on the screen."""
        geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())
    
    def closeEvent(self, event):
        """Handle the close event."""
        # Save window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitter", self.main_splitter.saveState())
        
        # Confirm exit if there are unsaved changes
        if self.editor_tab.has_unsaved_changes():
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                "You have unsaved changes. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept() 