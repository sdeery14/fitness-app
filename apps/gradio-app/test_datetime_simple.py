#!/usr/bin/env python3
"""
Simple test to understand Gradio DateTime component behavior
"""
import gradio as gr
from datetime import date, datetime

def test_datetime_component():
    """Test DateTime component creation and behavior"""
    print("Testing Gradio DateTime component...")
    
    # Test 1: Create with datetime.now()
    try:
        dt1 = gr.DateTime(
            value=datetime.now(),
            include_time=False,
            label="Test 1"
        )
        print(f"✓ Created DateTime with datetime.now(): {dt1.value}")
    except Exception as e:
        print(f"✗ Failed to create DateTime with datetime.now(): {e}")
    
    # Test 2: Create with date.today()
    try:
        dt2 = gr.DateTime(
            value=date.today(),
            include_time=False,
            label="Test 2"
        )
        print(f"✓ Created DateTime with date.today(): {dt2.value}")
    except Exception as e:
        print(f"✗ Failed to create DateTime with date.today(): {e}")
    
    # Test 3: Create with ISO string
    try:
        dt3 = gr.DateTime(
            value="2025-08-15",
            include_time=False,
            label="Test 3"
        )
        print(f"✓ Created DateTime with ISO string: {dt3.value}")
    except Exception as e:
        print(f"✗ Failed to create DateTime with ISO string: {e}")
    
    # Test 4: Create with no value
    try:
        dt4 = gr.DateTime(
            include_time=False,
            label="Test 4"
        )
        print(f"✓ Created DateTime with no value: {dt4.value}")
    except Exception as e:
        print(f"✗ Failed to create DateTime with no value: {e}")

if __name__ == "__main__":
    test_datetime_component()
