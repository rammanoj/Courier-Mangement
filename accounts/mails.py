from __future__ import print_function
from googleapiclient import discovery, errors
from httplib2 import Http
from oauth2client import file, client, tools
from parcelmanage.settings import STATIC_ROOT
from email.mime.text import MIMEText
from . import mail_content
import base64


SEND_MAIL = 'rammanojpotla1608@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.send']


def send_mail(service, to_mail, **kwargs):
    message = {}
    if kwargs['mail_type'] == 0:
        # user registration
        content = mail_content.registration['pre_message'] + mail_content.registration['uri'] + kwargs['id'] + \
                  mail_content.registration['post_message']
        message = MIMEText(content, 'html')
        message['subject'] = mail_content.registration['subject']
    elif kwargs['mail_type'] == 1:
        # Email change operation
        content = mail_content.email_change['pre_message'] + mail_content.email_change['uri'] + kwargs['id'] + \
                    mail_content.email_change['post_message']
        message = MIMEText(content, 'html')
        message['subject'] = mail_content.email_change['subject']
    elif kwargs['mail_type'] == 2:
        # user forgot password
        content = mail_content.forgot_password['pre_message'] + mail_content.forgot_password['uri'] + \
                  kwargs['id'] + mail_content.forgot_password['post_message']
        message = MIMEText(content, 'html')
        message['subject'] = mail_content.forgot_password['subject']
    elif kwargs['mail_type'] == 4:
        # user acceptance mail
        message = MIMEText(mail_content.accept['message'], 'html')
        message['subject'] = mail_content.accept['subject']
    elif kwargs['mail_type'] == 5:
        # user rejection mail
        message = MIMEText(mail_content.rejection['message'], 'html')
        message['subject'] = mail_content.rejection['subject']
    elif kwargs['mail_type'] == 6:
        # Clerk Added parcel to the student
        message = MIMEText(mail_content.add_parcel['message'], 'html')
        message['subject'] = mail_content.add_parcel['subject']
    elif kwargs['mail_type'] == 7:
        # Student taken parcel
        message = MIMEText(mail_content.deliver_parcel['message'], 'html')
        message['subject'] = mail_content.deliver_parcel['subject']

    message['to'] = to_mail
    message['from'] = SEND_MAIL

    msg = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    try:
        service.users().messages().send(userId='me', body=msg).execute()
        return 1
    except errors.HttpError as error:
        return 0


def main(to_mail, *args, **kwargs):
    store = file.Storage(STATIC_ROOT + '/accounts/json/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets((STATIC_ROOT + '/accounts/json/credentials.json'), SCOPES)
        creds = tools.run_flow(flow, store)
    service =discovery.build('gmail', 'v1', http=creds.authorize(Http()))

    return send_mail(service, to_mail, *args, **kwargs)
