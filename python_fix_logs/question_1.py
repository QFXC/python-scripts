import re
import sys
from enum import Enum

import xlsxwriter

import mixins
import settings

sys.path.insert(0, '')
from utils import timer


class OrderStatus(Enum):
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


CATEGORIES_NEEDED = (
    OrderStatus.FILLED,
    OrderStatus.PARTIALLY_FILLED,
    OrderStatus.CANCELLED,
)


class OrderStatusAnalyzer(mixins.FixLogMixin):
    """
    This script processes the FIX log files in the directory and reports a
    summary of the number of orders broken down by order status (Tag 39) in
    the categories that it's instantiated with.
    """

    def __init__(self, categories_needed: tuple, excel_filename: str = ''):
        if excel_filename:
            assert excel_filename[-5:] == '.xlsx', (
                'The excel_filename must end with ".xlsx"')
        self.excel_filename = excel_filename
        # Hard coding the execution_report_tag because it will always be
        # needed when traversing through FIX logs searching and analyzing
        # Tag 39. Every time a message has Tag 39 it has Tag 35=8.
        self.execution_report_tag = '35=8'
        self.order_status_tag = '39'

        # Store data into a dict where the the Tag is the key and the count of
        # orders is the value.
        report = {}
        for value in categories_needed:
            if isinstance(value, Enum):
                value = value.value
            report[f'{self.order_status_tag}={value}'] = 0

        self.report = report

    @timer
    def execute_report(self):
        """
        Executes the script to create a report in Excel format.
        """
        print()

        filenames = self.get_filenames()
        order_status_tag = self.order_status_tag + '='
        execution_report_tag = self.execution_report_tag

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')

            for message in fix_file.readlines():
                # Only tag "35-8" has order statuses (39=2, 39=1, and 39=4).
                # Search for "35=8" first because it's always near the
                # beginning of the message.
                # Proof: https://www.onixs.biz/fix-dictionary/4.2/tagnum_35.html
                end_index =  min([settings.START_INDEX * 2, len(message) - 1])
                message_beginning = message[settings.START_INDEX: end_index]
                if execution_report_tag in message_beginning:
                    tag_list = re.split(settings.DELIMITER, message)

                    # Only count messages that contain the order_status_tag (39).
                    # Traverse the tag_list backwards because it is always
                    # closer to the end of the message.
                    index = len(tag_list) - 1
                    while index > -1:
                        tag = tag_list[index]
                        if tag[:3] != order_status_tag:
                            index -= 1
                        else:
                            index = -1
                            # If there's a KeyError, then it's not needed.
                            try:
                                self.report[tag] += 1
                            except KeyError:
                                continue
            fix_file.close()

        self.save_to_excel()

    def save_to_excel(self):
        print(self.report)

        # Create a workbook and add a worksheet.
        output_path = self.get_output_path(__file__)
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0
        worksheet.write(row, col, 'Category')
        worksheet.write(row, col + 1, 'Count')

        # Iterate over the data and write it out row by row.
        for category, count in self.report.items():
            row += 1
            worksheet.write(row, col, category)
            worksheet.write(row, col + 1, count)

        workbook.close()
        print(f'Created: {output_path}')


if __name__ == '__main__':
    script = OrderStatusAnalyzer(CATEGORIES_NEEDED)
    script.execute_report()
