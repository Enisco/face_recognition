import re
from datetime import datetime

from flask import Flask, jsonify, send_file, request
import urllib.parse

import os
from urllib.request import urlretrieve

import face_recognition
import matplotlib.pyplot as plt
import requests
from PIL import Image


app = Flask(__name__)

# Get the current directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the folder to save images
images_folder = os.path.join(base_dir, 'images')

# Ensure the folder exists
os.makedirs(images_folder, exist_ok=True)


@app.route("/")
def home():
    return "Hello, David!"


def download_image(url):
    try:
        coded_url = ''
        try:
            coded_url = url.replace("/files/", "/files%2F")
        except: 
            coded_url = url

        print("Coded imageURL: " + coded_url)
        response = requests.get(coded_url, stream=True)
        response.raise_for_status()

        # image_path = 'venv\\downloaded_image.jpg'
        image_path = os.path.join(images_folder, 'downloaded_image.jpg')

        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return image_path

    except requests.exceptions.HTTPError as e:
        print('Server error: ' + str(e))
        return jsonify({'error': 'Server error: ' + str(e)}), 500


def recognize_face(image_path):
    captured_face = image_path
    registered_face = "david.jpeg"
    
    captured_image_ = Image.open(captured_face)
    registered_image_ = Image.open(registered_face)
    captured_image_
    registered_image_
    
    # loading the images into the face rec library
    captured_image = face_recognition.load_image_file(captured_face)
    registered_image = face_recognition.load_image_file(registered_face)

    # encoding the images in the face rec library
    registered_image_encoded = face_recognition.face_encodings(registered_image)[0]

    try:
        captured_image_encoded = face_recognition.face_encodings(captured_image)[0]
    except requests.exceptions.HTTPError as e:
        print('Error encoding image: ' + str(e))
        return False

    comparison_result = face_recognition.api.compare_faces([registered_image_encoded], captured_image_encoded, tolerance = 0.45)
    print("comparison result: " + str(comparison_result))

    return comparison_result


@app.route("/compare_faces")
def compare_faces():
    image_url = request.args.get('url')
    print("Received imageURL: " + image_url)

    # Download image and save to image_path
    image_path = download_image(image_url)
    send_file(image_path, mimetype='image/jpeg')

    result = recognize_face(image_path)
    print("Result in string: " + str(result))

    if str(result).__contains__('True'):
        return jsonify({'status': True, 'message': 'Faces match'})
    else:
        return jsonify({'status': False, 'message': 'Faces do not match'})
