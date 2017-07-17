from flask_restful import Resource, Api, request
from flask import jsonify
from base import baseResource
import smtplib
from email.mime.text import MIMEText
import json

config = json.load(open('./config.json'))

class bugReport(baseResource):
	def process(self):
	
		sender = request.form.get('email')
		message = request.form.get('message')
		subject = request.form.get('subject')
		    	
		
		email = MIMEText(message)

		email['Subject'] = '[ePandda Bug Report] ' + subject
		email['From'] = sender
		email['To'] = 'michael@whirl-i-gig.com'
		#return {'email': sender, 'msg': message, 'subject': subject}
		s = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
		s.login(config['smtp_user'], config['smtp_pswd'])
		s.sendmail(sender, 'michael@whirl-i-gig.com', email.as_string())
		s.quit()
		return {'status': 'SENT'}

	def description(self):
		return {
			'name': 'ePandda Bug Reports',
			'maintainer': 'Michael Benowitz',
			'maintainer_email': 'michael@epandda.org',
			'description': 'File Bug Reports Here',
			'params': [
			{
				"name": "email",
				"label": "Email",
				"type": "text",
				"required": False,
				"description": "Your email address"
			},
			{
				"name": "message",
				"label": "Message",
				"type": "text",
				"required": False,
				"description": "Body of your message"
			},
			{
				"name": "subject",
				"label": "Subject",
				"type": "boolean",
				"required": False,
				"description": "The Subject of your message"
			}]
		}
