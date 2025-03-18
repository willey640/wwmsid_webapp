from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random





app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Load email credentials securely
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "640willey@gmail.com"
PASSWORD = "aebn nnrj bixr yfis"  # Ideally, store this in an environment variable
current_year = datetime.datetime.now().year
# GIFs for guessing game
cheezy_list = [
    "https://media2.giphy.com/media/Km8Yi698fPFL84fEjX/giphy.gif",
    "https://media0.giphy.com/media/SZL40yJRgAOVKiVfah/giphy.gif",
    "https://media3.giphy.com/media/D2wQmQNMewjAVoCsyz/giphy.gif",
    "https://media3.giphy.com/media/TDMZWt69CBjfMYvZHG/giphy.gif",
    "https://media3.giphy.com/media/L8BS5AiR09FCnu4wtr/giphy.gif",
    "https://media3.giphy.com/media/ep7lPvQMedLcwjpdh9/giphy.gif",
    "https://media2.giphy.com/media/0o1HMTldSpFmICkbBh/giphy.gif",
    "https://media0.giphy.com/media/1ifXf6JpWbfJWGcGFU/giphy.gif",
    "https://media0.giphy.com/media/IpHDHqx8c1YQhvDYeK/giphy.gif"
]

WIN_GIF = "https://media4.giphy.com/media/ak49R7kVC4kccblgxZ/giphy.gif"

answer = random.randint(1, 9)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    login_identifier = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html', year=current_year)

@app.route('/store')
def store():
    return render_template('store.html', year=current_year)

@app.route('/crypto')
def crypto():
    return render_template('crypto.html', year=current_year)

@app.route('/aboutme')
def about():
    return render_template('aboutme.html', year=current_year)

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash("All fields are required!", "danger")
        else:
            try:
                # Prepare email
                msg = MIMEMultipart()
                msg["From"] = SENDER_EMAIL
                msg["To"] = "willey640@gmail.com"  # Send to yourself
                msg["Subject"] = f"New Contact Form Submission from {name}"

                # Email body
                body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
                msg.attach(MIMEText(body, "plain"))

                # Send email
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    # server.login(SENDER_EMAIL, PASSWORD)
                    server.login(SENDER_EMAIL, PASSWORD)
                    server.send_message(msg)

                flash("Message sent successfully!", "success")

            except Exception as e:
                flash(f"Error sending email: {e}", "danger")

        return redirect(url_for('contact'))

    return render_template("contact.html", year=current_year)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', year=current_year)

@app.route('/result')
def result():
    return render_template('result.html', year=current_year)

@app.route('/members')
def members():
    return render_template('members.html', year=current_year)

@app.route('/guess_game')
def game():
    return render_template('guess_game.html', year=current_year)

@app.route('/<int:num>')
def guess(num):
    global answer
    if num == answer:
        return render_template("result.html", message="YOU WIN!!!!", gif=WIN_GIF, year=current_year)
    else:
        hint = "Guess Higher!" if num < answer else "Guess Lower!"
        return render_template("result.html", message=hint, gif=cheezy_list[num - 1], year=current_year)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, year=current_year)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.login_identifier.data) | (User.email == form.login_identifier.data)).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check username/email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)