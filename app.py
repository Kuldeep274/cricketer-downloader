from flask import Flask, render_template, request, jsonify, redirect, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager 
import requests
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google OAuth Credentials (Use Firebase Auth for simplicity)
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"

@app.route("/")
def home():
    return render_template("doct.html")

@app.route("/login")
def login():
    return redirect(f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:5000/auth/callback&response_type=code&scope=email")

@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return "Login failed", 400
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:5000/auth/callback"
    }

    response = requests.post(token_url, data=token_data)
    token_info = response.json()
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + token_info["access_token"]
    user_info = requests.get(user_info_url).json()

    session["user"] = user_info
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return f"Welcome {session['user']['email']}! <br><a href='/scrape-images'>Get Cricketer Images</a>"

@app.route("/scrape-images")
def scrape_images():
    cricketer_name = "Virat Kohli"
    search_url = f"https://www.google.com/search?q={cricketer_name}+cricket+images&tbm=isch"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(search_url)
    images = driver.find_elements(By.TAG_NAME, "img")

    image_urls = [img.get_attribute("src") for img in images[:10]]  # Get first 10 images
    driver.quit()

    return jsonify({"images": image_urls})

if __name__ == "__main__":
    app.run(debug=True)
