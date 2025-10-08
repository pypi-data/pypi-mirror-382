import boto3
import logging
import argparse

from botocore.config import Config


class workflow_initiator:
    """
    A utility class to initiate a state machine using boto3 API for AWS step functions.
    To use this class, instantiate it using the desired product and environment, invoke
    its get_state_machine_arn() method to get the desired state machine's ARN and then
    invoke its initiate_workflow() to start the workflow.
    """

    def __init__(self,
                 product,
                 environment,
                 region='us-west-2',
                 logger_level='INFO'):
        """
        Class constructor.

        Parameters
        ----------
        product: str
                The name of product (e.g., rdms) for which the workflow should
                be instantiated.
        environment: str
                The environment (e.g., dev, test, or prod) in which the workflow
                should be instantiated.
        region (optional): str
                If provided, overrides the default 'us-west-2' region.
        logger_level (optional): str
                If provided, overrides the default INFO logger level.
                Permissible values are DEBUG, ERROR, or CRITICAL.
        """
        pgm_name = 'workflow_initiator.py'
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
        self.environment = environment.capitalize()
        self.region = region.lower()
        config = Config(
            region_name=self.region,
            retries=dict(
                total_max_attempts=25
            )
        )
        self.sfn_client = boto3.client('stepfunctions', config=config)

        self.logger.info(
            'Successfully instantiated the Workflow Initiator Utility class.')

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

    def initiate_workflow(self, state_machine_arn, state_machine_input='{}'):
        """
        Triggers the workflow using the input that is provided as the argument.

        Parameters
        ----------
        state_machine_arn: str
                The ARN of the state machine that needs to be initiated. The
                ARN can be obtained by first calling the get_state_machine_arn()
                method.
        state_machine_input: str
                An optional JSON structure that serves as the input to the workflow. If
                no input value is provided defaults to an empty JSON structure,
                for example: '{}'.
        Returns
        -------
        response from start_execution boto3 call. Response syntax:
        {
            'executionArn': 'string',
            'startDate': datetime(2015, 1, 1)
        }
        Exceptions
        ----------
        None
        """
        self.logger.debug('Now in initiate_workflow function')

        self.logger.debug(
            'About to start state machine={}'.format(state_machine_arn))

        response = self.sfn_client.start_execution(
            stateMachineArn=state_machine_arn, input=state_machine_input)

        return response

    def get_state_machine_arn(self,
                              state_machine_suffix,
                              state_machine_prefix=''):
        """
        Obtains the ARN for the state machine whose name starts with product
        plus the environment that were provided as arguments while instantiating
        the class and ends with the specified suffix.

        Parameters
        ----------
        state_machine_suffix: str
                A string representing the ending characters in the step function's
                name (e.g., studentEnrollmentWorkflow). Value provided as suffix is
                not case-sensitive as it is converted to lower case for matches.
        state_machine_prefix: str
                An optional string representing the starting characters in the step function's name.
                If no value is provided defaults to a value comprised of the
                concatenation of product and environment in lowercase letters.
        Returns
        -------
        State machine ARN
        Exceptions
        ----------
        Throws an AssertionError if either a state machine with the specified prefix
        and prefix is not found or more than one state machine with the specified
        prefix and suffix is found.
        """
        self.logger.debug('Now in get_state_machine_arn function')

        starting_token = None
        paginator = self.sfn_client.get_paginator('list_state_machines')
        response_iterator = paginator.paginate(
            PaginationConfig={
                'StartingToken': starting_token
            }
        )

        if state_machine_prefix == '':
            state_machine_prefix = self.product + '-' + self.environment

        sm_arn_list = []
        for state_machines in response_iterator:
            for state_machine in state_machines['stateMachines']:
                if state_machine['name'].lower().startswith(
                        state_machine_prefix.lower()
                ) and state_machine['name'].lower().endswith(
                        state_machine_suffix.lower()):
                    self.logger.debug(
                        "Found a state machine: '{}' whose name in lowercase letters starts with: '{}' "
                        "and ends with: '{}'"
                        .format(state_machine['name'].lower(),
                                state_machine_prefix,
                                state_machine_suffix.lower()))
                    sm_arn_list.append(state_machine['stateMachineArn'])
        self.logger.debug('List of state machines={}'.format(sm_arn_list))
        try:
            assert len(sm_arn_list) == 1
        except AssertionError as error:
            self.logger.error('List of state machines={}'.format(sm_arn_list))
            self.logger.error('Number of state machines found={}'.format(
                len(sm_arn_list)))
            if len(sm_arn_list) == 0:
                self.logger.exception(
                    'No state machine was found with the specified prefix={} and suffix={}!'
                    .format(state_machine_prefix, state_machine_suffix))
            else:
                self.logger.exception(
                    'More than one state machine was found with the specified prefix={} and suffix={}!'
                    .format(state_machine_prefix, state_machine_suffix))
            raise error

        return sm_arn_list[0]


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description="A utility class to initiate a step function's state machine such as an ETL workflow."
    )
    parser.add_argument(
        'product',
        help='product for which to invoke the Workflow Initiator class (e.g., rdms).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Workflow Initiator class (e.g., dev).',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Workflow Initiator class.',
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

    print(
        'About to instantiate Workflow Initiator class with mandatory positional arguments set '
        "to '{}' and '{}' and optional region and logger_level arguments set to '{}' and '{}'"
        .format(product, environment, region, logger_level))

    # Instantiate the class
    wi_obj = workflow_initiator(product, environment, region=region, logger_level=logger_level)

    # Get ARN for the desired step functions state machine.
    # Because no prefix is provided uses the default prefix.
    state_machine_arn = wi_obj.get_state_machine_arn(
        'hpejman-stepfunction')

    # Configure state machine's input
    state_machine_input = '{"query_datetime_list": ["2021-08-12@12.10.09"]}'

    # Initiate the workflow using the ARN obtained using get_state_machine_arn method
    response = wi_obj.initiate_workflow(
        state_machine_arn, state_machine_input=state_machine_input)
    print('Execution ARN={}'.format(response['executionArn']))
    print('Execution timestamp={}'.format(response['startDate']))

    print('\nExecuted initiate_workflow method successfully!')


if __name__ == '__main__':
    main()
