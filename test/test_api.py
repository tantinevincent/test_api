import unittest
import requests
import urllib3
import xml.etree.ElementTree as et
from parameterized import parameterized
import random
import string
import ConfigParser

urllib3.disable_warnings() # disable insecure warnings

class BaseApiTester(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseApiTester, self).__init__(*args, **kwargs)

        # config loading
        config = ConfigParser.ConfigParser()
        config.read('./config.ini')
        self.api_address = config.get('server', 'api_address')
        user_id = config.get('server', 'user_id')
        password = config.get('server', 'password')

        login_url = "%s/login?user_id=%s&password=%s" % (self.api_address, user_id, password)

        self.session = requests.Session()
        try:
            response = self.session.get(login_url, verify=False)
        except requests.exceptions.RequestException:
            raise AssertionError("connection failed, please check api_address in config.ini")

        rc = self.to_return_code(response.content)
        if rc != 0:
            raise AssertionError("login failed, return code= %s" % rc)

        self.cookies = response.cookies

    def to_return_code(self, content):
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

    def generate_random_string(self, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length+1))

# test cases for shared folder
class SharedFolderTester(BaseApiTester):

    def create_shared_folder(self, name, nfs=False, smb=False, read_only=False, mode="sync"):
        url = "%s/create_shared_folder?name=%s&nfs=%s&smb=%s&mode=%s&read_only=%s" % (self.api_address, name, 
            str(nfs).lower(), str(smb).lower(), mode, str(read_only).lower())

        response = self.session.get(url, cookies=self.cookies)
        return response

    def delete_shared_folder(self, name):
        url = "%s/delete_shared_folder?name=%s" % (self.api_address ,name)
        response = self.session.get(url, cookies=self.cookies)
        return response

    def edit_shared_folder(self, name, nfs=False, smb=False, allow_hosts=None, read_only=None, mode="sync", nfs_allowed_hosts=None):
        url = "%s/edit_shared_folder" % (self.api_address)
        data = {"name": name, 
                "nfs": str(nfs).lower(), 
                "smb": str(smb).lower(),
                "mode":  mode, 
                "read_only": str(read_only).lower()}

        if nfs_allowed_hosts is not None:
            data["nfs_allowed_hosts"] = nfs_allowed_hosts

        response = self.session.post(url, cookies=self.cookies, data=data)
        return response

    def get_realtime_statistic(self):
        url = "%s/json/realtime_statistic?categories=protocol_accumulate&gateway_group=" % self.api_address
        response = self.session.get(url, cookies=self.cookies)
        return response
        
    @parameterized.expand([
        ["chars",            "abc",           0],
        ["digits",           "123",           0],
        ["digits and chars", "abc_1234",      0],
        ["with spaces",      "  cde_789",     0],
        ["less sign",        "<",           606],
        ["greater sign",     ">",           606],
        ["colon",            ":",           606],
        ["doube quotation",  "\"",          606],
        ["slash",            "/",           606],
        ["bakcslash",        "\\",          606],
        ["vertical bar",     "|",           606],
        ["question mark",    "?",           606],
        ["asterisk",         "*",           606],
    ])
    def test_create(self, param_name, name, return_code):
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name.strip())

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "create shared folder with name %s get wrong return code %s, not %s" % (name, rc, return_code))
    
    @parameterized.expand([
        ["254", 254,   0],
        ["255", 255, 606],
    ])
    def test_create_with_name_length(self, param_name, name_length, return_code):
        name = self.generate_random_string(name_length)
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "create shared folder with name length %s get wrong return code %s, not %s" % (name_length, rc, return_code))

    @parameterized.expand([
        ["same name",      "abcd", "abcd", 33],
        ["different name", "abcd", "1234",  0],
    ])
    def test_create_twice(self, param_name, first, second, return_code):
        self.create_shared_folder(first, nfs=True)
        response = self.create_shared_folder(second, nfs=True)
        self.delete_shared_folder(first)
        self.delete_shared_folder(second)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "after create %s, create folder %s get wrong return code %s, not %s" % (first, second, rc, return_code))
    
    @parameterized.expand([
        ["target exists",     "abcd", "abcd",  0],
        ["target non exitst", None,   "1234", 34],
    ])
    def test_delete(self, param_name, created, deleted, return_code):
        if created is not None:
            self.create_shared_folder(created, nfs=True)
        response = self.delete_shared_folder(deleted)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "after create %s, delete folder %s get wrong return code %s, not %s" % (created, deleted, rc, return_code))
    
    @parameterized.expand([
        ["true to true",   True,  True,  0],
        ["true to false",  True,  False, 0],
        ["false to false", False, False, 0],
        ["false to true",  False, True,  0],
    ])
    def test_edit_read_only_setting(self, param_name, on_created, on_edited, return_code):
        name = self.generate_random_string(10)
        self.create_shared_folder(name, nfs=True, read_only=on_created)
        response = self.edit_shared_folder(name, nfs=True, read_only=on_edited)
        self.delete_shared_folder(name)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "create with read_only=%s and edit to read_only=%s get wrong return code %s, not %s" % (on_created, on_edited, rc, return_code))

    def test_edit_read_only_settings_with_non_exists(self):
        name = self.generate_random_string(10)
        return_code = 34
        response = self.edit_shared_folder(name, nfs=True, read_only=True)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "edit read_only to non exists shared folder get wrong return code %s, not %s" % (rc, return_code))

    @parameterized.expand([
        ["true to true",   True,  True,  0],
        ["true to false",  True,  False, 0],
        ["false to false", False, False, 0],
        ["false to true",  False, True,  0],
    ])
    def test_edit_read_only_setting(self, param_name, on_created, on_edited, return_code):
        name = self.generate_random_string(10)
        self.create_shared_folder(name, nfs=True, read_only=on_created)
        response = self.edit_shared_folder(name, nfs=True, read_only=on_edited)
        self.delete_shared_folder(name)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "create with read_only=%s and edit to read_only=%s get wrong return code %s, not %s" % (on_created, on_edited, rc, return_code))

    def test_edit_read_only_settings_with_non_exists(self):
        name = self.generate_random_string(10)
        return_code = 34
        response = self.edit_shared_folder(name, nfs=True, read_only=True)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "edit read_only to non exists shared folder get wrong return code %s, not %s" % (rc, return_code))

    # nfs_allowed_hosts format is <host>:<is_root_squash>:<uid>:<gid> (no document)
    @parameterized.expand([
        ["ip",           "192.168.122.66:false::",      0],
        ["cidr",         "192.168.122.0/24:false::",    0],
        ["hostname",     "test-host:false::",           0],
        ["wrong ip",     "256.256.256.256:false::",     0],   # yes, definitely bug
    ])
    def test_add_allowed_hosts(self, param_name, nfs_allowed_hosts, return_code):
        name = self.generate_random_string(10)
        self.create_shared_folder(name, nfs=True)
        response = self.edit_shared_folder(name, nfs=True, nfs_allowed_hosts=nfs_allowed_hosts)
        self.delete_shared_folder(name)

        rc = self.to_return_code(response.content)
        self.assertEquals(rc, return_code, 
            "add allowed host %s get wrong return code %s, not %s" % (nfs_allowed_hosts, rc, return_code))

    def test_realtime_statistic_format(self):
        response = self.get_realtime_statistic()
        import json
        result = json.loads(response.content)

        # check return code
        if "return_code" not in result:
            raise AssertionError("return code is not exists, content= %s" % response.content)

        self.assertEquals(result["return_code"],  0)

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

if __name__ == '__main__':
    unittest.main()
