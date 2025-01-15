import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import GMAIL

class SendAlerts:

	@staticmethod
	def send_email(to_address, subject, body):
		gmail_user = GMAIL
		# gmail_password = ""
		# with open('.env', 'r') as f:
		#     for line in f:
		#         if line.startswith('GMAIL_PASSWORD'):
		#             gmail_password = line.split('=')[1].strip()
		gmail_password = os.environ.get('GMAIL_PASSWORD')
		# Email parameters
		from_address = gmail_user

		# Create the email message
		msg = MIMEMultipart()
		msg['From'] = from_address
		msg['To'] = to_address
		msg['Subject'] = subject

		# Attach the email body (text or HTML)
		msg.attach(MIMEText(body, 'plain'))

		try:
			# Connect to Gmail SMTP server
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()  # Enable security

			# Login to the Gmail account
			server.login(gmail_user, gmail_password)

			# Send the email
			text = msg.as_string()
			server.sendmail(from_address, to_address, text)

			# Terminate the SMTP session
			server.quit()

			print(f"Email sent to {to_address}!")
		except Exception as e:
			print(f"Error: {str(e)}")


if __name__ == '__main__':
	alerter= SendAlerts()
	alerter.send_email("abhisar.muz@gmail.com", "Alert Email", "Successfully sent")