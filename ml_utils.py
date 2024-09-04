import requests
import pandas as pd
import joblib 
from user_models import UserFeedback, ClothingItem
import re 
import random
import json 
import base64 
import os
import cv2 


file_path_weather = "static/weather.csv"
file_path_city_list = "static/city_list.txt"


models_male_path = 'models/models_male.pkl'
models_female_path = 'models/models_female.pkl'
weather_encoder_path = 'models/weather_encoder.pkl'


def load_models_and_encoders(models_male_path, models_female_path, weather_encoder_path):
    try:
        models_male = joblib.load(models_male_path)
        models_female = joblib.load(models_female_path)
        weather_encoder = joblib.load(weather_encoder_path)
        return models_male, models_female, weather_encoder
    except Exception as e:
        print(f"Greška prilikom učitavanja modela i enkodera: {e}")
        return None, None, None



models_male, models_female, weather_encoder = load_models_and_encoders(models_male_path, models_female_path, weather_encoder_path)


def load_random_image_as_base64(image_folder):
    try:
        if not os.path.exists(image_folder):
            print(f"Folder {image_folder} does not exist.")
            return None

        image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
        if not image_files:
            print(f"No images found in folder {image_folder}.")
            return None
        image_file = random.choice(image_files)
        image_path = os.path.join(image_folder, image_file)
        image = cv2.imread(image_path)
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def get_weather_recommendation(temperature, weather_condition, gender, session):
    try:

        normalized_gender = gender.lower()
        if normalized_gender not in ['male', 'female']:
            raise ValueError("Invalid gender. Please enter 'male' or 'female'.")


        rounded_temperature = round(temperature)


        weather_map = {
            'Clear': 'Clear',
            'Clouds': 'Clouds',
            'Rain': 'Rainy',
            'Drizzle': 'Drizzle',
            'Thunderstorm': 'Thunderstorm',
            'Snow': 'Snow',
            'Mist': 'Foggy',
            'Smoke': 'Foggy',
            'Haze': 'Haze',
            'Dust': 'Foggy',
            'Fog': 'Foggy',
            'Sand': 'Foggy',
            'Ash': 'Foggy',
            'Squall': 'Windy',
            'Tornado': 'Tornado'
        }

        if weather_condition not in weather_map:
            raise ValueError(f"Unknown weather condition: {weather_condition}")

        mapped_weather_condition = weather_map[weather_condition]

        weather_df = pd.read_csv(file_path_weather)


        weather_df['Temperature'] = pd.to_numeric(weather_df['Temperature'], errors='coerce')


        matching_rows = weather_df[weather_df['Weather'] == mapped_weather_condition]

        if matching_rows.empty:
            raise ValueError(f"Nema podataka za weather condition: {mapped_weather_condition}")

        relevant_rows = matching_rows[matching_rows['Temperature'].isin(range(rounded_temperature - 5, rounded_temperature + 5))]

        if relevant_rows.empty:
            relevant_rows = matching_rows


        if normalized_gender == 'male':
            upper_wear_options = relevant_rows['UpperWear_Male'].unique()
            lower_wear_options = relevant_rows['LowerWear_Male'].unique()
            footwear_options = relevant_rows['Footwear_Male'].unique()
        else:
            upper_wear_options = relevant_rows['UpperWear_Female'].unique()
            lower_wear_options = relevant_rows['LowerWear_Female'].unique()
            footwear_options = relevant_rows['Footwear_Female'].unique()

        upper_wear = relevant_rows.iloc[0]['UpperWear_Male'] if normalized_gender == 'male' else relevant_rows.iloc[0]['UpperWear_Female']
        lower_wear = relevant_rows.iloc[0]['LowerWear_Male'] if normalized_gender == 'male' else relevant_rows.iloc[0]['LowerWear_Female']
        footwear = relevant_rows.iloc[0]['Footwear_Male'] if normalized_gender == 'male' else relevant_rows.iloc[0]['Footwear_Female']

        user_id = session.get('user_id')
        feedbacks = UserFeedback.query.filter_by(user_id=user_id).order_by(UserFeedback.timestamp.desc()).all()

        feedback_applied = False

        for feedback in feedbacks:
            feedback_data = json.loads(feedback.feedback)
            min_temp = feedback.min_temp
            max_temp = feedback.max_temp
            if min_temp <= rounded_temperature <= max_temp:
                upper_wear = feedback_data.get('upper_wear', upper_wear)
                lower_wear = feedback_data.get('lower_wear', lower_wear)
                footwear = feedback_data.get('footwear', footwear)
                feedback_applied = True
                break

        if not feedback_applied:
            print("No applicable feedback found. Using default recommendations.")

        if upper_wear.lower() in ['haljina', 'dress', 'kombinezon']:
            lower_wear = ''

        upper_wear_folder = f'data/UpperWear_{normalized_gender.capitalize()}/{upper_wear.replace(" ", "_")}'
        lower_wear_folder = f'data/LowerWear_{normalized_gender.capitalize()}/{lower_wear.replace(" ", "_")}' if lower_wear else None
        footwear_folder = f'data/Footwear_{normalized_gender.capitalize()}/{footwear.replace(" ", "_")}'

        upper_wear_image = load_random_image_as_base64(upper_wear_folder)
        lower_wear_image = load_random_image_as_base64(lower_wear_folder) if lower_wear else None
        footwear_image = load_random_image_as_base64(footwear_folder)

        return {
            'upper_wear': upper_wear,
            'lower_wear': lower_wear,
            'footwear': footwear,
            'upper_wear_image': upper_wear_image,
            'lower_wear_image': lower_wear_image,
            'footwear_image': footwear_image,
            'upper_wear_options': upper_wear_options,
            'lower_wear_options': lower_wear_options,
            'footwear_options': footwear_options
        }

    except Exception as e:
        print(f"Greška prilikom dohvatanja preporuke za odjeću: {e}")
        return None


def get_weather(city):
  
    API_KEY = "your_key"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

    try:
        url = f"{BASE_URL}q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)  
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


def get_clothing_items_for_conditions(temperature, weather_condition, gender):
    temperature = round(temperature)
    items = ClothingItem.query.filter_by(weather_condition=weather_condition, gender=gender).all()
    suitable_items = [item for item in items if int(item.temperature_range.split('-')[0]) <= temperature <= int(item.temperature_range.split('-')[1])]
    return suitable_items


def get_weather_for_cities(cities):
    weather_data = {}
    for city in cities:
        try:
            weather = get_weather(city)
            weather_data[city] = {
                'temperature': weather['main']['temp'],
                'condition': weather['weather'][0]['main'],
                'wind_speed': weather['wind']['speed']
            }
        except Exception as e:
            weather_data[city] = {
                'temperature': None,
                'condition': None,
                'wind_speed': None
            }
    return weather_data


def is_valid_email(email):

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def get_cities_and_countries(city_list_file='static/city_list.txt'):
    cities = []
    countries = set()
    with open(city_list_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and ', ' in line:
                city, country = line.rsplit(', ', 1)
                cities.append((city, country))
                countries.add(country)
    return cities, sorted(countries)


def get_random_cities(country=None, n=5):
    cities, countries = get_cities_and_countries(file_path_city_list)
    if country:
        cities = [city for city in cities if city[1] == country]
    random_cities = random.sample(cities, min(n, len(cities)))
    return random_cities

def get_countries_from_city_list():
    _, countries = get_cities_and_countries(file_path_city_list)
    return countries


def get_user_feedback(user_id, rounded_temperature):
    feedbacks = UserFeedback.query.filter_by(user_id=user_id).all()
    for feedback in feedbacks:
        feedback_data = json.loads(feedback.feedback)
        feedback_temperature = feedback_data.get('temperature')
        if feedback_temperature is not None and feedback_temperature != "":
            feedback_temperature = float(feedback_temperature)
            if rounded_temperature - 5 <= feedback_temperature <= rounded_temperature + 5:
                return feedback_data
    return None


def get_clothing_images(upper_wear, lower_wear, footwear, gender):
    upper_wear_folder = f'data/UpperWear_{gender.capitalize()}/{upper_wear.replace(" ", "_")}'
    lower_wear_folder = f'data/LowerWear_{gender.capitalize()}/{lower_wear.replace(" ", "_")}'
    footwear_folder = f'data/Footwear_{gender.capitalize()}/{footwear.replace(" ", "_")}'

    upper_wear_image = load_random_image_as_base64(upper_wear_folder)
    lower_wear_image = load_random_image_as_base64(lower_wear_folder)
    footwear_image = load_random_image_as_base64(footwear_folder)

    return upper_wear_image, lower_wear_image, footwear_image
