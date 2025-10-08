import sys
import boto3
import logging
import json
import argparse

from botocore.exceptions import ClientError
from botocore.config import Config

from ucop_util import stack_info
from ucop_util.util_exception import ValueNotFoundError


class lf_perms_helper:
    """
    A utility class that grants or revokes Lake Formation permissions for
    one or more tables based on an application and a permissions config JSON file.
    This class is used during deployments to grant permissions to newly created
    tables. Similarly, post deployment, the class could be used to grant table
    permissions after a table is dropped and recreated.
    To instantiate the class, call its constructor method and pass the required
    parameters (see example below). The class can be used to either grant or
    revoke permissions using the mode parameter.
    Example: helper = lf_perms_helper('grant', product, environment, 'app',
                           'config/config.json', 'config/config_perm.json')
    """

    def __init__(self,
                 mode,
                 product,
                 environment,
                 config_bucket_label,
                 config_full_path,
                 perm_config_full_path,
                 sso_roles_config_full_path='config/sso_roles_config.json',
                 region='us-west-2',
                 logger_level='INFO'):
        """
        Class constructor.
        Parameters
        ----------
        mode: str
                The mode in which the class should operate. Permissible values
                are: grant or revoke.
        product: str
                The name of product (e.g., rdms) for which permissions should be
                granted.
        environment: str
                The environment (e.g., dev, qa, or prod) for which permissions
                should be granted.
        config_bucket_label: str
                The label for the bucket in which the config files are located.
        config_full_path: str
                The full path/key to the application config file.
        perm_config_full_path: str
                The full path/key to the permissions config files.
        sso_roles_config_full_path (optional): str
                The full path/key to the config JSON file that contains a list of SSO roles that are managed at
                the organization level. If provided, overwrites the default: config/sso_roles_config.json.
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        if mode.lower() not in ('grant', 'revoke'):
            raise ValueNotFoundError(
                "Permitted values for mode are: 'grant' and 'revoke'. Unknown mode: ",
                mode)
        else:
            self.mode = mode

        pgm_name = 'lf_perms_helper.py'
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
        self.logger.debug('product={}'.format(self.product))
        self.environment = environment.capitalize()
        self.logger.debug('environment={}'.format(self.environment))
        self.config_bucket_label = config_bucket_label
        self.logger.debug('config_bucket_label={}'.format(self.config_bucket_label))
        self.config_full_path = config_full_path
        self.logger.debug('config_full_path={}'.format(self.config_full_path))
        self.perm_config_full_path = perm_config_full_path
        self.logger.debug('perm_config_full_path={}'.format(self.perm_config_full_path))
        self.sso_roles_config_full_path = sso_roles_config_full_path
        self.logger.debug('sso_roles_config_full_path={}'.format(self.sso_roles_config_full_path))
        self.region = region.lower()
        config = Config(
            region_name=self.region,
            retries=dict(
                total_max_attempts=25
            )
        )

        self.lf_client = boto3.client('lakeformation', config=config)
        self.s3_resource = boto3.resource('s3', config=config)
        self.iam_client = boto3.client('iam', config=config)

        # Obtain the bucket name of the S3 bucket where the config JSON files are located.
        self.bucket_name = stack_info(logger_level=self.logger_level).get_bucket_name_by_label(
            self.product, self.environment, self.config_bucket_label)

        # Load the application config JSON file. Table location prefix contained
        # in this file is required for data location access permissions.
        try:
            obj = self.s3_resource.Object(self.bucket_name,
                                          self.config_full_path)
            file_body = obj.get()['Body']
            self.config_dict = json.load(file_body)
        except ClientError as err2:
            if err2.response['Error']['Code'] == 'NoSuchKey':
                self.logger.exception(
                    "Unable to locate the specified application configuration file '{}' in the specified bucket '{}'!".
                    format(self.config_full_path, self.bucket_name))
                raise
            else:
                self.logger.exception(err2)
                raise

        # Load the grant permissions config JSON file.
        try:
            perm_obj = self.s3_resource.Object(self.bucket_name,
                                               self.perm_config_full_path)
            perm_file_body = perm_obj.get()['Body']
            self.config_perm_dict = json.load(perm_file_body)
        except ClientError as err3:
            if err3.response['Error']['Code'] == 'NoSuchKey':
                self.logger.exception(
                    "Unable to locate the specified permissions configuration file '{}' in the specified bucket '{}'!".
                    format(self.perm_config_full_path, self.bucket_name))
                raise
            else:
                self.logger.exception(err3)
                raise

        # Load the SSO organizational roles config JSON file.
        try:
            sso_roles_obj = self.s3_resource.Object(self.bucket_name, self.sso_roles_config_full_path)
            sso_roles_file_body = sso_roles_obj.get()['Body']
            self.sso_roles_dict = json.load(sso_roles_file_body)
        except ClientError as err4:
            if err4.response['Error']['Code'] == 'NoSuchKey':
                self.logger.exception(
                    "Unable to locate the specified SSO roles configuration file '{}' in the specified bucket '{}'!".
                    format(self.sso_roles_config_full_path, self.bucket_name))
                raise
            else:
                self.logger.exception(err4)
                raise

        self.logger.debug(
            'Successfully instantiated Lake Formation Permissions Helper class and loaded all its '
            'configuration JSON files.'
        )

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

    def get_table_names(self, prefix=None, suffix=None):
        """
        Returns a list of Athena table names for the product, environment and
        database that is specified in the class constructor.
        Parameters
        ----------
        prefix (optional): str
                 A prefix that is used to filter table names starting with the specified prefix.
        suffix (optional): str
                 A suffix that is used to filter table names ending with the specified suffix.
        Returns
        -------
        table_names_list: list
                A list of Athena table names from the application config JSON files.
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        table_names_list = []
        i = 0
        for table in self.config_dict['athena_tables']:
            self.logger.debug('table={}'.format(table))
            if prefix is not None:
                if suffix is not None:
                    if table['table_name'].startswith(
                            prefix) and table['table_name'].endswith(suffix):
                        table_names_list.append(table['table_name'])
                else:
                    if table['table_name'].startswith(prefix):
                        table_names_list.append(table['table_name'])
            elif suffix is not None:
                if table['table_name'].endswith(suffix):
                    table_names_list.append(table['table_name'])
            else:
                table_names_list.append(table['table_name'])
            i = +i

        return table_names_list

    def get_table_loc_prefix(self, table_name):
        """
        Parses the preloaded application config dictionary and returns the
        location prefix for the table whose name matches the table name passed
        as an argument.
        Parameters
        ----------
        table_name: str
                The name of Athena table whose data location's prefix is desired.
        Returns
        -------
        loc_prefix: str
                The data location prefix of the Athena table.
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        loc_prefix = 'Null'
        for config in self.config_dict['athena_tables']:
            if config['table_name'] == table_name:
                loc_prefix = config['location_dir']

        self.logger.debug(
            'get_table_loc_prefix->config_dict={}'.format(loc_prefix))
        return loc_prefix

    def parse_config_perm_json(self, table_name):
        """
        For each IAM role in config perm JSON, constructs a dictionary of all
        permissions for the Athena table whose name is provided as an argument.
        Parameters
        ----------
        table_name: str
                The table name for which to grant/revoke permissions.
        Returns
        -------
        perm_dict: dictionary
                The dictionary that contains information about the database,
                table, associated roles and their policies.
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        perm_dict = dict()
        if self.config_perm_dict['database']['include_env_suffix'].lower() == 'true':
            perm_dict.update(db_name=self.config_perm_dict['database']['name'] + '_' + self.environment.lower())
        else:
            perm_dict.update(db_name=self.config_perm_dict['database']['name'])

        self.logger.debug('Database name is set to {}'.format(perm_dict['db_name']))

        for grant in self.config_perm_dict['grants']:
            for table in grant['table']:
                if table['name'] != table_name:
                    continue
                perm_dict.update(table_name=table['name'])
                perm_dict.update(
                    bucket_label=table['bucket_label'].capitalize())
                for sensitivity in table['sensitivity']:
                    high_list = list()
                    for level in sensitivity['high']:
                        high_list.append(level['column'])
                    medium_list = list()
                    for level in sensitivity['medium']:
                        medium_list.append(level['column'])
                    low_list = list()
                    for level in sensitivity['low']:
                        low_list.append(level['column'])
                    perm_dict.update(
                        sensitivity_high_list=high_list,
                        sensitivity_medium_list=medium_list,
                        sensitivity_low_list=low_list)
                for policy in table['policy']:
                    target_role_list = list()
                    for role in policy['roles']:
                        perm_list = list()
                        perm_with_grant_opt_list = list()
                        data_loc_access = False
                        with_grant_data_loc_access = False
                        role_dict = dict()
                        for permission in role['role']['permissions'][
                                'permission']:
                            if permission['perm'] == 'DATA_LOCATION_ACCESS':
                                data_loc_access = True
                            else:
                                perm_list.append(permission['perm'])
                        for perm_with_grant_opt in role['role']['permissions'][
                                'permissionWithGrantOption']:
                            if perm_with_grant_opt['perm'] == 'DATA_LOCATION_ACCESS':
                                with_grant_data_loc_access = True
                            else:
                                perm_with_grant_opt_list.append(
                                    perm_with_grant_opt['perm'])

                        role_dict.update(
                            role_label=role['role']['label'],
                            role_sensitivity=role['role']['permissions'][
                                'sensitivity_level'],
                            role_perm_list=perm_list,
                            role_perm_with_grant_opt_list=perm_with_grant_opt_list,
                            role_data_loc_access=data_loc_access,
                            role_data_loc_access_with_grant=with_grant_data_loc_access)
                        target_role_list.append(role_dict)

                        perm_dict.update(role_list=target_role_list)

        self.logger.debug(
            'parse_config_perm_json->config_dict={}'.format(perm_dict))
        return perm_dict

    def handle_role_perms(self, perm_dict):
        """
        Based on the policy defined in the permissions dictionary that is passed
        as an argument, calls the required set permissions method for each role.
        Parameters
        ----------
        perm_dict: dictionary
                The dictionary that contains information about the database,
                table, associated roles and their policies.
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        bucket_arn_value = stack_info(logger_level=self.logger_level).get_bucket_arn_by_label(
            self.product, self.environment, perm_dict['bucket_label'].lower())

        for i in range(len(perm_dict['role_list'])):
            role_arn_value = stack_info(logger_level=self.logger_level).get_role_arn_by_label(
                self.product, self.environment, perm_dict['role_list'][i]['role_label'],
                [element for element in self.sso_roles_dict if element['Environment'].lower() ==
                 self.environment.lower()])
            if 'CREATE_TABLE' in perm_dict['role_list'][i]['role_perm_list'] \
                    and 'CREATE_TABLE' in perm_dict['role_list'][i]['role_perm_with_grant_opt_list']:
                self.set_database_permissions(role_arn_value, perm_dict['db_name'], list(['CREATE_TABLE']),
                                              list(['CREATE_TABLE']))
                perm_dict['role_list'][i]['role_perm_list'].remove('CREATE_TABLE')
                perm_dict['role_list'][i]['role_perm_with_grant_opt_list'].remove('CREATE_TABLE')
            elif 'CREATE_TABLE' in perm_dict['role_list'][i]['role_perm_list'] \
                    and 'CREATE_TABLE' not in perm_dict['role_list'][i]['role_perm_with_grant_opt_list']:
                self.set_database_permissions(role_arn_value, perm_dict['db_name'], list(['CREATE_TABLE']), list([]))
                perm_dict['role_list'][i]['role_perm_list'].remove('CREATE_TABLE')
            elif 'CREATE_TABLE' not in perm_dict['role_list'][i]['role_perm_list'] \
                    and 'CREATE_TABLE' in perm_dict['role_list'][i]['role_perm_with_grant_opt_list']:
                self.set_database_permissions(role_arn_value, perm_dict['db_name'], list([]), list(['CREATE_TABLE']))
                perm_dict['role_list'][i]['role_perm_with_grant_opt_list'].remove('CREATE_TABLE')
            else:
                pass

            if perm_dict['role_list'][i]['role_sensitivity'].lower() == 'high':
                self.set_table_permissions(
                    role_arn_value, perm_dict['db_name'],
                    perm_dict['table_name'],
                    perm_dict['role_list'][i]['role_perm_list'],
                    perm_dict['role_list'][i]['role_perm_with_grant_opt_list'])
            elif perm_dict['role_list'][i]['role_sensitivity'].lower() == 'medium':
                self.set_column_permissions(
                    role_arn_value, perm_dict['db_name'],
                    perm_dict['table_name'],
                    perm_dict['sensitivity_high_list'],
                    perm_dict['role_list'][i]['role_perm_list'],
                    perm_dict['role_list'][i]['role_perm_with_grant_opt_list'])
            elif perm_dict['role_list'][i]['role_sensitivity'].lower() == 'low':
                self.set_column_permissions(
                    role_arn_value, perm_dict['db_name'],
                    perm_dict['table_name'], perm_dict['sensitivity_high_list']
                    + perm_dict['sensitivity_medium_list'],
                    perm_dict['role_list'][i]['role_perm_list'],
                    perm_dict['role_list'][i]['role_perm_with_grant_opt_list'])
            elif perm_dict['role_list'][i]['role_sensitivity'].lower() == 'none':
                self.set_column_permissions(
                    role_arn_value, perm_dict['db_name'],
                    perm_dict['table_name'], perm_dict['sensitivity_high_list']
                    + perm_dict['sensitivity_medium_list'] +
                    perm_dict['sensitivity_low_list'],
                    perm_dict['role_list'][i]['role_perm_list'],
                    perm_dict['role_list'][i]['role_perm_with_grant_opt_list'])

            if perm_dict['role_list'][i]['role_data_loc_access']:
                if perm_dict['role_list'][i]['role_data_loc_access_with_grant']:
                    self.set_data_location_permissions(
                        role_arn_value, bucket_arn_value,
                        perm_dict['table_name'], ['DATA_LOCATION_ACCESS'],
                        ['DATA_LOCATION_ACCESS'])
                else:
                    self.set_data_location_permissions(
                        role_arn_value, bucket_arn_value,
                        perm_dict['table_name'], ['DATA_LOCATION_ACCESS'], [])
            else:
                continue

    def set_column_permissions(self, role_arn, db_name, table_name,
                               excluded_columns_list, permission_list,
                               perm_with_grant_opt_list):
        """
        grants or revokes column-level permissions. Excludes access to columns
        based on each column's sensitivity level and the associated IAM role's policy.
        Parameters
        ----------
        role_arn: str
                The required role's resource ARN.
        db_name: str
                The database name that houses the Athena table.
        table_name: str
                The Athena table name to which grant/revoke permissions.
        excluded_columns_list: list
                The list of sensitive columns to be excluded.
        permission_list: list
                The list of Lake Formation data permissions that are required by the role.
        perm_with_grant_opt_list: list
                The list of Lake Formation data permissions with grant option that are required by the role.
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if self.mode == 'grant':
            response = self.lf_client.grant_permissions(
                Principal={'DataLakePrincipalIdentifier': role_arn},
                Resource={
                    'TableWithColumns': {
                        'DatabaseName': db_name,
                        'Name': table_name,
                        'ColumnWildcard': {
                            'ExcludedColumnNames': excluded_columns_list
                        },
                    }
                },
                Permissions=permission_list,
                PermissionsWithGrantOption=perm_with_grant_opt_list)
            self.logger.debug(
                'set_column_permissions->response={}'.format(response))
        else:
            try:
                response = self.lf_client.revoke_permissions(
                    Principal={'DataLakePrincipalIdentifier': role_arn},
                    Resource={
                        'TableWithColumns': {
                            'DatabaseName': db_name,
                            'Name': table_name,
                            'ColumnWildcard': {
                                'ExcludedColumnNames': excluded_columns_list
                            },
                        }
                    },
                    Permissions=permission_list,
                    PermissionsWithGrantOption=perm_with_grant_opt_list)
                self.logger.debug(
                    'set_column_permissions->response={}'.format(response))
            except ClientError as e:
                # If grantee has no permissions, ignore revoke failures.
                if e.response['Error']['Code'] == 'InvalidInputException':
                    self.logger.warning('Grantee has no permissions to revoke - ignoring InvalidInputException')

    def set_table_permissions(self, role_arn, db_name, table_name,
                              permission_list, perm_with_grant_opt_list):
        """
        Grants or revokes access to a table based on the IAM role's policy.
        Parameters
        ----------
        role_arn: str
                The required role's resource ARN.
        db_name: str
                The database name that houses the Athena table.
        table_name: str
                The Athena table name to which grant/revoke permissions.
        permission_list: list
                The list of Lake Formation data permissions that are required by the role.
        perm_with_grant_opt_list: list
                The list of Lake Formation data permissions with grant option that are required by the role.
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if self.mode == 'grant':
            response = self.lf_client.grant_permissions(
                Principal={'DataLakePrincipalIdentifier': role_arn},
                Resource={
                    'Table': {
                        'DatabaseName': db_name,
                        'Name': table_name,
                    }
                },
                Permissions=permission_list,
                PermissionsWithGrantOption=perm_with_grant_opt_list)
            self.logger.debug(
                'set_table_permissions->response={}'.format(response))
        else:
            try:
                response = self.lf_client.revoke_permissions(
                    Principal={'DataLakePrincipalIdentifier': role_arn},
                    Resource={
                        'Table': {
                            'DatabaseName': db_name,
                            'Name': table_name,
                        }
                    },
                    Permissions=permission_list,
                    PermissionsWithGrantOption=perm_with_grant_opt_list)
                self.logger.debug(
                    'set_table_permissions->response={}'.format(response))
            except ClientError as e:
                # If grantee has no permissions, ignore revoke failures.
                if e.response['Error']['Code'] == 'InvalidInputException':
                    self.logger.warning('Grantee has no permissions to revoke - ignoring InvalidInputException')

    def set_database_permissions(self, role_arn, db_name,
                                 permission_list, perm_with_grant_opt_list):
        """
        Grants or revokes access to a database based on the IAM role's policy.
        Parameters
        ----------
        role_arn: str
                The required role's resource ARN.
        db_name: str
                The database name that houses the Athena table.
        permission_list: list
                The list of Lake Formation data permissions that are required by the role.
        perm_with_grant_opt_list: list
                The list of Lake Formation data permissions with grant option that are required by the role.
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if self.mode == 'grant':
            response = self.lf_client.grant_permissions(
                Principal={'DataLakePrincipalIdentifier': role_arn},
                Resource={
                    'Database': {
                        'Name': db_name
                    }
                },
                Permissions=permission_list,
                PermissionsWithGrantOption=perm_with_grant_opt_list)
            self.logger.debug(
                'set_database_permissions->response={}'.format(response))
        else:
            try:
                response = self.lf_client.revoke_permissions(
                    Principal={'DataLakePrincipalIdentifier': role_arn},
                    Resource={
                        'Table': {
                            'DatabaseName': db_name
                        }
                    },
                    Permissions=permission_list,
                    PermissionsWithGrantOption=perm_with_grant_opt_list)
                self.logger.debug(
                    'set_database_permissions->response={}'.format(response))
            except ClientError as e:
                # If grantee has no permissions, ignore revoke failures.
                if e.response['Error']['Code'] == 'InvalidInputException':
                    self.logger.warning('Grantee has no permissions to revoke - ignoring InvalidInputException')

    def set_data_location_permissions(self, role_arn, bucket_arn,
                                      table_name, permission_list,
                                      perm_with_grant_opt_list):
        """
        Grants or revokes data location access permissions based on the IAM
        role's policy for roles that need to create a table in the specified S3
        data location.
        Parameters
        ----------
        role_arn: str
                The required role's resource ARN.
        bucket_arn: str
                The required bucket's resource ARN where the table data is located.
        table_name: str
                The Athena table name to which grant/revoke permissions.
        permission_list: list
                The list of Lake Formation data permissions that are required by the role.
        perm_with_grant_opt_list: list
                The list of Lake Formation data permissions with grant option that are required by the role.
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        if self.mode == 'grant':
            response = self.lf_client.grant_permissions(
                Principal={'DataLakePrincipalIdentifier': role_arn},
                Resource={
                    'DataLocation': {
                        'ResourceArn':
                        bucket_arn + self.get_table_loc_prefix(table_name) +
                        '/' + table_name
                    }
                },
                Permissions=permission_list,
                PermissionsWithGrantOption=perm_with_grant_opt_list)
            self.logger.debug(
                'set_data_location_permissions->response={}'.format(response))
        else:
            try:
                response = self.lf_client.revoke_permissions(
                    Principal={'DataLakePrincipalIdentifier': role_arn},
                    Resource={
                        'DataLocation': {
                            'ResourceArn':
                            bucket_arn + self.get_table_loc_prefix(table_name)
                            + '/' + table_name
                        }
                    },
                    Permissions=permission_list,
                    PermissionsWithGrantOption=perm_with_grant_opt_list)
                self.logger.debug(
                    'set_data_location_permissions->response={}'.format(
                        response))
            except ClientError as e:
                # If grantee has no permissions, ignore revoke failures.
                if e.response['Error']['Code'] == 'InvalidInputException':
                    self.logger.warning(
                        'Grantee has no permissions to revoke - ignoring InvalidInputException'
                    )

    def handle_permissions(self, table_name_list):
        """
        Iterates through a list of table names that is provided as an argument
        and grants or revokes permissions based on a permissions config JSON
        file that declares the policies for each role on each table.
        Parameters
        ----------
        table_name_list: list
                A list of one or more tables
        Returns
        -------
        N/A
        Exceptions
        ----------
        N/A
        """
        self.logger.debug('Now in {}...'.format(sys._getframe().f_code.co_name))

        for table in table_name_list:
            self.logger.info(
                '----------------- Now processing table: {} in mode: {} -----------------'
                .format(table, self.mode))
            perm_dict = self.parse_config_perm_json(table)
            self.logger.debug(
                'handle_permissions->perm_dict={}'.format(perm_dict))
            self.handle_role_perms(perm_dict)
            perm_dict.clear()


def main():
    """
    Main function (entry point)
    """
    parser = argparse.ArgumentParser(
        description='A utility class to grant Lake Formation permissions.')
    parser.add_argument(
        'mode',
        help='Mode in which you want the Lake Formation Helper class to operate (e.g., grant or revoke).',
        type=str,
        choices=['grant', 'revoke'])
    parser.add_argument(
        'product',
        help='product for which to invoke the Lake Formation Helper class (e.g., rdms).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Lake Formation Helper class (e.g., dev).',
        type=str)
    parser.add_argument(
        'bucket_label',
        help='S3 Bucket label for the bucket in which the config JSON files are stored (e.g., app).',
        type=str)
    parser.add_argument(
        'app_config_file',
        help='Full path/name of the application configuration JSON file in S3 (e.g., config/config.json).',
        type=str)
    parser.add_argument(
        'perm_config_file',
        help='Full path/name of the permissions configuration JSON file in S3 (e.g., config/config_perm.json).',
        type=str)
    parser.add_argument(
        '-sor',
        '--sso_org_roles_config_file',
        help='Full path/name of the configuration JSON file in S3 that contains the SSO roles that '
             'are managed at the AWS organization level (e.g., config/sso_roles_config.json).',
        type=str)
    parser.add_argument(
        '-p',
        '--prefix',
        help='Prefix for use in calls to get_table_name() method to limit the list of table names returned '
             'to a set that begins with the provided prefix.',
        type=str)
    parser.add_argument(
        '-s',
        '--suffix',
        help='Suffix for use in calls to lf_perms_helper.get_table_name to limit the list of table names '
             'returned to a set that ends with the provided suffix.',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Lake Formation Helper class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])
    parser.add_argument(
        '-l',
        '--logger_level',
        help='Desired level of logging.',
        choices=['debug', 'info', 'error', 'critical'])
    args = parser.parse_args()

    mode = args.mode
    product = args.product
    environment = args.environment.capitalize()
    bucket_label = args.bucket_label
    app_config_file = args.app_config_file
    perm_config_file = args.perm_config_file
    org_roles_config_file = args.org_roles_config_file
    prefix = args.prefix
    suffix = args.suffix
    if args.region is not None:
        region = args.region.lower()
    else:
        region = 'us-west-2'
    if args.logger_level is not None:
        logger_level = args.logger_level.upper()
    else:
        logger_level = 'DEBUG'

    print(
        'About to instantiate Lake Formation Helper class with mandatory positional arguments set to:\n\t'
        "mode='{}', product='{}', environment='{}', bucket_label='{}', app_config_file='{}', "
        "and perm_config_file='{}'.\nThe following optional arguments are set: org_roles_config_file='{}', "
        "prefix='{}', suffix='{}', region='{}' and logger_level='{}'."
        .format(mode, product, environment, bucket_label, app_config_file,
                perm_config_file, org_roles_config_file, prefix, suffix, region, logger_level))

    if org_roles_config_file is None:
        lfph = lf_perms_helper(mode, product, environment, bucket_label,
                               app_config_file, perm_config_file, region=region,
                               logger_level=logger_level)
    else:
        lfph = lf_perms_helper(mode, product, environment, bucket_label,
                               app_config_file, perm_config_file, org_roles_config_file, region=region,
                               logger_level=logger_level)

    # Example of how to call get_table_names method.
    table_names_list = lfph.get_table_names(prefix, suffix)
    print('\ntable_names_list={}'.format(table_names_list))

    if len(table_names_list) == 0:
        print('************* No tables were found! *************')
        sys.exit(1)

    # Example of how to call handle_permissions method.
    lfph.handle_permissions(table_names_list)


if __name__ == '__main__':
    main()
