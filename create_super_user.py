from user_models import SuperUser, db
from hashlib import sha256
from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:pw@localhost/brench_u_need'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)


def hash_password(password):
    salt = b'some_random_salt'
    return sha256(salt + password.encode()).hexdigest() 


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


if __name__ == '__main__':
    username = input("Unesite korisničko ime za super korisnika: ")
    password = input("Unesite lozinku za super korisnika: ")
    create_super_user(username, password)
