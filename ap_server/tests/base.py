from flask_testing import TestCase

from base_api import app


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass