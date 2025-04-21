from PIL import Image, ImageDraw, ImageFont
import os

# Create directory if it doesn't exist
os.makedirs("src/static", exist_ok=True)

# Create a placeholder image
width, height = 512, 512
background_color = (240, 240, 240)
text_color = (100, 100, 100)

# Create image with background color
image = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(image)

# Draw a border
border_width = 2
draw.rectangle(
    [(border_width, border_width), (width - border_width, height - border_width)],
    outline=(200, 200, 200),
    width=border_width
)

# Add text
message = "Image Not Available"
try:
    # Try to use a system font
    font = ImageFont.truetype("arial.ttf", 40)
except:
    # Fall back to default font
    font = ImageFont.load_default()

# Calculate text position to center it
text_width = draw.textlength(message, font=font)
text_position = ((width - text_width) / 2, height / 2 - 20)

# Draw the text
draw.text(text_position, message, font=font, fill=text_color)

# Add smaller subtext
submessage = "The original image is no longer available"
try:
    subfont = ImageFont.truetype("arial.ttf", 20)
except:
    subfont = ImageFont.load_default()

subtext_width = draw.textlength(submessage, font=subfont)
subtext_position = ((width - subtext_width) / 2, height / 2 + 20)
draw.text(subtext_position, submessage, font=subfont, fill=text_color)

# Save the image
image.save("src/static/placeholder.png")
print("Placeholder image created at src/static/placeholder.png")
