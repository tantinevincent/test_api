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
        url = "%s/create_shared_folder?name=%s&nfs=%s&smb=%s&mode=%s&read_only=%s" % (self.api_address ,name, nfs, smb, mode, read_only)
        response = self.session.get(url, cookies=self.cookies)
        return response

    def delete_shared_folder(self, name):
        url = "%s/delete_shared_folder?name=%s" % (self.api_address ,name)
        response = self.session.get(url, cookies=self.cookies)
        return response
    
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
        self.assertEquals(int(rc_elm.text), return_code, "create shared folder with name %s return code %s, not %s" % (name, rc_elm.text, return_code))
    
    @parameterized.expand([
        [254, 0],
        [255, 606]
    ])
    def test_create_with_name_length(self, name_length, return_code):
        name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(name_length+1))
        response = self.create_shared_folder(name, nfs=True)
        self.delete_shared_folder(name.strip())

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, "create shared folder with name length %s return code %s, not %s" % (name_length, rc_elm.text, return_code))

    @parameterized.expand([
        ["abcd", "abcd", 33],
        ["abcd", "1234", 0],
    ])
    def test_create_twice(self, first, second, return_code):
        self.create_shared_folder(first, nfs=True)
        response = self.create_shared_folder(second, nfs=True)
        self.delete_shared_folder(first.strip())
        self.delete_shared_folder(second.strip())

        root = et.fromstring(response.content)
        rc_elm = root.find("API_return/return_code")
        assert rc_elm is not None
        self.assertEquals(int(rc_elm.text), return_code, "after create %s, create fodler %s return code %s, not %s" % (first, second, rc_elm.text, return_code))

if __name__ == '__main__':
    unittest.main()
