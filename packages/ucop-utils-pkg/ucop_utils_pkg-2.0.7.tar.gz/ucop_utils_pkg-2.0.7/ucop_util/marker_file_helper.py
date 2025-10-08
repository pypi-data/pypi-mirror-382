import boto3
import logging
import datetime
import argparse

from datetime import timedelta
from tzlocal import get_localzone

from ucop_util import date_handler


class marker_file_helper:
    """
    A generic helper class to handle all things related to marker files.
    """

    def __init__(self, region='us-west-2', logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        PGM_NAME = 'marker_file_helper.py'
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

        self.logger.info('logger_level={}'.format(self.logger_level))
        self.region = region.lower()
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.s3_resource = boto3.resource('s3', region_name=self.region)
        self.logger.debug('Debug in instantiation')
        self.logger.info(
            'Successfully instantiated the Marker File Helper Utility class.')

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

    # Local 'generator' function to list files (i.e., Keys) in an S3 bucket
    def list_marker_files(self, bucket, prefix='', suffix=''):
        """
        Obtain object keys of all marker files contained in a specified S3 bucket.

        Parameters
        ----------
        bucket: str
                Name of the S3 bucket where marker files are stored.
        prefix: str
                Optional argument to fetch only keys that start with this prefix.
        suffix: str
                Optional argument to fetch only keys that end with this suffix.
        Returns
        -------
        A list of marker file keys in the specified S3 bucket.
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in list_marker_files...')
        self.logger.debug('list_marker_files->bucket={}'.format(bucket))
        self.logger.debug('list_marker_files->prefix={}'.format(prefix))
        self.logger.debug('list_marker_files->suffix={}'.format(suffix))
        kwargs = {'Bucket': bucket, 'Prefix': prefix}
        response1 = self.s3_client.list_objects_v2(**kwargs)
        self.logger.debug('response1:{}'.format(response1))
        for content in response1.get('Contents', []):
            self.logger.debug('content:{}'.format(content))
            key = content['Key']
            if key.endswith(suffix):
                yield key

    def get_files_to_process(self, marker_bucket, marker_prefix,
                             marker_suffix):
        """
        As files go through different stages of ETL pipeline processing a
        marker file with a specific suffix is generated to signify the
        completion of the stage:

            Marker File Suffix             Process               Peer Marker
                                                                 File Suffix
            ------------------  -------------------------------  -------------
                .archived       -- ingest process ------------>   .recevied
                .received       -- record numbering process -->   .numbered
                .numbered       -- validation process -------->   .checked
                .checked        -- parquet file gen ---------->   .processed
             * failure at any stage results in creation of a peer marker file
               with a .failed suffix.
            ** Archived files with invalid names result in creation of a peer
               marker file with a .rejected suffix.

        This method iterates through the marker files whose suffix matches the
        specified marker_suffix and returns a list of files that don't have a
        corresponding peer marker file. For example, if '.archived' is passed as
        the marker_suffix, this method returns a list of marker files that
        don't have a matching '.received' file; hence, need to be processed.
        Also, note that this method detects if a file that was previously
        processed has been resubmitted by calling is_file_resubmitted method and
        adds the file to the list of files to be processed.

        Parameters
        ----------
        marker_bucket: str
                Name of the S3 bucket in which marker files are stored.
        marker_prefix: str
                The prefix (folder name) for the marker files.
        marker_suffix: str
                The suffix for the marker files.
        Returns
        -------
        A list of files that need to be processed. The list will be empty if no files
        are found.

        Exceptions
        ----------
        TypeError is raised when the string provided as marker_suffix is not recognized j
        """
        self.logger.debug('Now in get_files_to_process...')
        if marker_suffix == '.archived':
            peer_suffix = '.received'
        elif marker_suffix == '.received':
            peer_suffix = '.numbered'
        elif marker_suffix == '.numbered':
            peer_suffix = '.checked'
        elif marker_suffix == '.checked':
            peer_suffix = '.processed'
        else:
            raise TypeError(
                "The value provided as the marker file suffix '{}' to this method is invalid. Valid values are "
                '.archived, .received, .numbered, and .checked'
                .format(marker_suffix))

        peer_file_list = self.list_marker_files(
            bucket=marker_bucket, prefix=marker_prefix, suffix=peer_suffix)

        peer_file_names_list = []
        # Create a list of peer marker files
        for peer_file in peer_file_list:
            # Find the last slash to strip out folder name and return the peer file name
            peer_file_name = peer_file[peer_file.rindex('/') + 1:]
            peer_file_names_list.append(peer_file_name)

        to_be_processed_list = []

        # Create a list of marker files with the suffix that is passed as an
        # argument and identify those marker files that don't have a peer file.
        for s3_obj_name in self.list_marker_files(
                bucket=marker_bucket, prefix=marker_prefix,
                suffix=marker_suffix):
            # Find the last slash to strip out folder name and return marker file name
            marker_file_name = s3_obj_name[s3_obj_name.rindex('/') + 1:]
            # Find the last period and strip out the suffix
            stripped_marker_file_name = marker_file_name[
                0:marker_file_name.rindex(marker_suffix)]
            # If a marker file does not have a peer file then append it to the
            # list of files to be processed.
            if stripped_marker_file_name + peer_suffix not in peer_file_names_list or self.is_file_resubmitted(
                    marker_bucket, marker_prefix,
                    stripped_marker_file_name) is True:
                to_be_processed_list.append(stripped_marker_file_name)

        return to_be_processed_list

    def is_file_resubmitted(self, marker_bucket, marker_prefix,
                            stripped_marker_file_name):
        """
        Determines if a previously processed file is resubmitted by comparing
        the last modified date of its corresponding .archived marker file to the
        last modified date of its corresponding .received or .rejected peer file.
        If the .archived file is more recent than the .received or .rejected file
        then the file is considered a resubmit.

        Parameters
        ----------
        marker_bucket: str
                Name of the S3 bucket in which marker files are stored.
        marker_prefix: str
                The prefix (folder name) for the marker files.
        stripped_marker_file_name: str
                Marker file name without any processing suffix.
        Returns
        -------
        Boolean True if the file is a resubmit or False if the file is not a resubmit
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in is_file_resubmitted...')
        obj_list = self.s3_client.list_objects_v2(
            Bucket=marker_bucket,
            Prefix=marker_prefix + stripped_marker_file_name)
        tz = get_localzone()
        archived_modified_date = tz.localize(
            datetime.datetime(1970, 1, 1, 0, 0))
        # Initialize peer_modified_date with the oldest/earliest date in local timezone
        peer_modified_date = tz.localize(datetime.datetime(1970, 1, 1, 0, 0))

        for content in obj_list.get('Contents', []):
            if content['Key'].endswith('.archived'):
                self.logger.debug(" content['Key']={}".format(content['Key']))
                archived_modified_date = content['LastModified']
                self.logger.debug(
                    'archived_modified_date={}'.format(archived_modified_date))
            elif content['Key'].endswith(
                    '.received') or content['Key'].endswith('.rejected'):
                peer_modified_date = content['LastModified']
                self.logger.debug(
                    'peer_modified_date={}'.format(peer_modified_date))

        if archived_modified_date > peer_modified_date:
            self.logger.debug('File is a resubmit')
            return True
        else:
            self.logger.debug('File is not a resubmit')
            return False

    def handle_marker_file(self,
                           target_bucket,
                           marker_folder,
                           file_name,
                           suffix='.failed'):
        """
        Places the appropriate marker file in the marker folder in the incoming bucket.

        Parameters
        ----------
        target_bucket : str
                Name of the S3 bucket where marker files are stored.
        marker_folder : str
                Name of the folder where marker file is placed ending with a slash '/'.
        file_name: str
                Name of the source file from which marker file name is derived.
        suffix: str
                Optional desired marker file suffix. Must be one of: '.received', '.numbered',
                '.checked', '.processed', or '.rejected'.
                Defaults to '.failed' if no value is provided.
        Returns
        -------
        None
        Exceptions
        ----------
        Any processing errors.
        """
        self.logger.debug('Now in handle_marker_file...')
        marker_file = file_name + suffix

        obj_list = self.s3_client.list_objects_v2(
            Bucket=target_bucket, Prefix=marker_folder + file_name)

        if suffix == '.archived':
            # Clean up any existing post '.archived' marker files
            for content in obj_list.get('Contents', []):
                if content['Key'].endswith(
                        '.received') or content['Key'].endswith(
                            '.numbered') or content['Key'].endswith(
                                '.checked') or content['Key'].endswith(
                                    '.processed') or content['Key'].endswith(
                                        '.failed') or content['Key'].endswith(
                                            '.rejected'):
                    self.s3_client.delete_object(
                        Bucket=target_bucket, Key=content['Key'])
        elif suffix != '.failed':
            # Clean up any existing '.failed' marker files
            for content in obj_list.get('Contents', []):
                if content['Key'].endswith('.failed'):
                    self.s3_client.delete_object(
                        Bucket=target_bucket, Key=content['Key'])

        self.logger.debug(
            'Now creating the requested marker file in {} folder in {} S3 bucket'
            .format(marker_folder, target_bucket))
        self.s3_resource.Object(target_bucket,
                                marker_folder + marker_file).put(Body='')

    def set_process_date(self,
                         marker_folder_prefix,
                         process_date,
                         num_prior_days=1):
        """
        Determines date(s) for which files need to be processed, using the date
        subfolders under the marker file folder. If "current_date"
        is provided as the value for the process_date argument, it will convert the
        current system date to PST and look in the marker files folder for the
        dates matching the resulting date. If a date in yyyy-mm-dd is provided
        as the value for the process_date argument, it will look for files in the
        marker file folder for the date matching the provided date.
        If num_prior_days is not provided it will default to 1 prior day. Otherwise,
        it will return the N number of prior days based on the process_date value.

        Parameters
        ----------
        marker_folder_prefix : str
                Name of the marker file folder.
        process_date : str
                Either "current_date" or a date in yyyy-mm-dd format can be provided.
        num_prior_days: int
                Optional number of prior days to be considered. Defaults to one prior day,
                if no value is provided.
        Returns
        -------
        A list of one or more dates in yyyy-mm-dd format.
        Exceptions
        ----------
        None.
        """
        self.logger.debug('Now in set_process_date...')
        # If "current_date" is passed as an argument, use today's date as the process date,
        # otherwise use the specified date argument value
        if process_date == 'current_date':
            # Get current system datetime
            # AWS datetime is based on UTC and needs to be converted to US Pacific
            local_datetime_pst = date_handler().get_local_datetime_pst()
        else:
            local_timestamp = datetime.datetime.strptime(
                process_date, '%Y-%m-%d').timestamp()
            local_datetime_pst = datetime.datetime.fromtimestamp(
                local_timestamp)

        marker_prefix_list = []
        # We need to process any unprocessed file from today and N prior days.
        for i in range(num_prior_days + 1):
            target_datetime_pst = local_datetime_pst - timedelta(days=i)
            # Strip time portion from datetime to get date only
            target_date_pst = target_datetime_pst.strftime('%Y-%m-%d')
            marker_foler_full_prefix = marker_folder_prefix + target_date_pst + '/'
            marker_prefix_list.append(marker_foler_full_prefix)

        return marker_prefix_list


def main():
    """
    Main function to test the class
    """
    parser = argparse.ArgumentParser(
        description='A helper class to handle marker files that need to be created in various stages of processing.'
    )
    parser.add_argument(
        'target_bucket',
        help='The S3 bucket name in which to create the marker file.',
        type=str)
    parser.add_argument(
        'suffix',
        help='The desired suffix for the marker file (e.g., .archived).',
        type=str,
        choices=[
            '.archived', '.received', '.numbered', '.checked', '.processed',
            '.failed', '.rejected'
        ])
    parser.add_argument(
        'marker_folder',
        help="The root folder name ending with a '/' in which the marker files are stored (e.g., _MARKER_FILES/).",
        type=str)
    parser.add_argument(
        '-f',
        '--file_name',
        help='Optional argument signifying the name of the file for which a marker needs to be created '
             '(e.g., CSS3WKBK.Q416).',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='Optional argument signifying the AWS region in which to invoke the Marker File Helper class. '
             "By default 'us-west-2' is used.",
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help="Optional argument signifying the desired level of logging. By default 'INFO' is used.",
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    target_bucket = args.target_bucket
    suffix = args.suffix
    marker_folder = args.marker_folder
    file_name = args.file_name
    if args.region is not None:
        region = args.region
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    print(
        'About to instantiate Marker File Helper class with positional target_bucket, marker_folder, '
        'and suffix arguments set to: {}, {} and {}; and optional file_name, region and logger_level '
        'arguments set to: {}, {} and {}'
        .format(target_bucket, marker_folder, suffix, file_name, region,
                logger_level))

    print('\nCalling marker_file_helper class...')
    print('target_bucket={}'.format(target_bucket))
    print('marker_folder={}'.format(marker_folder))
    print('suffix={}'.format(suffix))
    print('file_name={}'.format(file_name))
    print('region={}'.format(region))
    print('logger_level={}'.format(logger_level))

    try:
        mfh = marker_file_helper(region, logger_level)

        print(
            '\nNow demonstrating how to use set_process_date method using current_date and 10 prior days...'
        )
        response = mfh.set_process_date(marker_folder, 'current_date', 10)
        print('marker_prefix_list={}'.format(response))

        print('\nNow demonstrating how to use get_files_to_process method...')
        for i in range(len(response)):
            print('response[{}]={}'.format(i, response[i]))
            files_to_process_list = mfh.get_files_to_process(target_bucket, response[i], suffix)
            print('List of files to process={}'.format(files_to_process_list))
        '''
        print(
            "\nNow demonstrating how to use set_process_date method using '2020-01-25' as the date and 3 prior days..."
        )
        response = mfh.set_process_date(marker_folder, '2020-01-25', 3)
        print("marker_prefix_list={}".format(response))
        '''

        if file_name is not None:
            print(
                '\nNow demonstrating how to create a .failed marker file using handle_marker_file method and the'
                "file_name argument in today's subfolder ..."
            )
            # AWS datetime is based on UTC and needs to be converted to US Pacific
            target_date_pst = date_handler().get_local_date_pst()
            target_folder = marker_folder + target_date_pst + '/'

            mfh.handle_marker_file(target_bucket, target_folder, file_name)
            print('Created file: {}.failed in S3 bucket: {} in subfolder: {}'.
                  format(file_name, target_bucket, target_folder))

    except TypeError as error:
        print('Call to marker_file_helper class failed with error: {}'.format(
            error))
        raise error

    print('Call to marker_file_helper class was successful!')


if __name__ == '__main__':
    main()
