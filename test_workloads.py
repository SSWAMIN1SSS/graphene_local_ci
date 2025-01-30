#!/usr/bin/env python3
import sys
import logging
import glob
from os import path
import os
import pytest
import re

sgx_mode = os.environ.get('SGX')
no_cores = os.environ.get('no_cpu', '8')
os_version = os.environ.get('os_version')
base_os = os.environ.get('base_os')
os_release_id = os.environ.get('os_release_id')
node_label = os.environ.get('node_label')
edmm_mode = os.environ.get('EDMM')
distro_ver = os.environ.get('distro_ver')
ra_type = os.environ.get("RA_TYPE", "none")

class Test_Workload_Results():
    @pytest.mark.examples
    @pytest.mark.skipif((os_release_id not in ["ubuntu","rhel","centos"]) or
                       not(int(no_cores) > 16), reason="Run only on Ubuntu/RHEL/CentOS Server machines")
    def test_mysql_workload(self):
        mysql_result = open("CI-Examples/mysql/CREATE_RESULT", "r")
        mysql_contents = mysql_result.read()
        assert("Creating table 'sbtest2'..." in mysql_contents)
        assert("Creating table 'sbtest1'..." in mysql_contents)
        assert("Inserting 100000 records into 'sbtest2'" in mysql_contents)
        assert("Inserting 100000 records into 'sbtest1'" in mysql_contents)
        assert("error: " not in mysql_contents)
        mysql_result = open("CI-Examples/mysql/RUN_RESULT", "r")
        mysql_contents = mysql_result.read()
        assert("Threads fairness:" in mysql_contents)
        assert("error: " not in mysql_contents)
        mysql_result = open("CI-Examples/mysql/DELETE_RESULT", "r")
        mysql_contents = mysql_result.read()
        assert("Dropping table 'sbtest1'..." in mysql_contents)
        assert("Dropping table 'sbtest2'..." in mysql_contents)
        assert("error: " not in mysql_contents)

    @pytest.mark.examples
    @pytest.mark.skipif(not(int(no_cores) > 16), reason="Run only on servers")
    def test_mariadb_workload(self):
        # NOT is added in the skip condition to improve readability
        # Test Sequence - Spawn mariadb server in background, run mariadb client, print SUCCESS if successfully launched
        # Check if the string "SUCCESS" is present in and client_output which generated after running the Makefile
        assert "SUCCESS" in open("CI-Examples/mariadb/client_output", "r").read()
