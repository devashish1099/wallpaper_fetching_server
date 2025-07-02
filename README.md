This server fetches images using pexels AI and can also generate them using Stability AI

curl examples -> 
For generation
curl -X POST -H "Content-Type: application/json"      -d '{"prompt": "a knight looking at a castle", "device": "pc"}'      http://127.0.0.1:5000/api/generate -o knight.png

for fetching -> 
curl "http://127.0.0.1:5000/api/fetch?query=tokyo+street&device=mobile" -o tokyo_mobile.jpg
