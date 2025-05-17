"""
Generate an icon for the Automata Visualizer application.
This script creates a simple icon.png file in the assets directory.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_icon(size=(128, 128), bg_color="#3498db", save_path=None):
    """
    Create a simple icon for the Automata Visualizer.
    
    Args:
        size: Icon size (width, height)
        bg_color: Background color
        save_path: Path to save the icon
        
    Returns:
        Path to the saved icon
    """
    # Create a new image with blue background
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a circle (representing a state)
    circle_radius = size[0] // 4
    circle_center = (size[0] // 2, size[1] // 2)
    
    # Draw outer circle (regular state)
    draw.ellipse(
        (
            circle_center[0] - circle_radius, 
            circle_center[1] - circle_radius,
            circle_center[0] + circle_radius, 
            circle_center[1] + circle_radius
        ), 
        fill="#FFFFFF", outline="#2c3e50", width=3
    )
    
    # Draw inner circle (final state)
    inner_radius = circle_radius - 5
    draw.ellipse(
        (
            circle_center[0] - inner_radius, 
            circle_center[1] - inner_radius,
            circle_center[0] + inner_radius, 
            circle_center[1] + inner_radius
        ), 
        fill=None, outline="#2c3e50", width=2
    )
    
    # Draw an arrow (transition)
    arrow_start = (size[0] // 4 - 10, size[1] // 4)
    arrow_end = (circle_center[0] - circle_radius, circle_center[1] - 5)
    
    # Draw the arrow line
    draw.line([arrow_start, arrow_end], fill="#2c3e50", width=3)
    
    # Draw the arrow head
    arrow_head_size = 10
    draw.polygon(
        [
            arrow_end,
            (arrow_end[0] - arrow_head_size, arrow_end[1] - arrow_head_size // 2),
            (arrow_end[0] - arrow_head_size, arrow_end[1] + arrow_head_size // 2)
        ],
        fill="#2c3e50"
    )
    
    # Save the icon
    if not save_path:
        save_path = os.path.join(os.path.dirname(__file__), "icon.png")
    
    img.save(save_path, "PNG")
    print(f"Icon saved to: {save_path}")
    return save_path

if __name__ == "__main__":
    # Create and save the icon
    create_icon() 