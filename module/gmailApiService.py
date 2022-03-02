import os
import pickle
import sys
# Gmail API utils
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachment MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type


class GmailApi:

    def __init__(self, credentials_file, api_name, api_version, *scopes, prefix=''):
        self.CREDENTIALS = credentials_file
        self.API_SERVICE_NAME = api_name
        self.API_VERSION = api_version
        self.SCOPES = [scope for scope in scopes[0]]

        cred = None
        working_dir = os.getcwd()
        token_dir = 'token'
        pickle_file = 'token.pickle'

        # Check if token dir exists first, if not, create the folder
        if not os.path.exists(os.path.join(working_dir, token_dir)):
            os.mkdir(os.path.join(working_dir, token_dir))

        print(os.path.join(working_dir, token_dir, pickle_file))
        if os.path.exists(os.path.join(working_dir, token_dir, pickle_file)):
            with open(os.path.join(working_dir, token_dir, pickle_file), 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                try:
                    cred.refresh(Request())
                except Exception as e:
                    os.remove(os.path.join(working_dir, token_dir, pickle_file))
                    flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS, self.SCOPES)
                    cred = flow.run_local_server()
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS, self.SCOPES)
                cred = flow.run_local_server()

            with open(os.path.join(working_dir, token_dir, pickle_file), 'wb') as token:
                pickle.dump(cred, token)

        try:
            self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=cred)
            print(self.API_SERVICE_NAME, self.API_VERSION, 'service created successfully')

        except Exception as e:
            print(e)
            print(f'Failed to create service instance for {self.API_SERVICE_NAME}')
            os.remove(os.path.join(working_dir, token_dir, pickle_file))
            self.service = None

    def build_message(self, our_email, destination, subject, body, messageId, replyId, attachments=[]):
        if not attachments:  # no attachments given
            message = MIMEText(body)
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = subject
            if replyId:
                # message['threadId'] = replyId
                message['In-Reply-To'] = messageId
                message['References'] = messageId
        else:
            message = MIMEMultipart()
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = subject
            if replyId:
                message['threadId'] = replyId
            message.attach(MIMEText(body))
            for filename in attachments:
                self.add_attachment(message, filename)

        return {
            'raw': urlsafe_b64encode(message.as_bytes()).decode(),
            'threadId': replyId
        }

    def send_message(self, our_email, destination, subject, body, messageId, replyId=None, attachments=[]):

        try:
            return self.service.users().messages().send(
                userId="me",
                body=self.build_message(our_email, destination, subject, body, messageId, replyId, attachments)
            ).execute()
        except Exception as error:
            print(f"An error occurred: {error}")

    def search_messages(self, query, maxResults):
        result = self.service.users().messages().list(userId='me', q=query, maxResults=maxResults).execute()
        messages = []
        if 'messages' in result:
            messages.extend(result['messages'])
        # while 'nextPageToken' in result:
        #     page_token = result['nextPageToken']
        #     result = self.service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        #     if 'messages' in result:
        #         messages.extend(result['messages'])
        resultEmails = []
        for email in messages:
            email = self.service.users().messages().get(userId="me", id=email["id"], format='full').execute()
            resultEmail = self.process_email(email)
            resultEmails.append(resultEmail)
        return resultEmails

    def getAllLabels(self):
        return self.service.users().labels().list(userId="me").execute()

    def download_attachment(self, attachment_id, message_id):
        try:
            attachment = self.service.users().messages() \
                .attachments().get(id=attachment_id, userId='me', messageId=message_id).execute()
            data = attachment.get("data")
            return urlsafe_b64decode(data)
        except Exception as error:
            print(f"An error occurred: {error}")

    def process_parts(self, parts):
        my_body = ""
        my_attachments = []

        if parts:
            for part in parts:
                filename = part.get("filename")
                mimeType = part.get("mimeType")
                body = part.get("body")
                data = body.get("data")
                part_headers = part.get("headers")
                if part.get("parts"):
                    _body, _attachments = self.process_parts(part.get("parts"))
                    my_body = my_body + _body
                    for attachment in _attachments:
                        my_attachments.append(attachment)
                if mimeType == "text/html":
                    my_body = my_body + urlsafe_b64decode(data).decode()
                else:
                    for part_header in part_headers:
                        part_header_name = part_header.get("name")
                        part_header_value = part_header.get("value")
                        if part_header_name == "Content-Disposition":
                            if "attachment" in part_header_value:
                                my_attachments.append({
                                    'id': body.get("attachmentId"),
                                    'name': filename
                                })
        return [my_body, my_attachments]

    def process_email(self, email):
        resultEmail = {'id': email['id'], 'labelIds': email['labelIds'], 'threadId': email['threadId']}

        payload = email['payload']
        mimeType = payload['mimeType']
        headers = payload.get('headers')
        parts = payload.get('parts')

        if headers:
            for header in headers:
                name = header.get('name')
                value = header.get('value')

                if name.lower() == 'from':
                    try:
                        index = value.index('<')
                        resultEmail['from'] = {
                            'name': value[:index],
                            'email': value[index + 1:-1]
                        }
                    except:
                        resultEmail['from'] = {
                            'name': "",
                            'email': value
                        }
                if name.lower() == "subject":
                    resultEmail['subject'] = value
                if name.lower() == "date":
                    resultEmail['date'] = value[:-9]

        if parts:
            body, attachments = self.process_parts(parts)
            resultEmail['body'] = body
            resultEmail['attachments'] = attachments
        else:
            resultEmail['body'] = urlsafe_b64decode(payload.get('body').get('data')).decode()

        return resultEmail

    def get_emails_by_tags(self, tags, maxResults):
        emails = self.service.users().messages().list(userId="me", labelIds=tags, maxResults=maxResults).execute()
        resultEmails = []
        if emails.get('messages'):
            for email in emails['messages']:
                email = self.service.users().messages().get(userId="me", id=email["id"], format='full').execute()
                resultEmail = self.process_email(email)
                resultEmails.append(resultEmail)

        return resultEmails

    def get_email_by_id(self, email_id):
        email = self.service.users().messages().get(userId="me", id=email_id, format='full').execute()
        resultEmail = self.process_email(email)
        return resultEmail

    def modify_labels_to_emails(self, emails_ids, add_labels_ids, remove_labels_ids):
        try:
            self.service.users().messages().batchModify(userId="me", body={
                'ids': emails_ids,
                'addLabelIds': add_labels_ids,
                'removeLabelIds': remove_labels_ids
            }).execute()
        except Exception as error:
            print(f"An error occurred: {error}")

    def modify_labels_to_email(self, email_id, add_labels_ids, remove_labels_ids):
        try:
            self.service.users().messages().modify(userId="me", id=email_id, body={
                'addLabelIds': add_labels_ids,
                'removeLabelIds': remove_labels_ids
            }).execute()
        except Exception as error:
            print(f"An error occurred: {error}")

    def delete_emails(self, emails_ids):
        try:
            self.service.users().messages().batchDelete(userId="me", body={
                'ids': emails_ids
            }).execute()
        except Exception as error:
            print(f"An error occurred: {error}")

    def get_custom_labels(self):
        try:
            response = self.service.users().labels().list(userId="me").execute()
            labels = response.get('labels')
            if labels:
                return [label for label in labels if label.get('type') == 'user']

        except Exception as error:
            print(f"An error occurred: {error}")

    def create_custom_label(self, name):
        try:
            created_label = self.service.users().labels().create(userId="me", body={
                "name": name
            }).execute()
            return created_label
        except Exception as error:
            print(f"An error occurred: {error}")

    def add_attachment(self, message, filename):
        content_type, encoding = guess_mime_type(filename)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(filename, 'rb')
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(filename, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(filename, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(filename, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(filename)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    def get_profile(self):
        return self.service.users().getProfile(userId="me").execute()
