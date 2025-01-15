from flask import Flask
from config import Config
from model import db, bcrypt
from routes import register_routes
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
	db.create_all()
	# db.drop_all()

register_routes(app)


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 10000))
	app.run(host='0.0.0.0', port=port, debug=True)