from PIL import Image
import math
import io

# Load the image
input_path = "image/TSP_CMC_49791-fig-1.jpg"  # Replace with your image file
output_path = "compressed_image.jpg"  # Path to save the compressed image

# Open the image
with Image.open(input_path) as image:

    # Increase the limit for large images
    Image.MAX_IMAGE_PIXELS = None

    width, height = image.size

    # Calculate the original resolution (diagonal size in pixels)
    original_resolution = math.sqrt(width**2 + height**2)

    # Determine the scale factor to get the desired resolution in the range of 400-500
    target_resolution = 1000 + (1500 - 1000) * (original_resolution / (original_resolution + 1))

    # Calculate the new width and height based on the target resolution
    scale_factor = target_resolution / original_resolution

    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize the image
    resized_image = image.resize((new_width, new_height))

    # Save the resized image
    resized_image.save(output_path, quality=100)
    # Save with reduced quality (e.g., 30 out of 100)
    # img.save(output_path, "JPEG", quality=10)

print(f"Compressed image saved at: {output_path}")
