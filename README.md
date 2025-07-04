This server fetches images using pexels AI and can also generate them using Stability AI <br/>
<br/>
curl examples -> <br/>
For generation<br/>
curl -X POST -H "Content-Type: application/json"      -d '{"prompt": "a knight looking at a castle", "device": "pc"}'      http://127.0.0.1:5000/api/generate -o knight.png <br/>
<br/>
for fetching -> <br/>
curl "http://127.0.0.1:5000/api/fetch?query=tokyo+street&device=mobile" -o tokyo_mobile.jpg <br/>
<br/>
<br/>
wallpaperBot_local is for running stability diffusion model on local machine<br/>
<br/>
I have uploaded a few examples from model = stabilityai/stable-diffusion-2 in the repo <br/>
![example 1](examples/sunrise_on_a_mountain_top.png) <br/>
<br/>
![example 2](examples/cinematic_view_of_a_sunset.png) <br/>
<br/>
Created by model = stabilityai/stable-diffusion-xl-base-1.0 for mobile <br/>
![example 3](examples/sunrise_on_a_mountain_mobile.png) <br/>
<br/>
You Can also try other stable-diffusion models based on your machine like -> <br/>
stabilityai/stable-diffusion-2-1 <br/>
stabilityai/stable-diffusion-xl-base-1.0 <br/>
runwayml/stable-diffusion-v1-5 <br/>
