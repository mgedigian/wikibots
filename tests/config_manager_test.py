import unittest
import sys
sys.path.append('..')

class ConfigManagerTestCase(unittest.TestCase):

    def testImport(self):
        import config_manager
        config = config_manager.load()

    def testGet(self):
        import config_manager
        config = config_manager.load()
        config.get("editor_encoding");

    def testGetBad(self):
        import config_manager
        config = config_manager.load()
        try:
            config.get("editor_encoding_BLAH");
        except config_manager.InvalidKeyException:
            pass
        else:
            fail("InvalidKeyException not raised for invalid key")

if __name__ == '__main__':
    unittest.main()
