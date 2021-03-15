import mixins
import os
import pandas as pd
import settings
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, '')
from utils import timer

NAMES_IN_REPORT = ["Ryan", "Ben", "Eugene"]
EXCEL_SHEETNAME = 'Great Report'


class Script(mixins.BabyNamesMixin):
    """
    This script details the rankings over the available years for specific
    baby names.
    """

    def __init__(self, names_in_report: list, excel_filename: str = '',
                 excel_sheetname: str = ''):
        if excel_filename:
            assert excel_filename[-5:] == '.xlsx', (
                'The excel_filename must end with ".xlsx"')
        self.excel_filename = excel_filename
        self.names_in_report = names_in_report
        self.excel_sheetname = excel_sheetname

    @timer
    def execute_report(self):
        # Instantiate the table/dataframe for males.
        header_2 = ['Year'] + self.names_in_report
        male_df = pd.DataFrame(columns=header_2)
        header_1 = ['Male Name Rankings Per Year'] + len(self.names_in_report) * ['']
        male_df.columns = pd.MultiIndex.from_tuples(zip(header_1, header_2))

        # Instantiate the table/dataframe for females.
        female_df = pd.DataFrame(columns=header_2)
        header_1 = ['Female Name Rankings Per Year'] + len(self.names_in_report) * ['']
        female_df.columns = pd.MultiIndex.from_tuples(zip(header_1, header_2))

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
            rows = table.find_all('tr', attrs={'align': 'right'})[1:]

            # The dictionary element's key will be the name.
            # The dictionary element's value will be the rank.
            male_names = {}
            female_names = {}
            for row in rows:
                # For most of the HTML files, the table rows are missing the
                # closing tr tags, so I am calling "next" until I get the
                # correct element.
                rank_el = row.next.next
                rank_num = int(str(rank_el))
                tag = rank_el.next
                male_name = tag.text.strip()
                male_names[male_name] = rank_num
                female_name = tag.next_sibling.text.strip()
                female_names[female_name] = rank_num

            # Append a new row to the male's table.
            male_df.loc[len(male_df.index)] = \
                self.add_data_to_row(male_names, [year])

            # Append a new row to the female's table.
            female_df.loc[len(female_df.index)] = \
                self.add_data_to_row(female_names, [year])
            html_file.close()

        self.save_to_excel([male_df, female_df])

    def add_data_to_row(self, names: dict, new_row_data: list = []) -> list:
        for name in self.names_in_report:
            try:
                rank = names[name]
            except KeyError:
                rank = 'N/A'
            new_row_data.append(rank)
        return new_row_data

    def save_to_excel(self, dataframes):
        output_path = self.get_output_path(__file__)
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        row = 0
        for df in dataframes:
            df.to_excel(
                writer,
                sheet_name=self.excel_sheetname,
                startrow=row,
                startcol=0,
            )
            row = row + len(df.index) + 2
        writer.save()
        print(f'Created: {output_path}')


Script(
    NAMES_IN_REPORT,
    excel_sheetname=EXCEL_SHEETNAME,
).execute_report()
