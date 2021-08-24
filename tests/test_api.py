import os
import sys
import shutil
import tempfile
import time

import requests
from pandas import DataFrame

from classifier import TestService

sys.path.append("./")
from deploy import deploy
from describe import describe
from delete import delete


class Setup:
    def __init__(self):
        """
        Setup the deployment on the deployment choosen
        """
        self.deployment_name = "ec2_bento_deploy_test"
        self.dirpath = tempfile.mkdtemp()
        print("temp dir {} created!".format(self.dirpath))
        self.saved_dir = os.path.join(self.dirpath, "saved_dir")

        # make config file
        config = """
        {
          "region": "us-west-1",
          "ec2_auto_scale": {
            "min_size": 1,
            "desired_capacity": 1,
            "max_size": 1
          },
          "instance_type": "t2.micro",
          "ami_id": "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2",
          "elb": {
            "health_check_interval_seconds": 5,
            "health_check_path": "/healthz",
            "health_check_port": 5000,
            "health_check_timeout_seconds": 3,
            "healthy_threshold_count": 2
          }
        }
        """
        self.config_file = os.path.join(self.dirpath, "config.json")
        with open(self.config_file, "w") as f:
            f.write(config)

        # make bento service
        os.mkdir(self.saved_dir)
        test_service = TestService()
        # test_service.pack()
        test_service.save_to_dir(self.saved_dir)

    def make_deployment(self):
        deploy(self.saved_dir, self.deployment_name, self.config_file)
        info_json = describe(self.deployment_name, self.config_file)
        url = info_json["Url"] + "/{}"

        # ping /healthz to check if deployment is up
        attempt = 0
        print('Checking is service is up...', end='')
        url_healthz = url.format('healthz')
        while attempt < 5:
            try:
                if requests.get(url_healthz).ok:
                    print('Ok!')
                    break
                else:
                    time.sleep(20)
            except Exception:
                time.sleep(20)
            finally:
                attempt += 1

        return url

    def teardown(self):
        delete(self.deployment_name, self.config_file)
        shutil.rmtree(self.dirpath)
        print("Removed {}!".format(self.dirpath))


def test_json(url):
    """
    GIVEN the api is deployed
    WHEN a valid json is given
    THEN accepts the binary_data and returns it
    """
    headers = {"content-type": "application/json"}
    input_json = "[[1, 2, 3, 4]]"
    resp = requests.post(url, data=input_json, headers=headers)
    assert resp.ok
    assert resp.content == bytearray(input_json, "ascii")


def test_df(url):
    """
    GIVEN the api is deployed
    WHEN a dataframe is passed, as json or csv
    THEN accepts the binary_data and returns it
    """
    input_array = [[1, 2, 3, 4]]

    # request as json
    resp = requests.post(url, json=input_array)
    assert resp.ok
    assert DataFrame(resp.json()).to_json() == DataFrame(input_array).to_json()

    # request as csv
    headers = {"content-type": "text/csv"}
    csv = DataFrame(input_array).to_csv(index=False)
    resp = requests.post(url.format("dfapi"), data=csv, headers=headers)
    assert resp.ok
    assert DataFrame(resp.json()).to_json() == DataFrame(input_array).to_json()


def test_files(url):
    """
    GIVEN the api is deployed
    WHEN a file is passed either as raw bytes with any content-type or as mulitpart/form
    THEN it accepts the binary_data and returns it
    """
    binary_data = b"test"

    # request with raw data
    headers = {"content-type": "image/jpeg"}
    resp = requests.post(url, data=binary_data, headers=headers)
    assert resp.ok
    assert resp.content == b'"test"'

    # request mulitpart/form-data
    file = {"audio": ("test", binary_data)}
    resp = requests.post(url.format("fileapi"), files=file)
    assert resp.ok
    assert resp.content == b'"test"'


if __name__ == "__main__":

    setup = Setup()
    failed = False
    try:
        url = setup.make_deployment()
        print(url)
    except Exception as e:
        print("Setup failed")
        raise e
    else:
        # setup successful!
        print("Setup successful")

        # list of tests to perform
        TESTS = [(test_json, "jsonapi"), (test_df, "dfapi"), (test_files, "fileapi")]

        for test_func, endpoint in TESTS:
            try:
                print("Testing endpoint /{}...".format(endpoint), end="")
                test_func(url.format(endpoint))
                print("\033[92m passed! \033[0m")
            except Exception as e:
                print("\033[91m failed! \033[0m")
                print("\nTest at endpoint /{} failded: ".format(endpoint), e)
                failed = True
    finally:
        setup.teardown()

    if failed:
        sys.exit(1)
    else:
        sys.exit(0)
