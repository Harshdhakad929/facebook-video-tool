from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import os

# Initialize the Flask app
app = Flask(__name__)

# Function to extract Facebook video details
def get_facebook_video_details(video_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Send a request to the Facebook video page
        response = requests.get(video_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the video title
        title = soup.find("title").text.strip() if soup.find("title") else "Title not found"

        # Return the video details
        return {
            "title": title,
            "url": video_url,
        }
    except Exception as e:
        return {"error": str(e)}

# Function to search Google
def google_search(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Route to handle search requests
@app.route('/search', methods=['POST'])
def search():
    # Get the video URL from the request
    video_url = request.json.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Step 1: Get Facebook video details
    video_details = get_facebook_video_details(video_url)
    if "error" in video_details:
        return jsonify(video_details), 500

    # Step 2: Search Google for the video title
    google_api_key = "AIzaSyC4Q0d-27SKLxsQUDJ3WzMFboUOGy4aVZQ"  # Replace with your Google API key
    google_cx = "7354c4ce18a7d434c"  # Replace with your Custom Search Engine ID
    google_results = google_search(video_details["title"], google_api_key, google_cx)

    if "error" in google_results:
        return jsonify(google_results), 500

    # Step 3: Return the results
    return jsonify({
        "video_details": video_details,
        "google_results": google_results.get("items", [])
    })

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)