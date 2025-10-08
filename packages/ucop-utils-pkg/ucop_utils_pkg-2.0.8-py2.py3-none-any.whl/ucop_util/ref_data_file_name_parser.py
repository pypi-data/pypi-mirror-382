import logging
import argparse

from ucop_util.util_exception import NameError


class ref_data_file_name_parser:
    """
    A utility class to parse reference data file names.
    """

    def __init__(self, logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """

        PGM_NAME = 'ref_data_file_name_parser.py'
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

        self.logger.info("Logging level is set to '{}'".format(
            self.logger_level))

        self.logger.info(
            'Successfully instantiated the reference data file name parser utility class.'
        )

    @property
    def logger_level(self):
        return self.__logger_level

    @logger_level.setter
    def logger_level(self, logger_level):
        self.__logger_level = logger_level

    def infer_ref_data_target_folder(self, file_name):
        """
        This function accepts a Reference data file name as its argument and infers the
        target S3 bucket and folder structure based on the file name,
        using the pattern shown below.

        File name patterns:
            File-name: <table_name>.<MM><YYYY>.csv
                where <table_name> example: campus_college_major, academic_degree
                      <MM> = 2-digit month of the reference data file - Part of the partition key
                      <YYYY> = 4-digit year of the reference data file - Part of the partition key
            maps to S3 -> incoming bucket/
                          <file_name>/
                          file_year=<YYYY>/
                          file_month=<MM>/
                      <file year> = 4-digit year (e.g., 2017)
                      <file month> = 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12
        Full file name examples: campus_college_major.012018.csv
        Description: Reference data file for Campus College Major (ccm) belonging to Jan 2018

        Parameters
        ----------
        file_name: str
                   Reference data file name to be parsed.
        Returns
        -------
        {'FileYear': <value>, 'FileYear-YYYY': <value>,
         'FileMonth': <value>, 'FileMonth-MM': <value>,
        }
                   A dictionary of key/value pairs that could be used
                   to place the file in the correct folder in the S3 target
                   bucket.
        Exceptions
        ----------
        NameError: raised when any file name does not meet naming standards.
        """
        self.logger.debug('Now in infer_ref_data_target_folder...')
        self.logger.debug('file_name={}'.format(file_name))

        if len(file_name.split('.')) != 3:
            raise NameError(
                'Invalid file name. Valid file name format: <table_name>.MMYYYY.csv',
                file_name)

        table_name, file_month_year, file_extension = file_name.split('.')
        self.logger.debug(
            'table_name={}, file_month_year={}, file_extension={}'.format(
                table_name, file_month_year, file_extension))

        month_list = [
            '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
            '12'
        ]
        file_month = file_month_year[0:2]
        self.logger.debug('file_month={}'.format(file_month))

        file_year = file_month_year[2:6]
        self.logger.debug('file_year={}'.format(file_year))

        if len(file_month) != 2 or file_month not in month_list:
            raise NameError(
                "Invalid month: '{}' in file -- expect a 2-digit month between 01-12 in the following format: <table_name>.MMYYYY.csv"
                .format(file_month), file_name)
        elif len(file_year) != 4 or file_year.isdigit() is False:
            raise NameError(
                "Invalid file year: '{}' -- expect a 4-digit year in the following format: <table_name>.MMYYYY.csv".
                format(file_year), file_name)
        elif file_extension != 'csv':
            raise NameError(
                "Invalid file extension: {} in file (expected 'csv').".format(
                    file_extension), file_name)

        return {
            'FileYear': file_year,
            'FileMonth': file_month,
            'TableName': table_name,
            'FileName': file_name
        }


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description='A utility class for parsing reference data file names.')
    parser.add_argument(
        'file_name',
        help='Name of the file that needs to be parsed.',
        type=str)
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    file_name = args.file_name
    if args.logger_level is not None:
        logger_level = args.logger_level
    else:
        logger_level = 'DEBUG'

    rdfnp = ref_data_file_name_parser(logger_level=logger_level)
    parser_dict = rdfnp.infer_ref_data_target_folder(file_name)
    print('parser_dict={}'.format(parser_dict))
    print('\nFileYear={}, \nFileMonth={}, \nTableName={}, \nFileName={}' \
           .format(parser_dict['FileYear'], parser_dict['FileMonth'], parser_dict['TableName'], parser_dict['FileName']))


if __name__ == '__main__':
    main()
