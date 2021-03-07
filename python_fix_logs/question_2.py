import os
import re
import mixins
import settings


SYMBOL_TAG = '55=ES'


class ExecutionReportAnalyzer(mixins.FixLogMixin):
    """
    This script that processes the FIX log files and reports a summary of the
    quantity filled on a specific symbol_tag. It uses Execution reports
    (Tag 35=8) and examines the CumQty field (Tag 14).
    """

    def __init__(self, symbol_tag: str):
        self.symbol_tag = symbol_tag
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

        return self.finish_report(report)

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

        # # Test
        # previous_id = '0'
        # for order_id, qty_list in report:
        #     assert previous_id < order_id, f'assert {previous_id} < {order_id}'
        #     previous_id = order_id
        #     print(order_id, qty_list)

        return report


report = ExecutionReportAnalyzer(SYMBOL_TAG).execute_report()
print(report)
