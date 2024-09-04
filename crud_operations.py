# Import neophodnih modula i funkcija
import hashlib #Uvozi se za rad sa hash funkcijama (koristi se za hashiranje lozinki).
from user_models import User, db

# Funkcija za hashiranje lozinke
def hash_password(password):
    salt = b'some_random_salt'  # Dodajte svoj random salt ovde
    return hashlib.sha256(salt + password.encode()).hexdigest() #o	SHA-256 (Secure Hash Algorithm 256-bit) je kriptografski hash algoritam koji generiše jedinstveni fiksno-dugi niz od 256 bita (32 bajta) za bilo koji ulaz podataka.

# Funkcija za kreiranje korisnika
def create_user(username, password, email, ime, prezime, spol):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password, email=email, ime=ime, prezime=prezime, spol=spol)
    db.session.add(user)
    db.session.commit()

# Funkcija za čitanje korisnika po korisničkom imenu
def read_user(username):
    return User.query.filter_by(username=username).first()

# Funkcija za ažuriranje podataka korisnika
def update_user_data(username, new_username, new_password, new_ime, new_prezime, new_spol):
    user = User.query.filter_by(username=username).first()
    if user:
        if new_password:
            hashed_password = hash_password(new_password)
            user.password = hashed_password
        if new_username:
            user.username = new_username
        if new_ime:
            user.ime = new_ime
        if new_prezime:
            user.prezime = new_prezime
        if new_spol:
            user.spol = new_spol
        db.session.commit()

# Funkcija za brisanje korisnika
def delete_existing_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()

# Funkcija za uređivanje korisnika sa provjerom trenutne lozinke
def edit_user(user_id, current_password, new_username, new_password, new_ime, new_prezime, new_spol):
    user = User.query.get(user_id)
    if user:
        # Provjera trenutne lozinke
        hashed_current_password = hash_password(current_password)
        if hashed_current_password != user.password:
            return False, 'Trenutna lozinka nije ispravna.'

        if new_password:
            hashed_password = hash_password(new_password)
            user.password = hashed_password
        if new_username:
            user.username = new_username
        if new_ime:
            user.ime = new_ime
        if new_prezime:
            user.prezime = new_prezime
        if new_spol:
            user.spol = new_spol
        db.session.commit()
        return True, 'Korisnik uspješno ažuriran.'
    return False, 'Korisnik nije pronađen.'
