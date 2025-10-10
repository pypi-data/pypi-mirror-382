import boto3
from botocore.exceptions import ClientError

from utils import Singleton, Log, who_am_i


class SesFactory(object, metaclass=Singleton):
    def __init__(
            self,
            aws_region='us-east-1', aws_access_key='', aws_secret_access_key='',
            sender='', configuration_set=None, charset='utf-8'):
        self.aws_region = aws_region
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.configuration_set = configuration_set
        self.sender = sender
        self.charset = charset
        self._logger = Log().logger
        self.client = boto3.client(
            service_name='ses', region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_access_key)
        self.logger.info('SES_FACTORY created')

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger=None):  # lazy logger
        if logger is None:
            logger = Log().logger
        if (self._logger is None) or (self._logger.name != logger.name):
            self._logger = logger
            self._logger.debug(f"SES_FACTORY logger set to {self._logger.name}")

    def send_email(self, recipient, subject, body_text, body_html=None):
        __name__ = who_am_i()
        try:
            if not isinstance(recipient, list):
                recipient = [recipient]
            if body_html in [None, '']:
                body_html = body_text
            destination = {'ToAddresses': recipient, }
            message = {
                'Body': {
                    'Html': {
                        'Charset': self.charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': self.charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': self.charset,
                    'Data': subject,
                },
            }
            response = self.client.send_email(Destination=destination, Message=message, Source=self.sender)
            self.logger.info(f"SES_FACTORY.{__name__} - Email sent! Message ID: {response['MessageId']}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'MessageRejected':
                self.logger.error(f"SES_FACTORY.{__name__} - Message rejected by Amazon SES: {e.response['Error']['Message']}")
            else:
                self.logger.error(f"SES_FACTORY.{__name__} - An error occurred while sending the email: {str(e)}")
            return False
