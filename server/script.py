import base64
import mimetypes
import os

def encode_png_to_base64(file_path):
    # Read the PNG file
    with open(file_path, 'rb') as image_file:
        image_content = image_file.read()
    
    # Encode the image content to base64
    encoded_image = base64.b64encode(image_content).decode('utf-8')
    
    # Get the MIME type (should be 'image/png' for PNG files)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'image/png'  # Default to 'image/png' if unable to determine
    
    # Create the data URL
    image_src = f'data:{mime_type};base64,{encoded_image}'
    
    return image_src

# Example usage
png_file_path = '/Users/brendanhoskins/Downloads/question.png'
result = encode_png_to_base64(png_file_path)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create the output file path
output_file_path = os.path.join(script_dir, 'question_mark.txt')

# Write the result to the output file
with open(output_file_path, 'w') as output_file:
    output_file.write(result)

print(f"Result has been written to: {output_file_path}")
