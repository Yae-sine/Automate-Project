from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QLineEdit, QGroupBox, QTextEdit, QMessageBox,
                          QSpinBox, QListWidget, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from automata.automaton import Automaton
from utils.visualization import animate_word_processing

class WordProcessingTab(QWidget):
    """Tab for word processing and language operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_automaton = None
        self.animation_frames = []
        self.current_frame = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Word testing section
        self.word_group = QGroupBox("Word Recognition")
        self.word_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.word_layout = QVBoxLayout(self.word_group)
        self.word_layout.setContentsMargins(10, 15, 10, 10)
        
        self.word_input_layout = QHBoxLayout()
        self.word_input_layout.setSpacing(8)
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word to test")
        
        self.test_word_button = QPushButton("Test Word")
        self.test_word_button.clicked.connect(self.test_word)
        
        self.animate_word_button = QPushButton("Animate Processing")
        self.animate_word_button.clicked.connect(self.animate_word)
        
        # Simple button styling
        button_style = "QPushButton { padding: 4px 8px; }"
        self.test_word_button.setStyleSheet(button_style)
        self.animate_word_button.setStyleSheet(button_style)
        
        word_label = QLabel("Word:")
        bold_font = QFont()
        bold_font.setBold(True)
        word_label.setFont(bold_font)
        
        self.word_input_layout.addWidget(word_label)
        self.word_input_layout.addWidget(self.word_input, 3)  # Give more space to the input
        self.word_input_layout.addWidget(self.test_word_button)
        self.word_input_layout.addWidget(self.animate_word_button)
        
        self.word_result = QLabel("No word tested yet")
        self.word_result.setAlignment(Qt.AlignCenter)
        self.word_result.setStyleSheet("QLabel { background-color: #f5f5f5; padding: 5px; border-radius: 3px; }")
        
        self.word_layout.addLayout(self.word_input_layout)
        self.word_layout.addWidget(self.word_result)
        
        self.layout.addWidget(self.word_group)
        
        # Animation controls (initially hidden)
        self.animation_group = QGroupBox("Animation Controls")
        self.animation_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.animation_layout = QHBoxLayout(self.animation_group)
        self.animation_layout.setSpacing(8)
        
        self.prev_frame_button = QPushButton("Previous Step")
        self.prev_frame_button.clicked.connect(self.show_prev_frame)
        
        self.next_frame_button = QPushButton("Next Step")
        self.next_frame_button.clicked.connect(self.show_next_frame)
        
        self.animation_label = QLabel("Frame 0/0")
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setStyleSheet("QLabel { background-color: #f5f5f5; padding: 3px; border-radius: 3px; }")
        
        self.save_animation_button = QPushButton("Save Animation")
        self.save_animation_button.clicked.connect(self.save_animation)
        
        # Apply the same button styling
        self.prev_frame_button.setStyleSheet(button_style)
        self.next_frame_button.setStyleSheet(button_style)
        self.save_animation_button.setStyleSheet(button_style)
        
        self.animation_layout.addWidget(self.prev_frame_button)
        self.animation_layout.addWidget(self.animation_label)
        self.animation_layout.addWidget(self.next_frame_button)
        self.animation_layout.addWidget(self.save_animation_button)
        
        self.animation_group.setVisible(False)
        self.layout.addWidget(self.animation_group)
        
        # Word generation section
        self.generation_group = QGroupBox("Word Generation")
        self.generation_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.generation_layout = QVBoxLayout(self.generation_group)
        self.generation_layout.setContentsMargins(10, 15, 10, 10)
        
        self.generation_input_layout = QHBoxLayout()
        self.generation_input_layout.setSpacing(8)
        
        length_label = QLabel("Max Length:")
        length_label.setFont(bold_font)
        
        self.max_length_input = QSpinBox()
        self.max_length_input.setRange(1, 10)
        self.max_length_input.setValue(3)
        
        self.generate_button = QPushButton("Generate Words")
        self.generate_button.clicked.connect(self.generate_words)
        self.generate_button.setStyleSheet(button_style)
        
        self.generation_input_layout.addWidget(length_label)
        self.generation_input_layout.addWidget(self.max_length_input)
        self.generation_input_layout.addWidget(self.generate_button)
        self.generation_input_layout.addStretch(1)
        
        self.generation_layout.addLayout(self.generation_input_layout)
        
        self.words_list = QListWidget()
        self.words_list.setAlternatingRowColors(True)
        self.words_list.setStyleSheet("QListWidget { border: 1px solid #ddd; }")
        self.generation_layout.addWidget(self.words_list)
        
        self.layout.addWidget(self.generation_group)
        
        # Word statistics section
        self.stats_group = QGroupBox("Word Statistics")
        self.stats_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.stats_layout = QVBoxLayout(self.stats_group)
        self.stats_layout.setContentsMargins(10, 15, 10, 10)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("QTextEdit { border: 1px solid #ddd; }")
        self.stats_layout.addWidget(self.stats_text)
        
        self.layout.addWidget(self.stats_group)
    
    def set_current_automaton(self, automaton):
        """Set the current automaton for word processing."""
        self.current_automaton = automaton
        self.word_result.setText(f"Automaton: {automaton.name}")
        self.word_result.setStyleSheet("QLabel { background-color: #e8f0fe; padding: 5px; border-radius: 3px; }")
        self.words_list.clear()
        self.stats_text.clear()
        self.clear_animation()
    
    def test_word(self):
        """Test if the current automaton accepts a word."""
        if not self.current_automaton:
            self.show_message("No Automaton", "Please load an automaton first.")
            return
        
        word = self.word_input.text().strip()
        if not word and word != "":  # Allow empty word (epsilon)
            self.show_message("Empty Input", "Please enter a word to test.")
            return
        
        # Check if all symbols are in the alphabet
        invalid_symbols = [symbol for symbol in word if symbol not in self.current_automaton.alphabet.symbols]
        if invalid_symbols:
            self.word_result.setText(
                f"Word contains symbols not in the alphabet: {', '.join(invalid_symbols)}"
            )
            self.word_result.setStyleSheet("QLabel { background-color: #fff8e1; padding: 5px; border-radius: 3px; color: #856404; }")
            return
        
        # Test the word
        accepted = self.current_automaton.accepts_word(word)
        
        if accepted:
            self.word_result.setText(f"The word '{word}' is ACCEPTED by the automaton.")
            self.word_result.setStyleSheet("QLabel { background-color: #e8f5e9; padding: 5px; border-radius: 3px; color: green; font-weight: bold; }")
        else:
            self.word_result.setText(f"The word '{word}' is REJECTED by the automaton.")
            self.word_result.setStyleSheet("QLabel { background-color: #ffebee; padding: 5px; border-radius: 3px; color: red; font-weight: bold; }")
    
    def animate_word(self):
        """Animate the processing of a word by the automaton."""
        if not self.current_automaton:
            self.show_message("No Automaton", "Please load an automaton first.")
            return
        
        word = self.word_input.text().strip()
        if not word and word != "":  # Allow empty word (epsilon)
            self.show_message("Empty Input", "Please enter a word to test.")
            return
        
        # Check if all symbols are in the alphabet
        invalid_symbols = [symbol for symbol in word if symbol not in self.current_automaton.alphabet.symbols]
        if invalid_symbols:
            self.word_result.setText(
                f"Word contains symbols not in the alphabet: {', '.join(invalid_symbols)}"
            )
            self.word_result.setStyleSheet("QLabel { background-color: #fff8e1; padding: 5px; border-radius: 3px; color: #856404; }")
            return
        
        try:
            # Generate animation frames
            self.animation_frames = animate_word_processing(self.current_automaton, word)
            self.current_frame = 0
            
            # Show animation controls
            self.animation_group.setVisible(True)
            self.animation_label.setText(f"Frame 1/{len(self.animation_frames)}")
            
            # Display first frame
            self.display_animation_frame(0)
        except Exception as e:
            self.show_message("Animation Error", f"Error creating animation: {str(e)}")
    
    def display_animation_frame(self, frame_index):
        """Display a specific animation frame."""
        if not self.animation_frames or frame_index < 0 or frame_index >= len(self.animation_frames):
            return
        
        try:
            # Clear previous visualization
            for i in reversed(range(self.parent.visualization_layout.count())):
                widget = self.parent.visualization_layout.itemAt(i).widget()
                if widget != self.parent.visualization_label:
                    widget.setParent(None)
            
            # Create canvas for the current frame
            fig = self.animation_frames[frame_index]
            canvas = FigureCanvas(fig)
            
            # Add to the visualization panel
            self.parent.visualization_layout.addWidget(canvas)
            
            # Update frame counter
            self.animation_label.setText(f"Frame {frame_index + 1}/{len(self.animation_frames)}")
            self.current_frame = frame_index
            
            # Enable/disable navigation buttons
            self.prev_frame_button.setEnabled(frame_index > 0)
            self.next_frame_button.setEnabled(frame_index < len(self.animation_frames) - 1)
        except Exception as e:
            self.show_message("Display Error", f"Error displaying animation frame: {str(e)}")
    
    def show_prev_frame(self):
        """Show the previous animation frame."""
        if self.current_frame > 0:
            self.display_animation_frame(self.current_frame - 1)
    
    def show_next_frame(self):
        """Show the next animation frame."""
        if self.current_frame < len(self.animation_frames) - 1:
            self.display_animation_frame(self.current_frame + 1)
    
    def save_animation(self):
        """Save all animation frames as images."""
        if not self.animation_frames:
            self.show_message("No Animation", "No animation to save.")
            return
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Save Animation Frames", "Automates"
        )
        
        if directory:
            try:
                word = self.word_input.text().strip()
                base_filename = f"{self.current_automaton.name}_{word}"
                
                for i, fig in enumerate(self.animation_frames):
                    filename = os.path.join(directory, f"{base_filename}_frame{i+1}.png")
                    fig.savefig(filename, bbox_inches='tight')
                
                self.show_message(
                    "Animation Saved", 
                    f"Animation frames saved to {directory}"
                )
            except Exception as e:
                self.show_message("Save Error", f"Error saving animation: {str(e)}")
    
    def clear_animation(self):
        """Clear the current animation."""
        self.animation_frames = []
        self.current_frame = 0
        self.animation_group.setVisible(False)
    
    def generate_words(self):
        """Generate all accepted words up to a given length."""
        if not self.current_automaton:
            self.show_message("No Automaton", "Please load an automaton first.")
            return
        
        max_length = self.max_length_input.value()
        
        try:
            # Generate words
            print(f"Generating words with max length: {max_length}")
            print(f"Current automaton: {self.current_automaton.name}")
            print(f"Is deterministic: {self.current_automaton.is_deterministic()}")
            print(f"States: {len(self.current_automaton.states)}")
            print(f"Initial states: {len(self.current_automaton.get_initial_states())}")
            print(f"Final states: {len(self.current_automaton.get_final_states())}")
            accepted_words = self.current_automaton.generate_words(max_length)
            print(f"Generated {len(accepted_words)} words")
            
            # Display words
            self.words_list.clear()
            for word in sorted(accepted_words, key=lambda w: (len(w), w)):
                display_word = word if word else "ε (empty word)"
                self.words_list.addItem(display_word)
            
            # Update statistics
            self.update_word_statistics(accepted_words, max_length)
        except Exception as e:
            print(f"Error generating words: {str(e)}")
            import traceback
            traceback.print_exc()
            self.show_message("Generation Error", f"Error generating words: {str(e)}")
    
    def update_word_statistics(self, words, max_length):
        """Update the word statistics display."""
        stats = []
        
        total_words = len(words)
        stats.append(f"Total accepted words (up to length {max_length}): {total_words}")
        
        # Count by length
        by_length = {}
        for word in words:
            length = len(word)
            if length not in by_length:
                by_length[length] = []
            by_length[length].append(word)
        
        stats.append("\nWords by length:")
        for length in range(max_length + 1):
            words_of_length = by_length.get(length, [])
            count = len(words_of_length)
            stats.append(f"  Length {length}: {count} word(s)")
            
            # Add the actual words
            if count > 0:
                # Sort words for better readability
                words_of_length.sort()
                # Format the display of each word
                formatted_words = [f"'{w}'" if w else "'ε' (empty word)" for w in words_of_length]
                # Join the words with commas
                words_text = ", ".join(formatted_words)
                stats.append(f"    Words: {words_text}")
        
        # Is the language finite or infinite?
        is_finite = True
        if self.current_automaton.is_deterministic():
            # A DFA accepts an infinite language if there's a cycle that includes a final state
            # Simple heuristic: if we keep seeing more words as length increases, it might be infinite
            if max_length >= 3:
                growth_rate = [len(by_length.get(i, [])) for i in range(max_length + 1)]
                if growth_rate[-1] > growth_rate[-2] > growth_rate[-3]:
                    is_finite = False
        
        stats.append(f"\nLanguage appears to be: {'infinite' if not is_finite else 'finite'}")
        
        self.stats_text.setText("\n".join(stats))
    
    def show_message(self, title, message):
        """Show a message dialog."""
        QMessageBox.information(self, title, message) 