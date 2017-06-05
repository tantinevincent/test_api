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

    def edit_shared_folder(self, name, nfs=False, smb=False, allow_hosts=None, read_only=None, mode="sync"):
        url = "%s/edit_shared_folder" % (self.api_address)
        data = {"name": name, 
                "nfs": str(nfs).lower(), 
                "smb": str(smb).lower(),
                "mode":  mode, 
                "read_only": str(read_only).lower()}

        response = self.session.post(url, cookies=self.cookies, data=data)
        return response

    def generate_random_string(self, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length+1))

    @parameterized.expand([
        ["abc", 0],
        ["123", 0],
        ["abc_1234", 0],
        ["  cde_789", 0],
        ["<", 606],
        [">", 606],
        [":", 606],
        ["\"", 606],
        ["/", 606],
        ["\\", 606],
        ["|", 606],
        ["?", 606],
        ["*", 606],
    ])
    def test_create(self, name, return_code):
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name.strip())

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "create shared folder with name %s return code %s, not %s" % (name, rc_elm.text, return_code))
    
    @parameterized.expand([
        [254, 0],
        [255, 606]
    ])
    def test_create_with_name_length(self, name_length, return_code):
        name = self.generate_random_string(name_length)
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "create shared folder with name length %s return code %s, not %s" % (name_length, rc_elm.text, return_code))

    @parameterized.expand([
        ["abcd", "abcd", 33],
        ["abcd", "1234", 0],
    ])
    def test_create_twice(self, first, second, return_code):
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
        ["abcd", "abcd", 0],
        [None, "1234", 34],
    ])
    def test_delete(self, created, deleted, return_code):
        if created is not None:
            self.create_shared_folder(created, nfs=True)

        response = self.delete_shared_folder(deleted)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, 
            "after create %s, delete folder %s return code %s, not %s" % (created, deleted, rc_elm.text, return_code))
    
    @parameterized.expand([
        [True, True, 0],
        [True, False, 0],
        [False, False, 0],
        [False, True, 0],
    ])
    def test_edit_read_only_setting(self, on_created, on_edited, return_code):
        name = self.generate_random_string(10)
        self.create_shared_folder(name, nfs=True, read_only=on_created)
        response = self.edit_shared_folder(name, nfs=True, read_only=on_edited)
        self.delete_shared_folder(name)

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        self.assertEquals(int(rc_elm.text), return_code, 
            "create with read_only=%s and edit to read_only=%s return code %s, not %s" % (on_created, on_edited, rc_elm.text, return_code))

if __name__ == '__main__':
    unittest.main()
