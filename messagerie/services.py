import os
import re
import base64
import requests
import urlparse

from pyshorteners import Shortener
from boto3 import client


class AWSEntity(object):
    __ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    __ACCESS_ID = os.environ['AWS_ACCESS_KEY_ID']
    __REGION = os.environ['AWS_REGION']

    @classmethod
    def upload_b64(cls, base64_image, filename, bucket_name=os.environ['AWS_STORAGE_BUCKET_NAME']):
        """
        Upload base64 encoded image to s3
        :return:
        """
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            _file = re.sub("data:image/jpeg;base64,", '', base64_image)
            resp = s3.put_object(ACL='public-read-write', Bucket=bucket_name,
                                 Body=_file.decode('base64'), Key=filename)
            return True, resp
        except:
            return False, {}

    @classmethod
    def upload_file(cls, file_path, bucket_name=os.environ['AWS_STORAGE_BUCKET_NAME'], filename=None):
        """
        Upload base64 encoded image to s3
        :return:
        """
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            filename = filename if filename else os.path.basename(file_path)
            resp = s3.upload_file(file_path, bucket_name, filename)
            return True, resp
        except:
            return False, {}

    @staticmethod
    def convert_to_b64(image_url):
        """
        base64 encodes an image url
        :param image_url:
        :return:
        """
        try:
            return base64.b64encode(requests.get(image_url).content)
        except Exception, e:
            raise e

    @classmethod
    def send_formatted_message(cls, sender, subject, text_body, to, html_body='', cc=list(), bcc=list(),
                               reply_to=list()):
        """
        send formatted message using ses
        :return:
        """
        # validate email address
        if not cls.__validate_email(sender):
            raise Exception('Sender address not an email address')

        recipients = to if isinstance(to, (list, tuple)) else [to]
        invalid_recipients = filter(lambda x: not cls.__validate_email(x), recipients)
        if len(invalid_recipients) > 0:
            raise Exception('Invalid recipient addresses - {}'.format(invalid_recipients))

        cc_recipients = cc if isinstance(cc, (list, tuple)) else list(cc)
        invalid_cc = filter(lambda x: not cls.__validate_email(x), cc_recipients)
        if len(invalid_cc) > 0:
            raise Exception('Invalid cc addresses - {}'.format(invalid_cc))

        bcc_recipients = bcc if isinstance(bcc, (list, tuple)) else list(bcc)
        invalid_bcc = filter(lambda x: not cls.__validate_email(x), bcc_recipients)
        if len(invalid_bcc) > 0:
            raise Exception('Invalid bcc addresses - {}'.format(invalid_bcc))

        try:
            ses_client = client('ses', aws_secret_access_key=cls.__ACCESS_KEY,
                                aws_access_key_id=cls.__ACCESS_ID, region_name=cls.__REGION)

            response = ses_client.send_email(
                Source = sender,
                Destination={
                    'ToAddresses': recipients,
                    'CcAddresses': cc_recipients,
                    'BccAddresses': bcc_recipients
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': text_body,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        }
                    }
                },
                ReplyToAddresses= reply_to if len(reply_to) > 0 else list(sender),
                ReturnPath='',
                ReturnPathArn='',
                SourceArn='',
            )
            return response
        except Exception, e:
            raise e

    @staticmethod
    def __validate_email(email):
        regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[A-Za-z]+'
        return True if re.match(regex, email) else False

    @classmethod
    def send_raw_message(cls, sender, subject, body, recipient):
        """
        send formatted message using ses
        :return:
        """
        # validate email address
        if not cls.__validate_email(sender):
            raise Exception('Sender address not an email address')

        if not cls.__validate_email(recipient):
            raise Exception('Recipient address not an email address')

        data = {
            'Data': 'From: %s\nTo: %s\nSubject: %s\nMIME-Version: 1.0\n'
                    'Content-Type: text/plain\n\n%s.\n\n--NextPart\n'
                    % (sender, recipient, subject, body),
        }
        print(data)

        try:
            ses_client = client('ses', aws_secret_access_key=cls.__ACCESS_KEY,
                                aws_access_key_id=cls.__ACCESS_ID, region_name=cls.__REGION)

            response = ses_client.send_raw_email(
                Destinations=[
                ],
                FromArn='',
                RawMessage=data,
                ReturnPathArn='',
                Source='',
                SourceArn='',
            )
            return response
        except Exception, e:
            raise e
