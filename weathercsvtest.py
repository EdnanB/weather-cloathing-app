import os
import pandas as pd


temperatures = range(-20, 41)  # Temperatures from -20 to 40 degrees Celsius
weather_conditions = ["Clear", "Clouds", "Rainy", "Drizzle", "Thunderstorm", "Snow", "Foggy", "Haze", "Windy", "Tornado"]


clothing_recommendations = {
    "Clear": {
        "male": [("T-shirt", "Shorts", "Sandals"), ("T-shirt", "Shorts", "Sneakers"), ("Polo", "Shorts", "Loafers")],
        "female": [("T-shirt", "Skirt", "Sandals"), ("Blouse", "Skirt", "Flats"), ("Tank Top", "Shorts", "Sneakers"), ("Dress", "", "Sandals")]
    },
    "Clouds": {
        "male": [("T-shirt", "Jeans", "Sneakers"), ("Polo", "Chinos", "Loafers"), ("Sweatshirt", "Jeans", "Boots")],
        "female": [("Blouse", "Jeans", "Sneakers"), ("Sweater", "Jeans", "Boots"), ("T-shirt", "Trousers", "Loafers"), ("Dress", "", "Sneakers")]
    },
    "Rainy": {
        "male": [("Long Sleeve Shirt", "Pants", "Boots"), ("Raincoat, Long Sleeve Shirt", "Pants", "Rain Boots"), ("Hoodie", "Jeans", "Sneakers")],
        "female": [("Long Sleeve Shirt", "Pants", "Boots"), ("Raincoat, Long Sleeve Shirt", "Pants", "Rain Boots"), ("Hoodie", "Jeans", "Sneakers"), ("Dress", "", "Rain Boots")]
    },
    "Drizzle": {
        "male": [("Coat, Long Sleeve Shirt", "Pants", "Boots"), ("Trench Coat, Long Sleeve Shirt", "Pants", "Loafers"), ("Jacket, Long Sleeve Shirt", "Jeans", "Sneakers")],
        "female": [("Coat, Long Sleeve Shirt", "Pants", "Boots"), ("Trench Coat, Long Sleeve Shirt", "Pants", "Heels"), ("Jacket, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Dress", "", "Boots")]
    },
    "Thunderstorm": {
        "male": [("Long Sleeve Shirt", "Jeans", "Boots"), ("Waterproof Jacket, Long Sleeve Shirt", "Jeans", "Boots"), ("Sweatshirt", "Pants", "Rain Boots")],
        "female": [("Blouse", "Jeans", "Boots"), ("Waterproof Jacket, Blouse", "Jeans", "Boots"), ("Sweater", "Pants", "Rain Boots"), ("Dress", "", "Rain Boots")]
    },
    "Snow": {
        "male": [("Coat, Sweater", "Pants", "Boots"), ("Parka, Sweater", "Pants", "Snow Boots"), ("Sweater", "Jeans", "Boots")],
        "female": [("Coat, Sweater", "Pants", "Boots"), ("Parka, Sweater", "Pants", "Snow Boots"), ("Sweater", "Jeans", "Boots"), ("Dress", "", "Boots")]
    },
    "Foggy": {
        "male": [("Jacket, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Hoodie", "Jeans", "Sneakers"), ("Sweatshirt", "Jeans", "Boots")],
        "female": [("Jacket, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Hoodie", "Jeans", "Sneakers"), ("Sweatshirt", "Jeans", "Boots"), ("Dress", "", "Sneakers")]
    },
    "Haze": {
        "male": [("T-shirt", "Shorts", "Sandals"), ("T-shirt", "Jeans", "Sneakers"), ("Polo", "Shorts", "Loafers")],
        "female": [("T-shirt", "Skirt", "Sandals"), ("Blouse", "Jeans", "Sneakers"), ("Tank Top", "Shorts", "Sneakers"), ("Dress", "", "Sandals")]
    },
    "Windy": {
        "male": [("Windbreaker, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Jacket, Long Sleeve Shirt", "Pants", "Boots"), ("Sweatshirt", "Jeans", "Boots")],
        "female": [("Windbreaker, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Jacket, Long Sleeve Shirt", "Pants", "Boots"), ("Sweatshirt", "Jeans", "Boots"), ("Dress", "", "Sneakers")]
    },
    "Tornado": {
        "male": [("Windbreaker, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Jacket, Long Sleeve Shirt", "Pants", "Boots"), ("Sweatshirt", "Jeans", "Boots")],
        "female": [("Windbreaker, Long Sleeve Shirt", "Jeans", "Sneakers"), ("Jacket, Long Sleeve Shirt", "Pants", "Boots"), ("Sweatshirt", "Jeans", "Boots"), ("Dress", "", "Boots")]
    }
}

# Generate all combinations of temperature and weather conditions
data = []
weather_code = 0
for temp in temperatures:
    for condition in weather_conditions:
        recommendations = clothing_recommendations[condition]
        male_clothing_options = recommendations["male"]
        female_clothing_options = recommendations["female"]
        
        for male_clothing, female_clothing in zip(male_clothing_options, female_clothing_options):
            data.append([temp, condition, weather_code, *male_clothing, *female_clothing])
            weather_code += 1

# Create DataFrame
columns = ["Temperature", "Weather", "Weather_Code", "UpperWear_Male", "LowerWear_Male", "Footwear_Male", "UpperWear_Female", "LowerWear_Female", "Footwear_Female"]
df = pd.DataFrame(data, columns=columns)

# Ensure "static" directory exists, create if not
if not os.path.exists('static'):
    os.makedirs('static')

# Create CSV file
file_path = os.path.join('static', 'weather.csv')
df.to_csv(file_path, index=False)

print(f"CSV file successfully created at {file_path}")
