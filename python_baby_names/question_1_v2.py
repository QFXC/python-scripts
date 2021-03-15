import re
import sys

import question_1 as original
import settings

sys.path.insert(0, '')
from utils import timer


class Script2(original.Script):
    """
    This script scrapes all HTML files in the directory and report the top
    names for each year for both males and females.
    """

    @timer
    def execute_report(self):
        """
        Executes the script to create a report in Excel format.

        Uses Regular Expressions to search the files.
        """
        print()

        male_name_key = 'male_names'
        female_name_key = 'female_names'

        # Store data into a nested dict.
        # Example:
        # {
        #   'male_names': {'1990': ['Michael', 'Christopher', 'Matthew', 'Joshua', 'Daniel']},
        #   'female_names': {'1990': ['Jessica', 'Ashley', 'Brittany', 'Amanda', 'Samantha']}
        # }
        report = {
            male_name_key: {},
            female_name_key: {},
        }
        filenames, available_years = self.get_filename_info()

        # Gather the data from the files.
        for index, filename in enumerate(filenames):
            html_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            contents = html_file.read()

            male_names = []
            female_names = []
            year = available_years[index]

            results = re.findall(
                r'<td>.*</td><td>(\w+)</td>\<td>(\w+)</td>', contents)

            for group in results[:self.name_quantity_needed]:
                male_name, female_name = group
                male_names.append(male_name)
                female_names.append(female_name)

            report[male_name_key][year] = male_names
            report[female_name_key][year] = female_names
            html_file.close()

        self.save_to_excel(report)


if __name__ == '__main__':
    script = Script2(original.NAME_QUANTITY_NEEDED)
    script.execute_report()
