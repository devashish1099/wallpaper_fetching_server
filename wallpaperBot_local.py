import os
import io
import torch

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

MODEL_ID = "stabilityai/stable-diffusion-2"
OUTPUT_DIR = "generated_images"

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

        safe_filename = "".join([c for c in prompt if c.isalnum() or c in " _-"]).rstrip()[:60]
        image_path = os.path.join(OUTPUT_DIR, f"{safe_filename}_{device_type}.png")

        image.save(image_path)
    except Exception as e:
        print(f"An error occurred during image generation: {e}")

if __name__ == "__main__":
    if pipe:
        while True:
            user_prompt = input("Enter your wallpaper image prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == 'quit':
                break
            device_choice = input("for 'pc' or 'mobile'?")
            if device_choice.lower() not in ['pc', 'mobile']:
                device_choice = 'pc'
            generate_locally(user_prompt, device_choice)
    else:
        print("\nmodel could not be loaded.")
