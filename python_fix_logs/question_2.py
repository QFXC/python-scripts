import re
import sys

import xlsxwriter

import mixins
import settings

sys.path.insert(0, '')
from utils import timer

SYMBOL_TAG = '55=ES'


class ExecutionReportAnalyzer(mixins.FixLogMixin):
    """
    This script processes the FIX log files and reports a summary of the
    quantity filled on a specific Symbol. It uses execution report (Tag 35=8)
    and examines the CumQty field (Tag 14).
    """

    def __init__(self, symbol_tag: str, excel_filename: str = ''):
        if excel_filename:
            assert excel_filename[-5:] == '.xlsx', (
                'The excel_filename must end with ".xlsx"')
        self.excel_filename = excel_filename
        self.symbol_tag = symbol_tag
        self.execution_report_tag = '35=8'

    @timer
    def execute_report(self):
        print()

        filenames = self.get_filenames()
        symbol_tag = self.symbol_tag
        execution_report_tag = self.execution_report_tag

        # Store data into a dict where the Order Id is the key and the a list
        # of cumulative quantities is the value.
        report = {}

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')

            for message in fix_file.readlines():
                # Search for "35=8" first because it's always near the
                # beginning of the message.
                # Proof: https://www.onixs.biz/fix-dictionary/4.2/tagnum_35.html

                end_index =  min([settings.START_INDEX * 2, len(message) - 1])
                message_beginning = message[settings.START_INDEX: end_index]
                if execution_report_tag in message_beginning:
                    tag_list = re.split(settings.DELIMITER, message)

                    # Only report messages with self.symbol_tag "55=ES".
                    # Traverse the tag_list backwards because that tag is
                    # always closer to the end of the message.
                    index = len(tag_list) - 1
                    while index > -1:
                        if tag_list[index] != symbol_tag:
                            index -= 1
                        else:
                            index = -1
                            # Get the message's Order Id and Cumulative Quantity.
                            order_id = cumulative_qty = None
                            for tag in tag_list:
                                if tag[:3] == '11=':
                                    order_id = tag[3:]
                                elif tag[:3] == '14=':
                                    cumulative_qty = int(tag[3:])
                            assert order_id is not None, (
                                'Tag 11 was not in the message.')

                            report.setdefault(
                                order_id, [cumulative_qty]).append(cumulative_qty)

            fix_file.close()

        result = self.finish_report(report)
        self.save_to_excel(*result)

    def finish_report(self, report) -> tuple:
        """
        Change the value for each order from a list of Cumulative Quantities
        to the max Cumulative Quantity because an order (uniquely identified
        by Order Id, Tag 11) can receive multiple execution reports.
        Intermediate quantities should not be counted multiple times.
        """
        cumulative_qty_sum = 0
        for order_id, qty_list in report.items():
            try:
                cumulative_qty = max(qty_list)
                cumulative_qty_sum += cumulative_qty
                report[order_id] = cumulative_qty
            except TypeError as e:
                # Example Exception:
                #   TypeError: '>' not supported between instances of 'NoneType' and 'int'
                raise TypeError(
                    str(e) +
                    '\nThis means that Tag 14 was not in one of the messages.')

        # Sort the dictionary by key/Order Id, because it's not guaranteed to
        # be in order.
        # (report get's reassigned as a list of 2-tuples)
        report = sorted(report.items())
        return cumulative_qty_sum, report

    def save_to_excel(self, cumulative_qty_sum: int, report: dict):
        # Create a workbook and add a worksheet.
        output_path = self.get_output_path(__file__)
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        worksheet.write(row, col, 'Cumulative Quantity Sum')
        row += 1
        worksheet.write(row, col, cumulative_qty_sum)
        row += 2

        worksheet.write(row, col, 'Order Id')
        worksheet.write(row, col + 1, 'Cumulative Quantity')
        print(f'Cumulative Quantity for symbol "{self.symbol_tag}": {cumulative_qty_sum}')

        for order_id, qty in report:
            row += 1
            worksheet.write(row, col, order_id)
            worksheet.write(row, col + 1, qty)

        workbook.close()
        print(f'Detailed Report Created: {output_path}')


script = ExecutionReportAnalyzer(SYMBOL_TAG)
script.execute_report()
