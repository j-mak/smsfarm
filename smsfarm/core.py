import datetime
import hashlib
import os

import zeep
import zeep.exceptions

WSDL_URL = "http://app.smsfarm.sk/api/?wsdl"


class ApiResponse(object):
    """
    Representation of result SOAP operation.

    ApiResponse contain two attributes. The **data** attribute contain result
    of performed SOAP operation. The **error** attribute is empty if operation
    was performed with success. The data attribute is mostly empty in case
    error.

    Attributes:
        data:
            Result of SOAP operation.
        error:
            Contain error message, if is error occurred during
            SOAP operation.
    """

    def __init__(self):
        self.data = None
        self.error = None

    @property
    def success(self):
        """
        this property is used for check if SOAP operation was success.

        Returns:
            True -  if SOAP operation was success.
            False - if during SOAP operation was occurred error.
        """
        if self.error:
            return False
        return True

    @property
    def failed(self):
        """
        this property is used for check if SOAP operation was failed.

        Returns:
            True -  if SOAP operation was failed.
            False - if SOAP operation was successful.
        """
        if self.error:
            return True
        return False


class Client(object):
    """
    Implementation of Client class.
    """

    def __init__(self, integration_code, integration_id, sender=None):
        """
        Implementation of API client for smsfarm.sk.

        Args:
            integration_code:
                Integration code provided by smsfarm.sk.
            integration_id:
                Integration id provided by smsfarm.sk.
            sender:
                String representation of sender name or number. By default
                is used a hostname of machine.
        """
        self.__recipients = []
        self.__integration_code = integration_code
        self.__integration_id = integration_id
        if not sender:
            self.__sender = os.uname()[1]
        else:
            self.__sender = sender
        self.__service = zeep.Client(WSDL_URL).service

    @staticmethod
    def __generate_signature(first, second) -> str:
        if not first or not second:
            raise ValueError("Both arguments are required and cannot be empty")
        raw_string = (first + second).encode()
        md5_sum = hashlib.md5(raw_string).hexdigest()
        signature = md5_sum[10:21]
        return signature

    @property
    def sender(self):
        """
        Attribute which contain client name.

        If was not specified during class initialization then is implicit
        set to hostname of machine.

        Returns:
            String representation of sender name or number.
        """
        return self.__sender

    @property
    def recipients(self):
        """
        A property which returns the recipients.

        Returns:
            String representation of recipients.

        """
        return ','.join(self.__recipients)

    @recipients.setter
    def recipients(self, recipients: (str, list)) -> None:
        """
        Setter for property recipients.

        Does not any validation if given telephone number is valid or not.

        Args:
            recipients:
                Recipients for whom message will be send. Possible value
                is instance of str or list of strings. For example:
                "+421900123456" or ["+421900654321"].
        Raises:
            ValueError:
                is raised if recipients argument is not type of list or string.
        """
        if isinstance(recipients, str):
            self.__recipients.append(recipients)
        elif isinstance(recipients, list):
            self.__recipients.extend(recipients)
        else:
            raise ValueError("Invalid type of recipients")

    def send_message(self, message: str) -> ApiResponse:
        """
        Send message to the recipients.

        Args:
            message:
                String content of message which you want to send.
        Returns:
            ApiResponse:
                which contain id of request or error if was occurred during
                operation.
        Raises:
            ValueError:
                An error when is given empty string.
        """

        if not message:
            raise ValueError("Message cannot be empty!")

        signature = self.__generate_signature(self.__integration_code,
                                              self.recipients)
        response = self.__send_message(message, signature)

        if response.success:
            response.data = str(response.data)
        return response

    def get_message_status(self, request_id: str,
                           recipient: str = None) -> ApiResponse:
        """
        Get message delivery status.

        Args:
            request_id:
                id of message request returned by send_message method.
            recipient:
                number of recipient of the message.
        Returns:
            ApiResponse:
                response contain delivery status for given recipient.

                Possible delivery status:
                    QUEUED
                        message is queued and will be sent shortly
                    SENDING
                        message is being sent right now
                    SENT
                        message was sent successfully
                    DELIVERED
                        message was delivered to cell phone
                    INVALID-NUMBER
                        no valid number was supplied in request
                    MESSAGE-CANCELLED
                        message was cancelled by user
                    MESSAGE-EXPIRED
                        delivery time expired
                    MESSAGE-UNDELIVERED
                        message not delivered for unknown reason
                    SENT-DELIVERY-UNKNOWN
                        message was sent, but status is unknown
                    COUNTRY-FORBIDDEN
                        destination country is forbidden
                    SENDING-FAILED
                        unknown error while sending
        Raises:
            ValueError:
                if recipient was not explicit specified and during
                initialization was used a list of recipients with at least
                two recipients.
        """
        if not recipient:
            if len(self.__recipients) == 1:
                recipient = self.__recipients[0]
            else:
                raise ValueError("Please specify recipient.")

        signature = self.__generate_signature(self.__integration_code,
                                              request_id)
        response = self.__get_message_status(request_id, recipient, signature)
        return response

    def send_scheduled_message(self, message: str,
                               send_time: str) -> ApiResponse:
        """
        Send message at specified time.

        Args:
            message:
                String content of message which you want to send.
            send_time:
                String representation of specified time. Must be in
                "%Y-%m-%d %H:%M" format, for example (2018-01-01 12:29).
        Returns:
            ApiResponse:
                which contain id of request or error if was occurred during
                operation.
        Raises:
            ValueError:
                is raised if given time is not valid.
        """
        if not self.__validate_time(send_time):
            raise ValueError("Invalid time.")

        signature = self.__generate_signature(
            self.__integration_code, self.recipients)
        response = self.__send_scheduled_message(message, send_time,
                                                 self.recipients, signature)
        if response.success:
            response.data = str(response.data)
        return response

    def get_credit(self) -> ApiResponse:
        """
        Get amount of credit.

        Returns:
            ApiResponse:
                which contain amount of remaining credit.
        """
        signature = self.__generate_signature(self.__integration_code,
                                              self.__integration_id)
        return self.__get_credit(signature)

    def get_all_message_statuses(self, request_id) -> ApiResponse:
        """
        Get status for all send messages.

        Args:
            request_id:
                id of message request returned by send_message method.

        Returns:
            ApiResponse:
                A dict mapping keys to the corresponding list returned by
                SOAP service. Each key is recipient number and each value
                is delivery status.

                Possible delivery status:
                    QUEUED
                        message is queued and will be sent shortly
                    SENDING
                        message is being sent right now
                    SENT
                        message was sent successfully
                    DELIVERED
                        message was delivered to cell phone
                    INVALID-NUMBER
                        no valid number was supplied in request
                    MESSAGE-CANCELLED
                        message was cancelled by user
                    MESSAGE-EXPIRED
                        delivery time expired
                    MESSAGE-UNDELIVERED
                        message not delivered for unknown reason
                    SENT-DELIVERY-UNKNOWN
                        message was sent, but status is unknown
                    COUNTRY-FORBIDDEN
                        destination country is forbidden
                    SENDING-FAILED
                        unknown error while sending
        """

        signature = self.__generate_signature(self.__integration_code,
                                              request_id)
        response = self.__get_all_message_statuses(request_id, signature)

        result = {}
        if response.success:
            for item in response.data:
                key, value = item.split(":")
                result[key] = value
            response.data = result
        return response

    #
    #    === Low level calls ===
    #

    def __get_credit(self, signature) -> ApiResponse:
        # integration_id -> str
        # signature -> str
        response = ApiResponse()
        try:
            result = self.__service.GetCreditAmount(
                self.__integration_id, signature)
        except zeep.exceptions.Fault as error:
            response.error = error
        else:
            response.data = result
        finally:
            return response

    def __send_message(self, msg: str, sign: str) -> ApiResponse:
        # sender -> str
        # recipients -> str
        # msg -> str
        # integration_id -> str
        # sign -> str
        response = ApiResponse()
        try:
            result = self.__service.SendMessage(
                self.sender, self.recipients, msg, self.__integration_id, sign)
        except zeep.exceptions.Fault as error:
            response.error = error
        else:
            response.data = result
        finally:
            return response

    def __get_all_message_statuses(self, req_id: str, sign: str) -> ApiResponse:
        # integration_id -> str
        # req_id -> str
        # signature -> str
        response = ApiResponse()
        try:
            result = self.__service.GetAllMessageStatuses(
                self.__integration_id, req_id, sign)
        except zeep.exceptions.Fault as error:
            response.error = error
        else:
            response.data = result
        finally:
            return response

    def __get_message_status(self, req_id: str, rcpt: str,
                             sign: str) -> ApiResponse:
        # req_id -> str
        # rcpt -> str
        # integration_id -> str
        # signature -> str
        response = ApiResponse()
        try:
            result = self.__service.GetMessageStatus(
                req_id, rcpt, self.__integration_id, sign)
        except zeep.exceptions.Fault as error:
            response.error = error
        else:
            response.data = result
        finally:
            return response

    def __send_scheduled_message(self, msg: str, time: str,
                                 rcpt: str, sign: str) -> ApiResponse:
        # sender -> str
        # rcpt -> str
        # msg -> str
        # time -> str
        # integration_id -> str
        # signature -> str
        response = ApiResponse()
        try:
            result = self.__service.SendScheduledMessage(
                self.sender, rcpt, msg, time, self.__integration_id, sign)
        except zeep.exceptions.Fault as error:
            response.error = error
        else:
            response.data = result
        finally:
            return response

    @staticmethod
    def __validate_time(send_time):
        date_format = "%Y-%m-%d %H:%M"
        try:
            datetime.datetime.strptime(send_time, date_format)
        except ValueError:
            return False
        else:
            return True
