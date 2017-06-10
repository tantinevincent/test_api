#import unittest
import requests
import urllib3
import xml.etree.ElementTree as et
from parameterized import parameterized
import random
import string
import ConfigParser
import pytest

urllib3.disable_warnings() # disable insecure warnings

session = None
cookies = None
api_address = None

def to_return_code(content):
    root = None
    # check content is xml
    try:
        root = et.fromstring(content)
    except et.ParseError:
        raise AssertionError("response content should be xml, content= %s" % content)

    # check content contains return code
    rc_element = root.find("API_return/return_code")
    if rc_element is None:
        raise AssertionError("return code is not exists, content= %s" % content)

    return int(rc_element.text)

def init():
    global session
    global cookies
    global api_address

    if session is not None and cookies is not None and api_address is not None:
        print "cached"
        return (api_address, session, cookies)
        
    # config loading
    config = ConfigParser.ConfigParser()
    config.read('./config.ini')
    api_address = config.get('server', 'api_address')
    user_id = config.get('server', 'user_id')
    password = config.get('server', 'password')

    login_url = "%s/login?user_id=%s&password=%s" % (api_address, user_id, password)

    session = requests.Session()
    try:
        response = session.get(login_url, verify=False)
    except requests.exceptions.RequestException:
        raise AssertionError("connection failed, please check api_address in config.ini")

    rc = to_return_code(response.content)
    if rc != 0:
        raise AssertionError("login failed, return code= %s" % rc)

    cookies = response.cookies
    return (api_address, session, cookies)

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length+1))

def create_shared_folder(name, nfs=False, smb=False, read_only=False, mode="sync"):
    api_address, session, cookies = init()
    url = "%s/create_shared_folder?name=%s&nfs=%s&smb=%s&mode=%s&read_only=%s" % (api_address, name, 
        str(nfs).lower(), str(smb).lower(), mode, str(read_only).lower())

    response = session.get(url, cookies=cookies)
    return response

def delete_shared_folder(name):
    api_address, session, cookies = init()
    url = "%s/delete_shared_folder?name=%s" % (api_address, name)
    response = session.get(url, cookies=cookies)
    return response

def edit_shared_folder(name, nfs=False, smb=False, allow_hosts=None, read_only=None, mode="sync", nfs_allowed_hosts=None):
    api_address, session, cookies = init()
    url = "%s/edit_shared_folder" % api_address
    data = {"name": name, 
            "nfs": str(nfs).lower(), 
            "smb": str(smb).lower(),
            "mode":  mode, 
            "read_only": str(read_only).lower()}

    if nfs_allowed_hosts is not None:
        data["nfs_allowed_hosts"] = nfs_allowed_hosts

    response = session.post(url, cookies=cookies, data=data)
    return response

def get_realtime_statistic():
    api_address, session, cookies = init()
    url = "%s/json/realtime_statistic?categories=protocol_accumulate&gateway_group=" % api_address
    response = session.get(url, cookies=cookies)
    return response
        
@pytest.mark.parametrize("param_name, name, return_code", [
    ("chars",            "abc",           0),
    ("digits",           "123",           0),
    ("digits and chars", "abc_1234",      0),
    ("with spaces",      "  cde_789",     0),
    ("less sign",        "<",           606),
    ("greater sign",     ">",           606),
    ("colon",            ":",           606),
    ("doube quotation",  "\"",          606),
    ("slash",            "/",           606),
    ("bakcslash",        "\\",          606),
    ("vertical bar",     "|",           606),
    ("question mark",    "?",           606),
    ("asterisk",         "*",           606),
])
def test_create(param_name, name, return_code):
    response = create_shared_folder(name, nfs=True)
    delete_shared_folder(name.strip())

    rc = to_return_code(response.content)
    msg = "create shared folder with name %s get wrong return code %s, not %s" % (name, rc, return_code)
    assert rc == return_code, msg 

@pytest.mark.parametrize("param_name, name_length, return_code", [
    ("254", 254,   0),
    ("255", 255, 606),
])
def test_create_with_name_length(param_name, name_length, return_code):
    name = generate_random_string(name_length)
    response = create_shared_folder(name, nfs=True)
    delete_shared_folder(name)

    rc = to_return_code(response.content)
    msg = "create shared folder with name length %s get wrong return code %s, not %s" % (name_length, rc, return_code)
    assert rc == return_code, msg


@pytest.mark.parametrize("param_name, first, second, return_code", [
        ("same name",      "abcd", "abcd", 33),
        ("different name", "abcd", "1234",  0),
    ])
def test_create_twice(param_name, first, second, return_code):
    create_shared_folder(first, nfs=True)
    response = create_shared_folder(second, nfs=True)
    delete_shared_folder(first)
    delete_shared_folder(second)

    rc = to_return_code(response.content)
    msg = "after create %s, create folder %s get wrong return code %s, not %s" % (first, second, rc, return_code)
    assert rc == return_code, msg
    
@pytest.mark.parametrize("param_name, created, deleted, return_code", [
    ("target exists",     "abcd", "abcd",  0),
    ("target non exitst", None,   "1234", 34),
])
def test_delete(param_name, created, deleted, return_code):
    if created is not None:
        create_shared_folder(created, nfs=True)

    response = delete_shared_folder(deleted)

    rc = to_return_code(response.content)
    msg = "after create %s, delete folder %s get wrong return code %s, not %s" % (created, deleted, rc, return_code)
    assert rc == return_code, msg

@pytest.mark.parametrize("param_name, on_created, on_edited, return_code", [
    ["true to true",   True,  True,  0],
    ["true to false",  True,  False, 0],
    ["false to false", False, False, 0],
    ["false to true",  False, True,  0],
])
def test_edit_read_only_setting(param_name, on_created, on_edited, return_code):
    name = generate_random_string(10)
    create_shared_folder(name, nfs=True, read_only=on_created)
    response = edit_shared_folder(name, nfs=True, read_only=on_edited)
    print response
    delete_shared_folder(name)

    rc = to_return_code(response.content)
    msg = "create with read_only=%s and edit to read_only=%s get wrong return code %s, not %s" % (on_created, on_edited, rc, return_code)
    assert rc == return_code, msg

def test_edit_read_only_settings_with_non_exists():
    name = generate_random_string(10)
    return_code = 34
    response = edit_shared_folder(name, nfs=True, read_only=True)

    rc = to_return_code(response.content)
    msg = "edit read_only to non exists shared folder get wrong return code %s, not %s" % (rc, return_code)
    assert rc == return_code, msg

# nfs_allowed_hosts format is <host>:<is_root_squash>:<uid>:<gid> (no document)
@pytest.mark.parametrize("param_name, nfs_allowed_hosts, return_code", [
    ("ip",           "192.168.122.66:false::",      0),
    ("cidr",         "192.168.122.0/24:false::",    0),
    ("hostname",     "test-host:false::",           0),
    ("wrong ip",     "256.256.256.256:false::",     0),   # yes, definitely bug
])
def test_add_allowed_hosts(param_name, nfs_allowed_hosts, return_code):
    name = generate_random_string(10)
    create_shared_folder(name, nfs=True)
    response = edit_shared_folder(name, nfs=True, nfs_allowed_hosts=nfs_allowed_hosts)
    delete_shared_folder(name)

    rc = to_return_code(response.content)
    msg = "add allowed host %s get wrong return code %s, not %s" % (nfs_allowed_hosts, rc, return_code)
    assert rc == return_code, msg

def test_realtime_statistic_format():
    response = get_realtime_statistic()
    import json
    result = json.loads(response.content)

    # check return code
    if "return_code" not in result:
        raise AssertionError("return code is not exists, content= %s" % response.content)

    assert result["return_code"] == 0, "return code is not zero"

    # check format
    if "response" not in result:
        raise AssertionError("response is not exists, content= %s" % response.content)

    if "protocol_accumulate" not in result["response"]:
        raise AssertionError("response/protocol_accumulate is not exists, content= %s" % response.content)

    if "Default" not in result["response"]["protocol_accumulate"]:
        raise AssertionError("response/protocol_accumulate/Default is not exists, content= %s" % response.content)

    for key in ["nfs_write_ops", "nfs_write_time", "nfs_read_time", "nfs_read_ops", "nfs_read_bytes", "nfs_write_bytes"]:
        if key not in result["response"]["protocol_accumulate"]["Default"]:
            msg = "response/protocol_accumulate/%s is not exists, content= %s" % (key, response.content)
            raise AssertionError(msg)
