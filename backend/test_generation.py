from generator import generate_manim_code
from code_writer import save_code

prompt = "Animate a sine wave on coordinate axes"

code = generate_manim_code(prompt)
print(code)

file_path = save_code(code)
print("Saved to:", file_path)
