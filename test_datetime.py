#!/usr/bin/env python3
"""
Test script to understand how Gradio Date component works
"""
import gradio as gr
from datetime import date, datetime

def test_date_input(date_value):
    """Test function to see what format gr.Date passes to the function"""
    print(f"Received: {date_value}")
    print(f"Type: {type(date_value)}")
    if hasattr(date_value, '__dict__'):
        print(f"Attributes: {date_value.__dict__}")
    
    # Try to convert to string representation
    str_repr = str(date_value)
    print(f"String representation: '{str_repr}'")
    
    return f"Input: {date_value} (type: {type(date_value).__name__})\nString: {str_repr}"

# Create a simple interface to test the Date component
demo = gr.Interface(
    fn=test_date_input,
    inputs=gr.DateTime(
        value=datetime.now(),  # Use datetime.now() instead of date.today()
        label="Test DateTime Picker",
        include_time=False
    ),
    outputs=gr.Textbox(label="Result"),
    title="DateTime Component Test"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861, debug=True)
