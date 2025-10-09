import base64
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_image(image_file, text, logo_file=None):
    image = Image.open(image_file).convert("RGBA")
    width, height = image.size

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(height // 3):
        alpha = int(255 * (1 - i / (height // 3)))
        draw.line([(0, height - i), (width, height - i)], fill=(0, 0, 0, alpha))

    combined = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(combined)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()

    max_text_width = width - 80
    lines = []
    for line in text.split("\n"):
        words = line.split()
        cur_line = ""
        for word in words:
            test_line = (cur_line + " " + word).strip()
            if draw.textlength(test_line, font=font) <= max_text_width:
                cur_line = test_line
            else:
                lines.append(cur_line)
                cur_line = word
        if cur_line:
            lines.append(cur_line)

    line_heights = [
        draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1]
        for l in lines
    ]
    total_text_height = sum(line_heights) + (len(line_heights) - 1) * 5
    margin_left = 60
    y_start = height - total_text_height - 50

    line_x = margin_left - 20
    draw.line(
        [(line_x, y_start), (line_x, y_start + total_text_height)],
        fill=(0, 0, 255, 255),
        width=5,
    )

    y = y_start
    for i, line in enumerate(lines):
        draw.text((margin_left, y), line, font=font, fill=(255, 215, 0, 255), anchor="la")
        y += line_heights[i] + 5

    if logo_file:
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((120, 120))
            combined.paste(logo, (20, 20), logo)
        except Exception:
            pass

    buffer = io.BytesIO()
    combined.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
