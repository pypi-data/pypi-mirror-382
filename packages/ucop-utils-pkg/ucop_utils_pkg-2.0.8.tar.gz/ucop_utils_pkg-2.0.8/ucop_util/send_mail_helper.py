import logging
import argparse

import boto3
from botocore.exceptions import ClientError


class send_mail_helper:
    """
    A utility class that uses AWS Simple Email Service to send email notifying
    the recipients of the status of ETL workflows.

    To instantiate the class, call its constructor method and pass the required
    parameters (see example below).
    Example: smh = send_mail_helper('sdap', 'Dev', 'hooman.pejman@ucop.edu')
             handle_permissions(table_name_list)
    """

    def __init__(self,
                 product,
                 environment,
                 sender_email,
                 region='us-west-2',
                 logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        product: str
                The name of product (e.g., sdap) for which permissions should be
                granted.
        environment: str
                The environment (e.g., dev, test, or prod) for which permissions
                should be granted.
        sender_email: str
                A verified Amazon SES email address of the sender.
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """

        PGM_NAME = 'send_mail_helper.py'
        MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
        self.logger = logging.getLogger(PGM_NAME)
        self.logger_level = logger_level.upper()
        if self.logger_level == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif self.logger_level == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        elif self.logger_level == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif self.logger_level == 'CRITICAL':
            self.logger.setLevel(logging.CRITICAL)

        self.product = product.lower()
        self.logger.debug('product={}'.format(self.product))
        self.environment = environment.capitalize()
        self.logger.debug('environment={}'.format(self.environment))
        self.sender_email = sender_email
        self.logger.debug('sender_email={}'.format(self.sender_email))
        self.region = region.lower()

        # The character encoding for the email.
        self.CHARSET = 'UTF-8'

        # Create a new SES resource and specify a region.
        self.ses = boto3.client('ses', region_name=self.region)
        self.logger.info(
            'Successfully instantiated the Send Mail Helper class.')

    @property
    def region(self):
        return self.__region

    @property
    def logger_level(self):
        return self.__logger_level

    @region.setter
    def region(self, region):
        self.__region = region

    @logger_level.setter
    def logger_level(self, logger_level):
        self.__logger_level = logger_level

    def send_email(self, recipients_list, subject, body):
        """
        Sends an email from the sender's email address that is provided in the
        class constructor to a list of one or more recipients' email addresses
        with a specific subject line and email body based on the arguments
        that are provided to this method.

        Parameters
        ----------
        recipients_list: list
                A list of one or more recipients' email addresses.
        subject: str
                Email subject line
        body: str
                Contents for the email body
        Returns
        -------
        None
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in send_email...')
        self.logger.debug('Number of recipients={}'.format(
            len(recipients_list)))
        self.logger.debug("Recipients' emails list={}".format(recipients_list))

        for recipient in recipients_list:
            try:
                # Provide the contents of the email.
                response = self.ses.send_email(
                    Destination={
                        'ToAddresses': [
                            recipient,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset':
                                self.CHARSET,
                                'Data':
                                '<html><head></head><body><p>' + body +
                                '</p></body></html>',
                            },
                            'Text': {
                                'Charset': self.CHARSET,
                                'Data': body,
                            },
                        },
                        'Subject': {
                            'Charset':
                            self.CHARSET,
                            'Data':
                            subject + ' - application: ' + self.product +
                            ', environment: ' + self.environment,
                        },
                    },
                    Source=self.sender_email,
                )
            except ClientError as e:
                self.logger.error(e.response['Error']['Message'])
            else:
                self.logger.info('Email sent! Message ID: {}'.format(
                    response['MessageId']))


def main():
    """
    Main function (entry point)
    """
    # Sample command line to execute this class:
    #   send_mail_helper.py sdap dev hooman.pejman@ucop.edu 'hpejman@ucop.edu', 'hooman.pejman@ucop.edu' sdapDev-studentEnrollmentWorkflow "This is a test!"

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description='A utility class to send email using AWS Simple Email Service (SES).')
    parser.add_argument(
        'product',
        help='Product for which to invoke the Send Mail Helper class (e.g., sdap).',
        type=str)
    parser.add_argument(
        'environment',
        help='Environment in which to invoke the Send Mail Helper class (e.g., dev).',
        type=str)
    parser.add_argument(
        'sender_email',
        help="The sender's email address. Email address must be verfied with AWS SES prior to use.",
        type=str)
    parser.add_argument(
        'recipients_list',
        nargs='+',
        help="A list of recipients' email addresses. Each email address in the list must be surrounded by quotes"
             "and separated by a comma followed by a space (e.g., 'email1@ucop.edu', 'email2@ucop.edu', ...). "
             "At least one recipient email is required. Each recipient's email address must be verified with AWS "
             'SES prior to use.',
        type=str)
    parser.add_argument(
        'subject',
        help='Email subject line.',
        type=str)
    parser.add_argument(
        'body',
        help='Email body content.',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Send Mail Helper class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    product = args.product
    environment = args.environment
    sender_email = args.sender_email
    recipients_list = args.recipients_list
    subject = args.subject
    body = args.body

    if args.region is not None:
        region = args.region
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    print(
        "About to instantiate Send Mail Helper class with mandatory positional arguments product='{}', "
        "environment='{}', sender_email='{}', recipients_list='{}', subject='{}' and body='{}'; and optional "
        "arguments region={} and logger_level='{}'"
        .format(product, environment, sender_email, recipients_list, subject,
                body, region, logger_level))

    # Example of how to instantiate the class.
    smh_obj = send_mail_helper(product, environment, sender_email, region=region,
                               logger_level=logger_level)

    # Example of how to send email.
    smh_obj.send_email(args.recipients_list, subject, body)


if __name__ == '__main__':
    main()
