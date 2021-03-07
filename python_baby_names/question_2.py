import os
import mixins
import pandas
import settings

from bs4 import BeautifulSoup
# from IPython.display import display, HTML


NAMES_IN_REPORT = ["Ryan", "Ben", "Eugene"]


class Script(mixins.BabyNamesMixin):
    """
    This script details the rankings over the available years for specific
    baby names.
    """

    def __init__(self, names_in_report: list):
        self.names_in_report = names_in_report

    def execute_report(self):
        columns = ['Year'] + self.names_in_report
        male_df = pandas.DataFrame(columns=columns)
        female_df = pandas.DataFrame(columns=columns)

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
                # For most of the html files, the table rows are missing the
                # closing tr tags, so I am calling "next" until I get the correct
                # element.
                rank_el = row.next.next
                rank_num = int(str(rank_el))
                tag = rank_el.next
                male_name = tag.text.strip()
                male_names[male_name] = rank_num
                female_name = tag.next_sibling.text.strip()
                female_names[female_name] = rank_num

            data_in_row = [year]
            # Example:
            # https://www.geeksforgeeks.org/how-to-add-one-row-in-an-existing-pandas-dataframe/
            # Append a new row to the male's table.
            male_df.loc[len(male_df.index)] = \
                self.append_data_to_row(male_names, data_in_row)

            # Append a new row to the female's table.
            female_df.loc[len(female_df.index)] = \
                self.append_data_to_row(female_names, data_in_row)
            html_file.close()

        print('Male Names Ranking Per Year')
        print(male_df.to_string())
        print('Female Names Ranking Per Year')
        print(female_df.to_string())

    def append_data_to_row(names: dict, new_row: list = []) -> list:
        for name in self.names_in_report:
            try:
                rank = names[name]
            except KeyError:
                rank = 'N/A'
            new_row.append(rank)
        return new_row


Script(NAMES_IN_REPORT).execute_report()
