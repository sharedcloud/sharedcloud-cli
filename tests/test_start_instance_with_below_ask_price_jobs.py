import multiprocessing
import os

import time

from tests.constants import Image, InstanceType, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_start_instance_and_process_one_batch_of_jobs_that_end_up_not_being_processed_because_their_bid_price_is_too_low():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,),(3,))'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )
    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=1.0)

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )
    p.terminate()


    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_start_instance_and_process_two_batches_of_jobs_with_only_one_being_processed_because_the_other_bid_price_is_too_low():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,),(3,))'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )
    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=1.0)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0)

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED', 'CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=6
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['3'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED', 'IN_PROGRESS', 'IN_PROGRESS', 'IN_PROGRESS'],
        expected_num_jobs=6
    )
    p.join(30.0)  # 30 seconds of timeout
    p.terminate()

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)