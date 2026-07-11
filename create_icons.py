from PIL import Image, ImageDraw, ImageFont
import os

def create_jarvis_icon(size, output_path):
    img = Image.new('RGB', (size, size), '#0a0a0f')
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # Outer circle
    outer_radius = int(size * 0.4)
    draw.ellipse(
        [center - outer_radius, center - outer_radius, 
         center + outer_radius, center + outer_radius],
        outline='#00d4ff', width=max(2, size // 100)
    )
    
    # Middle circle
    middle_radius = int(size * 0.3)
    draw.ellipse(
        [center - middle_radius, center - middle_radius,
         center + middle_radius, center + middle_radius],
        outline='#0088aa', width=max(2, size // 120)
    )
    
    # Inner circle
    inner_radius = int(size * 0.2)
    draw.ellipse(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        outline='#00d4ff', width=max(2, size // 150)
    )
    
    # Center dot
    dot_radius = int(size * 0.08)
    draw.ellipse(
        [center - dot_radius, center - dot_radius,
         center + dot_radius, center + dot_radius],
        fill='#00d4ff'
    )
    
    # Cross lines
    line_width = max(2, size // 80)
    line_length = int(size * 0.1)
    
    # Top
    draw.line([(center, center - outer_radius - 10), 
               (center, center - outer_radius + line_length)], 
              fill='#00d4ff', width=line_width)
    # Bottom
    draw.line([(center, center + outer_radius + 10),
               (center, center + outer_radius - line_length)],
              fill='#00d4ff', width=line_width)
    # Left
    draw.line([(center - outer_radius - 10, center),
               (center - outer_radius + line_length, center)],
              fill='#00d4ff', width=line_width)
    # Right
    draw.line([(center + outer_radius + 10, center),
               (center + outer_radius - line_length, center)],
              fill='#00d4ff', width=line_width)
    
    img.save(output_path, 'PNG')
    print(f"Created: {output_path}")

output_dir = r"C:\Users\Kimet\OneDrive\Documents\mis proyectos visual studio core\github trabajo\jarvis\frontend\public\icons"
os.makedirs(output_dir, exist_ok=True)

create_jarvis_icon(192, os.path.join(output_dir, "icon-192.png"))
create_jarvis_icon(512, os.path.join(output_dir, "icon-512.png"))
