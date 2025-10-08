# WELCOME TO UCOP UTILITIES PACKAGE FOR PYTHON!
This package contains an eclectic collection of Python utility classes
that are used for the AWS-based projects. Below is a list of such utility classes
and their functionality.

>Note1: To display usage information for a class, enter the following command in a bash terminal:
  * python \<full path and class-name\>.py --help

>Note2: To display docstrings for a class, start the Python interactive shell (REPL) by entering "python" at the command line in a bash terminal. Then enter the following:
  * python
  * \>>> from ucop_util.<class-name> import \<class-name>
  * \>>> help(<class-name>)
  * To exit REPL press \<ctrl> + D
  - > Example:
  * >          from ucop_util.lf_perms_helper import lf_perms_helper
  * >          help(lf_perms_helper)

# LIST OF CLASSES:
1. ___date_handler.py___
  * For AWS services that use UTC date formats, this class could be used to convert the date and time to Pacific Standard (PST). To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util import date_handler
    * current_date = date_handler().get_local_date_pst()
    * current_time = date_handler().get_local_time_pst()
    > To display the documentation for the class follow instructions in note 2 above.
2. ___file_name_parser.py___
  * Provides methods for parsing SDAP Enrollment files names and inferring the optimum Athena partitioning scheme. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util import file_name_parser
    * parser_dict = file_name_parser().infer_enrollment_target_folder(file_name)
    > To display the documentation for the class follow instructions in note 2 above.
3. ___marker_file_helper.py___
  * Provides methods for managing SDAP Enrollment marker files. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.marker_file_helper import marker_file_helper
    * marker_prefix_list = marker_file_helper().set_process_date(
            marker_folder_prefix, process_date, int(num_prior_days))
    * file_processing_list = marker_file_helper().get_files_to_process(
                marker_bucket, marker_prefix, marker_suffix)
    * marker_file_helper().handle_marker_file(
                        marker_bucket, marker_prefix, file_name, marker_suffix)
    > To display the documentation for the class follow instructions in note 2 above.
4. ___running_stacks_info.py___
  * Provides a method for obtaining stack names of all running stacks from CloudFormation for the product and environment that are provided as arguments. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.running_stacks_info import running_stacks_info
    * running_stacks_info().get_stack_names(product, environment)
    > To display the documentation for the class follow instructions in note 2 above.
5. ___stack_info.py___
  * Provides methods for resolving S3 logical bucket labels to their corresponding physical bucket names in UCOP data lake projects. Similarly, you can resolve IAM logical role labels to their corresponding ARN. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util import stack_info
    * bucket_arn_value = stack_info(logger_level='DEBUG').get_bucket_arn_by_label(
            product, environment, perm_dict['bucket_label'].lower())
    * bucket_name = stack_info(logger_level='INFO').get_bucket_name_by_label(
            product, environment, config_bucket_label)
    > To display the documentation for the class follow instructions in note 2 above.
6. ___util_exception.py___
  * Includes the various exception classes that could be raised by ucop_util classes. To use any of the exception classes import the class in your Python module:
    * from ucop_util.util_exception import <exception-name> where <exception-name> is one of the exception classes contained in util_exception.py
    > To display the documentation for the class follow instructions in note 2 above.
7. ___athena_util.py___
  * Provides methods for performing Athena operations such as MSCK REPAIR TABLE or ALTER TABLE ADD PARTITION. To use this class, include the following import and one of the listed class usage statements in your Python module:
    * from ucop_util.athena_util import athena_util
    * au_obj = athena_util(product, environment, region=<desired-region>, logger_level=<desired-logger-level>)
    * au_obj.add_partition(table-name, partition)
    * au_obj.repair_table(table-name)
    > To display the documentation for the class follow instructions in note 2 above.
8. ___job_run_waiter.py___
  * Provides a wait mechanism to ensure only one instance of a given Glue job runs at any given time. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.job_run_waiter import job_run_waiter
    * job_waiter = job_run_waiter()
    * job_waiter.wait_if_running(glue-job-name, seconds-to-wait)
    > To display the documentation for the class follow instructions in note 2 above.
9. ___lf_perms_helper.py___
  * Provides methods for granting and revoking fine-grained permissions using AWS Lake Formation API. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.lf_perms_helper import lf_perms_helper
    * lfph = lf_perms_helper('grant or revoke', product, environment, application-bucket-label,
                           S3-path-to-application-config-json, S3-path-to-grant-config-json, region=<desired-region>, logger_level=<desired-logger-level>)
    * lfph.handle_permissions(table_name_list)
    > To display the documentation for the class follow instructions in note 2 above.
10. ___ref_data_file_name_parser.py___
  * Provides methods for parsing Reference data files names and inferring the optimum Athena partitioning scheme. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util import ref_data_file_name_parser
    * parser_dict = ref_data_file_name_parser().infer_ref_data_target_folder(file_name)
    > To display the documentation for the class follow instructions in note 2 above.
11. ___ref_data_queue_helper.py___
  * Provides methods for communicating the reference data file attributes between the Lambda function that moves the file from the landing zone to the archive S3 bucket and the Lambda function that ingests the file. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util import ref_data_queue_helper
    * rdqh = ref_data_queue_helper(product, environment, logger_level='DEBUG')
    * parser_dict = {
    *   'FileName': 'campus_college_major.012018.csv',
    *   'FileYear': '2018',
    *   'FileMonth': '01',
    *   'TableName': 'campus_college_major'
    * }
    * send_msg_response = rdqh.send_file_attributes(parser_dict)
    > To display the documentation for the class follow instructions in note 2 above.
12. ___workflow_initiator.py___
  * Provides methods for initiating a step functions' state machine (workflow). To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.workflow_initiator import workflow_initiator
    * wi_obj = workflow_initiator(product, environment, region=<desired-region>, logger_level=<desired-logger-level>)
    * sm_arn = wi_obj.get_state_machine_arn(<desired-suffix>, state_machine_prefix=<desired-prefix> optional)
    * sm_input = 'optional JSON structure used as input to the state machine'
    * response = wi_obj.initiate_workflow(sm_arn, state_machine_input=sm_input)
    > To display the documentation for the class follow instructions in note 2 above.
13. ___send_mail_helper.py___
  * Provides methods for sending email to one or more recipients -- primarily used for ETL workflow status notifications. To use this class, include the following import and class usage statements in your Python module:
    * from ucop_util.send_mail_helper import send_mail_helper
    * smh_obj = send_mail_helper(product, environment, sender_email, region=<desired-region>, logger_level=<desired-logger-level>)
    * smh_obj.send_email(args.recipients_list, subject, body)
    > To display the documentation for the class follow instructions in note 2 above.
