import unittest
import requests
import urllib3
import xml.etree.ElementTree as et
from parameterized import parameterized
import random
import string

urllib3.disable_warnings() # disable insecure warnings

class BaseApiTester(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseApiTester, self).__init__(*args, **kwargs)

        self.api_address = "https://192.168.122.77:8080/cgi-bin/ezs3"
        self.session = requests.Session()
        response = self.session.get(self.api_address + "/login?user_id=admin&password=password", verify=False)
        #self.assertTrue(self.is_query_success(response))
        self.cookies = response.cookies

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

    def edit_shared_folder(self, name, nfs=False, smb=False, allow_hosts=None, read_only=None, mode="sync", allowed_hosts=None):
        url = "%s/edit_shared_folder" % (self.api_address)
        data = {"name": name, 
                "nfs": str(nfs).lower(), 
                "smb": str(smb).lower(),
                "mode":  mode, 
                "read_only": str(read_only).lower()}

        if allowed_hosts is not None:
            data["allowed_hosts"] = allowed_hosts

        response = self.session.post(url, cookies=self.cookies, data=data)
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

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "create shared folder with name %s return code %s, not %s" % (name, rc_elm.text, return_code))
    
    @parameterized.expand([
        ["254", 254,   0],
        ["255", 255, 606],
    ])
    def test_create_with_name_length(self, param_name, name_length, return_code):
        name = self.generate_random_string(name_length)
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "create shared folder with name length %s return code %s, not %s" % (name_length, rc_elm.text, return_code))

    @parameterized.expand([
        ["same name",      "abcd", "abcd", 33],
        ["different name", "abcd", "1234",  0],
    ])
    def test_create_twice(self, param_name, first, second, return_code):
        self.create_shared_folder(first, nfs=True)
        response = self.create_shared_folder(second, nfs=True)
        self.delete_shared_folder(first)
        self.delete_shared_folder(second)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "after create %s, create folder %s return code %s, not %s" % (first, second, rc_elm.text, return_code))
    
    @parameterized.expand([
        ["target exists",     "abcd", "abcd",  0],
        ["target non exitst", None,   "1234", 34],
    ])
    def test_delete(self, param_name, created, deleted, return_code):
        if created is not None:
            self.create_shared_folder(created, nfs=True)

        response = self.delete_shared_folder(deleted)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "after create %s, delete folder %s return code %s, not %s" % (created, deleted, rc_elm.text, return_code))
    
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

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "create with read_only=%s and edit to read_only=%s return code %s, not %s" % (on_created, on_edited, rc_elm.text, return_code))

    def test_edit_read_only_settings_with_non_exists(self):
        name = self.generate_random_string(10)
        return_code = 34
        response = self.edit_shared_folder(name, nfs=True, read_only=True)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "edit read_only to non exists shared folder return code %s, not %s" % (rc_elm.text, return_code))

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

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "create with read_only=%s and edit to read_only=%s return code %s, not %s" % (on_created, on_edited, rc_elm.text, return_code))

    def test_edit_read_only_settings_with_non_exists(self):
        name = self.generate_random_string(10)
        return_code = 34
        response = self.edit_shared_folder(name, nfs=True, read_only=True)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "edit read_only to non exists shared folder return code %s, not %s" % (rc_elm.text, return_code))

    @parameterized.expand([
        ["empty", "",               0],
        ["ip",    "192.168.122.66", 0],
    ])
    def test_add_allowed_hosts(self, param_name, allowed_hosts, return_code):
        name = self.generate_random_string(10)
        self.create_shared_folder(name, nfs=True)
        response = self.edit_shared_folder(name, nfs=True, allowed_hosts=allowed_hosts)
        self.delete_shared_folder(name)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "add allowed host %s return code %s, not %s" % (allowed_hosts, rc_elm.text, return_code))


if __name__ == '__main__':
    unittest.main()
