import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier #Koristi se za kreiranje modela stabla odlučivanja.
#DecisionTreeClassifier je klasa u biblioteci scikit-learn (sklearn), koja se koristi za kreiranje modela stabla odlučivanja za klasifikacione zadatke
from sklearn.preprocessing import LabelEncoder #Koristi se za enkodiranje kategorijskih podataka u numeričke vrednosti.
import joblib #Koristi se za serijalizaciju i deserializaciju Python objekata (čuvanje modela).

# Konfiguracije
MODELS_DIR = 'models'
WEATHER_CSV_PATH = 'static/weather.csv'
WEATHER_ENCODER_PATH = os.path.join(MODELS_DIR, 'weather_encoder.pkl')
MODELS_MALE_PATH = os.path.join(MODELS_DIR, 'models_male.pkl')
MODELS_FEMALE_PATH = os.path.join(MODELS_DIR, 'models_female.pkl')

# Provjera postojanja direktorija "models", a ako ne, kreiranje
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# Učitavanje podataka iz CSV datoteke
df = pd.read_csv(WEATHER_CSV_PATH)

# Kreiranje instance LabelEncoder-a za vremenski uvjet
label_encoder = LabelEncoder()
df['Weather_Code'] = label_encoder.fit_transform(df['Weather'])

# Spremanje enkodera za weather
joblib.dump(label_encoder, WEATHER_ENCODER_PATH) #json.dumps pretvara Python objekat u JSON string za serializaciju podataka.
print("Enkoder za vremenski uvjet je uspješno ažuriran.")

# Funkcija za treniranje modela za određenu vrstu odjeće i skladištenje u jedan pkl fajl
def train_and_save_models(X, y_dict, output_filename):
    models = {} #Inicijalizuje prazan rečnik za čuvanje modela.
    for key, y in y_dict.items(): #Iterira kroz rečnik sa etiketama.
        model = DecisionTreeClassifier() #Kreira instancu 
        model.fit(X, y) #Treninira model koristeći ulazne podatke X i izlazne etikete y.
        models[key] = model #Čuva trenirani model u rečnik models pod ključem key.
    joblib.dump(models, output_filename)
    print(f"Modeli su uspješno sačuvani u fajl: {output_filename}")

# Definiranje varijabli za treniranje
X = df[['Temperature', 'Weather_Code']].values #Definiše ulazne podatke X koji sadrže temperaturu i kod vremenskih uslova.
y_dict_male = {  #Definiše izlazne etikete za modele za muškarce.
    'upper_wear': df['UpperWear_Male'],
    'lower_wear': df['LowerWear_Male'],
    'footwear': df['Footwear_Male']
}
y_dict_female = {
    'upper_wear': df['UpperWear_Female'],
    'lower_wear': df['LowerWear_Female'],
    'footwear': df['Footwear_Female']
}

# Treniranje i spremanje modela za muškarce
train_and_save_models(X, y_dict_male, MODELS_MALE_PATH)

# Treniranje i spremanje modela za žene
train_and_save_models(X, y_dict_female, MODELS_FEMALE_PATH)

print("Modeli za muškarce i žene su uspješno sačuvani.")
