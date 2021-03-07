import os
import re
import mixins
import settings
import xlsxwriter


SYMBOL_TAG = '55=ES'


class ExecutionReportAnalyzer(mixins.FixLogMixin):
    """
    This script processes the FIX log files and reports a summary of the
    quantity filled on a specific Symbol. It uses execution reports
    (Tag 35=8) and examines the CumQty field (Tag 14).
    """

    def __init__(self, symbol_tag: str, excel_filename: str = ''):
        self.symbol_tag = symbol_tag
        self.excel_filename = excel_filename
        self.execution_report_tag = '35=8'

    def execute_report(self):
        filenames = self.get_filenames()

        # The dictionary element's key will be the Order Id.
        # The dictionary element's value will be a list of cumulative quantities.
        report = {}

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            for message in fix_file.readlines():
                # Search for "35=8" first because it's always in near beginning
                # of the message.
                # Proof: https://www.onixs.biz/fix-dictionary/4.2/tagnum_35.html
                end_index =  min([settings.START_INDEX * 2, len(message) - 1])
                message_beginning = message[settings.START_INDEX: end_index]
                if self.execution_report_tag in message_beginning:
                    tag_list = re.split(settings.DELIMITER, message)

                    # Only report messages with self.symbol_tag "55=ES".
                    # Traverse backwards because that tag is always closer to
                    # the end of the message.
                    index = len(tag_list) - 1
                    while index > -1:
                        if tag_list[index] != self.symbol_tag:
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
                            try:
                                report[order_id].append(cumulative_qty)
                            except KeyError:
                                report[order_id] = [cumulative_qty]

            fix_file.close()

        report = self.finish_report(report)
        self.save_to_excel(report)

    def finish_report(self, report):
        """
        Change the value for each order from a list of Cumulative Quantities
        to the max Cumulative Quantity because an order (uniquely identified
        by Order Id, Tag 11) can receive multiple execution reports.
        Intermediate quantities should not be counted multiple times.
        """
        for order_id, qty_list in report.items():
            try:
                report[order_id] = max(qty_list)
            except TypeError as e:
                # Example Exception:
                #   TypeError: '>' not supported between instances of 'NoneType' and 'int'
                raise TypeError(
                    str(e) + '\nThis means that cumulative quantity was not in one of the messages.')


        # Sort the dictionary by key/Order Id, because it's not guaranteed to be in order.
        # (report get's reassigned as list of 2-tuples)
        report = sorted(report.items())
        return report

    def save_to_excel(self, report):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(self.output_path(__file__))
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0
        worksheet.write(row, col, 'Order Id')
        worksheet.write(row, col + 1, 'Cumulative Quantity')

        # Iterate over the data and write it out row by row.
        for order_id, qty in report:
            row += 1
            worksheet.write(row, col, order_id)
            worksheet.write(row, col + 1, qty)

        workbook.close()

ExecutionReportAnalyzer(SYMBOL_TAG).execute_report()
