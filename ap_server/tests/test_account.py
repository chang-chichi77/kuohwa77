import unittest

import json
from tests.base import BaseTestCase
from utils.orcl_utils import OracleAccess

def login_user(self):
    return self.client.post(
        '/api/account/login',
        data=json.dumps(dict(
            username='tami',
            passwd='tami'
        )),
        content_type='application/json'
    )


class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = login_user(self)
            data = json.loads(response.data)
            self.assertTrue(data['result'] == 0)
            self.assertTrue(data['data'] == '登入成功')
            self.assertTrue(data['test'] == '123')
            self.assertEqual(response.status_code, 200)