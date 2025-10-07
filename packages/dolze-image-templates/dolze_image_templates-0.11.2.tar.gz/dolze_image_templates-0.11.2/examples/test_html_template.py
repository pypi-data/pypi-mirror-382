"""
Test script for template rendering.

This script demonstrates how to render different templates with various configurations.
It supports rendering multiple templates with different data.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from dolze_image_templates import (
    get_template_registry,
    configure,
    get_font_manager,
)

# Initialize font manager to scan for fonts
font_manager = get_font_manager()
print("Font manager initialized. Available fonts:", font_manager.list_fonts())

# Configure the library
configure(
    templates_dir=os.path.join(
        os.path.dirname(__file__), "..", "dolze_image_templates", "available_templates"
    ),
    output_dir=os.path.join(os.path.dirname(__file__), "output"),
)


def render_template(template_name, template_data):
    """Render a template with the provided data.

    Args:
        template_name (str): Name to use for the output file
        template_data (dict): Template data with custom content

    Returns:
        The rendered image
    """
    # Get the template registry
    registry = get_template_registry()

    # Render the template with the data
    output_path = os.path.join("output", f"{template_name}.png")
    rendered_image = registry.render_template(
        template_name,  # Use the actual template name
        template_data,
        output_path=output_path,
    )

    print(f"Template saved to {os.path.abspath(output_path)}")
    return rendered_image


def get_faq_template_data():
    """Get sample data for the FAQ template."""
    return {
        "company_name": "TechCorp",
        "question1": "How do I start a return?",
        "answer1": "Email us your order number to initiate the return process.",
        "question2": "What if I received a damaged item?",
        "answer2": "Send us photos right away. We'll arrange a replacement.",
        "website_url": "www.techcorp.com",
        "background_image_url": "https://i.ibb.co/ZpSCsQFB/faq-template.png"
    }


def get_qa_template_data():
    """Get sample data for the Q&A template."""
    return {
        "question": "What is renewable energy?",
        "answer": "One wind turbine can power 1,500 homes annually!",
        "username": "@techcorp",
        "website_url": "techcorp.com",
        "theme_color": "#795548",
        "logo_url": "https://images.rawpixel.com/image_png_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDI0LTA3L2hpcHBvdW5pY29ybl9waG90b19vZl9kaXNzZWN0ZWRfZmxvYXRpbmdfdGFjb19zZXBhcmF0ZV9sYXllcl9vZl84M2Q0ODAwNC03MDc0LTRlZjItYjYyOC1jZTU3ODhiYzQxOGEucG5n.png"
    }


def get_spotlight_launching_data():
    """Get sample data for the spotlight launching template."""
    return {
        "main_title": "Launching Soon",
        "subheading": "Countdown",
        "days": "15",
        "hours": "08",
        "minutes": "45",
        "cta_text": "Stay Tuned!"
    }


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Define the templates to render
        templates = [
            {"name": "faq_template", "data": get_faq_template_data()},
            {"name": "qa_template", "data": get_qa_template_data()},
            {"name": "spotlight_launching", "data": get_spotlight_launching_data()}
        ]

        # Render each template
        for template in templates:
            render_template(template["name"], template["data"])

        print("\nAll templates generated successfully!")
    except Exception as e:
        print(f"\nError generating templates: {str(e)}")
        import traceback

        traceback.print_exc()
