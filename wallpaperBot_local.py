import os
import requests
import torch

from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

load_dotenv()
MODEL_ID = "stabilityai/stable-diffusion-2"
OUTPUT_DIR = "generated_images"
OUTPUT_DIR_FI = "fetched_images"
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY','--')

pipe = None
try:
    scheduler = EulerDiscreteScheduler.from_pretrained(MODEL_ID, subfolder="scheduler")
    if torch.cuda.is_available():
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            scheduler=scheduler,
            torch_dtype=torch.float16
        )
        pipe = pipe.to("cuda")
        pipe.enable_attention_slicing()
    elif torch.backends.mps.is_available():
        pipe = DiffusionPipeline.from_pretrained(
            MODEL_ID,
            scheduler=scheduler,
            torch_dtype=torch.float32
        )
        pipe = pipe.to("mps")
        pipe.enable_attention_slicing()
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            scheduler=scheduler,
            torch_dtype=torch.float32
        ).to("cpu")
        pipe.enable_attention_slicing()
        print("WARNING: No GPU detected. AI generation will be disabled.")
except Exception as e:
    pipe = None
    print(f"Error loading the model: {e}")

def get_dimensions(device_type='pc'):
    if device_type == 'mobile':
        return 768, 1344
    return 1344, 768

def generate_locally(prompt: str, device_type: str):
    if not pipe:
        return None

    width, height = get_dimensions(device_type)
    try:
        enhanced_prompt = f"({prompt}), cinematic, stunning, high detail, 4k, photorealistic"
        negative_prompt = "blurry, cartoon, drawing, deformed, ugly, low quality"
        image = pipe(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=25,
            guidance_scale=9
        ).images[0]

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        safe_filename = "".join([c for c in prompt if c.isalnum() or c in " _-"]).rstrip()[:60].replace(" ", "_")
        image_path = os.path.join(OUTPUT_DIR, f"{safe_filename}_{device_type}.png")

        image.save(image_path)
    except Exception as e:
        print(f"An error occurred during image generation: {e}")

def fetch_from_pexels(query : str, device_type : str):
    orientation = 'portrait' if device_type == 'mobile' else 'landscape'
    headers = {'Authorization': PEXELS_API_KEY}
    params = {'query': query, 'per_page': 1, 'orientation': orientation}
    try:
        response = requests.get('https://api.pexels.com/v1/search', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['photos']:
            photo = data['photos'][0]
            image_url = photo['src']['original']
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            safe_filename = "".join([c for c in query if c.isalnum() or c in " _-"]).rstrip()[:60].replace(" ", "_")
            image_path = os.path.join(OUTPUT_DIR_FI, f"{safe_filename}_{device_type}.png")

            if not os.path.exists(OUTPUT_DIR_FI):
                os.makedirs(OUTPUT_DIR_FI)

            with open(image_path, 'wb') as f:
                f.write(image_response.content)
        else:
            return {"success": False, "message": "No results found."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"API Error: {e}"}

if __name__ == "__main__":
    if pipe:
        while True:
            user_prompt = input ("press 1 to generate and 2 to fetch wallpaper (or type 'quit' to exit)")
            if user_prompt == '1':
                user_prompt = input("Enter your wallpaper image prompt: ")
                device_choice = input("for 'pc' or 'mobile'?")
                if device_choice.lower() not in ['pc', 'mobile']:
                    device_choice = 'pc'
                generate_locally(user_prompt, device_choice)
            elif user_prompt == '2' :
                user_query = input("Enter your wallpaper image query: ")
                device_choice = input("for 'pc' or 'mobile'?")
                if device_choice.lower() not in ['pc', 'mobile']:
                    device_choice = 'pc'
                fetch_from_pexels(user_query, device_choice)
            elif user_prompt.lower() == 'quit':
                break
            else :
                print("please enter correct input.")
                continue
    else:
        print("\nmodel could not be loaded.")
        while True:
            user_query = input("Enter your wallpaper image query (or type 'quit' to exit): ")
            if user_query.lower() == 'quit':
                break
            device_choice = input("for 'pc' or 'mobile'?")
            if device_choice.lower() not in ['pc', 'mobile']:
                device_choice = 'pc'
            fetch_from_pexels(user_query, device_choice)