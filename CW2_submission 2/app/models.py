from app import db
from flask_login import UserMixin

# Association table for many-to-many relationship between Movie and Genre
movie_genre_association = db.Table(
    'movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    # Relationship with Movie model (One-to-Many)
    movies = db.relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Password hashing and verification methods
    @staticmethod
    def hash_password(password):
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)

    def verify_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)


# Genre model
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Backref for many-to-many relationship with Movie
    movies = db.relationship(
        'Movie',
        secondary=movie_genre_association,
        back_populates='genres'
    )

    def __repr__(self):
        return f'<Genre {self.name}>'


# Movie model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(100))  # URL of the movie poster
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Many-to-Many relationship with Genre
    genres = db.relationship(
        'Genre',
        secondary=movie_genre_association,
        back_populates='movies'
    )

    def __repr__(self):
        return f'<Movie {self.title}>'


# Review model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with Movie and User models
    movie = db.relationship('Movie', backref='reviews', lazy=True)
    user = db.relationship('User', backref='reviews', lazy=True)

    def __repr__(self):
        return f'<Review by {self.user.username} for {self.movie.title}>'
