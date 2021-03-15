import re
import sys

import question_2 as original
import settings

sys.path.insert(0, '')
from utils import timer


class Script2(original.Script):
    """
    This script details the rankings over the available years for specific
    baby names.
    """

    @timer
    def execute_report(self):
        """
        Executes the script to create a report in Excel format.

        Uses Regular Expressions to search the files.
        """
        print()

        male_df, female_df = self.get_empty_dataframes()
        filenames, available_years = self.get_filename_info()

        # Gather the data from the files.
        for index, filename in enumerate(filenames):
            html_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            contents = html_file.read()
            year = available_years[index]
            # Store data into a dict where the name is the key and the name's
            # rank as the value.
            male_names = {}
            female_names = {}

            results = re.finditer(
                r'<td>(\d+)</td><td>(\w+)</td>\<td>(\w+)</td>', contents)

            for line in results:
                rank_num, male_name, female_name = line.groups()
                male_names[male_name] = rank_num
                female_names[female_name] = rank_num

            # Append a new row to the male's table.
            male_df.loc[len(male_df.index)] = \
                self.get_all_row_data(male_names, [year])

            # Append a new row to the female's table.
            female_df.loc[len(female_df.index)] = \
                self.get_all_row_data(female_names, [year])

            html_file.close()

        self.save_to_excel(male_df, female_df)


if __name__ == '__main__':
    script = Script2(
        original.NAMES_IN_REPORT,
        excel_sheetname=original.EXCEL_SHEETNAME,
    )
    script.execute_report()
