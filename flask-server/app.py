import os
import random
import string
import datetime
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_mail import Mail, Message
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from threading import Timer

# Application configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MieLockDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-email-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'your-email@example.com')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
api = Api(app)
csrf = CSRFProtect(app)
limiter = Limiter(app, key_func=get_remote_address)

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info():
    logger.info('Request Headers: %s', request.headers)
    logger.info('Request Body: %s', request.get_data())

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Models
class Master(db.Model):
    __tablename__ = 'master'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    verifications = db.relationship('Verification', backref='master', lazy=True)
    accesses = db.relationship('Access', backref='master', lazy=True)

class Verification(db.Model):
    __tablename__ = 'verification'
    vid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)
    email_id = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    question_1_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=False)
    question_1_answer = db.Column(db.String(100), nullable=False)
    question_2_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=False)
    question_2_answer = db.Column(db.String(100), nullable=False)
    question_3_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=False)
    question_3_answer = db.Column(db.String(100), nullable=False)
    protected = db.relationship('Protected', backref='verification', lazy=True)

class Protected(db.Model):
    __tablename__ = 'protected'
    pid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('verification.vid'), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Access(db.Model):
    __tablename__ = 'access'
    room_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)
    room_number = db.Column(db.String(100), nullable=False)

class SecurityQuestion(db.Model):
    __tablename__ = 'security_question'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)

class OTPManager:
    def __init__(self):
        self.otp_store = {}

    def generate_otp(self, email):
        otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.otp_store[email] = otp
        Timer(30.0, self.expire_otp, [email]).start()
        return otp

    def expire_otp(self, email):
        if email in self.otp_store:
            del self.otp_store[email]

    def validate_otp(self, email, otp):
        return self.otp_store.get(email) == otp

otp_manager = OTPManager()

class SecurityQuestions(Resource):
    @limiter.limit("10 per minute")
    def get(self):
        questions = SecurityQuestion.query.all()
        selected_questions = random.sample(questions, 3)
        result = [{'question_id': q.question_id, 'question': q.question} for q in selected_questions]
        return jsonify(result)

class RegisterUser(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.json
        # Validate and sanitize inputs
        name = data.get('name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        questions_answers = data.get('questions_answers')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Generate OTP and send via email
        otp = otp_manager.generate_otp(email)
        msg = Message('Your OTP Code', recipients=[email])
        msg.body = f'Your OTP code is {otp}. It will expire in 30 seconds.'
        mail.send(msg)

        return jsonify({'message': 'OTP sent to your email. Please verify within 30 seconds.'})

class VerifyRegistration(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.json
        email = data.get('email')
        otp = data.get('otp')

        if not otp_manager.validate_otp(email, otp):
            return jsonify({'message': 'OTP is invalid or has expired.'}), 400

        name = data.get('name')
        phone_number = data.get('phone_number')
        username = data.get('username')
        password = data.get('password')
        questions_answers = data.get('questions_answers')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        try:
            new_master = Master(name=name, phone_number=phone_number)
            db.session.add(new_master)
            db.session.flush()  # to get the master id

            new_verification = Verification(
                id=new_master.id,
                email_id=email,
                username=username,
                question_1_id=questions_answers[0]['question_id'],
                question_1_answer=questions_answers[0]['answer'],
                question_2_id=questions_answers[1]['question_id'],
                question_2_answer=questions_answers[1]['answer'],
                question_3_id=questions_answers[2]['question_id'],
                question_3_answer=questions_answers[2]['answer'],
            )
            db.session.add(new_verification)
            db.session.flush()  # to get the verification id

            new_protected = Protected(
                vid=new_verification.vid,
                password=hashed_password
            )
            db.session.add(new_protected)
            db.session.commit()
            return jsonify({'message': 'User registered successfully.'})
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while registering the user.'}), 400

class SignIn(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        verification = Verification.query.filter_by(username=username).first()

        if verification and check_password_hash(verification.protected[0].password, password):
            email = verification.email_id
            otp = otp_manager.generate_otp(email)
            msg = Message('Your OTP Code', recipients=[email])
            msg.body = f'Your OTP code is {otp}. It will expire in 30 seconds.'
            mail.send(msg)
            return jsonify({'message': 'OTP sent to your email. Please verify within 30 seconds.'})
        else:
            return jsonify({'message': 'Invalid username or password.'}), 400

class VerifySignIn(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.json
        email = data.get('email')
        otp = data.get('otp')

        if otp_manager.validate_otp(email, otp):
            return jsonify({'message': 'Sign in successful.'})
        else:
            return jsonify({'message': 'OTP is invalid or has expired.'}), 400

# Register API resources
api.add_resource(SecurityQuestions, '/security-questions')
api.add_resource(RegisterUser, '/register')
api.add_resource(VerifyRegistration, '/verify-registration')
api.add_resource(SignIn, '/signin')
api.add_resource(VerifySignIn, '/verify-signin')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
