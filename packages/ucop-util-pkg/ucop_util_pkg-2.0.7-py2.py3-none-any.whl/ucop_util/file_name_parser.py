import logging
import boto3
import argparse

from ucop_util.util_exception import NameLenghtError
from ucop_util.util_exception import NameError


class file_name_parser:
    """
    A utility class to parse campus enrollment file names.
    """

    def __init__(self,
                 product,
                 environment,
                 file_name,
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
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        PGM_NAME = 'file_name_parser.py'
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
        self.environment = environment.lower()
        self.region = region.lower()
        self.target_db = self.product + '_' + self.environment
        self.s3_client = boto3.client('s3', region_name=region)
        self.logger.info(
            'Successfully instantiated the File Name Parser Utility class.')

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

    def infer_enrollment_target_folder(self, file_name):
        """
        This function accepts a file name as its argument and infers the
        target S3 bucket and folder structure based on the file name,
        using the pattern shown below.

        File name patterns:
            File-name: CSS<rec-type><campus-alpha-code>.Q<term-code><file-year>
                where <rec-type> = 3WK, EOT, or RES
                      <campus-alpha-code> = BK, DV, IR, LA, MC, RV, SB, SC, SD, SF
                      <term-code> = 1 (summer), 2 (fall), 3 (winter), or 4 (spring)
                      <file-year> = 2-digit year (e.g., 17)
            maps to S3 -> incoming bucket/
                          student_reg_<bucket-suffix>/
                          year_registered=<file-year-ccyy>/
                          term_registered_code=<file-term>/
                          record_type=<rec-type>/
                          campus_registered_code=<campus-code>
                where <bucket-suffix> = 3wk, 3wk_summer, eot, eot_summer, or res
                      <file-year-ccyy> = 4-digit year (e.g., 2017)
                      <file-term> = 1 (summer), 2 (fall), 3 (winter), or 4 (spring)
                      <rec-type> = 3WK, EOT, or RES
                      <campus-code> = 01, 02, 03, 04, 05, 06, 07, 08, 09, 10
        File name examples: CSS3WKBK.Q120, CSSEOTDV.Q218, CSSRESSF.Q315
        Parameters
        ----------
        file_name: str
                   Student Enrollment campus file name to be parsed.
        Returns
        -------
        {'FileYear': <value>, 'FileYearCCYY': <value>,
         'FileTerm': <value>, 'DQLocID': <value>,
         'DQLocation': <value>, 'CampusCode': <value>,
         'RecordType': <value>, 'BucketSuffix': <value>
         'RefDataFileYear': <value>, 'RefDataFileMonth': <value>
        }
                   A dictionary of key/value pairs that could be used
                   to place the file in the correct folder in the S3 target
                   bucket.
        Exceptions
        ----------
        NameLenghtError:
                   raised when any file name length violation occurs.
        NameError: raised when any file name does not meet naming standards.
    """
        self.logger.debug('Now in infer_enrollment_target_folder...')
        file_year = ''
        file_year_ccyy = ''
        file_term = ''
        record_type = ''
        campus_code = ''
        bucket_suffix = ''
        dq_loc_id = ''
        dq_location = ''
        ref_data_file_year = 0
        ref_data_file_month = ''

        if len(file_name) != 13:
            raise NameLenghtError(
                'File name: {} has an invalid length: {} (expected lenght is 13-characters).'
                .format(file_name, len(file_name)), file_name, len(file_name))
        elif file_name.count('.Q') == 0:
            raise NameError("File name does not contain '.Q'", file_name)
        elif file_name.index('.Q') != 8:
            raise NameError("The '.Q' in file name is not in position 9.",
                            file_name)

        file_term = file_name[file_name.index('.Q') + 2]

        file_year = file_name[11:13]

        if file_year.isdigit():
            if file_year < '90':
                file_year_ccyy = '20' + file_name[11:13]
            elif file_year >= '90':
                file_year_ccyy = '19' + file_name[11:13]
        else:
            raise NameError(
                'Invalid year: {} in file name (expected numeric 2-digit year).'
                .format(file_year), file_name)

        if file_term not in ('1', '2', '3', '4'):
            raise NameError(
                'Invalid term: {} in file name (expected terms are 1, 2, 3, and 4).'
                .format(file_term), file_name)

        if file_name[6:8] == 'BK':
            dq_loc_id = '14'
            dq_location = 'BKCMP'
            campus_code = '01'
        elif file_name[6:8] == 'DV':
            dq_loc_id = '7'
            dq_location = 'DVCMP'
            campus_code = '03'
        elif file_name[6:8] == 'IR':
            dq_loc_id = '9'
            dq_location = 'IRCMP'
            campus_code = '09'
        elif file_name[6:8] == 'LA':
            dq_loc_id = '3'
            dq_location = 'LACMP'
            campus_code = '04'
        elif file_name[6:8] == 'MC':
            dq_loc_id = '5'
            dq_location = 'MECMP'
            campus_code = '10'
        elif file_name[6:8] == 'RV':
            dq_loc_id = '6'
            dq_location = 'RVCMP'
            campus_code = '05'
        elif file_name[6:8] == 'SB':
            dq_loc_id = '11'
            dq_location = 'SBCMP'
            campus_code = '08'
        elif file_name[6:8] == 'SC':
            dq_loc_id = '12'
            dq_location = 'SCCMP'
            campus_code = '07'
        elif file_name[6:8] == 'SD':
            dq_loc_id = '17'
            dq_location = 'SDCMP'
            campus_code = '06'
        elif file_name[6:8] == 'SF':
            dq_loc_id = '19'
            dq_location = 'SFCMP'
            campus_code = '02'
        else:
            raise NameError(
                "Invalid campus code: {} in file name (expected campus codes are 'BK' through 'SF')."
                .format(file_name[6:8]), file_name)

        if file_name.startswith('CSS3WK'):
            record_type = '3WK'
            if file_term == '1':
                bucket_suffix = '3wk_summer'
            elif file_term == '2' or file_term == '3' or file_term == '4':
                bucket_suffix = '3wk'
        elif file_name.startswith('CSSEOT'):
            record_type = 'EOT'
            if file_term == '1':
                bucket_suffix = 'eot_summer'
            elif file_term == '2' or file_term == '3' or file_term == '4':
                bucket_suffix = 'eot'
        elif file_name.startswith('CSSRES'):
            record_type = 'RES'
            bucket_suffix = 'res'
            file_term = '2'
            record_type = '3WK'
        else:
            raise NameError(
                'Invalid prefix in file name (expected prefixes are: CSS3WK, CSSEOT, and CSSRES).',
                file_name)

        if file_term == '1' and record_type == '3WK':
            ref_data_file_year = int(file_year_ccyy)
            ref_data_file_month = '09'
        elif file_term == '1' and record_type == 'EOT':
            ref_data_file_year = int(file_year_ccyy)
            ref_data_file_month = '11'
        elif file_term == '2' and record_type == '3WK':
            ref_data_file_year = int(file_year_ccyy)
            ref_data_file_month = '11'
        elif file_term == '2' and record_type == 'EOT':
            ref_data_file_year = int(file_year_ccyy) + 1
            ref_data_file_month = '01'
        elif file_term == '3' and record_type == '3WK':
            ref_data_file_year = int(file_year_ccyy) + 1
            ref_data_file_month = '02'
        elif file_term == '3' and record_type == 'EOT':
            ref_data_file_year = int(file_year_ccyy) + 1
            ref_data_file_month = '05'
        elif file_term == '4' and record_type == '3WK':
            ref_data_file_year = int(file_year_ccyy) + 1
            ref_data_file_month = '05'
        elif file_term == '4' and record_type == 'EOT':
            ref_data_file_year = int(file_year_ccyy) + 1
            ref_data_file_month = '06'

        return {
            'FileYear': file_year,
            'FileYearCCYY': file_year_ccyy,
            'FileTerm': file_term,
            'DQLocID': dq_loc_id,
            'DQLocation': dq_location,
            'CampusCode': campus_code,
            'RecordType': record_type,
            'BucketSuffix': bucket_suffix,
            'RefDataFileYear': ref_data_file_year,
            'RefDataFileMonth': ref_data_file_month
        }

    def reject_source_file(self, params):
        """
        Handles rejection of invalid files from source folder to target folder.

        Parameters
        ----------
        params: Dictionary
                A dictionary of key/value pairs, such as target bucket name and prefix
                that are required to persist the rejected file.
        Returns
        -------
        None
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in reject_source_file function')

        # Copy the invalid source file to the reject folder and delete it from landing zone
        self.logger.debug('Reject Bucket={}, Key={}'.format(
            params['reject_data_bucket'],
            params['reject_file_foler'] + params['file_name']))
        self.s3_client.copy_object(
            Bucket=params['reject_data_bucket'],
            Key=params['reject_file_foler'] + params['file_name'],
            CopySource={
                'Bucket': params['input_data_bucket'],
                'Key': params['input_file_folder'] + params['file_name']
            })
        self.logger.info(
            'Rejected invalid incoming file: {} in S3 bucket: {}, folder: {}'.
            format(params['file_name'], params['reject_data_bucket'],
                   params['reject_file_foler']))


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description='A utility class for parsing enrollment file names.')
    parser.add_argument(
        'product',
        help='product for which to invoke the File Name Parser class (e.g., sdap).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the File Name Parser class (e.g., dev).',
        type=str)
    parser.add_argument(
        'file_name',
        help='Name of the file that needs to be parsed.',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the File Name Parser class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    product = args.product
    environment = args.environment
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
        "About to instantiate File Name Parser class with mandatory positional arguments set to '{}', '{}', and '{}' "
        "and optional region and logger_level arguments set to: '{}' and '{}'"
        .format(product, environment, file_name, region, logger_level))

    fnp_obj = file_name_parser(product, environment, file_name, region=region,
                               logger_level=logger_level)

    # Example of how to call infer_enrollment_target_folder method.
    parser_dict = fnp_obj.infer_enrollment_target_folder(file_name)

    print('parser_dict={}'.format(parser_dict))
    print('\nFileYear={}, \nFileYearCCYY={}, '
          '\nFileTerm={}, \nDQLocID={}, '
          '\nDQLocation={}, \nCampusCode={}, '
          '\nRecordType={}, \nBucketSuffix={}, '
          '\nRefDataFileYear={}, \nRefDataFileMonth={}'.format(
           parser_dict['FileYear'],
           parser_dict['FileYearCCYY'],
           parser_dict['FileTerm'], parser_dict['DQLocID'],
           parser_dict['DQLocation'], parser_dict['CampusCode'],
           parser_dict['RecordType'], parser_dict['BucketSuffix'],
           parser_dict['RefDataFileYear'], parser_dict['RefDataFileMonth']
           ))


if __name__ == '__main__':
    main()
