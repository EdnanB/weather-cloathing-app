import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier 
from sklearn.preprocessing import LabelEncoder 
import joblib


MODELS_DIR = 'models'
WEATHER_CSV_PATH = 'static/weather.csv'
WEATHER_ENCODER_PATH = os.path.join(MODELS_DIR, 'weather_encoder.pkl')
MODELS_MALE_PATH = os.path.join(MODELS_DIR, 'models_male.pkl')
MODELS_FEMALE_PATH = os.path.join(MODELS_DIR, 'models_female.pkl')

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)


df = pd.read_csv(WEATHER_CSV_PATH)


label_encoder = LabelEncoder()
df['Weather_Code'] = label_encoder.fit_transform(df['Weather'])


joblib.dump(label_encoder, WEATHER_ENCODER_PATH) #json.dumps pretvara Python objekat u JSON string za serializaciju podataka.
print("Enkoder za vremenski uvjet je uspješno ažuriran.")


def train_and_save_models(X, y_dict, output_filename):
    models = {} 
    for key, y in y_dict.items(): 
        model = DecisionTreeClassifier() 
        model.fit(X, y) 
        models[key] = model 
    joblib.dump(models, output_filename)
    print(f"Modeli su uspješno sačuvani u fajl: {output_filename}")


X = df[['Temperature', 'Weather_Code']].values 
y_dict_male = {  
    'upper_wear': df['UpperWear_Male'],
    'lower_wear': df['LowerWear_Male'],
    'footwear': df['Footwear_Male']
}
y_dict_female = {
    'upper_wear': df['UpperWear_Female'],
    'lower_wear': df['LowerWear_Female'],
    'footwear': df['Footwear_Female']
}


train_and_save_models(X, y_dict_male, MODELS_MALE_PATH)


train_and_save_models(X, y_dict_female, MODELS_FEMALE_PATH)

print("Modeli za muškarce i žene su uspješno sačuvani.")
