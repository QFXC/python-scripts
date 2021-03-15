import re
import sys
from enum import Enum

import question_1 as original
import settings

sys.path.insert(0, '')
from utils import timer


class OrderStatusAnalyzer2(original.OrderStatusAnalyzer):
    """
    This script processes the FIX log files in the directory and reports a
    summary of the number of orders broken down by order status (Tag 39) in
    the categories that it's instantiated with.
    """

    def __init__(self, categories_needed: tuple, excel_filename: str = ''):
        super().__init__(categories_needed, excel_filename)

        # Create a string where the categories are side to side without any
        # delimeters.
        categories_needed_iterable = ''

        for value in categories_needed:
            if isinstance(value, Enum):
                value = value.value
            categories_needed_iterable += str(value)

        self.categories_needed = categories_needed_iterable

    @timer
    def execute_report(self):
        """
        Executes the script to create a report in Excel format.

        Uses Regular Expressions to search the files.
        """
        print()

        filenames = self.get_filenames()
        order_status_tag = self.order_status_tag + '='

        for filename in filenames:
            fix_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')

            contents = fix_file.read()
            pattern = rf'39=([{self.categories_needed}])'
            results = re.finditer(pattern, contents)

            for message in results:
                order_status = message.group(1)
                self.report[order_status_tag + order_status] += 1
            fix_file.close()

        self.save_to_excel()


if __name__ == '__main__':
    script = OrderStatusAnalyzer2(original.CATEGORIES_NEEDED)
    script.execute_report()
