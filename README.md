# test_api

## How to use

1. install python 2.7 and pip
2. execute `pip install -r requirements.txt` to install python packages
3. edit api_address, user_id, password in config.ini for testing
4. execute `./run_all_test.sh`

## Sreenshot
```
(env)vincent@vincent-home:~/test_api$ ./run_all_test.sh 
test_add_allowed_hosts_0_ip (test.test_api.SharedFolderTester) ... ok
test_add_allowed_hosts_1_cidr (test.test_api.SharedFolderTester) ... ok
test_add_allowed_hosts_2_hostname (test.test_api.SharedFolderTester) ... ok
test_add_allowed_hosts_3_wrong_ip (test.test_api.SharedFolderTester) ... ok
test_create_0_chars (test.test_api.SharedFolderTester) ... ok
test_create_10_vertical_bar (test.test_api.SharedFolderTester) ... ok
test_create_11_question_mark (test.test_api.SharedFolderTester) ... ok
test_create_12_asterisk (test.test_api.SharedFolderTester) ... ok
test_create_1_digits (test.test_api.SharedFolderTester) ... ok
test_create_2_digits_and_chars (test.test_api.SharedFolderTester) ... ok
test_create_3_with_spaces (test.test_api.SharedFolderTester) ... ok
test_create_4_less_sign (test.test_api.SharedFolderTester) ... ok
test_create_5_greater_sign (test.test_api.SharedFolderTester) ... ok
test_create_6_colon (test.test_api.SharedFolderTester) ... ok
test_create_7_doube_quotation (test.test_api.SharedFolderTester) ... ok
test_create_8_slash (test.test_api.SharedFolderTester) ... ok
test_create_9_bakcslash (test.test_api.SharedFolderTester) ... ok
test_create_twice_0_same_name (test.test_api.SharedFolderTester) ... ok
test_create_twice_1_different_name (test.test_api.SharedFolderTester) ... ok
test_create_with_name_length_0_254 (test.test_api.SharedFolderTester) ... ok
test_create_with_name_length_1_255 (test.test_api.SharedFolderTester) ... ok
test_delete_0_target_exists (test.test_api.SharedFolderTester) ... ok
test_delete_1_target_non_exitst (test.test_api.SharedFolderTester) ... ok
test_edit_read_only_setting_0_true_to_true (test.test_api.SharedFolderTester) ... ok
test_edit_read_only_setting_1_true_to_false (test.test_api.SharedFolderTester) ... ok
test_edit_read_only_setting_2_false_to_false (test.test_api.SharedFolderTester) ... ok
test_edit_read_only_setting_3_false_to_true (test.test_api.SharedFolderTester) ... ok
test_edit_read_only_settings_with_non_exists (test.test_api.SharedFolderTester) ... ok

----------------------------------------------------------------------
Ran 28 tests in 78.810s

OK
```

## Run single testing

- just execute `python -m unittest test.test_api.SharedFolderTester.<test_case_name>`
- for example:

```
(env)vincent@vincent-home:~/test_api$ python -m unittest test.test_api.SharedFolderTester.test_delete_0_target_exists
.
----------------------------------------------------------------------
Ran 1 test in 2.893s

OK
```
