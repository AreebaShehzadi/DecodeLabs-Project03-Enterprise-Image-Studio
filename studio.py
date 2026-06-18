import argparse
import requests
import urllib.parse
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from PIL import Image

# Translate Aspect Ratios to exact pixel dimensions
ASPECT_RATIOS = {
    "16:9": {"width": 1344, "height": 768},   # Landscape
    "1:1": {"width": 1024, "height": 1024},   # Square
    "9:16": {"width": 768, "height": 1344}    # Vertical
}

# Plan B API (No Key Required, Fast, Unblocked)
BASE_API_URL = "https://image.pollinations.ai/prompt/"

# CLI Setup (Terminal se input lene ke liye)
def get_user_input():
    parser = argparse.ArgumentParser(description="Enterprise Multimodal Image Studio")
    parser.add_argument("--prompt", type=str, required=True, help="Image ki description")
    parser.add_argument("--ratio", type=str, choices=["16:9", "1:1", "9:16"], default="1:1", help="Image ka aspect ratio")
    parser.add_argument("--output", type=str, default="generated_artwork.png", help="Output file ka naam")
    return parser.parse_args()

# Exponential Backoff Retry Shield
@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), reraise=True)
def generate_and_save_image(prompt, width, height, output_filename):
    encoded_prompt = urllib.parse.quote(prompt)
    final_url = f"{BASE_API_URL}{encoded_prompt}?width={width}&height={height}&nologo=true"
    
    print(f"\nSending payload to GPU cluster... Generating {width}x{height} image.")
    
    # --- DAY 2 TASK 1: Memory-Safe Streaming ---
    # stream=True lagane se file aahista aahista download hoti hai, RAM full nahi hoti
    response = requests.get(final_url, timeout=(3.05, 60), stream=True)
    
    if response.status_code != 200:
        raise Exception(f"Server Error {response.status_code}")
        
    print("Streaming data to local storage...")
    
    # iter_content use kar ke 64KB ke chunks mein save karna
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                
    # --- DAY 2 TASK 2: Integrity Verification ---
    print("Verifying binary integrity (Pixel check)...")
    try:
        # Pillow library use kar ke image check karna
        with Image.open(output_filename) as img:
            img.load() # Yeh check karta hai ke kya image file theek se download hui hai
        print("Integrity Check Passed: Image is 100% complete and healthy.")
        
    except OSError as e:
        # Agar image kharab hui, toh usey delete kar do aur error do taake dobara try ho
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise Exception(f"Data stream corrupted during download. File deleted. Retrying... Error: {e}")

def main():
    args = get_user_input()
    dimensions = ASPECT_RATIOS[args.ratio]
    
    print("--- Enterprise Image Studio Initialized ---")
    try:
        generate_and_save_image(args.prompt, dimensions["width"], dimensions["height"], args.output)
        print(f"\nSuccess! Artwork safely saved as '{args.output}'")
    except Exception as e:
        print(f"\nFailed to generate image. Error: {e}")

if __name__ == "__main__":
    main()