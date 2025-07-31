
import cv2
import joblib
import numpy as np

model = joblib.load('iris_recognition/iris_model.pkl')

def preprocess_iris(image_path):
    img = cv2.imread(image_path, 0)
    img = cv2.resize(img, (100, 100))
    return img.flatten()

def recognize_iris(image_path):
    features = preprocess_iris(image_path)
    prediction = model.predict([features])
    return prediction[0] if prediction else None
