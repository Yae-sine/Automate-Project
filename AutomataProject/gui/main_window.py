import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTabWidget, 
                          QVBoxLayout, QHBoxLayout, QSplitter, QLabel, 
                          QStatusBar, QAction, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

from .automaton_tab import AutomatonTab
from .editor_tab import EditorTab
from .analysis_tab import AnalysisTab
from .word_processing_tab import WordProcessingTab

# Modern color scheme
COLORS = {
    'primary': '#2c3e50',       # Dark blue/slate for primary elements
    'secondary': '#34495e',     # Slightly lighter blue/slate for secondary elements
    'accent': '#3498db',        # Bright blue for accent/highlights
    'success': '#2ecc71',       # Green for success indicators
    'warning': '#f39c12',       # Orange for warnings
    'danger': '#e74c3c',        # Red for errors/danger
    'light': '#ecf0f1',         # Light grey for backgrounds
    'dark': '#2c3e50',          # Dark for text
    'border': '#bdc3c7',        # Medium grey for borders
    'highlight': '#3498db',     # Bright blue for highlights
}

class MainWindow(QMainWindow):
    """Main window for the automata application."""
    
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("AutomataProject", "Automata Visualizer")
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Automata Visualizer & Simulator")
        self.setMinimumSize(1200, 800)
        
        # Set app icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
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
        self.main_splitter.setHandleWidth(2)  # Thin splitter handle
        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['border']};
            }}
            QSplitter::handle:hover {{
                background-color: {COLORS['accent']};
            }}
        """)
        
        # Create the visualization panel with a border
        self.visualization_panel = QWidget()
        self.visualization_panel.setObjectName("visualizationPanel")
        self.visualization_layout = QVBoxLayout(self.visualization_panel)
        self.visualization_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add a header for the visualization panel
        self.visualization_header = QLabel("Automaton Visualization")
        self.visualization_header.setObjectName("panelHeader")
        self.visualization_header.setAlignment(Qt.AlignCenter)
        
        self.visualization_layout.addWidget(self.visualization_header)
        self.visualization_label = QLabel("No automaton selected")
        self.visualization_label.setAlignment(Qt.AlignCenter)
        self.visualization_label.setObjectName("visualizationLabel")
        self.visualization_layout.addWidget(self.visualization_label)
        
        # Create the right panel with tabs
        self.right_panel = QTabWidget()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setDocumentMode(True)  # Cleaner tab appearance
        self.right_panel.setTabPosition(QTabWidget.North)
        
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
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create status bar with styling
        self.statusBar().setObjectName("statusBar")
        self.statusBar().showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Restore splitter state
        if self.settings.contains("splitter"):
            self.main_splitter.restoreState(self.settings.value("splitter"))
    
    def apply_styles(self):
        """Apply modern styling to the application."""
        # Set application font
        app_font = QFont("Segoe UI", 9)
        QApplication.setFont(app_font)
        
        # Apply stylesheet
        self.setStyleSheet(f"""
            /* Main Window */
            QMainWindow {{
                background-color: {COLORS['light']};
                color: {COLORS['dark']};
            }}
            
            /* Panels */
            #visualizationPanel {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            
            #rightPanel {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            
            /* Labels */
            #panelHeader {{
                font-size: 14px;
                font-weight: bold;
                color: {COLORS['primary']};
                padding: 5px;
                border-bottom: 1px solid {COLORS['border']};
                margin-bottom: 10px;
            }}
            
            #visualizationLabel {{
                color: {COLORS['secondary']};
                font-size: 13px;
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                top: -1px;
            }}
            
            QTabBar::tab {{
                background-color: {COLORS['light']};
                color: {COLORS['dark']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 2px solid {COLORS['accent']};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: #d6dbdf;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            
            QPushButton:pressed {{
                background-color: #1f6aa5;
            }}
            
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
            
            /* ComboBox */
            QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            /* Line Edit */
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {COLORS['accent']};
            }}
            
            /* List Widget */
            QListWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }}
            
            QListWidget::item {{
                padding: 5px;
                border-radius: 3px;
            }}
            
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            
            /* Status Bar */
            #statusBar {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 5px;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 10px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {COLORS['secondary']};
            }}
            
            QMenu {{
                background-color: white;
                border: 1px solid {COLORS['border']};
            }}
            
            QMenu::item {{
                padding: 6px 20px 6px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            
            /* Text Edit */
            QTextEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: white;
            }}
            
            /* Scroll Bar */
            QScrollBar:vertical {{
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['accent']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                height: 0px;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: #f0f0f0;
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['border']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {COLORS['accent']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                width: 0px;
                background: none;
            }}
        """)
    
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
            from utils.visualization import save_automaton_image
            save_automaton_image(current_automaton, file_path, format=format_type)
            self.statusBar().showMessage(f"Image exported to {file_path}")
    
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        # Check current theme
        current_theme = self.settings.value("theme", "light")
        
        # Toggle theme
        if current_theme == "light":
            # Switch to dark theme
            self.settings.setValue("theme", "dark")
            self.apply_dark_theme()
            self.statusBar().showMessage("Dark theme applied")
        else:
            # Switch to light theme
            self.settings.setValue("theme", "light")
            self.apply_styles()  # Default is light
            self.statusBar().showMessage("Light theme applied")
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        dark_colors = {
            'primary': '#1a1a2e',     # Very dark blue
            'secondary': '#16213e',   # Dark blue
            'accent': '#0f3460',      # Darker accent
            'text': '#e1e1e1',        # Light gray for text
            'background': '#121212',  # Very dark gray almost black
            'border': '#333333',      # Dark gray for borders
            'highlight': '#8BC34A',   # Bright green for highlight
        }
        
        self.setStyleSheet(f"""
            /* Main Window */
            QMainWindow {{
                background-color: {dark_colors['background']};
                color: {dark_colors['text']};
            }}
            
            /* Panels */
            #visualizationPanel {{
                background-color: {dark_colors['secondary']};
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
            }}
            
            #rightPanel {{
                background-color: {dark_colors['secondary']};
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
            }}
            
            /* Labels */
            #panelHeader {{
                font-size: 14px;
                font-weight: bold;
                color: {dark_colors['text']};
                padding: 5px;
                border-bottom: 1px solid {dark_colors['border']};
                margin-bottom: 10px;
            }}
            
            #visualizationLabel {{
                color: {dark_colors['text']};
                font-size: 13px;
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
                top: -1px;
                background-color: {dark_colors['secondary']};
            }}
            
            QTabBar::tab {{
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
                border: 1px solid {dark_colors['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {dark_colors['secondary']};
                border-bottom: 2px solid {dark_colors['highlight']};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: #2a2a4a;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {dark_colors['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: #1a4870;
            }}
            
            QPushButton:pressed {{
                background-color: #0c2635;
            }}
            
            QPushButton:disabled {{
                background-color: #404040;
                color: #707070;
            }}
            
            /* All widgets */
            QWidget {{
                background-color: {dark_colors['secondary']};
                color: {dark_colors['text']};
            }}
            
            /* ComboBox */
            QComboBox {{
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
                selection-background-color: {dark_colors['accent']};
            }}
            
            /* Line Edit */
            QLineEdit {{
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
            }}
            
            QLineEdit:focus {{
                border: 1px solid {dark_colors['highlight']};
            }}
            
            /* List Widget */
            QListWidget {{
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
                padding: 5px;
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
            }}
            
            QListWidget::item {{
                padding: 5px;
                border-radius: 3px;
            }}
            
            QListWidget::item:selected {{
                background-color: {dark_colors['accent']};
                color: white;
            }}
            
            /* Status Bar */
            #statusBar {{
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
                padding: 5px;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 10px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {dark_colors['accent']};
            }}
            
            QMenu {{
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
                border: 1px solid {dark_colors['border']};
            }}
            
            QMenu::item {{
                padding: 6px 20px 6px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {dark_colors['accent']};
                color: white;
            }}
            
            /* Text Edit */
            QTextEdit {{
                border: 1px solid {dark_colors['border']};
                border-radius: 4px;
                background-color: {dark_colors['primary']};
                color: {dark_colors['text']};
            }}
            
            /* Scroll Bar */
            QScrollBar:vertical {{
                border: none;
                background-color: {dark_colors['primary']};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {dark_colors['border']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {dark_colors['accent']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                height: 0px;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {dark_colors['primary']};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {dark_colors['border']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {dark_colors['accent']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                width: 0px;
                background: none;
            }}
        """)
    
    def show_about(self):
        """Show about dialog with improved styling."""
        about_text = """
        <div style="text-align: center;">
            <h2 style="color: #3498db;">Automata Visualizer & Simulator</h2>
            <p>A powerful tool for visualizing and analyzing finite automata.</p>
            <p>Create, edit, and simulate automata with a modern interface.</p>
            <p><small>Version 1.0</small></p>
            <p><small>© 2023 Academic Project</small></p>
        </div>
        """
        
        QMessageBox.about(self, "About Automata Visualizer", about_text)
    
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