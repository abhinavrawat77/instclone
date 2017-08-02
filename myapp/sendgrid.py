import sendgrid

import os
from sendgrid.helpers.mail import *

#setting the send grid api key
sg = sendgrid.SendGridAPIClient(apikey='SG')

#email content
from_email = Email("guptasa00@gmail.com")
to_email = Email("srishtichauhan3@gmail.com")
subject = "Sending with SendGrid is Fun"
content = Content("text/plain", "and easy to do anywhere, even with Python")
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())

#print response status  from client the mail has send
print(response.status_code)
print(response.body)
print(response.headers)