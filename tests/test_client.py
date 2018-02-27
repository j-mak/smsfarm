import unittest.mock

import smsfarm
import smsfarm.core
import tests.helpers


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = smsfarm.Client("some-code", "some-id")

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
        client = smsfarm.Client("some-code", "some-id", sender='smsfarm-sender')
        self.assertEqual(client.sender, "smsfarm-sender")

    # just for coverage completion
    @unittest.mock.patch('smsfarm.Client._Client__get_credit')
    def test_get_credit(self, mocked):
        mocked.return_value = smsfarm.ApiResponse()
        mocked.return_value.data = 9.23
        response = self.client.get_credit()
        self.assertEqual(response.data, 9.23)

    @unittest.mock.patch('smsfarm.Client._Client__send_message')
    def test_send_message(self, mocked):
        mocked.return_value = smsfarm.ApiResponse()
        mocked.return_value.data = 2410290
        self.client.recipients = "900123456"

        response = self.client.send_message("hello world!")
        self.assertEqual(response.data, '2410290')

    @unittest.mock.patch('smsfarm.Client._Client__get_all_message_statuses')
    def test_all_message_statuses(self, mocked):
        mocked.return_value = smsfarm.ApiResponse()
        mocked.return_value.data = ['421900123456:MESSAGE-EXPIRED',
                                    '421900654321:DELIVERED']
        resp = self.client.get_all_message_statuses('12312312')
        self.assertEqual(resp.data, {'421900654321': 'DELIVERED',
                                     '421900123456': 'MESSAGE-EXPIRED'})
        self.assertEqual(resp.success, True)
        self.assertEqual(resp.failed, False)

    def test_try_send_empty_message(self):
        with self.assertRaises(ValueError):
            self.client.send_message("")

    def test_get_message_status_with_multiple_recipients(self):
        self.client.recipients = ["421900123456", "421900654321"]
        with self.assertRaises(ValueError):
            self.client.get_message_status("12345678")

    @unittest.mock.patch('smsfarm.Client._Client__get_message_status')
    def test_get_message_status_without_recipient(self, mocked_response):
        mocked_response.return_value = smsfarm.ApiResponse()
        mocked_response.return_value.data = "DELIVERED"
        self.client.recipients = ["421900123456"]
        response = self.client.get_message_status("123456")
        self.assertEqual(response.data, "DELIVERED")

    @unittest.mock.patch('smsfarm.Client._Client__get_message_status')
    def test_get_message_status_with_recipient(self, mocked_response):
        mocked_response.return_value = smsfarm.ApiResponse()
        mocked_response.return_value.data = "DELIVERED"
        response = self.client.get_message_status("123456", "421900123456")
        self.assertEqual(response.data, "DELIVERED")

    @unittest.mock.patch('smsfarm.Client._Client__send_scheduled_message')
    def test_send_scheduled_message(self, mocked_response):
        mocked_response.return_value = smsfarm.ApiResponse()
        mocked_response.return_value.data = 2410290
        self.client.recipients = "900123456"

        send_date = '2018-01-01 00:00'
        response = self.client.send_scheduled_message("Hello World!", send_date)
        self.assertEqual(response.data, "2410290")

    def test_send_scheduled_message_with_invalid_time(self):
        self.client.recipients = "900123456"
        with self.assertRaises(ValueError):
            msg = "Hello World!"
            self.client.send_scheduled_message(msg, "2018-12-0 25:00")

    @unittest.mock.patch('smsfarm.Client._Client__send_message')
    def test_failed_send_message(self, mocked_response):
        mocked_response.return_value = smsfarm.ApiResponse()
        mocked_response.return_value.error = 'SomeSOAPError'
        self.client.recipients = "900123456"

        response = self.client.send_message("Hello World!")

        self.assertEqual(response.error, "SomeSOAPError")
        self.assertFalse(response.success)
        self.assertTrue(response.failed)
