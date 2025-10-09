"""
Handle everything revolving around zephyr testcases.
"""
import datetime
import time
from enum import Enum
from typing import List

import zephyr.exceptions as exceptions
from zephyr.filecache import filecache
from zephyr.filecache import WEEK
from zephyr.interface import ZephyrInterface


class TestVerdicts(Enum):
    """
    Enum class for test verdicts.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EXECUTED = "NOT EXECUTED"


class TestManagement(ZephyrInterface):
    """
    Handles management of test cases
    """

    def __init__(self, bearer_token: str, *args, **kwargs):
        """
        Initializes the TestManagement class

        :param bearer_token:
            token to use for authentication (without Bearer prefix)
        """
        super().__init__(bearer_token, *args, **kwargs)

    def create_testcase(
        self,
        project_key: str,
        testcase_name: str,
        folder_name: str = None,
        tc_objective: str = "",
        tc_precondition: str = "",
        priority: str = "Normal",
        est_time: int = None,
        labels: list = [],
        *args,
        **kwargs,
    ):
        """
        Creates a testcase in Zephyr

        :param project_key:
            key of the project to add the testcase to
        :param testcase_name:
            name of the testcase
        :param folder_name:
            name of the folder to add the testcase to
        :param tc_objective:
            objective of the testcase
        :param tc_precondition:
            precondition of the testcase
        :param labels:
            list of labels to add to the testcase
        :param est_time:
            estimated time to complete the testcase
        :param priority:
            priority of the testcase (Low, Normal, High)
        :return:
            key and id of created testcase
        """
        url = self.base_url + "/testcases"

        if folder_name is not None:
            try:
                folder_id = self.get_folder_id(project_key=project_key, folder_name=folder_name)
            except exceptions.FolderNotFoundError:
                folder_id = None
        else:
            folder_id = None

        payload = dict(
            projectKey=project_key,
            name=testcase_name,
            objective=tc_objective,
            precondition=tc_precondition,
            estimatedTime=est_time,
            priorityName=priority,
            folderId=folder_id,
            labels=labels,
            **kwargs,
        )

        resp = self.post_request(url, payload)

        return resp["key"], resp["id"]

    def get_testcase(self, testcase_key: str, *args, **kwargs):
        """
        Gets a testcase from Zephyr

        :param testcase_key:
            key of the testcase (e.g. BSBS-T1
        :return:
            testcase
        """
        url = self.base_url + "/testcases/{}".format(testcase_key)

        try:
            return self.get_request(url)
        except exceptions.BadResponseError:
            raise exceptions.TestCaseNotFoundError(testcase_key)

    def get_test_case_by_name(
        self, project_key: str, testcase_name: str, folder_path: str, partial_match: bool = False, *args, **kwargs
    ):
        """
        Gets a testcase from Zephyr

        :param testcase_name:
            name of the testcase (e.g. Application_test
        :param folder_path:
            folder path (e.g. Gtest/Master/bolognasc
        :param partial_match:
            match type (e.g. set partial_match to True for partially matching testcase name
        :return:
            testcases
        """
        folder_path = folder_path.split("/")
        parent_id = self.get_folder_id(
            project_key=project_key, folder_name=folder_path[0], parent_id=None, folder_type="TEST_CASE"
        )
        for folder_name in folder_path[1:]:
            parent_id = self.get_folder_id(
                project_key=project_key, folder_name=folder_name, parent_id=parent_id, folder_type="TEST_CASE"
            )

        try:
            testcases = self.get_all_testcases(project_key=project_key, folder_id=parent_id)
            _testcases = []
            for testcase in testcases:
                if not partial_match and testcase["name"] == testcase_name:
                    _testcases.append(testcase)
                if partial_match and testcase_name in testcase["name"]:
                    _testcases.append(testcase)
            return _testcases
        except exceptions.BadResponseError:
            raise exceptions.TestCaseNotFoundError(testcase_name)

    def get_all_testcases(
        self, project_key: str = None, folder_id: int = None, timeout_s: float = 1.0, *args, **kwargs
    ):
        """
        Gets testcases from Zephyr

        :param project_key:
            key of the project we want to look at
        :param folder_id:
            id of the folder to look into
        :param timeout_s:
            time to wait between retries
        :return:
            testcases as a data dictionary
        """
        tcs = None
        url = self.base_url + "/testcases"
        payload = dict(projectKey=project_key, folderId=folder_id, startAt=0, maxResults=1, **kwargs)
        try:
            data = self.get_request(url, payload)
        except exceptions.BadResponseError:
            raise exceptions.FolderNotFoundError(folder_id)

        if data is not None:
            total_testcases = data["total"]
            if total_testcases > 0:
                payload = dict(
                    projectKey=project_key, folderId=folder_id, startAt=0, maxResults=total_testcases, **kwargs
                )
                data = self.get_request(url, payload)
                tcs = data["values"]
                # check if all tcs were returned, get rest otherwise
                if data["maxResults"] != total_testcases:
                    while data["next"] is not None:
                        data = self.get_request(data["next"])
                        tcs.extend(data["values"])
                        time.sleep(timeout_s)
        return tcs

    def get_testcasekeys_from_cycle(
        self,
        project_key: str = None,
        testcycle_key: str = None,
        date_after: str = None,
        date_before: str = None,
        timeout_s: float = 1.0,
        *args,
        **kwargs,
    ):
        """
        Gets all testcase keys of a given test cycle from Zephyr

        :param project_key:
            key of the project we want to look at
        :param testcycle_key:
            key of the test cycle we want to look at
        :param date_after:
            only return test executions after this date (format: yyyy-MM-dd'T'HH:mm:ss'Z')
        :param date_before:
            only return test executions before this date (format: yyyy-MM-dd'T'HH:mm:ss'Z')
        :param timeout_s:
            time to wait between retries
        :return:
            testcase keys as a list
        """
        test_execs = self.get_test_executions(
            project_key=project_key,
            testcycle_key=testcycle_key,
            date_after=date_after,
            date_before=date_before,
            timeout_s=timeout_s,
        )
        testcaseKeyList = []
        if test_execs:
            for test_exec in test_execs:
                if test_exec["testCase"]:
                    tc = self.get_request(test_exec["testCase"]["self"])
                    testcaseKeyList.append(tc["key"])
        return testcaseKeyList

    def get_testcycle(self, testcycle_key: str, *args, **kwargs):
        """
        Gets a testcycle from Zephyr

        :param testcycle_key:
            key of the testcycle (e.g. BSBS-R21)
        :return:
            testcycle
        """
        url = self.base_url + "/testcycles/{}".format(testcycle_key)

        try:
            return self.get_request(url)
        except exceptions.BadResponseError:
            raise exceptions.TestCycleNotFoundError(testcycle_key)

    def get_all_testcycles(self, project_key: str, folder_name: str = None, timeout_s: float = 1.0, *args, **kwargs):
        """
        Get all testcycles for a project or a folder in a project

        :param project_key:
            key of the project (e.g. BSBS)
        :param folder_name:
            folder name (optional)
        :param timeout_s:
            time to wait between retries
        :return:
            list of testcycles
        """
        url = self.base_url + "/testcycles"

        if folder_name is not None:
            try:
                folder_id = self.get_folder_id(
                    project_key=project_key, folder_name=folder_name, folder_type="TEST_CYCLE"
                )
            except exceptions.FolderNotFoundError:
                folder_id = None
        else:
            folder_id = None

        payload = dict(projectKey=project_key, folderId=folder_id, maxResults=1, **kwargs)

        resp = self.get_request(url, payload)
        total_cycles = resp["total"]

        payload = dict(projectKey=project_key, folderId=folder_id, maxResults=total_cycles, **kwargs)
        resp = self.get_request(url, payload)
        cycles = resp["values"]

        # check if all cycles are returned, get rest otherwise
        if resp["maxResults"] != total_cycles:
            while resp["next"] is not None:
                resp = self.get_request(resp["next"])
                cycles.extend(resp["values"])
                time.sleep(timeout_s)

        # remove duplicates before returning
        non_dup_ids = list(set([x["id"] for x in cycles]))
        return [x for x in cycles if x["id"] in non_dup_ids]

    def create_folder(self, project_key: str, folder_name: str, folder_type: str, parent_folder_path: str):
        """
        Creates a new test cycle

        :param project_key:
            key of the project (e.g. BSBS)
        :param folder_name:
            name of the folder
        :param folder_type:
           folder type : [TEST_CASE, TEST_CYCLE]
        :param parent_folder_path:
            id of the folder to create the test cycle in (optional)
        :return:
            response data from post command
        """
        folder_path = parent_folder_path.split("/")
        parent_id = self.get_folder_id(
            project_key=project_key, folder_name=folder_path[0], parent_id=None, folder_type="TEST_CASE"
        )
        for folder_name in folder_path[1:]:
            parent_id = self.get_folder_id(
                project_key=project_key, folder_name=folder_name, parent_id=parent_id, folder_type="TEST_CASE"
            )
        payload = {"parentId": parent_id, "name": folder_name, "projectKey": project_key, "folderType": folder_type}
        url = self.base_url + "/folders"
        try:
            return self.post_request(url=url, payload=payload)
        except exceptions.BadResponseError:
            raise exceptions.BadResponseError(f"Folder creation failed for new folder: {folder_name}.")

    def create_testcycle(self, project_key: str, name: str, descr: str = None, folder_id: int = None, *args, **kwargs):
        """
        Creates a new test cycle

        :param project_key:
            key of the project (e.g. BSBS)
        :param name:
            name of the test cycle
        :param descr:
            description of the test cycle (optional)
        :param folder_id:
            id of the folder to create the test cycle in (optional)
        :return:
            key and id of the created cycle
        """
        url = self.base_url + "/testcycles"

        payload = dict(projectKey=project_key, name=name, description=descr, folderId=folder_id, **kwargs)

        resp = self.post_request(url, payload)

        return resp["key"], resp["id"]

    def get_status_by_id(self, status_id: int, *args, **kwargs):
        """
        Get test execution status by its id

        :param status_id:
            id of the status
        :return:
            status
        """
        url = self.base_url + "/statuses"

        resp = self.get_request(url, dict(statusId=status_id), **kwargs)

        return resp

    def get_test_executions(
        self,
        project_key: str = None,
        testcycle_key: str = None,
        testcase_key: str = None,
        date_after: str = None,
        date_before: str = None,
        issue_links: bool = None,
        timeout_s: float = 1.0,
        *args,
        **kwargs,
    ):
        """
        Get all test executions

        :param project_key:
            key of the project (e.g. BSBS)
        :param testcycle_key:
            key of the test cycle
        :param testcase_key:
            key of the test case
        :param date_after:
            only return test executions after this date (format: yyyy-MM-dd'T'HH:mm:ss'Z')
        :param date_before:
            only return test executions before this date (format: yyyy-MM-dd'T'HH:mm:ss'Z')
        :param issue_links:
            include execution step issue links if True
        :param timeout_s:
            time to wait between retries
        :return:
            test executions as a data dictionary
        """
        url = self.base_url + "/testexecutions"

        payload = dict(
            projectKey=project_key,
            testCycle=testcycle_key,
            testCase=testcase_key,
            maxResults=1,
            startAt=0,
            actualEndDateAfter=date_after,
            actualEndDateBefore=date_before,
            includeStepLinks=issue_links,
            **kwargs,
        )
        try:
            data = self.get_request(url, payload)
        except exceptions.BadResponseError:
            raise exceptions.TestCycleNotFoundError(testcycle_key)

        total_executions = data["total"]
        payload = dict(
            projectKey=project_key,
            testCycle=testcycle_key,
            testCase=testcase_key,
            maxResults=total_executions,
            startAt=0,
            actualEndDateAfter=date_after,
            actualEndDateBefore=date_before,
            includeStepLinks=issue_links,
            **kwargs,
        )
        data = self.get_request(url, payload)

        if data is not None:
            test_execs = data["values"]
            # check if all test executions were returned, get rest otherwise
            if data["maxResults"] != total_executions:
                while data["next"] is not None:
                    data = self.get_request(data["next"])
                    test_execs.extend(data["values"])
                    time.sleep(timeout_s)
            return test_execs
        else:
            return None

    @filecache(seconds_of_validity=2 * WEEK)
    def _env_exists(self, env_name: str, project_key: str):
        envs = self.get_environments(project_key)
        return env_name in [x["name"] for x in envs]

    def post_test_execution(
        self,
        project_key: str,
        testcase_key: str,
        testcycle_key: str,
        status_name: TestVerdicts,
        env_name: str = None,
        exec_time: int = None,
        comment: str = None,
        *args,
        **kwargs,
    ):
        """
        Posts a test execution to a test cycle

        :param project_key:
            key of the project (e.g. BSBS)
        :param testcase_key:
            key of the testcase (e.g. BSBS-1)
        :param testcycle_key:
            key of the testcycle (e.g. BSBS-R1)
        :param status_name:
            test verdict (pass, fail or not executed)
        :param env_name:
            name of the test environment (e.g. HIL_automated) (optional)
        :param exec_time:
            execution time in seconds (optional)
        :param comment:
            comment for the test execution
            This is where we usually put the test results (optional)
        :return:
            id of the created test execution
        """
        url = self.base_url + "/testexecutions"

        if env_name is not None:
            if not self._env_exists(env_name, project_key):
                env_name = None

        payload = dict(
            projectKey=project_key,
            testCaseKey=testcase_key,
            testCycleKey=testcycle_key,
            statusName=status_name.value,
            environmentName=env_name,
            executionTime=exec_time,
            comment=comment,
        )

        resp = self.post_request(url, payload)
        return resp["id"]

    @filecache(seconds_of_validity=2 * WEEK)
    def _find_cycle_key(self, cycle_name: str, proj_key: str):
        cycles = self.get_all_testcycles(proj_key)
        cycle_key = None
        for cycle in cycles:
            if cycle["name"] == cycle_name:
                cycle_key = cycle["key"]
                break

        return cycle_key

    def upload_results(
        self,
        cycle_name: str,
        hw_ver: str,
        test_key: str,
        test_result: TestVerdicts,
        execution_time: int,
        log_path: str,
        comments: str,
        test_version: str = None,
        config_id: str = None,
        env_name: str = "HIL_automated",
    ):
        """
        Uploads test results to Zephyr Test Cloud.

        :param cycle_name:
            name of the test cycle (e.g. R12_2022XXX)
        :param config_id:
            config_id written in FEE (setup at runtine, we read it from redis)
        :param hw_ver:
            Hardware version of the DUT.
        :param test_key:
            key of the test. (e.g. BSBS-T1)
        :param test_result:
            Result of the test (PASS, FAIL, NOT EXECUTED).
        :param execution_time:
            Execution time of the test.
        :param log_path:
            Path to the test log.
        :param comments:
            Comments to be added to the test.
            This is where we usually put step descriptions and verdicts
        :param test_version:
            Test case version (hash) import from git 8 bytes (e.g. 3d588890).
        :param env_name:
            Name of the test environment.
        :return:
            True if the upload was successful, False otherwise.
        """
        proj_key = test_key.split("-")[0]
        # first check if test exists
        try:
            self.get_testcase(test_key)
        except exceptions.TestCaseNotFoundError:
            # Cannot upload to a non-existent test
            return False

        cycle_key = self._find_cycle_key(cycle_name, proj_key)

        if cycle_key is None:
            # Create new cycle
            if "HIL_" in env_name:  # HiL test cycles should be created in "SWRelease" folder
                folderIDForTestCycle = self.get_folder_id(
                    project_key=proj_key, folder_name="SWRelease", folder_type="TEST_CYCLE"
                )
            else:  # all others end up in root folder
                folderIDForTestCycle = None
            cycle_key, _ = self.create_testcycle(project_key=proj_key, name=cycle_name, folder_id=folderIDForTestCycle)

        if test_version is None:
            test_hash = "Not available"
        else:
            test_hash = test_version
        if config_id is None:
            configuration_id = "Not available"
        else:
            configuration_id = config_id

        # upload test execution
        description = (
            f"Test {test_result.name} on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. <br>"
            f"SW Version and Revision: {cycle_name} <br>"
            f"SW Config ID: {configuration_id} <br>"
            f"HW Version: {hw_ver} <br>"
            f"Test Version (git hash): {test_hash} <br>"
            f"Logs: {log_path} <br>"
            f"{comments}"
        )

        test_id = self.post_test_execution(
            proj_key, test_key, cycle_key, test_result, env_name, execution_time, description
        )

        if test_id is None or cycle_key is None:
            return None
        else:
            return cycle_key, test_id

    def update_testcase(
        self,
        key: str,
        name: str = None,
        id: int = None,
        project: dict = None,
        objective: str = None,
        precondition: str = None,
        est_time: int = None,
        labels: List[str] = None,
        priority: dict = None,
        status: object = None,
        **kwargs,
    ) -> bool:
        """
        Updates a Zephyr test case.

        :param key:
            Key of the test case.
        :param name:
            Name of the test case.
        :param id:
            ID of the test case.
        :param project:
            Project of the test case.
        :param objective:
            Objective of the test case.
        :param precondition:
            Precondition of the test case.
        :param est_time:
            Estimated time of the test case.
        :param labels:
            Labels of the test case.
        :param priority:
            Priority of the test case.
        :param status:
            Status of the test case.
        """

        def custom_field_formatter(value):
            """
            self.get_testcase may return empty custom fields which the zephyr API does not allow

            If we encounter an empty value thats not None, it needs to be explicitly set to None
            """
            if value == []:
                return None
            if value == "":
                return None

            return value

        url = self.base_url + f"/testcases/{key}"
        payload = self.get_testcase(key)

        if "customFields" in kwargs:
            custom_payload = kwargs.get("customFields", {})
        else:
            custom_payload = {}

        for k, v in payload.items():
            if k == "customFields":
                for key, val in v.items():
                    if key in custom_payload:
                        # already have this
                        continue
                    custom_payload[key] = custom_field_formatter(val)
                payload[k] = custom_payload
            if locals().get(k) is not None:
                payload[k] = locals().get(k)
            elif kwargs.get(k) is not None:
                payload[k] = kwargs.get(k)

        self.put_request(url, payload)

    def get_sorted_testexecutions_for_cycle(self, project_key: str, testcycle_key: str, *args, **kwargs):
        """
        Sorts test executions for a given test cycle by ActualEndDate
        :param project_key:
            Key of the zephyr project.
        :param testcycle_key:
            Key of the test cycle.
        :return:
            Test executions as a sorted data dictionary,
             in ascending order from oldest to most recent
        """
        test_executions = self.get_test_executions(project_key=project_key, testcycle_key=testcycle_key, **kwargs)
        sorted_executions = sorted(test_executions, key=lambda x: x["actualEndDate"], reverse=False)
        return sorted_executions


if __name__ == "__main__":
    with open("mytoken.txt", "r") as f:
        token = f.read()

    testmgmt = TestManagement(token)
    # room for some tests here
