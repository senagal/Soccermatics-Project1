from PIL import Image

# ---------------------------
# 1. Load images
# ---------------------------
image_files = ["PassesPer90.png", "ShotAssistsPer90.png", "GoalAssistsPer90.png"]
images = [Image.open(img) for img in image_files]

# ---------------------------
# 2. Determine size for combination
# ---------------------------
# Max height among images
max_height = max(img.height for img in images)
# Total width if placed side by side
total_width = sum(img.width for img in images)
# Gap between images (optional)
gap = 20  # pixels
total_width_with_gaps = total_width + gap * (len(images)-1)

# ---------------------------
# 3. Scale images if too wide
# ---------------------------
max_total_width = 2000  # adjust depending on your document width
if total_width_with_gaps > max_total_width:
    scale_factor = max_total_width / total_width_with_gaps
    images = [
        img.resize(
            (int(img.width * scale_factor), int(img.height * scale_factor)),
            Image.Resampling.LANCZOS
        )
        for img in images
    ]
    total_width_with_gaps = sum(img.width for img in images) + gap * (len(images)-1)
    max_height = max(img.height for img in images)

# ---------------------------
# 4. Create blank canvas
# ---------------------------
combined_img = Image.new('RGB', (total_width_with_gaps, max_height), color=(255, 255, 255))

# ---------------------------
# 5. Paste images side by side
# ---------------------------
x_offset = 0
for img in images:
    combined_img.paste(img, (x_offset, 0))
    x_offset += img.width + gap

# ---------------------------
# 6. Save and show combined image
# ---------------------------
combined_img.save("Combined_BarGraphs.png")
combined_img.show()

print("Combined image saved as 'Combined_BarGraphs.png'")
