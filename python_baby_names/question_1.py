import os
import mixins
import settings
import xlsxwriter

from bs4 import BeautifulSoup


# NAME_QUANTITY_NEEDED represents the first X names
NAME_QUANTITY_NEEDED = 5


class Script(mixins.BabyNamesMixin):
    """
    This script scrapes all HTML files in the directory and reports
    the top 5 names for each year for both males and females.
    """

    male_name_key = 'male_names'
    female_name_key = 'female_names'

    def __init__(self, name_quantity_needed, excel_filename: str = ''):
        self.name_quantity_needed = name_quantity_needed
        self.excel_filename = excel_filename

    def execute_report(self):
        report = {
            self.male_name_key: {},
            self.female_name_key: {},
        }

        filenames, available_years = self.get_filename_info()

        # Gather the data from the files.
        for index, filename in enumerate(filenames):
            html_file = open(f'{settings.RELATIVE_PATH}/{filename}', 'r')
            contents = html_file.read()
            soup = BeautifulSoup(contents, 'html.parser')

            year = available_years[index]
            self.validate_year(year, soup)
            table = self.get_table(soup)

            # Find all the rows in the table.
            # The first row is the header, so skip it.
            shift = 1
            rows = table.find_all('tr')[shift: self.name_quantity_needed + shift]

            male_names = []
            female_names = []
            for row in rows:
                # For most of the html files, the table rows are missing the
                # closing tr tags, so I am calling "next" until I get the
                # correct element.
                tag = row.next.next.next
                male_name = tag.text.strip()
                male_names.append(male_name)
                female_name = tag.next_sibling.text.strip()
                female_names.append(female_name)

            report[self.male_name_key][year] = male_names
            report[self.female_name_key][year] = female_names
            html_file.close()

        self.save_to_excel(report)

    def save_to_excel(self, report):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(self.output_path(__file__))
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        worksheet.write(row, col, 'Year')
        rank_list = [1, 2, 3, 4, 5]
        for rank in rank_list:
            col += 1
            worksheet.write(row, col, 'Rank ' + str(rank))

        first_col = 0

        for mf, year_list in report.items():
            row += 1
            # Write a row saying whether this list will be males or females.
            worksheet.write(row, first_col, mf)
            row += 1

            # Write a new row that contains the year and names.
            for year, name_list in year_list.items():
                worksheet.write(row, first_col, year)
                col = first_col + 1
                for i, name in enumerate(name_list):
                    worksheet.write(row, i + 1, name)
                row += 1

        workbook.close()


Script(NAME_QUANTITY_NEEDED).execute_report()
