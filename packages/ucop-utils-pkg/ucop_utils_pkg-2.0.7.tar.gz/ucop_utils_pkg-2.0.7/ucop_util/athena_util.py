import sys
import boto3
import logging
import time
import argparse

from botocore.exceptions import ClientError
from botocore.config import Config

from ucop_util.stack_info import stack_info


class athena_util:
    """
    A utility class to perform Athena operations such as MSCK REPAIR TABLE.
    """

    def __init__(self,
                 product,
                 environment,
                 database_name=None,
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
        database_name (optional): str
                The name of database in which to operate.
                If provided, overrides the default product_environment database name.
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        pgm_name = 'athena_util.py'
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

        self.product = product.lower()
        self.environment = environment.lower()
        self.region = region.lower()
        if database_name is None:
            self.target_db = self.product + '_' + self.environment
        else:
            self.target_db = database_name
        self.logger.debug('target_db={}'.format(self.target_db))
        config = Config(
            region_name=self.region,
            retries=dict(
                total_max_attempts=25
            )
        )
        self.client = boto3.client('athena', config=config)
        self.s3_resource = boto3.resource('s3', config=config)
        self.glue_client = boto3.client('glue', config=config)
        self.logger.info('Successfully instantiated the Athena Utility class.')

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

    def does_table_exist(self, target_table_name):
        """
        Checks to see if the target Athena table exists in Glue metastore.
        Note that in the current version of Athena MSCK REPAIR TABLE command
        succeeds even when it is executed on a table that does not exist in
        metastore. Hence, the need to precheck the table's existence before
        executing repair.

        Parameters
        ----------
        target_table_name : str
                Name of the Athena table whose existence in metastore needs to be checked.
        Returns
        -------
        Boolean True if table exists in metastore or boolean False if table does not exist in metastore
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        try:
            response = self.glue_client.get_table(
                DatabaseName=self.target_db, Name=target_table_name.lower())
            self.logger.debug(
                "response['Table']['DatabaseName']={}, response['Table']['Name']={}"
                .format(response['Table']['DatabaseName'],
                        response['Table']['Name']))
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityNotFoundException':
                return False

        return True

    def __get_output_bucket(self):
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))
        output_bucket = stack_info(logger_level=self.logger_level).get_bucket_name_by_label(
            self.product, self.environment, 'output')
        self.logger.debug('output_bucket={}'.format(output_bucket))
        # TODO: remove hardcoding of folder name
        output_prefix = '_temporary/sql'
        output_location = 's3://' + output_bucket + '/' + output_prefix

        return output_location

    def __execute_query(self, target_table_name, sql_string):
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))
        output_location = self.__get_output_bucket()

        if self.does_table_exist(target_table_name) is False:
            msg = 'Table does not exist in metastore. You must first create the table: ' + target_table_name + \
                  ' in database:' + self.target_db
            raise Exception(msg)

        context = {'Database': self.target_db}
        self.logger.debug('context={}'.format(context))
        config = {'OutputLocation': output_location}
        self.logger.debug('config={}'.format(config))

        start_query_response = self.client.start_query_execution(
            QueryString=sql_string,
            QueryExecutionContext=context,
            ResultConfiguration=config,
            WorkGroup='rdms-etl'
        )

        query_exec_id = start_query_response['QueryExecutionId']

        # Waiter to allow for query execution state change from RUNNING state
        while True:
            time.sleep(1)
            get_query_response = self.client.get_query_execution(
                QueryExecutionId=query_exec_id)
            if get_query_response['QueryExecution']['Status']['State'] != 'RUNNING':
                break
        self.logger.debug('get_query_response={}'.format(get_query_response))

        if get_query_response['QueryExecution']['Status']['State'] == 'FAILED':
            msg = 'Query execution failed on table: {} in database: {}. QueryExecution: {}.\nReason for failure: {}'.\
                format(
                    target_table_name, self.target_db, query_exec_id,
                    get_query_response['QueryExecution']['Status']['StateChangeReason'])
            raise Exception(msg)

    def get_table_names(self, expression):
        """
        Returns a list of Athena table names for the product, environment and
        database that is specified in the class constructor, using list_table_metadata
        call in boto3 Athena API. Note that the IAM role that is used to invoke this
        method must have Lake Formation select privileges on all tables in the database.

        Parameters
        ----------
        expression : str
                 A regex filter that pattern-matches table names. If no expression is
                 supplied, table names for all tables are listed.
        Returns
        -------
        table_names_list: list
                A list of Athena table names.
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        starting_token = None
        paginator = self.client.get_paginator('list_table_metadata')
        if expression is not None:
            response_iterator = paginator.paginate(
                CatalogName='AwsDataCatalog',
                DatabaseName=self.target_db,
                Expression=expression,
                PaginationConfig={
                    'StartingToken': starting_token
                })
        else:
            response_iterator = paginator.paginate(
                CatalogName='AwsDataCatalog',
                DatabaseName=self.target_db,
                PaginationConfig={
                    'StartingToken': starting_token
                })

        table_names_list = []

        for page in response_iterator:
            for i in range(len(page['TableMetadataList'])):
                self.logger.debug(
                    "page['TableMetadataList'][i]['Name']={}".format(
                        page['TableMetadataList'][i]['Name']))
                table_names_list.append(page['TableMetadataList'][i]['Name'])

        return table_names_list

    def add_partition(self, target_table_name, partition_key):
        """
        Executes "alter table add partition" to make the newly added
        partition in Athena table available for querying. Note that this method
        is an alternative to the repair_table method and should be used when the
        calling module is not using Spark SQL; otherwise, use repair_table method instead.

        Parameters
        ----------
        target_table_name : str
                Name of the Athena target table to which the partition needs to be added.
        partition_key : str
                A string comprised of comma separated partition-key=partition-value
                constructs that comprise the Athena table partitioning scheme.
                Example: year_registered='2014',term_registered_code='3',record_type='3WK',campus_registered_code='08'
        Returns
        -------
        None
        Exceptions
        ----------
        Any query execution failures or when the target table does not exist.
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if target_table_name.lower().endswith('view'):
            return

        sql_string = 'ALTER TABLE ' + target_table_name + ' ADD IF NOT EXISTS PARTITION (' + partition_key + ')'
        self.logger.debug('sql_string={}'.format(sql_string))

        self.__execute_query(target_table_name, sql_string)

    def repair_table(self, target_table_name):
        """
        Executes the Hive MSCK repair table utility to make the newly added
        partition in Athena table available for querying. Note that this method
        should only be called when the table uses Hive partitioning
        (i.e., partition column name is followed by an equal symbol); otherwise,
        the table repair fails with a "Tables not in metastore:" error that gets
        captured in the query execution output. For tables that do not follow Hive
        partitioning, use add_partition method instead.

        Parameters
        ----------
        target_table_name : str
                Name of the Athena table to be repaired.
        Returns
        -------
        None
        Exceptions
        ----------
        Any query execution failures or when the target table does not exist.
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if target_table_name.lower().endswith('view'):
            return

        sql_string = 'MSCK REPAIR TABLE ' + target_table_name
        self.logger.debug('sql_string={}'.format(sql_string))

        self.__execute_query(target_table_name, sql_string)


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description='A utility class to perform operations on Athena tables such as adding partitions.')
    parser.add_argument(
        'product',
        help='product for which to invoke the Athena utility class (e.g., sdap).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Athena utility class (e.g., dev).',
        type=str)
    parser.add_argument(
        '-d',
        '--database',
        help='database name in which to invoke the Athena utility class '
             'If not specified, default database name will be used: <product>_<environment>.',
        type=str)
    parser.add_argument(
        '-e',
        '--expression',
        help='A regex filter that pattern-matches table names. If no expression is supplied, table names for all '
             'tables are listed.'
    )
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Athena utility class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    product = args.product
    environment = args.environment
    if args.database is not None:
        database_name = args.database
    else:
        database_name = None
    expression = args.expression
    if args.region is not None:
        region = args.region
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    print(
        'About to instantiate Athena utility class with mandatory positional arguments set to: '
        "product='{}' and environment='{}'.\nThe following optional arguments are set: "
        "database_name='{}', expression='{}', region='{}' and logger_level='{}'."
        .format(product, environment, database_name, expression, region, logger_level))

    if database_name is None:
        au_obj = athena_util(product, environment, region=region, logger_level=logger_level)
    else:
        au_obj = athena_util(product, environment, database_name=database_name, region=region,
                             logger_level=logger_level)

    table_names_list = au_obj.get_table_names(expression)

    if len(table_names_list) == 0:
        sys.exit('Aborting (table_names_list is empty) - When calling get_table_names() method, '
                 'no tables qualified for the specified expression.')

    print(table_names_list)

    # Example of how to call repair_table method.
    for table_name in table_names_list:
        au_obj.repair_table(table_name)
        print("Executed repair_table method on table='{}' successfully!".format(table_name))

    # For testing the add_partition method in SDAP project.
    '''
    for table_name in table_names_list:
        partition_dict = {
            'FileYear': '12',
            'FileYearCCYY': '2014',
            'FileTerm': '3',
            'DQLocID': '14',
            'DQLocation': 'SBCMP',
            'CampusCode': '08',
            'RecordType': '3WK',
            'BucketSuffix': '3wk'
        }
        # Example of how to add a partition to a table.
        partition_key = 'year_registered=\'' + partition_dict['FileYearCCYY'] + \
                        '\',term_registered_code=\'' + partition_dict['FileTerm'] + \
                        '\',record_type=\'' + partition_dict['RecordType'] + \
                        '\',campus_registered_code=\'' + partition_dict['CampusCode'] + '\''
        au_obj.add_partition(table_name, partition_key)
    '''
    print('\nExecuted all methods successfully!')


if __name__ == '__main__':
    main()
