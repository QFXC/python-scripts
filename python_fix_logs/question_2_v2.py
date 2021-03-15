import re
import sys

import question_2 as original
import settings

sys.path.insert(0, '')
from utils import timer


class ExecutionReportAnalyzer2(original.ExecutionReportAnalyzer):
    """
    This script processes the FIX log files and reports a summary of the
    quantity filled on a specific Symbol. It uses execution report (Tag 35=8)
    and examines the CumQty field (Tag 14).
    """

    @timer
    def execute_report(self):
        """
        Executes the script to create a report in Excel format.

        Uses Regular Expressions to search the files.
        """
        print()

        filenames = self.get_filenames()

        # Store data into a dict where the Order Id is the key and the a list
        # of cumulative quantities is the value.
        report = {}

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            contents = fix_file.read()
            pattern = r'11=(?P<order_id>\w+).*14=(?P<qty>\d+)'
            results = re.finditer(pattern, contents)

            for message in results:
                order_id = message.group('order_id')
                cumulative_qty = int(message.group('qty'))
                report.setdefault(
                    order_id, [cumulative_qty]).append(cumulative_qty)
            fix_file.close()

        result = self.finish_report(report)
        self.save_to_excel(*result)


if __name__ == '__main__':
    script = ExecutionReportAnalyzer2(original.SYMBOL_TAG)
    script.execute_report()
