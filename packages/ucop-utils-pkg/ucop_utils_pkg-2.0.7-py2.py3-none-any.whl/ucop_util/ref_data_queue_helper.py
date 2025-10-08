import boto3
import logging
import json
import argparse


class ref_data_queue_helper:
    """
    A generic helper class to handle Simple Queue Service operations
    for SDAP refernce data ingest process.
    """

    def __init__(self,
                 product,
                 environment,
                 q_name_suffix,
                 region='us-west-2',
                 logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        product: str
                Product/application (e.g., sdap) for which to operate the queue.
        environment: str
                Environment (e.g., dev, qa or prod) in which the queue exists.
        q_name_suffix: str
                The name suffix of the queue to operate on.
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        PGM_NAME = 'ref_data_queue_helper.py'
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

        if len(product) == 0:
            raise ValueError(
                'Product is a mandatory argument for the class constructor')
        if len(environment) == 0:
            raise ValueError(
                'Environment is a mandatory argument for the class constructor'
            )
        if len(q_name_suffix) == 0:
            raise ValueError(
                'q_name_suffix is a mandatory argument for the class constructor'
            )

        self.region = region.lower()
        self.product = product.lower()
        self.environment = environment.lower()
        self.q_name_suffix = q_name_suffix

        self.sqs_client = boto3.client('sqs', region_name=self.region)

        queue_url = self.get_queue_url(self.product + '-' + self.environment,
                                       self.q_name_suffix)
        if queue_url is None:
            raise ValueError(
                'No queue was found matching the q_name_suffix provided to the class constructor'
            )

        self.queue_url = queue_url
        self.logger.debug('queue_url={}'.format(self.queue_url))

        self.logger.info(
            'Successfully instantiated the Reference Data Queue Helper Utility class for queue URL={}.'
            .format(self.queue_url))

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

    def get_queue_url(self, q_name_prefix, q_name_suffix):
        """
        Returns the URL for the queue matching the q_name_prefix and q_name_suffix.
        If no matching queue if found it returns Null.

        Parameters
        ----------
        q_name_prefix: str
                The name prefix to use as a filter to obtain the queue URL.
        q_name_suffix: str
                The name suffix to use as a filter to obtain the queue URL.

        Returns
        -------
        ApproximateNumberOfMessages attribute
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in get_queue_url...')

        response = self.sqs_client.list_queues(QueueNamePrefix=q_name_prefix)
        self.logger.debug('response={}'.format(response))

        for queue_url in response['QueueUrls']:
            if queue_url.endswith(q_name_suffix):
                return queue_url

        return None

    def get_approx_msg_count(self):
        """
        Returns an approximate count of the SQS queue.

        Parameters
        ----------
        None

        Returns
        -------
        ApproximateNumberOfMessages attribute
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in get_approx_msg_count...')

        response = \
            self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=[
                    'ApproximateNumberOfMessages'
                ]
            )

        return response['Attributes']['ApproximateNumberOfMessages']

    def send_file_attributes(self, file_attribute_dict):
        """
        Sends a message to the SQS queue that contains the values provided in
        file_attribute_dict.

        Parameters
        ----------
        file_attribute_dict: dictionary
                A dictionary of key-value pairs that need to be added as the
                body of the message to the queue.

        Returns
        -------
        Response from send_message call on SQS boto3 API
        Exceptions
        ----------
        ValueError if the argument passed is empty or is not a dict
        """
        self.logger.debug('Now in send_file_attributes...')

        if type(file_attribute_dict) is not dict or len(
                file_attribute_dict) == 0:
            raise ValueError(
                'send_file_attributes must be a dictionary and cannot be empty!'
            )

        response = \
            self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=(json.dumps(file_attribute_dict))
            )

        return response

    def receive_file_attributes(self):
        """
        Receives a message from the SQS queue that contains the values provided
        in file_attribute_dict in its body.

        Parameters
        ----------
        None

        Returns
        -------
        A list of files that need to be processed. The list will be empty if no files
        are found.

        Exceptions
        ----------
        A dictionary of key-value pairs that were added as the body of the
        message to the queue.
        """
        self.logger.debug('Now in receive_file_attributes...')

        file_attribute_dict = {}

        response = \
            self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                AttributeNames=[
                    'All'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'Body'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=0
            )

        try:
            file_attribute_dict = json.loads(response['Messages'][0]['Body'])
            self.logger.debug("response['Messages'][0]['Body']={}".format(
                response['Messages'][0]['Body']))

            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=response['Messages'][0]['ReceiptHandle'])

        except KeyError:
            # Reached the end of the queue
            file_attribute_dict = 'Null'

        return file_attribute_dict

    def purge_queue(self):
        self.logger.debug('Now in purge_queue...')

        # TODO: fill in the code


def main():
    """
    Main function to test the class
    """
    parser = argparse.ArgumentParser(
        description='A utility class to handle Simple Queue Service operations.'
    )
    parser.add_argument(
        'product',
        help='product for which to invoke the Simple Queue Service operations (e.g., sdap).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Simple Queue Service operations (e.g., dev).',
        type=str)
    parser.add_argument(
        '-q',
        '--q_name_suffix',
        help="Suffix of the target queue name (defaults to '-data-queue' if not specified).",
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Simple Queue Service operations.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    product = args.product
    environment = args.environment

    if args.region is not None:
        region = args.region
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    if args.q_name_suffix is not None:
        q_name_suffix = args.q_name_suffix
    else:
        q_name_suffix = '-data-queue'

    rdqh = ref_data_queue_helper(product, environment, q_name_suffix, region,
                                 logger_level)

    parser_dict = {
        'FileName': 'campus_college_major.012018.csv',
        'FileYear': '2018',
        'FileMonth': '01',
        'TableName': 'campus_college_major'
    }

    print('\nApproximate number of messages in the queue initially={}'.format(
        rdqh.get_approx_msg_count()))

    send_msg_response = rdqh.send_file_attributes(parser_dict)
    print('\nsend_msg_response={}'.format(send_msg_response))

    file_attribute_dict = rdqh.receive_file_attributes()

    while file_attribute_dict != 'Null':
        print('\nfile_attribute_dict={}'.format(file_attribute_dict))
        print('FileName={}'.format(file_attribute_dict['FileName']))
        print('FileYear={}'.format(file_attribute_dict['FileYear']))
        print('FileMonth={}'.format(file_attribute_dict['FileMonth']))
        print('TableName={}'.format(file_attribute_dict['TableName']))
        file_attribute_dict = rdqh.receive_file_attributes()

    print("\nApproximate number of messages in the queue after 'receive'={}".
          format(rdqh.get_approx_msg_count()))

    print('\nCall to ref_data_queue_helper class was successful!')


if __name__ == '__main__':
    main()
