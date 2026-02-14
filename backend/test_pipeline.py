from generator import generate_manim_code
from code_writer import save_code
from renderer import render_scene
from validator import ManimCodeValidator

prompt = "Animate a sine wave"

code = generate_manim_code(prompt)

validator = ManimCodeValidator()
result = validator.validate(code)

if not result.is_valid:
    print(result.errors)
    raise Exception("Validation failed")

file_path = save_code(code)
render_scene(file_path, result.scene_name)

print("Pipeline completed.")
