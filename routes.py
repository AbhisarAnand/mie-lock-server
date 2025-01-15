import urllib.parse
from datetime import datetime
import random

from flask import redirect, url_for, request, jsonify, session, flash  # type: ignore

from model import db, Master, Verification, Protected, Lock, UserAccess, RFIDTags, RFIDAccess, QRCodes, QRAccess, SecurityQuestion
from SendAlerts import SendAlerts


def register_routes(app):

	alerter = SendAlerts()

	@app.route('/')
	def index():
		return jsonify({'message': 'Welcome to MIE Door Locks API'}), 200

	@app.route('/register', methods=['POST'])
	def register():
		data = request.json

		username = data.get('username')
		email = data.get('email')
		password = data.get('password')
		name = data.get('name')
		phone_number = data.get('phone_number')

		print(f"Registering user: {username}, {email}, {name}, {phone_number}")

		# Check if username or email already exists
		if db.session.query(db.exists().where(Verification.username == username)).scalar():
			return jsonify({'message': 'Username already exists'}), 409

		if db.session.query(db.exists().where(Verification.email_id == email)).scalar():
			return jsonify({'message': 'Email already exists'}), 409

		# Create new Master entry
		master = Master(name=name, phone_number=phone_number, security_code="")

		# Create a new Verification entry
		verification = Verification(
			email_id=email,
			username=username,
			question_1_id=None,  # No security questions for now
			question_1_answer=None,
			question_2_id=None,
			question_2_answer=None,
			question_3_id=None,
			question_3_answer=None
		)

		print("Master and Verification created")

		# Hash the password and associate it with the Verification entry
		protected = Protected()
		protected.set_password(password)

		print("Password hashed")

		# Establish relationships
		verification.protected.append(protected)
		master.verifications.append(verification)

		print("Relationships established")

		# Save to the database
		db.session.add(master)
		db.session.commit()

		print("Saved to database")

		# Send confirmation email
		# message = "Thank you for registering with Mie Lock. Your email has been confirmed."
		# alerter.send_email(email, "Email Confirmation", message)

		return jsonify({'message': 'User registered successfully!'}), 201

	@app.route('/login', methods=['POST'])
	def login():
		# Extract data from the request
		data = request.json
		username = data.get('username')
		password = data.get('password')

		# Find the user by username in the Verification table
		verification = Verification.query.filter_by(username=username).first()

		if not verification:
			return jsonify({'message': 'User not found'}), 404

		# Verify the password using the Protected model
		protected = verification.protected[0]  # Assuming one protected password per verification
		if protected and protected.check_password(password):
			return jsonify({
				'message': 'User is authenticated!',
				'username': username,
				'email': verification.email_id,
				'name': verification.master.name  # Access the name from the Master table
			}), 200
		else:
			return jsonify({'message': 'User is unauthorized'}), 401

	@app.route('/verify_security_code', methods=['POST'])
	def verify_security_codes():
		data = request.get_json()

		# Validate required fields
		if not data.get('username') and not data.get('email'):
			return jsonify({'message': 'Username or email is required'}), 400

		if not data.get('code_type') or not data.get('code'):
			return jsonify({'message': 'Code type and code are required'}), 400

		username = data.get('username', "")
		email = data.get('email', "")

		# Find the user
		verification = None
		if username:
			verification = Verification.query.filter_by(username=username).first()
		elif email:
			verification = Verification.query.filter_by(email_id=email).first()

		if not verification:
			return jsonify({'message': 'No user found with the provided username or email'}), 404

		# Access the related Master object
		master = verification.master
		if not master:
			return jsonify({'message': 'Master record not found for the user'}), 404

		# Check for security codes
		codes = master.get_security_codes()
		code_type = data.get("code_type")
		provided_code = data.get("code")

		for code in codes:
			if code.startswith(f"{code_type}:"):
				stored_code = code.split(":")[1]
				if stored_code == provided_code:
					master.remove_security_code(code_type)  # Remove verified code
					db.session.commit()
					return jsonify({'message': 'Code verified successfully'}), 200
				else:
					return jsonify({'message': 'Invalid code'}), 400

		return jsonify({'message': 'Code type not found'}), 400

	@app.route('/forgot_password', methods=['POST'])
	def forgot_password():
		data = request.json

		# Validate required fields
		if not data.get('username') and not data.get('email'):
			return jsonify({'message': 'Username or email is required'}), 400

		username = data.get('username', "")
		email = data.get('email', "")

		# Find the user
		verification = None
		if username:
			verification = Verification.query.filter_by(username=username).first()
		elif email:
			verification = Verification.query.filter_by(email_id=email).first()

		if not verification:
			return jsonify({'message': 'No user found with the provided username or email'}), 404

		# Access the related Master object
		master = verification.master
		if not master:
			return jsonify({'message': 'Master record not found for the user'}), 404

		# Generate a security code
		code = str(random.randint(100000, 999999))  # 6-digit random code
		master.append_security_code("password_change", code)
		db.session.commit()

		# Send the verification email
		subject = "MIE Lock Password Reset Code"
		body = f"Dear {master.name},\n\nYour password reset code is: {code}\n\nIf you did not request a password reset, please ignore this email."

		try:
			alerter.send_email(verification.email_id, subject, body)
		except Exception as e:
			return jsonify({'message': f"Failed to send email: {str(e)}"}), 500

		return jsonify({'message': 'Verification code sent to the registered email address'}), 200

	@app.route('/change_password', methods=['POST'])
	def change_password():
		data = request.json

		# Validate required fields
		if not data.get('username') and not data.get('email'):
			return jsonify({'message': 'Username or email is required'}), 400

		if not data.get('new_password'):
			return jsonify({'message': 'New password is required'}), 400

		username = data.get('username', "")
		email = data.get('email', "")

		# Find the user
		verification = None
		if username:
			verification = Verification.query.filter_by(username=username).first()
		elif email:
			verification = Verification.query.filter_by(email_id=email).first()

		if not verification:
			return jsonify({'message': 'No user found with the provided username or email'}), 404

		# Update the password
		protected = verification.protected[0]  # Assuming one protected password per verification
		protected.set_password(data.get('new_password'))
		db.session.commit()

		return jsonify({'message': 'Password changed successfully!'}), 200

	@app.route('/add_lock', methods=['POST'])
	def add_lock():
		data = request.json

		# Extract required fields from the request
		mac_address = data.get('mac_address')
		lock_name = data.get('lock_name', "Unnamed Lock")  # Optional: Default name if not provided
		username = data.get('username')

		if not mac_address:
			return jsonify({'message': 'MAC address is required'}), 400

		if not username:
			return jsonify({'message': 'Username is required'}), 400

		# Check if the username exists
		verification = Verification.query.filter_by(username=username).first()
		if not verification:
			return jsonify({'message': f"Username '{username}' does not exist"}), 404

		# Check if the lock already exists
		existing_lock = Lock.query.filter_by(lock_mac_addr=mac_address).first()
		if existing_lock:
			return jsonify({'message': 'Lock with this MAC address already exists.'}), 409

		# Create a new Lock entry
		new_lock = Lock(
			lock_mac_addr=mac_address,
			lock_name=lock_name
		)

		# Save the new lock to the database
		db.session.add(new_lock)
		db.session.commit()

		# Assign the lock to the user (via UserAccess)
		user_access = UserAccess(
			lock_id=new_lock.lock_id,
			id=verification.master.id  # Assign lock access to the user's master ID
		)

		db.session.add(user_access)
		db.session.commit()

		# Send a confirmation response to the lock microcontroller
		return jsonify({
			'message': 'Lock added successfully and access granted to user',
			'lock_id': new_lock.lock_id,
			'mac_address': new_lock.lock_mac_addr,
			'username': username
		}), 201

	@app.route('/get_locks', methods=['POST'])
	def get_locks():
		"""
		Endpoint to retrieve all locks assigned to a specific user.
		"""
		data = request.json

		# Validate required fields
		username = data.get('username')
		if not username:
			return jsonify({'message': 'Username is required'}), 400

		# Find the user by username in the Verification table
		verification = Verification.query.filter_by(username=username).first()
		if not verification:
			return jsonify({'message': f"User '{username}' not found"}), 404

		# Retrieve all locks associated with the user
		master = verification.master
		user_accesses = UserAccess.query.filter_by(id=master.id).all()

		if not user_accesses:
			return jsonify({'message': f"No locks found for user '{username}'"}), 404

		# Construct a list of locks with details
		locks_list = []
		for access in user_accesses:
			lock = Lock.query.filter_by(lock_id=access.lock_id).first()
			if lock:
				lock_dict = {
					'lock_id': lock.lock_id,
					'lock_name': lock.lock_name,
					'mac_address': lock.lock_mac_addr
				}
				locks_list.append(lock_dict)

		# Return the locks as a JSON response
		return jsonify({
			'message': f"Locks found for user '{username}'",
			'locks': locks_list
		}), 200

	@app.route('/edit_lock', methods=['POST'])
	def edit_lock():
		data = request.json

		# Validate required fields
		mac_address = data.get('mac_address')
		edit_type = data.get('edit_type')
		username = data.get('username')

		if not mac_address or not edit_type or not username:
			return jsonify({'message': 'MAC address, edit type, and username are required'}), 400

		# Check if the username exists
		verification = Verification.query.filter_by(username=username).first()
		if not verification:
			return jsonify({'message': f"User '{username}' not found"}), 404

		# Check if the lock exists
		lock = Lock.query.filter_by(lock_mac_addr=mac_address).first()
		if not lock:
			return jsonify({'message': 'Lock not found'}), 404

		# Check if the user has access to the lock
		master = verification.master
		user_access = UserAccess.query.filter_by(lock_id=lock.lock_id, id=master.id).first()
		if not user_access:
			return jsonify({'message': f"User '{username}' does not have access to this lock"}), 403

		# Handle the edit based on edit_type
		if edit_type == "edit_name":
			updated_name = data.get('updated_name')
			if not updated_name:
				return jsonify({'message': 'Updated name is required'}), 400

			lock.lock_name = updated_name
			db.session.commit()
			return jsonify({'message': 'Lock name updated successfully'}), 200

		# Handle additional edit types as needed
		return jsonify({'message': 'Invalid edit type'}), 400

	@app.route('/keep_alive', methods=['GET'])
	def keep_alive():
		# Log the keep-alive ping
		print(f"Keep-alive ping received at {datetime.now()}")
		return jsonify({'message': 'Server is alive', 'timestamp': datetime.now().isoformat()}), 200

	@app.route('/check_user', methods=['POST'])
	def check_user():
		"""
		Endpoint to check if a user exists based on username or email.
		"""
		data = request.json

		# Validate input
		username = data.get('username', "")
		email = data.get('email', "")

		if not username and not email:
			return jsonify({'message': 'Username or email is required'}), 400

		# Check for user existence
		verification = None
		if username:
			verification = Verification.query.filter_by(username=username).first()
		elif email:
			verification = Verification.query.filter_by(email_id=email).first()

		if not verification:
			return jsonify({'message': 'User not found'}), 404

		# Return user details
		return jsonify({
			'message': 'User found',
			'username': verification.username,
			'email': verification.email_id,
			'name': verification.master.name  # Access the name from the Master table
		}), 200

	@app.route('/remove_lock', methods=['POST'])
	def remove_lock():
		"""
		Endpoint to remove a lock from the system based on its MAC address.
		"""
		data = request.json

		# Validate input
		mac_address = data.get('mac_address')
		username = data.get('username')

		if not mac_address:
			return jsonify({'message': 'MAC address is required'}), 400

		if not username:
			return jsonify({'message': 'Username is required'}), 400

		# Verify the username exists
		verification = Verification.query.filter_by(username=username).first()
		if not verification:
			return jsonify({'message': f"User '{username}' not found"}), 404

		# Find the lock by MAC address
		lock = Lock.query.filter_by(lock_mac_addr=mac_address).first()
		if not lock:
			return jsonify({'message': 'Lock not found'}), 404

		# Check if the user has access to the lock
		master = verification.master
		user_access = UserAccess.query.filter_by(lock_id=lock.lock_id, id=master.id).first()
		if not user_access:
			return jsonify({'message': f"User '{username}' does not have access to this lock"}), 403

		# Remove the lock and associated access
		db.session.delete(user_access)  # Remove the user's access to the lock
		db.session.delete(lock)  # Remove the lock itself
		db.session.commit()

		return jsonify({'message': f"Lock '{lock.lock_name}' removed successfully"}), 200

	@app.route('/remove_user', methods=['POST'])
	def remove_user():
		"""
		Endpoint to remove a user and all associated data, including locks and access records.
		"""
		data = request.json

		# Validate input
		username = data.get('username')

		if not username:
			return jsonify({'message': 'Username is required'}), 400

		# Verify the user exists
		verification = Verification.query.filter_by(username=username).first()
		if not verification:
			return jsonify({'message': f"User '{username}' not found"}), 404

		# Get the associated Master record
		master = verification.master
		if not master:
			return jsonify({'message': f"Master record not found for user '{username}'"}), 404

		# Remove all user access records
		user_accesses = UserAccess.query.filter_by(id=master.id).all()
		for access in user_accesses:
			# Remove locks associated with this user's access
			lock = Lock.query.filter_by(lock_id=access.lock_id).first()
			if lock:
				db.session.delete(lock)
			db.session.delete(access)

		# Remove all verifications and protected passwords associated with the user
		for verification in master.verifications:
			for protected in verification.protected:
				db.session.delete(protected)
			db.session.delete(verification)

		# Remove all RFID and QR data associated with the user
		rfid_tags = RFIDTags.query.filter_by(id=master.id).all()
		for tag in rfid_tags:
			rfid_accesses = RFIDAccess.query.filter_by(rid=tag.rid).all()
			for rfid_access in rfid_accesses:
				db.session.delete(rfid_access)
			db.session.delete(tag)

		qr_codes = QRCodes.query.filter_by(id=master.id).all()
		for qr_code in qr_codes:
			qr_accesses = QRAccess.query.filter_by(qid=qr_code.qid).all()
			for qr_access in qr_accesses:
				db.session.delete(qr_access)
			db.session.delete(qr_code)

		# Remove the Master record
		db.session.delete(master)

		# Commit all changes
		db.session.commit()

		return jsonify({'message': f"User '{username}' and all associated data removed successfully"}), 200

	def find_user(username=None, email=None):
		"""
		Utility function to find a user by username or email.

		Args:
			username (str): The username of the user (optional).
			email (str): The email of the user (optional).

		Returns:
			Verification: The Verification object for the user, if found.
			None: If no matching user is found.
		"""
		if not username and not email:
			return None

		# Search by username if provided
		if username:
			verification = Verification.query.filter_by(username=username).first()
			if verification and (not email or verification.email_id == email):
				return verification

		# Search by email if provided
		if email:
			verification = Verification.query.filter_by(email_id=email).first()
			if verification and (not username or verification.username == username):
				return verification

		# No matching user found
		return None
