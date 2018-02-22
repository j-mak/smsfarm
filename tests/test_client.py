import unittest.mock

import smsfarm
import tests.helpers

from smsfarm.exceptions import NotSpecifiedError


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = smsfarm.Client("", "")

    def test_recipients_exception(self):
        with self.assertRaises(ValueError):
            self.client.recipients = 123

    def test_one_recipient_with_list(self):
        self.client.recipients = ["900123456"]
        self.assertEqual(self.client.recipients, "900123456")

    def test_multiple_recipients_with_list(self):
        self.client.recipients = ["900123456", '900654321']
        recipients = self.client.recipients
        self.assertEqual(recipients, "900123456,900654321")

    def test_one_recipient_with_string(self):
        self.client.recipients = "900123456"
        self.assertEqual(self.client.recipients, "900123456")

    def test_verify_if_set_properly(self):
        self.assertEqual(self.client.sender, tests.helpers.get_hostname())
        client = smsfarm.Client("", "", sender='smsfarm-sender')
        self.assertEqual(client.sender, "smsfarm-sender")

    # just for coverage completion
    @unittest.mock.patch('smsfarm.Client._Client__get_credit')
    def test_get_credit(self, mocked):
        mocked.return_value = 9.23
        self.assertEqual(self.client.get_credit(), 9.23)

    @unittest.mock.patch('smsfarm.Client._Client__send_message')
    def test_send_message(self, mocked):
        mocked.return_value = "2410290"
        self.assertEqual(self.client.send_message("hello world!"), '2410290')

    @unittest.mock.patch('smsfarm.Client._Client__get_all_message_statuses')
    def test_all_message_statuses(self, mocked):
        mocked.return_value = ['421900123456:MESSAGE-EXPIRED',
                               '421900654321:DELIVERED']
        resp = self.client.get_all_message_statuses('12312312')
        self.assertEqual(resp, {'421900654321': 'DELIVERED',
                                '421900123456': 'MESSAGE-EXPIRED'})

    def test_try_send_empty_message(self):
        with self.assertRaises(ValueError):
            self.client.send_message("")

    def test_get_message_status_with_multiple_recipients(self):
        self.client.recipients = ["421900123456", "421900654321"]
        with self.assertRaises(NotSpecifiedError):
            self.client.get_message_status("12345678")

    @unittest.mock.patch('smsfarm.Client._Client__get_message_status')
    def test_get_message_status_without_recipient(self, mocked_response):
        mocked_response.return_value = "DELIVERED"
        self.client.recipients = ["421900123456"]
        status = self.client.get_message_status("123456")
        self.assertEqual(status, "DELIVERED")

    @unittest.mock.patch('smsfarm.Client._Client__get_message_status')
    def test_get_message_status_with_recipient(self, mocked_response):
        mocked_response.return_value = "DELIVERED"
        status = self.client.get_message_status("123456", "421900123456")
        self.assertEqual(status, "DELIVERED")
