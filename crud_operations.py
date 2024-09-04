import hashlib 
from user_models import User, db


def hash_password(password):
    salt = b'some_random_salt'  
    return hashlib.sha256(salt + password.encode()).hexdigest() 


def create_user(username, password, email, ime, prezime, spol):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password, email=email, ime=ime, prezime=prezime, spol=spol)
    db.session.add(user)
    db.session.commit()


def read_user(username):
    return User.query.filter_by(username=username).first()


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


def delete_existing_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()


def edit_user(user_id, current_password, new_username, new_password, new_ime, new_prezime, new_spol):
    user = User.query.get(user_id)
    if user:

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
