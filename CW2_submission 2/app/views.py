import os
from app import app, models, db, login_manager
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, login_required, current_user, logout_user
from .forms import LoginForm, RegisterForm, MovieForm, ReviewForm
from .models import Movie, Review, Genre

# Upload folder configuration
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dashboard route to display all movies
@app.route('/dashboard')
@login_required
def dashboard():
    movies = Movie.query.all()  # Get all movies or filter by user if needed
    return render_template('dashboard.html', movies=movies, current_page='dashboard')


# Login route with validation
@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Username does not exist. Please register first.", "danger")
        elif not user.verify_password(form.password.data):
            flash("Incorrect password. Please try again.", "danger")
        else:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form, current_page='login')


# Registration route with validation
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username exists
        existing_user = models.User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('register'))

        # Ensure passwords match
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match. Please check your entries.", "danger")
            return redirect(url_for('register'))

        # Create new user
        hashed_password = models.User.hash_password(form.password.data)
        new_user = models.User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful!", "success")
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form, current_page='register')


@app.route("/addMovie", methods=['GET', 'POST'])
@login_required
def addMovie():
    form = MovieForm()
    if form.validate_on_submit():
        # Ensure upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Handle poster upload
        poster_filename = None
        if form.poster.data:
            poster_filename = secure_filename(form.poster.data.filename)
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], poster_filename)
            form.poster.data.save(poster_path)

        # Find or create genres
        genre_names = form.genres.data  # This will be a list of genre names from the multi-select field
        genres = []
        for name in genre_names:
            genre = Genre.query.filter_by(name=name).first()
            if not genre:
                genre = Genre(name=name)
                db.session.add(genre)
            genres.append(genre)

        # Create new movie
        new_movie = Movie(
            title=form.title.data,
            description=form.description.data,
            poster_url=poster_filename,  # Save only the filename
            user_id=current_user.id,
            genres=genres  # Associate genres
        )

        # Add movie to database
        db.session.add(new_movie)
        db.session.commit()
        
        flash("Movie added successfully!", "success")
        return redirect(url_for('allMovies'))
    
    return render_template('addMovie.html', form=form, current_page='addMovie')


# Upload file route
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File successfully uploaded'


# Route to display all movies
@app.route("/allMovies")
def allMovies():
    # Get the genre from the query parameter
    selected_genre = request.args.get('genre')

    if selected_genre:
        # Filter movies by the selected genre
        movies = Movie.query.join(Movie.genres).filter
        (Genre.name == selected_genre).all()
    else:
        # Show all movies if no genre is selected
        movies = Movie.query.all()

    # Fetch all genres for the dropdown menu
    genres = Genre.query.order_by(Genre.name).all()

    return render_template('allMovies.html', movies=movies, 
        genres=genres, selected_genre=selected_genre, current_page='allMovies')


# Route to display the user's own movies
@app.route("/myMovies")
@login_required
def myMovies():
    movies = Movie.query.filter_by(user_id=current_user.id).all()
    return render_template('myMovies.html', movies=movies, current_page='myMovies')


# Route to delete a movie
@app.route("/deleteMovie/<int:movie_id>", methods=['POST'])
@login_required
def deleteMovie(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # Ensure the current user owns the movie
    if movie.user_id != current_user.id:
        flash("You can't delete a movie you didn't upload.", "danger")
        return redirect(url_for('myMovies'))

    # Remove movie poster if exists
    if movie.poster_url:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.poster_url)
        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete reviews and the movie
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    for review in reviews:
        db.session.delete(review)

    db.session.delete(movie)
    db.session.commit()

    flash("Movie and its image were deleted successfully!", "success")
    return redirect(url_for('myMovies'))


# Route to serve uploaded files
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    uploads_dir = os.path.join(app.root_path, 'uploads')
    return send_from_directory(uploads_dir, filename)


# Route to check if a username already exists (used for registration)
@app.route("/check_username/<username>")
@login_required
def check_username(username):
    existing_user = models.User.query.filter_by(username=username).first()
    return jsonify({'exists': existing_user is not None})


# Route to handle movie reviews
@app.route('/review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def review(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(content=form.content.data, movie_id=movie.id, user_id=current_user.id)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('review', movie_id=movie.id))

    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return render_template('review.html', movie=movie, form=form, reviews=reviews)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))
