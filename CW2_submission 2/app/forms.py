from flask_wtf import FlaskForm
from app import models
from wtforms import StringField, PasswordField, SelectMultipleField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.utils import secure_filename


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')


class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    genres = SelectMultipleField('Genres', choices=[('Action', 'Action'), ('Drama', 'Drama'), ('Comedy', 'Comedy'), ('Horror', 'Horror'), ('Sci-Fi', 'Sci-Fi'), ('Other', 'Other')], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(message="Description is required"), Length(max=500, message="Description cannot exceed 500 characters")])    
    poster = FileField('Poster Image', validators=[DataRequired(message="Poster image is required")])

    def validate_poster(self, poster):
        if poster.data:
            poster_filename = secure_filename(poster.data.filename)
            movie = models.Movie.query.filter_by(poster_url=poster_filename).first()
            if movie:
                raise ValidationError('A movie with this poster image already exists.')

    def validate_title(self, title):
        title_entered = models.Movie.query.filter_by(title=title.data).first()
        if title_entered:
            raise ValidationError('A movie with this title already exists.')


class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired()])
