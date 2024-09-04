# Import neophodnih modula i funkcija
import base64 #Koristi se za enkodiranje podataka u base64 format (enkodiranje slika).
#Cesto koristi za prenos binarnih podataka preko protokola koji očekuju tekstualne podatke, kao što su slike ili datoteke u emailu.
import cv2 #Koristi se za obradu slika (učitavanje i enkodiranje slika).
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate #flask_migrate je ekstenzija za Flask koja koristi Alembic za rad sa migracijama baza podataka.
#Ova biblioteka omogućava jednostavno upravljanje promenama u strukturi baze podataka kroz migracije.
import json #Koristi se za rad sa JSON podacima (parsiranje i generisanje JSON-a).
#Ova biblioteka omogućava serijalizaciju (konverziju Python objekata u JSON format) i deserijalizaciju (konverziju JSON formata u Python objekte). 
from ml_utils import get_weather, load_models_and_encoders, get_weather_recommendation, get_weather_for_cities, is_valid_email, get_random_cities, get_countries_from_city_list
from crud_operations import read_user, hash_password, edit_user
from user_models import User, SuperUser, db, UserRecommendations, UserFeedback, UserCities

#Flask je mikro web okvir za Python.
# Inicijalizacija Flask aplikacije
app = Flask(__name__) #Kreira instancu Flask aplikacije. __name__ predstavlja ime trenutnog modula. Flask koristi ovo kako bi znao gde da traži resurse poput statičkih fajlova i šablona.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ednan2544@localhost:3306/user_odjeca'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key' #Postavlja tajni ključ koji Flask koristi za sigurno upravljanje sesijama i zaštitu od CSRF napada.

#CSRF (Cross-Site Request Forgery) token je bezbednosna mera koja štiti web aplikacije od neovlašćenih zahteva iz drugih sajtova.
#Sprečava napade koji koriste autentifikaciju korisnika za slanje malicioznih zahteva.


# Inicijalizacija baze podataka i migracije
db.init_app(app) #Inicijalizuje SQLAlchemy sa Flask aplikacijom.
migrate = Migrate(app, db)

# Učitavanje ML modela i enkodera
models_male_path = 'models/models_male.pkl'
models_female_path = 'models/models_female.pkl'
weather_encoder_path = 'models/weather_encoder.pkl'

models_male, models_female, weather_encoder = load_models_and_encoders(models_male_path, models_female_path, weather_encoder_path)

if models_male is None or models_female is None or weather_encoder is None:
    raise ValueError("Nisu uspješno učitani modeli i enkoderi.")

#raise funkcija se koristi za podizanje izuzetka. ValueError predstavlja grešku koja se desi kada funkcija primi ispravnu vrstu argumenta, ali argument ima neispravnu vrednost.

# Provera sesije
def check_session():
    return 'logged_in' in session and session['logged_in']

# Filter za kapitalizaciju stringova
@app.template_filter('capitalize') #To je dekorator koji registruje funkciju kao filter za kapitalizaciju stringova u šablonima.
def capitalize_filter(s):
    if isinstance(s, str): #Metoda isinstance proverava da li je objekat instanca određene klase ili tuple klasa.
        return s.capitalize()
    return s

# Funkcija za enkodiranje slike
def encode_image(image):
    if image is None:
        return None
    _, buffer = cv2.imencode('.jpg', image) #Kodira sliku u JPEG format i čuva rezultat u buffer.
    return base64.b64encode(buffer).decode('utf-8')

#buffer je promenljiva koja sadrži binarne podatke (bajtove) JPEG kodirane slike
# _ Koristi se za ignorisanje vrednosti koja nije potrebna.
# Rute (endpoints) za različite funkcionalnosti aplikacije

@app.route('/', methods=['GET', 'POST'])
def index():
    # Glavna strana sa random gradovima i vremenskim podacima
    selected_country = None
    if request.method == 'POST':
        selected_country = request.form.get('country')
        cities = get_random_cities(country=selected_country)
        session['cities'] = cities

        if 'user_id' in session:
            user_id = session['user_id']
            user_cities = UserCities.query.filter_by(user_id=user_id).first()
            if user_cities:
                user_cities.cities = ','.join([f"{city}, {country}" for city, country in cities])
            else:
                new_cities = UserCities(user_id=user_id, cities=','.join([f"{city}, {country}" for city, country in cities]))
                db.session.add(new_cities)
            db.session.commit()

    if 'user_id' in session:
        user_id = session['user_id']
        user_cities = UserCities.query.filter_by(user_id=user_id).first()
        if user_cities:
            cities = [tuple(city_country.rsplit(', ', 1)) for city_country in user_cities.cities.split(', ') if ', ' in city_country]
            #Razlog za korišćenje tuple-a u ovoj liniji koda je taj što rsplit funkcija deli string na dva dela - naziv grada i naziv države, i vraća ih kao tuple (dva povezana elementa).
        else:
            cities = get_random_cities(country=selected_country)
    else:
        cities = session.get('cities', get_random_cities(country=selected_country))

    weather_data = get_weather_for_cities([f"{city}, {country}" for city, country in cities])
    countries = get_countries_from_city_list()
    return render_template('index.html', weather_data=weather_data, cities=cities, countries=countries, selected_country=selected_country)

@app.route('/logged_in_index', methods=['GET', 'POST'])
def logged_in_index():
    # Strana za prijavljene korisnike sa vremenskim podacima za random gradove
    if not check_session() or session.get('is_admin'):
        return redirect(url_for('index'))

    selected_country = None
    if request.method == 'POST':
        selected_country = request.form.get('country')
        cities = get_random_cities(country=selected_country)
        session['cities'] = cities

    cities = session.get('cities', get_random_cities(country=selected_country))
    weather_data = get_weather_for_cities([f"{city}, {country}" for city, country in cities])
    countries = get_countries_from_city_list()
    return render_template('logged_in_index.html', weather_data=weather_data, cities=cities, countries=countries, selected_country=selected_country)

@app.route('/main_page')
def main_page():
    # Glavna strana za prijavljene korisnike
    if not check_session():
        return redirect(url_for('login'))
    if session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    return render_template('main_page.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    # Strana sa rezultatom preporuke za odjeću bazirano na vremenskim uslovima
    if not check_session() or session.get('is_admin'):
        return redirect(url_for('login'))

    city = request.args.get('city')
    if not city:
        return redirect(url_for('main_page'))

    gender = session.get('gender', 'male')
    weather_data = get_weather(city)

    if weather_data and 'main' in weather_data:
        temperature = weather_data['main']['temp']
        session['current_temperature'] = temperature
        weather_condition = weather_data['weather'][0]['main']
        wind_speed = weather_data['wind']['speed']
        wind_degree = weather_data['wind']['deg']

        recommendation_data = get_weather_recommendation(temperature, weather_condition, gender.lower(), session)

        if recommendation_data is None:
            error_message = "Nije moguće dobiti preporuku za odjeću. Molimo pokušajte ponovo."
            return render_template('main_page.html', error_message=error_message)

        upper_wear = recommendation_data['upper_wear']
        lower_wear = recommendation_data['lower_wear']
        footwear = recommendation_data['footwear']
        upper_wear_image = recommendation_data.get('upper_wear_image')
        lower_wear_image = recommendation_data.get('lower_wear_image')
        footwear_image = recommendation_data.get('footwear_image')

        user_id = session.get('user_id')
        username = session.get('username')

        new_recommendation = UserRecommendations(
            user_id=user_id,
            username=username,
            city=city,
            recommendation=json.dumps({
                'upper_wear': upper_wear,
                'lower_wear': lower_wear,
                'footwear': footwear,
                'temperature': temperature
            })
        )

        db.session.add(new_recommendation)
        db.session.commit()

        recommendation_id = new_recommendation.id

        return render_template('result.html', city=city, temperature=temperature, weather_condition=weather_condition,
                              upper_wear=upper_wear, lower_wear=lower_wear, footwear=footwear,
                              upper_wear_image=upper_wear_image, lower_wear_image=lower_wear_image, footwear_image=footwear_image,
                              wind_speed=wind_speed, wind_degree=wind_degree, recommendation_id=recommendation_id)
    else:
        error_message = "Nije moguće dobiti podatke o vremenu. Molimo pokušajte ponovo."
        return render_template('main_page.html', error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registracija korisnika
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        ime = request.form['ime']
        prezime = request.form['prezime']
        spol = request.form['spol']

        if password != confirm_password:
            flash('Lozinke se ne podudaraju. Molimo pokušajte ponovo.', 'error')
            return redirect(url_for('register'))
        
        #flash je funkcija iz Flask framework-a koja se koristi za prikazivanje privremenih poruka korisnicima. 

        if not is_valid_email(email):
            flash('Email adresa nije validna. Molimo unesite ispravnu email adresu.', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Korisničko ime već postoji. Molimo odaberite drugo.', 'error')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email adresa već postoji. Molimo unesite drugu email adresu.', 'error')
            return redirect(url_for('register'))

        hashed_password = hash_password(password)

        new_user = User(username=username, password=hashed_password, email=email, ime=ime, prezime=prezime, spol=spol)
        db.session.add(new_user)
        db.session.commit()

        flash('Uspješno ste se registrirali. Sada se možete prijaviti.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Prijava korisnika
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if user:
            stored_password_hash = user.password
            input_password_hash = hash_password(password)

            if stored_password_hash == input_password_hash:
                session['logged_in'] = True
                session['username'] = user.username
                session['user_id'] = user.id
                session['gender'] = 'male' if user.spol == 'male' else 'female'
                flash('Uspješno ste se prijavili.', 'success')
                return redirect(url_for('main_page'))
            else:
                flash('Pogrešno korisničko ime, email ili lozinka.', 'error')
        else:
            flash('Pogrešno korisničko ime, email ili lozinka.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Odjava korisnika
    session.clear()
    flash('Uspješno ste se odjavljeni.', 'success')
    return redirect(url_for('index'))

@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    # Čuvanje povratnih informacija korisnika
    if not check_session():
        return redirect(url_for('login'))

    data = request.get_json()

    user_id = session.get('user_id')
    recommendation_id = data.get('recommendation_id')
    feedback = data.get('feedback')
    min_temp = data.get('min_temp')
    max_temp = data.get('max_temp')

    if not recommendation_id or not min_temp or not max_temp:
        print("Required data is missing")
        return 'Recommendation ID, min_temp, and max_temp are required', 400

    feedback_dict = json.loads(feedback)
    upper_wear = feedback_dict.get('upper_wear', '')
    lower_wear = feedback_dict.get('lower_wear', '')
    footwear = feedback_dict.get('footwear', '')
    temperature = feedback_dict.get('temperature', '')

    if upper_wear.lower() in ['kombinezon', 'haljina']:
        lower_wear = ''

    new_feedback = UserFeedback(
        user_id=user_id,
        recommendation_id=recommendation_id,
        feedback=json.dumps({'upper_wear': upper_wear, 'lower_wear': lower_wear, 'footwear': footwear, 'temperature': temperature}),
        min_temp=min_temp,
        max_temp=max_temp
    )

    db.session.add(new_feedback)
    db.session.commit()

    return 'Feedback saved successfully', 200

@app.route('/save_recommendation', methods=['POST'])
def save_recommendation():
    # Čuvanje preporuke
    if not check_session():
        return redirect(url_for('login'))

    data = request.get_json() #Konvertuje JSON podatke iz zahteva.
    user_id = session.get('user_id')
    username = session.get('username')
    city = data.get('city')
    recommendation = data.get('recommendation')

    new_recommendation = UserRecommendations(
        user_id=user_id,
        username=username,
        city=city,
        recommendation=recommendation
    )

    db.session.add(new_recommendation)
    db.session.commit()

    return 'Recommendation saved successfully', 200

@app.route('/admin_panel')
def admin_panel():
    # Admin panel za pregled korisnika
    if not check_session() or not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    users = User.query.all()
    return render_template('admin_panel.html', users=users)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user_route():
    # Kreiranje novog korisnika od strane admina
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        ime = request.form['ime']
        prezime = request.form['prezime']
        spol = request.form['spol']

        if password != confirm_password:
            flash('Lozinke se ne podudaraju. Molimo pokušajte ponovo.', 'error')
            return redirect(url_for('create_user'))

        if not is_valid_email(email):
            flash('Email adresa nije validna. Molimo unesite ispravnu email adresu.', 'error')
            return redirect(url_for('create_user'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Korisničko ime već postoji. Molimo odaberite drugo.', 'error')
            return redirect(url_for('create_user'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email adresa već postoji. Molimo unesite drugu email adresu.', 'error')
            return redirect(url_for('create_user'))

        hashed_password = hash_password(password)

        new_user = User(username=username, password=hashed_password, email=email, ime=ime, prezime=prezime, spol=spol)
        db.session.add(new_user)
        db.session.commit()

        flash('Uspješno ste kreirali novog korisnika.', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('create_user.html')

@app.route('/read_user/<int:user_id>')
def read_user_route(user_id):
    # Pregled detalja korisnika
    user = User.query.get(user_id)
    if user:
        return render_template('read_user.html', user=user)
    else:
        return 'Korisnik nije pronađen.', 404

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user_route(user_id):
    # Ažuriranje podataka korisnika
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        new_ime = request.form.get('new_ime')
        new_prezime = request.form.get('new_prezime')
        new_spol = request.form.get('new_spol')

        success, message = edit_user(user_id, current_password, new_username, new_password, new_ime, new_prezime, new_spol)
        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('admin_panel'))
        else:
            return render_template('edit_user.html', user=user)

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST', 'DELETE'])
def delete_user_route(user_id):
    # Brisanje korisnika
    if request.method == 'POST' or request.method == 'DELETE':
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f'Korisnik {user.username} uspješno obrisan.', 'success')
        else:
            flash('Korisnik ne postoji ili je već obrisan.', 'error')

        return redirect(url_for('admin_panel'))

    return 'Method Not Allowed', 405

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Prijava admina
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        super_user = SuperUser.query.filter_by(username=username).first()

        if super_user:
            stored_password_hash = super_user.password
            input_password_hash = hash_password(password)

            if stored_password_hash == input_password_hash:
                session['logged_in'] = True
                session['username'] = username
                session['is_admin'] = True
                flash('Uspješno ste se prijavili kao admin.', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('Pogrešno korisničko ime ili lozinka.', 'error')
        else:
            flash('Pogrešno korisničko ime ili lozinka.', 'error')

    return render_template('admin_login.html')

@app.route('/about_us')
def about_us():
    # Strana "O nama"
    return render_template('about_us.html')

# Pokretanje aplikacije
if __name__ == '__main__': 
    app.run(debug=True)

#Proverava da li se skripta pokreće direktno i pokreće Flask aplikaciju u debug modu.