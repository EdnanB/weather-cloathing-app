from flask_sqlalchemy import SQLAlchemy 


db = SQLAlchemy() 


class SuperUser(db.Model):
    __tablename__ = 'super_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)


class User(db.Model):
    __tablename__ = 'user_podatci'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    ime = db.Column(db.String(100), nullable=False)
    prezime = db.Column(db.String(100), nullable=False)
    spol = db.Column(db.String(10), nullable=False)


class UserRecommendations(db.Model):
    __tablename__ = 'user_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)


class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('user_recommendations.id'), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) 

    def __repr__(self): 
        return f'<UserFeedback {self.id}>'


class ClothingItem(db.Model): 
    __tablename__ = 'clothing_items'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    temperature_range = db.Column(db.String(20), nullable=False)  
    weather_condition = db.Column(db.String(50), nullable=False)


class UserCities(db.Model):
    __tablename__ = 'user_cities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_podatci.id'), nullable=False)
    cities = db.Column(db.String(500), nullable=False)
