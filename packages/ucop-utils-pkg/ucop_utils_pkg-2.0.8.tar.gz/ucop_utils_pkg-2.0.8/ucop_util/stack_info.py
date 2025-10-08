import sys
import boto3
import logging
import argparse

from botocore.config import Config
from ucop_util.util_exception import ValueNotFoundError


class stack_info:
    """
    A utility class that provides methods for obtaining useful information
    about a CloudFormation stack that is used for UCOP data lake projects.
    """
    SSO_ROLE_PREFIX = 'AWSReservedSSO'

    def __init__(self, region='us-west-2', logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        region: str
                Optional - If provided, overrides the default 'us-west-2' region.
        logger_level: str
                Optional - If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        pgm_name = 'stack_info.py'
        msg_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
        datetime_format = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(format=msg_format, datefmt=datetime_format)
        self.logger = logging.getLogger(pgm_name)
        self.logger_level = logger_level.upper()
        if self.logger_level == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif self.logger_level == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        elif self.logger_level == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif self.logger_level == 'CRITICAL':
            self.logger.setLevel(logging.CRITICAL)

        self.region = region.lower()
        config = Config(
            region_name=self.region,
            retries=dict(
                total_max_attempts=25
            )
        )

        self.s3_client = boto3.client('s3', config=config)
        self.iam_client = boto3.client('iam', config=config)

        self.logger.debug(
            'Successfully instantiated the Stack Info Utility class.')

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

    def get_bucket_name_by_label(self, product, environment, label):
        """
        For a given combination of product and environment, returns the
        S3 bucket name based on a label that is provided as an argument.

        Parameters
        ----------
        product: str
                The name of the desired product/application (e.g., rdms)
        environment: str
                The name of the desired environment (e.g., qa, dev, or prod)
        label: str
                The label for the bucket (e.g., incoming, processing, etc.)
        Returns
        -------
        bucket_name: str
                The name of the S3 bucket.
        Exceptions
        ----------
        ValueNotFoundError if the bucket is not found in the CloudFormation exports.
        Exception if more than one bucket label matches the label provided as an argument.
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        bucket_name = None
        bucket_name_prefix = str(product + environment).lower()
        bucket_match_count = 0

        response = self.s3_client.list_buckets()
        # self.logger.debug("response={}".format(response))

        for bucket in response['Buckets']:
            if bucket['Name'].lower().replace('-', '').startswith(bucket_name_prefix):
                if bucket['Name'].lower().find(label) > 0:
                    bucket_name = bucket['Name']
                    bucket_match_count += 1

        if bucket_name is None:
            raise ValueNotFoundError('No bucket found matching the label.',
                                     label)
        elif bucket_match_count > 1:
            raise Exception(
                "More than one bucket was found matching label='{}'.".format(
                    label))

        self.logger.debug("bucket_name={}".format(bucket_name))
        return bucket_name

    def get_bucket_arn_by_label(self, product, environment, label):
        """
        For a given combination of product and environment, returns the
        S3 bucket ARN based on a label that is provided as an argument.

        Parameters
        ----------
        product: str
                The name of the desired product/application (e.g., rdms)
        environment: str
                The name of the desired environment (e.g., qa, dev, or prod)
        label: str
                The label for the bucket (e.g., incoming, processing, etc.)
        Returns
        -------
        bucket_arn_value: str
                The ARN for the bucket whose label is passed as an argument.
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        bucket_name = self.get_bucket_name_by_label(product, environment, label)
        bucket_arn_value = 'arn:aws:s3:::' + bucket_name
        self.logger.debug("bucket_arn_value={}".format(bucket_arn_value))
        return bucket_arn_value

    def get_role_arn_by_label(self, product, environment, label, sso_roles_list):
        """
        For a given combination of product and environment, returns the
        role ARN based on a role label that is provided as an argument.

        Parameters
        ----------
        product: str
                The name of the desired product/application (e.g., rdms)
        environment: str
                The name of the desired environment (e.g., qa, dev, or prod)
        label: str
                The label for the role (e.g., Level1DataAccess, etc.)
        sso_roles_list: list
                A list of organization-level SSO roles in dictionary format
        Returns
        -------
        role_arn: str
                The ARN for the role.
        Exceptions
        ----------
        ValueNotFoundError if the role label is not found in the CloudFormation exports.
        Exception if more than one role matches the label provided as an argument.
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        role_arn = None
        role_name_prefix = str(product + environment).lower()
        role_match_count = 0
        starting_token = None
        paginator = self.iam_client.get_paginator('list_roles')
        response_iterator = paginator.paginate(
            PaginationConfig={
                'StartingToken': starting_token
            })

        for page in response_iterator:
            for roles in page['Roles']:
                if roles['RoleName'].lower().replace('-', '') == (role_name_prefix + label.lower() + 'role'):
                    self.logger.debug(
                        "roles['RoleName']={}".format(roles['RoleName']))
                    self.logger.debug(
                        "roles['Arn']={}".format(roles['Arn']))
                    role_arn = roles['Arn']
                    role_match_count += 1
                    self.logger.debug(
                        'role_match_count={}'.format(role_match_count))
                else:
                    # Use list comprehension to see if sso_roles_list contains the role label (i.e., len() > 0).
                    # If a match is found, store the role's corresponding dictionary entry (e.g.,
                    # {'Environment': 'dev', 'RoleLabel': 'RDMS_Developer', 'RoleName': 'AWSReservedSSO_RDMS_Developer_667462fe58341bf6'})
                    # in matching_role_dict.
                    if len([element for element in sso_roles_list if element['RoleLabel'].lower()
                            == label.lower()]) > 0:
                        matching_role_dict = \
                            [element for element in sso_roles_list if element['RoleLabel'].lower() == label.lower()][0]
                        if roles['RoleName'].lower() == \
                                matching_role_dict['RoleName'].lower():
                            self.logger.debug(
                                "roles['RoleName']={}".format(roles['RoleName']))
                            self.logger.debug(
                                "roles['Arn']={}".format(roles['Arn']))
                            role_arn = roles['Arn']
                            role_match_count += 1
                            self.logger.debug(
                                'role_match_count={}'.format(role_match_count))
                        else:
                            continue
                    else:
                        continue

        if role_arn is None:
            raise ValueNotFoundError('No role was found matching the label.', label)
        elif role_match_count > 1:
            raise Exception(
                "More than one role was found matching label='{}'.".format(
                    label))

        return role_arn


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description='A utility class to obtain information from CloudFormation stacks.')
    parser.add_argument(
        'product',
        help='product for which to invoke the Stack Info utility class (e.g., rdms).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Stack Info utility class (e.g., dev).',
        type=str)
    parser.add_argument(
        '-bl',
        '--bucket-label',
        help='Bucket label for which to return the bucket name (e.g., app or archive).'
    )
    parser.add_argument(
        '-rl',
        '--role-label',
        help='Role label for which to return the role ARN (e.g., Level1 or Level3Programmer).'
    )
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Stack Info utility class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    product = args.product
    environment = args.environment.capitalize()
    if args.region is not None:
        region = args.region
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    print(
        "About to instantiate Stack Info utility class with mandatory positional arguments set to '{}' and '{}' "
        "and optional region and logger_level arguments set to '{}' and '{}'"
        .format(product, environment, region, logger_level))

    stk_info = stack_info(region=region, logger_level=logger_level)

    # Examples of how to call get_bucket_name_by_label and get_bucket_arn_by_label
    # methods using the bucket label provided as an optional command line argument.
    bucket_label = args.bucket_label
    if bucket_label is not None:
        print("\nNow printing the bucket name using label '{}'".format(
            bucket_label))
        bucket_name = stk_info.get_bucket_name_by_label(product, environment, bucket_label)
        bucket_arn = stk_info.get_bucket_arn_by_label(product, environment, bucket_label)
        print('\tBucket Name={}'.format(bucket_name))
        print('\tBucket ARN={}'.format(bucket_arn))

    # Example of how to call get_role_arn_by_label method using a role label
    # provided as an optional command line argument.
    role_label = args.role_label
    if role_label is not None:
        print(
            "\nNow printing the role ARN using label '{}'".format(role_label))
        print('\tRole ARN={}'.format(
            stk_info.get_role_arn_by_label(product, environment, role_label,
                                           [{'Environment': 'dev', 'RoleLabel': 'RDMS_Admin',
                                             'RoleName': 'AWSReservedSSO_RDMS_Admin_acf720f1187dae4c'},
                                            {'Environment': 'dev', 'RoleLabel': 'RDMS_Analyst',
                                             'RoleName': 'AWSReservedSSO_RDMS_Analyst_f6042f4e5037ee29'},
                                            {'Environment': 'dev', 'RoleLabel': 'RDMS_Developer',
                                             'RoleName': 'AWSReservedSSO_RDMS_Developer_667462fe58341bf6'}]
                                           )))

    # The block of code below is to cause an AWS throttle error.
    '''
    if bucket_label is None:
        print(
            "\nERROR: Unable to cause an AWS throttle condition for testing. "
            "Provide a bucket label using -bl/--bucket-label command line arguments."
        )
        exit(1)
    else:
        for i in range(1, 101):
            print("Iteration={}".format(i))
            stk_info.get_bucket_name_by_label(product, environment,
                                              bucket_label)
    '''


if __name__ == '__main__':
    main()
