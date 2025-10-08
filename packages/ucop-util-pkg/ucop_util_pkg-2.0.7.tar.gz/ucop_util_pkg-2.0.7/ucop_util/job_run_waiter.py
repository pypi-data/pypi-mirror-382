import boto3
import time
import argparse

from botocore.config import Config


class job_run_waiter:
    """
    A utility class that polls the state of a Glue job run and if the job
    is in STARTING, RUNNING, or STOPPING state, it waits for a predetermined
    length of time before querying the job run state again.
    """

    def __init__(self, region='us-west-2'):
        self.region = region.lower()
        config = Config(
            region_name=self.region,
            retries=dict(
                total_max_attempts=25
            )
        )
        self.client = boto3.client('glue', config=config)

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, region):
        self.__region = region

    def wait_if_running(self, job_name, wait_seconds=60):
        """
        Determines the number of instances of a particular Glue job whose name is
        passed as an argument and if more than one instance of the job is in
        one of STARTING, RUNNING or STOPPING states, it waits for the number of
        seconds passed as an arugment and tries again.

        Default wait is 60 seconds but can be overridden by providing a
        value for wait_seconds.

        Parameters
        ----------
        job_name : str
                Name of the Glue job to wait for.
        wait_seconds: int
                Number of seconds to wait.

        Returns
        -------
        instance_count : int
                Count of number of job instances in STARTING, RUNNING or STOPPING state.
        Exceptions
        ----------
        None
        """
        while self.__check_for_concurrency(job_name) > 1:
            time.sleep(wait_seconds)

    def __check_for_concurrency(self, job_name):
        """
        This is a private method that calls get_job_runs method in boto3 Glue
        API and iterates through the response one page at a time to obtain a
        count of instances of a particular Glue job whose name is provided
        as an argument. The functionality of this method is similar to the
        following CLI command:
            aws glue get-job-runs --job-name <job-name>

        Default wait is 60 seconds.

        Parameters
        ----------
        job_name : str
                Name of the Glue job to wait for.

        Returns
        -------
        instance_count : int
                Count of number of job instances in STARTING, RUNNING or STOPPING state.
        Exceptions
        ----------
        None
        """
        instance_count = 0
        starting_token = None

        paginator = self.client.get_paginator('get_job_runs')
        response_iterator = paginator.paginate(
            JobName=job_name,
            PaginationConfig={
                'StartingToken': starting_token
            })

        for page in response_iterator:
            for job_run in page['JobRuns']:
                if job_run['JobRunState'] in ('STARTING', 'RUNNING',
                                              'STOPPING'):
                    instance_count += 1

        return instance_count


def main():
    """
    Main entry point to class
    """
    parser = argparse.ArgumentParser(
        description="A utility class that waits on a Glue job to change state from one of 'STARTING','RUNNING', "
                    "or 'STOPPING' states."
    )
    parser.add_argument(
        'product',
        help='product for which to invoke the Job Run Waiter utility class (e.g., sdap).',
        type=str)
    parser.add_argument(
        'environment',
        help='environment in which to invoke the Job Run Waiter utility class (e.g., dev).',
        type=str)
    parser.add_argument(
        '-r',
        '--region',
        help='AWS region in which to invoke the Stack Info utility class.',
        choices=['us-west-2', 'us-west-1', 'us-east-1', 'us-east-2'])

    args = parser.parse_args()

    product = args.product.lower()
    environment = args.environment.lower()

    if args.region is not None:
        region = args.region.lower()
    else:
        region = 'us-west-2'

    jrw_obj = job_run_waiter(region)

    print('AWS region is set to: {}\n'.format(jrw_obj.region))
    print(
        "Waiting for glue job if it is in one of 'STARTING','RUNNING', or 'STOPPING' states..."
    )
    # jrw_obj.wait_if_running(product + '-' + environment + '-datamorph-gluejob', 300)
    jrw_obj.wait_if_running(
        product + '-' + environment + '-reporting_day_d-gluejob')
    print('Done waiting!')


if __name__ == '__main__':
    main()
