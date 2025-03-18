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
import os
import pandas as pd
import requests
import json



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

class CryptoData:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url
        self.parameters = {'start': '1', 'limit': '100', 'convert': 'CAD'}
        self.headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': self.api_key}
        self.json_dicts = {}

    def load_data(self):
        try:
            with open("static/data.json", 'r') as data_file:
                data = json.load(data_file)
                coins = data.get('data', [])
            self.json_dicts = {x['symbol']: x['quote']['CAD']['price'] for x in coins if
                               'quote' in x and 'CAD' in x['quote']}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            self.json_dicts = {}

    def update_data(self):
        try:
            response = requests.get(self.url, params=self.parameters, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            with open("static/data.json", 'w') as data_file:
                json.dump(data, data_file, indent=4)
            self.load_data()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")


class UserHoldings:
    @staticmethod
    def get_user_holdings():
        try:
            data = pd.read_csv("static/holdings.csv")
            return data.to_dict(orient="list")  # Fix for returning structured dictionary
        except FileNotFoundError:
            return {'Coin': [], 'qty': [], 'value': []}

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

# Crypto section 
@app.route('/cryptoh')
def cryptoh():
    crypto_data.update_data()
    user_holdings = UserHoldings.get_user_holdings()
    holdings = []
    total_value = 0
    plus_minus_total = 0

    for i in range(len(user_holdings['Coin'])):
        symbol = user_holdings['Coin'][i]
        qty = user_holdings['qty'][i]
        buy_value = user_holdings['value'][i]
        current_price = crypto_data.json_dicts.get(symbol, 0)
        current_value = current_price * qty
        plus_minus = current_value - buy_value

        holdings.append({
            'symbol': symbol,
            'qty': qty,
            'current_price': round(current_price, 2),
            'current_value': round(current_value, 2),
            'plus_minus': round(plus_minus, 2)  # 🔹 Ensure this key exists
        })

        total_value += current_value
        plus_minus_total += plus_minus

    return render_template('cryptoh.html', holdings=holdings, total_value=round(total_value, 2), plus_minus_total=round(plus_minus_total, 2))


@app.route('/update_crypto', methods=['POST'])
def update_crypto():
    action = request.form.get('action')
    symbol = request.form['symbol'].upper()

    try:
        quantity = float(request.form['quantity'])
        amount = float(request.form['amount'])
    except ValueError:
        print("Error: Invalid numeric input")
        return redirect(url_for('index'))

    # When performing any update, first load (or create) the CSV file
    if os.path.exists("static/holdings.csv"):
        df = pd.read_csv("static/holdings.csv")
    else:
        df = pd.DataFrame(columns=['Coin', 'qty', 'value'])

    if action == "add":
        if symbol in df['Coin'].values:
            df.loc[df['Coin'] == symbol, 'qty'] += quantity
            df.loc[df['Coin'] == symbol, 'value'] += amount
        else:
            new_row = pd.DataFrame({'Coin': [symbol], 'qty': [quantity], 'value': [amount]})
            df = pd.concat([df, new_row], ignore_index=True)
        print(f"Added {quantity} of {symbol} with a total cost of {amount}")

    elif action == "remove":
        if symbol in df['Coin'].values:
            # Fetch current holdings
            current_qty = df.loc[df['Coin'] == symbol, 'qty'].values[0]
            current_value = df.loc[df['Coin'] == symbol, 'value'].values[0]
            new_qty = max(0, current_qty - quantity)
            new_value = max(0, current_value - amount)

            if new_qty == 0:
                df = df[df['Coin'] != symbol]
                print(f"Removed entire holding of {symbol}")
            else:
                df.loc[df['Coin'] == symbol, 'qty'] = new_qty
                df.loc[df['Coin'] == symbol, 'value'] = new_value
                print(f"Removed {quantity} of {symbol}; new qty: {new_qty}")
        else:
            print(f"Cannot remove {symbol} because it is not in the holdings")
    else:
        print("Invalid action received")

    df.to_csv("static/holdings.csv", index=False)
    return redirect(url_for('index'))


if __name__ == '__main__':
    KEY = os.environ.get("COIN_MARKETCAP_KEY")
    if not KEY:
        raise ValueError("COIN_MARKETCAP_KEY environment variable is missing!")

    URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    crypto_data = CryptoData(KEY, URL)

    with app.app_context():
        db.create_all()
    app.run()