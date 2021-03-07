import os
import re
import mixins
import settings

from enum import Enum


class OrdStatus(Enum):
    NEW = '0'
    PARTIALLY_FILLED = '1'
    FILLED = '2'
    DONE_FOR_DAY = '3'
    CANCELLED = '4'
    REPLACED = '5'
    PENDING_CANCEL = '6'
    STOPPED = '7'
    REJECTED = '8'
    SUSPENDED = '9'
    PENDING_NEW = 'A'
    CALCULATED = 'B'
    EXPIRED = 'C'
    ACCEPTED_FOR_BIDDING = 'D'
    PENDING_REPLACE = 'E'


class OrderStatusAnalyzer(mixins.FixLogMixin):
    """
    This script processes the FIX log files in the directory and reports a
    summary of the number of orders broken down by order status (Tag 39) in
    the categories that it's instantiated with.
    """

    def __init__(self, categories_needed: list):
        # Hard coding the execution_report_tag because it will always be
        # needed when traversing through FIX logs searching and analyzing
        # Tag 39. Every time a message has Tag 39 it has Tag 35=8.
        self.execution_report_tag = '35=8'
        self.order_status_tag = '39'

        # Initialize the structure of the dictionary.
        # The dictionary element's key will be the Tag.
        # The dictionary element's value will be count of orders.
        report = {}
        for value in categories_needed:
            if isinstance(value, Enum):
                value = value.value
            report[f'{self.order_status_tag}={value}'] = 0
        self.report = report

    def execute_report(self):
        filenames = self.get_filenames()
        order_status_tag = self.order_status_tag + '='

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            for message in fix_file.readlines():
                # Only tag "35-8" has order statuses (39=2, 39=1, and 39=4).
                # Search for "35=8" first because it's always near the beginning
                # of the message.
                # Proof: https://www.onixs.biz/fix-dictionary/4.2/tagnum_35.html
                end_index =  min([settings.START_INDEX * 2, len(message) - 1])
                message_beginning = message[settings.START_INDEX: end_index]
                if self.execution_report_tag in message_beginning:
                    tag_list = re.split(settings.DELIMITER, message)

                    # Only report messages with tag in report.
                    # Traverse backwards because that tag is always closer to
                    # the end of the message.
                    index = len(tag_list) - 1
                    while index > -1:
                        tag = tag_list[index]
                        if tag[:3] != order_status_tag:
                            index -= 1
                        else:
                            index = -1
                            try:
                                self.report[tag] += 1
                            except KeyError:
                                continue
            fix_file.close()

        return self.report

report = OrderStatusAnalyzer([
    OrdStatus.FILLED,
    OrdStatus.PARTIALLY_FILLED,
    OrdStatus.CANCELLED,
]).execute_report()

print(report)
