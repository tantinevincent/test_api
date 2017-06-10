# test_api

## How to use

1. install python 2.7 and pip
2. execute `pip install -r requirements.txt` to install python packages
3. edit api_address, user_id, password in config.ini for testing
4. execute `pytest --verbose test/`

## Screenshot

```
(env)vincent@vincent-home:~/test_api$ pytest --verbose test/
============================= test session starts ==============================
platform linux2 -- Python 2.7.6, pytest-3.1.2, py-1.4.34, pluggy-0.4.0 -- /home/vincent/test_api/env/bin/python
cachedir: .cache
rootdir: /home/vincent/test_api, inifile:
collected 29 items 

test/test_api.py::test_create[chars-abc-0] PASSED
test/test_api.py::test_create[digits-123-0] PASSED
test/test_api.py::test_create[digits and chars-abc_1234-0] PASSED
test/test_api.py::test_create[with spaces-  cde_789-0] PASSED
test/test_api.py::test_create[less sign-<-606] PASSED
test/test_api.py::test_create[greater sign->-606] PASSED
test/test_api.py::test_create[colon-:-606] PASSED
test/test_api.py::test_create[doube quotation-"-606] PASSED
test/test_api.py::test_create[slash-/-606] PASSED
test/test_api.py::test_create[bakcslash-\-606] PASSED
test/test_api.py::test_create[vertical bar-|-606] PASSED
test/test_api.py::test_create[question mark-?-606] PASSED
test/test_api.py::test_create[asterisk-*-606] PASSED
test/test_api.py::test_create_with_name_length[254-254-0] PASSED
test/test_api.py::test_create_with_name_length[255-255-606] PASSED
test/test_api.py::test_create_twice[same name-abcd-abcd-33] PASSED
test/test_api.py::test_create_twice[different name-abcd-1234-0] PASSED
test/test_api.py::test_delete[target exists-abcd-abcd-0] PASSED
test/test_api.py::test_delete[target non exitst-None-1234-34] PASSED
test/test_api.py::test_edit_read_only_setting[true to true-True-True-0] PASSED
test/test_api.py::test_edit_read_only_setting[true to false-True-False-0] PASSED
test/test_api.py::test_edit_read_only_setting[false to false-False-False-0] PASSED
test/test_api.py::test_edit_read_only_setting[false to true-False-True-0] PASSED
test/test_api.py::test_edit_read_only_settings_with_non_exists PASSED
test/test_api.py::test_add_allowed_hosts[ip-192.168.122.66:false::-0] PASSED
test/test_api.py::test_add_allowed_hosts[cidr-192.168.122.0/24:false::-0] PASSED
test/test_api.py::test_add_allowed_hosts[hostname-test-host:false::-0] PASSED
test/test_api.py::test_add_allowed_hosts[wrong ip-256.256.256.256:false::-0] PASSED
test/test_api.py::test_realtime_statistic_format PASSED

============================ 29 passed in 89.29 seconds =============================
```

## Run single testcase

```
(env)vincent@vincent-home:~/test_api$ pytest --verbose test/test_api.py::test_create[chars-abc-0]
================================ test session starts ================================
platform linux2 -- Python 2.7.6, pytest-3.1.2, py-1.4.34, pluggy-0.4.0 -- /home/vincent/test_api/env/bin/python
cachedir: .cache
rootdir: /home/vincent/test_api, inifile:
collected 30 items 

test/test_api.py::test_create[chars-abc-0] PASSED

============================= 1 passed in 4.06 seconds ==============================

```

## Run specific testcase set

```
(env)vincent@vincent-home:~/test_api$ pytest --verbose test/test_api.py::test_create_with_name_length
================================ test session starts ================================
platform linux2 -- Python 2.7.6, pytest-3.1.2, py-1.4.34, pluggy-0.4.0 -- /home/vincent/test_api/env/bin/python
cachedir: .cache
rootdir: /home/vincent/test_api, inifile:
collected 31 items 

test/test_api.py::test_create_with_name_length[254-254-0] PASSED
test/test_api.py::test_create_with_name_length[255-255-606] PASSED

============================= 2 passed in 5.78 seconds ==============================
```
