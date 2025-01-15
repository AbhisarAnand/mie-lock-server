import os
import secrets


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = secrets.token_hex(16)
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False