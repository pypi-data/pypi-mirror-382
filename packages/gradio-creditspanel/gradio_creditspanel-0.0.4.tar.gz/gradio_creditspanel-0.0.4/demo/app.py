# app.py

import gradio as gr
from gradio_creditspanel import CreditsPanel
import os

def setup_demo_files():
    """Creates necessary directories and dummy files for the demo."""
    os.makedirs("LICENSES", exist_ok=True)
    if not os.path.exists("LICENSES/Apache.txt"):
        with open("LICENSES/Apache.txt", "w") as f:
            f.write("Apache License\nVersion 2.0, January 2004...")
    if not os.path.exists("LICENSES/MIT.txt"):
        with open("LICENSES/MIT.txt", "w") as f:
            f.write("MIT License\nCopyright (c) 2025 Author...")
    os.makedirs("assets", exist_ok=True)
    if not os.path.exists("./assets/logo.webp"):
        with open("./assets/logo.webp", "w") as f:
            f.write("Placeholder WebP logo")

# --- Credits list with sections ---
credits_list = [
    {"section_title": "Project Leadership"},
    {"title": "Project Manager", "name": "Emma Thompson"},
    {"title": "Scrum Master", "name": "Ava Rodriguez"},
    
    {"section_title": "Development Team"},
    {"title": "Lead Developer", "name": "John Doe"},
    {"title": "Senior Backend Engineer", "name": "Michael Chen"},
    {"title": "Frontend Developer", "name": "Sarah Johnson"},
    {"title": "UI/UX Designer", "name": "Jane Smith"},
    {"title": "Database Architect", "name": "Alex Ray"},
    
    {"section_title": "Quality & Operations"},
    {"title": "DevOps Engineer", "name": "Liam Patel"},
    {"title": "Quality Assurance Lead", "name": "Sam Wilson"},
    {"title": "Test Automation Engineer", "name": "Olivia Brown"},
]

license_paths = {
    "Gradio Framework": "./LICENSES/Apache.txt",
    "This Component": "./LICENSES/MIT.txt"
}

DEFAULT_SPEEDS = {
    "scroll": 40.0,
    "starwars": 70.0,
    "matrix": 40.0
}
SCROLL_LOGO_PATH = "./assets/gradio_logo_white.png"
LOGO_PATH="./assets/logo.webp"

def update_panel(
    effect: str, 
    speed: float, 
    base_font_size: float,
    intro_title: str, 
    intro_subtitle: str, 
    sidebar_position: str,
    show_logo: bool, 
    show_licenses: bool, 
    show_credits: bool, 
    logo_position: str, 
    logo_sizing: str, 
    logo_width: str | None, 
    logo_height: str | None,
    scroll_background_color: str | None, 
    scroll_title_color: str | None, 
    scroll_section_title_color: str | None,
    scroll_name_color: str | None,    
    layout_style: str, 
    title_uppercase: bool, 
    name_uppercase: bool, 
    section_title_uppercase: bool,
    swap_font_sizes: bool,
    show_scroll_logo: bool,
    scroll_logo_height: str | None
) -> dict:
    """Callback function that updates all properties of the CreditsPanel component."""
        
    scroll_logo_path = SCROLL_LOGO_PATH if show_scroll_logo else None
    
    if not scroll_logo_height:
        scroll_logo_height = "120px"
        
    return {
        "credits": credits_list,
        "licenses": license_paths,
        "effect": effect,
        "speed": speed,
        "base_font_size": base_font_size,
        "intro_title": intro_title,
        "intro_subtitle": intro_subtitle,
        "sidebar_position": sidebar_position,
        "logo_path": LOGO_PATH, 
        "show_logo": show_logo,
        "show_licenses": show_licenses,
        "show_credits": show_credits,
        "logo_position": logo_position,
        "logo_sizing": logo_sizing,
        "logo_width": logo_width,
        "logo_height": logo_height,
        "scroll_background_color": scroll_background_color,
        "scroll_title_color": scroll_title_color,
        "scroll_name_color": scroll_name_color,
        "scroll_section_title_color": scroll_section_title_color,
        "layout_style": layout_style,
        "title_uppercase": title_uppercase,
        "name_uppercase": name_uppercase,
        "section_title_uppercase": section_title_uppercase,
        "swap_font_sizes_on_two_column": swap_font_sizes,
        "scroll_logo_path": scroll_logo_path,
        "scroll_logo_height": scroll_logo_height,
    }

def update_ui_on_effect_change(effect: str) -> tuple[float, float]:
    """Updates sliders to sensible defaults when the animation effect is changed."""
    font_size = 1.5
    if effect == "starwars":
        font_size = 3.8
    speed = DEFAULT_SPEEDS.get(effect, 40.0)
    return speed, font_size

def toggle_swap_checkbox_visibility(layout: str) -> dict:
    """Show the swap checkbox only for the two-column layout."""
    return gr.update(visible=(layout == 'two-column'))

with gr.Blocks(theme=gr.themes.Ocean(), title="CreditsPanel Demo") as demo:
    gr.Markdown(
        """
        # Interactive CreditsPanel Demo
        Use the sidebar controls to customize the `CreditsPanel` component in real-time.
        """
    )

    with gr.Sidebar(position="right"):
        gr.Markdown("### Effects Settings")
        effect_radio = gr.Radio(["scroll", "starwars", "matrix"], label="Animation Effect", value="scroll")
        speed_slider = gr.Slider(minimum=5.0, maximum=100.0, step=1.0, value=DEFAULT_SPEEDS["scroll"], label="Animation Speed")
        font_size_slider = gr.Slider(minimum=1.0, maximum=10.0, step=0.1, value=1.5, label="Base Font Size")      
        
        gr.Markdown("### Credits Layout Settings")
        layout_style_radio = gr.Radio(
            ["stacked", "two-column"], label="Layout Style", value="stacked",
            info="How to display titles and names."
        )
        swap_sizes_checkbox = gr.Checkbox(
            label="Swap Title/Name Font Sizes", value=False,
            info="Emphasize name over title in two-column layout.",
            visible=False
        )
        title_uppercase_checkbox = gr.Checkbox(label="Title Uppercase", value=False)
        name_uppercase_checkbox = gr.Checkbox(label="Name Uppercase", value=False)
        section_title_uppercase_checkbox = gr.Checkbox(label="Section Uppercase", value=True)
        
        gr.Markdown("### Scrolling Logo")
        show_scroll_logo_checkbox = gr.Checkbox(
            label="Show Logo in Credits Roll", 
            value=True, 
            info="Toggles the logo above the intro text."
        )
        scroll_logo_height_input = gr.Textbox(label="Scrolling Logo Height", value="100px")
        
        gr.Markdown("### Intro Text")
        intro_title_input = gr.Textbox(label="Intro Title", value="Gradio")
        intro_subtitle_input = gr.Textbox(label="Intro Subtitle", value="The best UI framework")

        gr.Markdown("### Layout & Visibility")
        sidebar_position_radio = gr.Radio(["right", "bottom"], label="Sidebar Position", value="right")
        show_logo_checkbox = gr.Checkbox(label="Show Logo", value=True)
        show_licenses_checkbox = gr.Checkbox(label="Show Licenses", value=True)
        show_credits_checkbox = gr.Checkbox(label="Show Credits", value=True)
        
        gr.Markdown("### Logo Customization")
        logo_position_radio = gr.Radio(["left", "center", "right"], label="Logo Position", value="center")
        logo_sizing_radio = gr.Radio(["stretch", "crop", "resize"], label="Logo Sizing", value="resize")
        logo_width_input = gr.Textbox(label="Logo Width", value="200px")
        logo_height_input = gr.Textbox(label="Logo Height", value="100px")

        gr.Markdown("### Color Settings (Scroll Effect)")
        scroll_background_color = gr.ColorPicker(label="Background Color", value="#000000")
        scroll_title_color = gr.ColorPicker(label="Title Color", value="#FFFFFF")
        scroll_section_title_color = gr.ColorPicker(label="Section Title Color", value="#FFFFFF")
        scroll_name_color = gr.ColorPicker(label="Name Color", value="#FFFFFF")

    panel = CreditsPanel(       
        height=500,
        credits=credits_list,
        licenses=license_paths,
        effect="scroll",
        speed=DEFAULT_SPEEDS["scroll"],
        base_font_size=1.5,
        intro_title="Gradio",
        intro_subtitle="The best UI framework",
        sidebar_position="right",
        logo_path=LOGO_PATH,
        show_logo=True,
        show_licenses=True,
        show_credits=True,
        logo_position="center",
        logo_sizing="resize",
        logo_width="200px",
        logo_height="100px",
        scroll_background_color="#000000",
        scroll_title_color="#FFFFFF",
        scroll_name_color="#FFFFFF",       
        scroll_section_title_color="#FFFFFF",
        layout_style="stacked",
        title_uppercase=False,
        name_uppercase=False,
        section_title_uppercase=True,
        swap_font_sizes_on_two_column=False,
        scroll_logo_path=SCROLL_LOGO_PATH,
        scroll_logo_height="100px",
    )

    inputs = [
        effect_radio, 
        speed_slider, 
        font_size_slider,
        intro_title_input, 
        intro_subtitle_input,
        sidebar_position_radio, 
        show_logo_checkbox, 
        show_licenses_checkbox,
        show_credits_checkbox, 
        logo_position_radio, 
        logo_sizing_radio, 
        logo_width_input, 
        logo_height_input,
        scroll_background_color, 
        scroll_title_color,
        scroll_section_title_color, 
        scroll_name_color,        
        layout_style_radio, 
        title_uppercase_checkbox, 
        name_uppercase_checkbox,
        section_title_uppercase_checkbox,
        swap_sizes_checkbox,
        show_scroll_logo_checkbox,
        scroll_logo_height_input
    ]

    demo.load(
        fn=update_panel,
        inputs=inputs,
        outputs=panel
    )
    layout_style_radio.change(
        fn=toggle_swap_checkbox_visibility,
        inputs=layout_style_radio,
        outputs=swap_sizes_checkbox
    )
    effect_radio.change(fn=update_ui_on_effect_change, inputs=effect_radio, outputs=[speed_slider, font_size_slider])

    for input_component in inputs:
        input_component.change(fn=update_panel, inputs=inputs, outputs=panel)

if __name__ == "__main__":
    setup_demo_files()
    demo.launch()