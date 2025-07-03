import os
import requests
import io
from flask import Flask, request, jsonify, send_from_directory, send_file
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY','--')
STABILITY_API_KEY = os.environ.get('STABILITY_API_KEY','--')
# HF_API_KEY = os.environ.get("HF_API_TOKEN")
# STABLE_DIFFUSION_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

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
            return io.BytesIO(image_response.content)
        else:
            return {"success": False, "message": "No results found."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"API Error: {e}"}
    
def get_dimensions(device_type='pc'):
    # if device_type == 'mobile':
    #     return 720, 1280
    # return 1920, 1080
    if device_type == 'mobile':
        return "9:16"
    return "16:9"

def generate_with_stability(prompt : str, device_type : str):
    try:
        headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
        }
        aspect_ratio = get_dimensions(device_type)
        host = f"https://api.stability.ai/v2beta/stable-image/generate/sd3"
        files = {}
        files["none"] = ''
        negative_prompt = "" #@param {type:"string"}
        # aspect_ratio = "3:2" #@param ["21:9", "16:9", "3:2", "5:4", "1:1", "4:5", "2:3", "9:16", "9:21"]
        seed = 0 #@param {type:"integer"}
        style_preset = "None" #@param ["None", "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art", "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound", "neon-punk", "origami", "photographic", "pixel-art", "tile-texture"]
        output_format = "jpeg"
        params = {
            "prompt" : prompt,
            "negative_prompt" : negative_prompt,
            "aspect_ratio" : aspect_ratio,
            "seed" : seed,
            "output_format": output_format
        }
        if style_preset != "None":
            params["style_preset"] = style_preset
        response = requests.post(
            host,
            headers=headers,
            files=files,
            data=params
        )
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        return io.BytesIO(response.content)
    except Exception as e:
        return {"success": False, "message": f"AI Generation Error: {e}"}

@app.route('/')
def index():
    return "Wallpaper API Server is running!"

@app.route('/api/fetch', methods=['GET'])
def fetch_wallpaper():
    query = request.args.get('query')
    device = request.args.get('device', 'pc')
    if not query:
        return jsonify({"success": False, "message": "Missing 'query' parameter."}), 400
    
    result = fetch_from_pexels(query,device)
    if isinstance(result, dict):
        return jsonify({"error": "Could not fetch image."}), 500
    if result:
        return send_file(result,mimetype='image/jpeg')

@app.route('/api/generate',methods=['POST'])
def generate_wallpaper():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"success": False, "message": "Missing 'prompt' in JSON body."}), 400
    
    prompt = data['prompt']
    device = data.get('device', 'pc')
    enhanced_prompt = f"{prompt}, 4k, beautiful, high-resolution, digital art for {device}"

    result = generate_with_stability(enhanced_prompt,device)
    if isinstance(result, dict):
        return jsonify(result), 503
    if result:
        return send_file(result,mimetype='image/jpeg')

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)