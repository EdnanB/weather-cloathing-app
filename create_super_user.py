# Import neophodnih modula i funkcija
from user_models import SuperUser, db
from hashlib import sha256 #Uvozi se za rad sa hash funkcijama (koristi se za hashiranje lozinki).
from flask import Flask

# Inicijalizacija Flask aplikacije
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ednan2544@localhost:3306/user_odjeca'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Inicijalizacija baze podataka
db.init_app(app)

# Funkcija za hashiranje lozinke
def hash_password(password):
    salt = b'some_random_salt'  # Koristite isti salt kao i u ostalim dijelovima aplikacije
    return sha256(salt + password.encode()).hexdigest() #o	SHA-256 (Secure Hash Algorithm 256-bit) je kriptografski hash algoritam koji generiše jedinstveni fiksno-dugi niz od 256 bita (32 bajta) za bilo koji ulaz podataka.

#Salt : Dodaje se random salt (nasumični niz bajtova) koji se kombinuje sa lozinkom pre hashiranja radi dodatne sigurnosti.
#b ispred stringa u Pythonu označava da je taj string bajtovni string (byte string). Bajtovni stringovi su nizovi bajtova, za razliku od običnih (Unicode) stringova koji su nizovi karaktera.

# Funkcija za kreiranje super korisnika
def create_super_user(username, password):
    with app.app_context():
        hashed_password = hash_password(password)
        super_user = SuperUser(username=username, password=hashed_password)

        try:
            db.session.add(super_user)
            db.session.commit()
            print("Super user created successfully.")
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

# Glavni deo skripte za unos podataka i kreiranje super korisnika
if __name__ == '__main__':
    username = input("Unesite korisničko ime za super korisnika: ")
    password = input("Unesite lozinku za super korisnika: ")
    create_super_user(username, password)