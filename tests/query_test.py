import unittest
import sys
sys.path.append('..')

class QueryTestCase(unittest.TestCase):

    def testImport(self):
        import query
        query_string = '{{#ask: [[Category::Disease]] [[Summary::+]] | ?Summary }}'
        opts = {"limit":5, "format":"csv"}
        q = query.Query(query_string, opts)
        print q.query
        result = q.execute();
        for result_row in result:
            print result_row

        # fail("InvalidKeyException not raised for invalid key")

if __name__ == '__main__':
    unittest.main()
