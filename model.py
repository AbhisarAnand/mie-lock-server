from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Master Table
class Master(db.Model):
	__tablename__ = 'master'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	phone_number = db.Column(db.String(15), nullable=False)
	security_code = db.Column(db.String(300), nullable=True, index=True)
	verifications = db.relationship('Verification', backref='master', lazy=True)
	user_accesses = db.relationship('UserAccess', backref='master', lazy=True)
	rfid_tags = db.relationship('RFIDTags', backref='master', lazy=True)
	qr_codes = db.relationship('QRCodes', backref='master', lazy=True)

	def check_security_code_type_exists(self, security_code_type):
		return security_code_type in self.security_code

	def append_security_code(self, security_code_type, security_code):
		for code_fragment in self.get_security_codes():
			if security_code_type == code_fragment.split(":")[0]:
				self.security_code = self.security_code.replace(f";{code_fragment}", "")
		self.security_code = f"{self.security_code};{security_code_type}:{security_code}"

	def get_security_codes(self):
		return self.security_code.split(";")[1:]

	def remove_security_code(self, security_code_type):
		for code_fragment in self.get_security_codes():
			if security_code_type == code_fragment.split(":")[0]:
				self.security_code = self.security_code.replace(f";{code_fragment}", "")

# Verification Table
class Verification(db.Model):
	__tablename__ = 'verification'
	vid = db.Column(db.Integer, primary_key=True)
	id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)
	email_id = db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(100), nullable=False)
	question_1_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=True)
	question_1_answer = db.Column(db.String(100), nullable=True)
	question_2_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=True)
	question_2_answer = db.Column(db.String(100), nullable=True)
	question_3_id = db.Column(db.Integer, db.ForeignKey('security_question.question_id'), nullable=True)
	question_3_answer = db.Column(db.String(100), nullable=True)
	protected = db.relationship('Protected', backref='verification', lazy=True)

# Protected Table
class Protected(db.Model):
	__tablename__ = 'protected'
	pid = db.Column(db.Integer, primary_key=True)
	vid = db.Column(db.Integer, db.ForeignKey('verification.vid'), nullable=False)
	password = db.Column(db.String(100), nullable=False)

	def set_password(self, password):
		self.password = bcrypt.generate_password_hash(password).decode('utf-8')

	def check_password(self, password):
		return bcrypt.check_password_hash(self.password, password)

# Lock Table
class Lock(db.Model):
	__tablename__ = 'lock'
	lock_id = db.Column(db.Integer, primary_key=True)
	lock_mac_addr = db.Column(db.String(50), nullable=False)
	user_accesses = db.relationship('UserAccess', backref='lock', lazy=True)
	rfid_accesses = db.relationship('RFIDAccess', backref='lock', lazy=True)
	qr_accesses = db.relationship('QRAccess', backref='lock', lazy=True)

# User Access Table
class UserAccess(db.Model):
	__tablename__ = 'user_access'
	access_id = db.Column(db.Integer, primary_key=True)
	lock_id = db.Column(db.Integer, db.ForeignKey('lock.lock_id'), nullable=False)
	id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)

# RFID Tags Table
class RFIDTags(db.Model):
	__tablename__ = 'rfid_tags'
	rid = db.Column(db.Integer, primary_key=True)
	id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)
	rfid_uid = db.Column(db.String(100), nullable=False)
	rfid_accesses = db.relationship('RFIDAccess', backref='rfid_tags', lazy=True)

# RFID Access Table
class RFIDAccess(db.Model):
	__tablename__ = 'rfid_access'
	rfid_access_id = db.Column(db.Integer, primary_key=True)
	rid = db.Column(db.Integer, db.ForeignKey('rfid_tags.rid'), nullable=False)
	lock_id = db.Column(db.Integer, db.ForeignKey('lock.lock_id'), nullable=False)

# QR Codes Table
class QRCodes(db.Model):
	__tablename__ = 'qr_codes'
	qid = db.Column(db.Integer, primary_key=True)
	id = db.Column(db.Integer, db.ForeignKey('master.id'), nullable=False)
	qr_uid = db.Column(db.String(100), nullable=False)
	expiry_date = db.Column(db.DateTime, nullable=False)
	qr_accesses = db.relationship('QRAccess', backref='qr_codes', lazy=True)

# QR Access Table
class QRAccess(db.Model):
	__tablename__ = 'qr_access'
	qr_access_id = db.Column(db.Integer, primary_key=True)
	qid = db.Column(db.Integer, db.ForeignKey('qr_codes.qid'), nullable=False)
	lock_id = db.Column(db.Integer, db.ForeignKey('lock.lock_id'), nullable=False)

# Security Question Table
class SecurityQuestion(db.Model):
	__tablename__ = 'security_question'
	question_id = db.Column(db.Integer, primary_key=True)
	question = db.Column(db.String(200), nullable=False)
