def run():
    import unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='*_test.py')
    return test_suite
