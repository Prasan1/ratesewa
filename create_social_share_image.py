#!/usr/bin/env python3
"""
Create a social share image for RankSewa (1200x630px for optimal social media display)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create image with brand colors
width, height = 1200, 630
bg_color = '#ffffff'
brand_color = '#0D8ABC'
text_color = '#0f172a'
accent_color = '#10b981'

# Create image
img = Image.new('RGB', (width, height), bg_color)
draw = ImageDraw.Draw(img)

# Add gradient background (simulate with rectangles)
for i in range(height):
    alpha = i / height
    # Light blue gradient
    r = int(255 - (255 - 13) * alpha * 0.05)
    g = int(255 - (255 - 138) * alpha * 0.05)
    b = int(255 - (255 - 188) * alpha * 0.05)
    draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))

# Load fonts
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Add main title
draw.text((600, 120), "RankSewa", font=title_font, fill=brand_color, anchor='mm')

# Add tagline
draw.text((600, 220), "Transparent Healthcare in Nepal", font=subtitle_font, fill=text_color, anchor='mm')

# Add key points
features = [
    "✓ Real patient reviews & ratings",
    "✓ Verify NMC credentials",
    "✓ 28,000+ doctors listed"
]

y_offset = 320
for feature in features:
    draw.text((600, y_offset), feature, font=body_font, fill=text_color, anchor='mm')
    y_offset += 60

# Add call to action
draw.rectangle([(350, 510), (850, 570)], fill=brand_color)
draw.text((600, 540), "Find Trustworthy Doctors", font=body_font, fill='white', anchor='mm')

# Add website
draw.text((600, 600), "ranksewa.com", font=small_font, fill='#64748b', anchor='mm')

# Save
output_path = 'static/img/social-share.png'
img.save(output_path, 'PNG', quality=95)
print(f"✅ Social share image created: {output_path}")
print(f"   Size: {width}x{height}px (optimized for TikTok, Instagram, Facebook)")
