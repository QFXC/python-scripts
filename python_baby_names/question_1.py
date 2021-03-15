import sys

import xlsxwriter
from bs4 import BeautifulSoup

import mixins
import settings

sys.path.insert(0, '')
from utils import timer

# NAME_QUANTITY_NEEDED represents the first X names
NAME_QUANTITY_NEEDED = 5


class Script(mixins.BabyNamesMixin):
    """
    This script scrapes all HTML files in the directory and report the top
    names for each year for both males and females.
    """

    def __init__(self, name_quantity_needed: int, excel_filename: str = ''):
        if excel_filename:
            assert excel_filename[-5:] == '.xlsx', (
                'The excel_filename must end with ".xlsx"')
        self.excel_filename = excel_filename
        self.name_quantity_needed = name_quantity_needed

    @timer
    def execute_report(self):
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
            soup = BeautifulSoup(contents, 'lxml')
            year = available_years[index]
            self.validate_year(year, soup)
            table = self.get_table(soup, filename)

            # Find all the rows in the table.
            # The first row is the header, so skip it.
            shift = 1
            rows = table.find_all('tr')[shift: self.name_quantity_needed + shift]

            male_names = []
            female_names = []
            for row in rows:
                # For most of the HTML files, the table rows are missing the
                # closing tr tags, so I am calling "next" until I get the
                # correct element.
                tag = row.next.next.next
                male_name = tag.text.strip()
                male_names.append(male_name)
                female_name = tag.next_sibling.text.strip()
                female_names.append(female_name)

            report[male_name_key][year] = male_names
            report[female_name_key][year] = female_names
            html_file.close()

        self.save_to_excel(report)

    def save_to_excel(self, report):
        # Create a workbook and add a worksheet.
        output_path = self.get_output_path(__file__)
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.

        # Write the header row.
        worksheet.write(row, col, 'Year')
        rank_list = [i + 1 for i in range(self.name_quantity_needed)]
        for rank in rank_list:
            col += 1
            worksheet.write(row, col, 'Rank ' + str(rank))

        first_col = 0

        for mf, year_list in report.items():
            row += 1
            # Write a row saying whether this list will be males or females.
            worksheet.write(row, first_col, mf)
            row += 1

            # Write a row for each name.
            for year, name_list in year_list.items():
                worksheet.write(row, first_col, year)
                for i, name in enumerate(name_list):
                    worksheet.write(row, i + 1, name)
                row += 1

        workbook.close()
        print(f'Created: {output_path}')


script = Script(NAME_QUANTITY_NEEDED)
script.execute_report()
