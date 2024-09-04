# Import neophodnih modula
from flask_sqlalchemy import SQLAlchemy #o	Uvozi SQLAlchemy klasu iz Flask SQLAlchemy ekstenzije, koja omogućava rad sa bazom podataka koristeći ORM (Object Relational Mapper). 

# Inicijalizacija SQLAlchemy objekta
db = SQLAlchemy() #Kreira instancu SQLAlchemy koja će biti korišćena za interakciju sa bazom podataka. 

# Model za super korisnika
class SuperUser(db.Model): #je baza za sve SQLAlchemy modele. Nasleđivanjem od db.Model, SuperUser klasa dobija funkcionalnosti potrebne za interakciju sa bazom podataka.
    __tablename__ = 'super_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)

# Model za običnog korisnika
class User(db.Model):
    __tablename__ = 'user_podatci'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    ime = db.Column(db.String(100), nullable=False)
    prezime = db.Column(db.String(100), nullable=False)
    spol = db.Column(db.String(10), nullable=False)

# Model za preporuke korisnika
class UserRecommendations(db.Model):
    __tablename__ = 'user_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

# Model za povratne informacije korisnika
class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('user_recommendations.id'), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) #Funkcija baze podataka koja vraća trenutni datum i vreme kada se red umetne. Ovo osigurava da svaki novi red ima tačnu vremensku oznaku kada je kreiran.

    def __repr__(self): #Metoda koja definiše string reprezentaciju objekta za lakše ispisivanje.
        return f'<UserFeedback {self.id}>'

# Model za odjevne predmete
class ClothingItem(db.Model): 
    __tablename__ = 'clothing_items'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # UpperWear, LowerWear, Footwear
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    temperature_range = db.Column(db.String(20), nullable=False)  # e.g., "15-25"
    weather_condition = db.Column(db.String(50), nullable=False)

# Model za gradove korisnika
class UserCities(db.Model):
    __tablename__ = 'user_cities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    cities = db.Column(db.String(500), nullable=False)
