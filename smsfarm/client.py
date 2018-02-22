import hashlib
import os

import zeep
import zeep.exceptions

from .exceptions import NotSpecifiedError, SOAPError

WSDL_URL = "http://app.smsfarm.sk/api/?wsdl"


class Client(object):
    def __init__(self, integration_code, integration_id, sender=None):
        """
        Implementation of API client for smsfarm.sk.

        Args:
            integration_code: Integration code provided by smsfarm.sk.
            integration_id: Integration id provided by smsfarm.sk.
            sender: String representation of sender name or number. By default
                    is used a hostname of machine.
        """
        self.__recipients = []
        self.__code = integration_code
        self.__id = integration_id
        if not sender:
            self.__sender = os.uname()[1]
        else:
            self.__sender = sender
        self.__service = zeep.Client(WSDL_URL).service

    @staticmethod
    def __generate_signature(first, second) -> str:
        if not first or not second:
            raise ValueError("Both arguments are required and cannot be empty!")
        raw_string = (first + second).encode()
        md5_sum = hashlib.md5(raw_string).hexdigest()
        signature = md5_sum[10:21]
        return signature

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
            recipients: Recipients for whom message will be send. Possible value
                is instance of str or list of strings. For example:
                "+421900123456" or ["+421900654321"].
        Raises:
            ValueError: if recipients argument is not type of list or string.
        """
        if isinstance(recipients, str):
            self.__recipients.append(recipients)
        elif isinstance(recipients, list):
            self.__recipients.extend(recipients)
        else:
            raise ValueError("Invalid type of recipients")

    def send_message(self, message: str) -> str:
        """
        Send message to the recipients.

        Args:
            message: Content of message which you want to send.

        Returns:
            id of sent message.
        Raises:
            ValueError: An error when is given empty message.
            SOAPError: An error occurred during sending message by SOAP service.
        """

        if not message:
            raise ValueError("Message cannot be empty!")

        try:
            return str(self.__send_message(message))
        except zeep.exceptions.Fault as error:
            raise SOAPError(error)

    def get_message_status(self, request_id: str, recipient: str = None)->str:
        """
        Get message delivery status.

        Args:
            request_id: id of message request returned by send_message
                method.
            recipient: number of recipient of the message.

        Returns:
            Delivery status for given recipient.
            Possible delivery status:

                QUEUED - message is queued and will be sent shortly

                SENDING - message is being sent right now

                SENT - message was sent successfully

                DELIVERED - message was delivered to cell phone

                INVALID-NUMBER - no valid number was supplied in request

                MESSAGE-CANCELLED - message was cancelled by user

                MESSAGE-EXPIRED - delivery time expired

                MESSAGE-UNDELIVERED - message not delivered for unknown reason

                SENT-DELIVERY-UNKNOWN - message was sent, but status is unknown

                COUNTRY-FORBIDDEN - destination country is forbidden

                SENDING-FAILED - unknown error while sending

        Raises:
            NotSpecifiedError: recipient was not explicit specified and during
                initialization was used a list of recipients.
            SOAPError: An error occurred by SOAP service.
        """
        if not recipient:
            if len(self.__recipients) == 1:
                recipient = self.__recipients[0]
            else:
                raise NotSpecifiedError("Please specify recipient.")
        try:
            return self.__get_message_status(request_id, recipient)
        except zeep.exceptions.Fault as error:
            raise SOAPError(error)

    def send_scheduled_message(self, message, send_time, recipient=None):
        # format: "send_time" => date("Y-m-d H:i")

        raise NotImplementedError("Not implemented")
        # self.__send_scheduled_message(message, send_time, recipient)

    def get_credit(self) -> float:
        """
        Get amount of credit.

        Returns:
            amount of remaining credit.
        """
        try:
            # get_credit -> integration_id, signature
            return self.__get_credit()
        except zeep.exceptions.Fault as error:
            raise SOAPError(error)

    def get_all_message_statuses(self, request_id) -> dict:
        """
        Get status for all send messages.

        Args:
            request_id: id of message request returned by send_message
                method.

        Returns:
            A dict mapping keys to the corresponding list returned by
            SOAP service. Each key is recipient number and each value is
            delivery status.
            Possible delivery status:

                QUEUED - message is queued and will be sent shortly

                SENDING - message is being sent right now

                SENT - message was sent successfully

                DELIVERED - message was delivered to cell phone

                INVALID-NUMBER - no valid number was supplied in request

                MESSAGE-CANCELLED - message was cancelled by user

                MESSAGE-EXPIRED - delivery time expired

                MESSAGE-UNDELIVERED - message not delivered for unknown reason

                SENT-DELIVERY-UNKNOWN - message was sent, but status is unknown

                COUNTRY-FORBIDDEN - destination country is forbidden

                SENDING-FAILED - unknown error while sending
        Raises:
            SOAPError: An error occurred by SOAP service.
        """
        try:
            statuses = self.__get_all_message_statuses(request_id)
        except zeep.exceptions.Fault as error:
            raise SOAPError(error)
        else:
            result = {}
            if statuses:
                for item in statuses:
                    key, value = item.split(":")
                    result.update({key: value})
            return result

    def __get_credit(self):
        signature = self.__generate_signature(self.__code, self.__id)

        # integration_id, signature
        return self.__service.GetCreditAmount(self.__id, signature)

    def __send_message(self, message):
        signature = self.__generate_signature(self.__code, self.recipients)

        # sender, recipients, message, integration_id, signature
        return self.__service.SendMessage(
            self.__sender,
            self.recipients,
            message,
            self.__id,
            signature)

    def __get_all_message_statuses(self, request_id):
        signature = self.__generate_signature(self.__code, request_id)

        # integration_id, request_id, signature
        return self.__service.GetAllMessageStatuses(self.__id,
                                                    request_id,
                                                    signature)

    def __get_message_status(self, request_id, recipient):
        signature = self.__generate_signature(self.__code, request_id)

        # request_id, recipient, integration_id, signature
        return self.__service.GetMessageStatus(request_id,
                                               recipient,
                                               self.__id,
                                               signature)

    def __send_scheduled_message(self, message, send_time, recipient):
        signature = self.__generate_signature(self.__code, recipient)

        # sender, recipient, message, send_time, integration_id, signature
        return self.__service.SendScheduledMessage(self.__sender,
                                                   recipient,
                                                   message,
                                                   send_time,
                                                   self.__id,
                                                   signature)
