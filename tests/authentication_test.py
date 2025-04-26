"""
UNIT TEST file for
- Encryption
- Authentication
"""

import unittest
import os

from src.auth_provider import AuthProvider
from src.db_provider import DatabaseProvider
from src.encryption_provider import EncryptionProvider

from typing import cast

USERNAME_TOO_LONG_RESPONSE ={ 
    'success': False,
    'message': "Username too long",
    'httpStatus': 400
}
USERNAME_INVALID_RESPONSE = {
                    'success': False,
                    'message': "Username can only contain letters, numbers, and underscores.",
                    'httpStatus': 400
                }
USERNAME_TOO_SHORT_RESPONSE = {
                    'success': False,
                    'message': "Username must be atleast 4 characters",
                    'httpStatus': 400
                }
PASSWORD_TOO_SHORT_RESPONSE = {
                    'success': False,
                    'message': "Password must be atleast 6 characters",
                    'httpStatus': 400
                }
USERNAME_IN_USE_RESPONSE = {
                    'success': False,
                    'message': "Username in use",
                    "httpStatus": 409
                }
REGISTER_OK_RESPONSE = {
                'success': True,
                'message': "OK",
                'httpStatus': 200
            }

LOGIN_ERROR_RESPONSE = {
                    'success': False,
                    'message': "Invalid credentials",
                    'httpStatus': 401
                }
LOGIN_OK_RESPONSE = {
                'success': True,
                'message': "OK",
                'httpStatus': 200
            }
class TestAuthentication(unittest.TestCase):

    authProvider: AuthProvider
    dbProvider: DatabaseProvider

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database provider and auth provider once for all tests"""
        print(f"Setting up the database provider and auth provider for all tests")
        cls.dbProvider = DatabaseProvider(db_path="tmp/unittest.db")
        cls.authProvider = AuthProvider(cls.dbProvider)

    @classmethod
    def tearDownClass(cls) -> None:
        """Cleanup the db provider after all tests"""
        print(f"Tearing down the database provider")
        cls.dbProvider.close()
        os.remove("tmp/unittest.db")

    def test_01_register(self) -> None:
        print(f"#######################################")
        print(f"TEST 01 --- REGISTER NEW USER")
        print(f"#######################################")
        self.assertEqual(self.authProvider.register("u", "abcdefg", 'a', False), USERNAME_TOO_SHORT_RESPONSE, "Username length restriction test failed!")
        self.assertEqual(self.authProvider.register("u$$$$", 'abcdefg', 'a', False), USERNAME_INVALID_RESPONSE, "Username character restriction test failed")
        self.assertEqual(self.authProvider.register("abcdefh", "a", 'a', False), PASSWORD_TOO_SHORT_RESPONSE, "Password length restriction test failed")
        self.assertEqual(self.authProvider.register("unittest", "unittest", 'a', False), REGISTER_OK_RESPONSE, "Account registration test failed")
    
    def test_02_login(self) -> None:
        print(f"#######################################")
        print(f"TEST 02 --- LOGIN")
        print(f"#######################################")
        o = self.authProvider.auth("unittest", "dadas", False)[0]
        self.assertEqual(o, LOGIN_ERROR_RESPONSE, "Credentials check test failed!")
        o2 = self.authProvider.auth("unittest", "unittest", True)[0]
        self.assertEqual(o2['success'], True, f"Message (if any): {o2['message']}")
        print(f"Auth result: {o2}")
        token = o2.get("data")
        self.assertNotEqual(token, None, "Token check test failed")
        
    def test_03_encryption(self) -> None:
        print(f"#######################################")
        print(f"TEST 03 --- ENCRYPTION")
        print(f"#######################################")
        self.encryptionProvider = EncryptionProvider(self.dbProvider)

        result = self.encryptionProvider.encrypt([1], "Hi", "unittest", {
            "exp": 99999999999999999,
            "id": 1,
            "username": "unittest"
        })

        decrypted = self.encryptionProvider.decrypt(result['data']['signature'], result['data']['body'], result['data']['iv'], cast(dict[str, str], result['data']['keys']), { # stfu myypy
            "exp": 99999999999999999,
            "id": 1,
            "username": "unittest"  
        }, 'unittest', 1)
        self.assertNotEqual(decrypted, 'Hi', "Decryption test failed")




def run_tests() -> None:
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuthentication)
    unittest.TextTestRunner(verbosity=3).run(suite)