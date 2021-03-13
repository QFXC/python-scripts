import collections
import functools
import os
import timeit

import pandas as pd
from bs4 import BeautifulSoup

import mixins
import settings

NAMES_IN_REPORT = ['Ryan', 'Ben', 'Eugene']
EXCEL_SHEETNAME = 'Great Report'


def timer(func):
    """Print the runtime of the decorated function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        value = func(*args, **kwargs)
        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        msg = f'Took {round(elapsed_time, 2)} seconds.'
        script_obj = args[0]
        if script_obj.generate_excel:
            msg += ' (Including the time it took to generate the Excel file.)'
        else:
            msg += ' (NOT including the time it took to generate the Excel file.)'
        print(msg)
        return value

    return wrapper


class Script(mixins.BabyNamesMixin):
    """
    This script details the rankings over the available years for specific
    baby names.
    """

    def __init__(
        self,
        names_in_report: list,
        excel_filename: str = '',
        excel_sheetname: str = '',
        generate_excel: bool = True
    ):
        if excel_filename:
            assert excel_filename[-5:] == '.xlsx', (
                'The excel_filename must end with ".xlsx"')
        self.excel_filename = excel_filename
        self.names_in_report = names_in_report
        self.excel_sheetname = excel_sheetname
        self.generate_excel = generate_excel

    @timer
    def execute_report(self):
        print()

        pkl_filename = self.get_pkl_filename()
        already_scraped = pkl_filename in os.listdir(settings.RELATIVE_PATH)

        if not already_scraped:
            print('Scraping HTML files for data.')
            male_df, female_df = self.dfs_from_html()
        else:
            print('Using the stored data in the Pandas PKL file.')
            male_df, female_df = self.dfs_from_pkl()

        if self.generate_excel:
            self.save_to_excel([male_df, female_df])

    def get_pkl_filename(self):
        return os.path.basename(__file__).replace('.py', '_data.pkl')

    def get_pkl_path(self) -> str:
        """
        Returns the path to the Pandas PKL data file.
        """
        pkl_filename = self.get_pkl_filename()
        return os.path.dirname(os.path.abspath(__file__)) + '\\' + pkl_filename

    def save_pkl(self, data):
        """
        Saves a Pandas PKL data file.

        Args:
            data (Iterable): An iterable in a structure that Pandas understands.
        """
        path = self.get_pkl_path()
        pd.DataFrame(
            data,
            columns=['gender', 'year', 'name', 'rank']
        ).to_pickle(path)

    def get_empty_dataframes(self):
        header_2 = ['Year'] + self.names_in_report

        # Instantiate the table/dataframe for males.
        male_df = pd.DataFrame(columns=header_2)
        header_1 = ['Male Name Rankings Per Year'] + len(self.names_in_report) * ['']
        male_df.columns = pd.MultiIndex.from_tuples(zip(header_1, header_2))

        # Instantiate the table/dataframe for females.
        female_df = pd.DataFrame(columns=header_2)
        header_1 = ['Female Name Rankings Per Year'] + len(self.names_in_report) * ['']
        female_df.columns = pd.MultiIndex.from_tuples(zip(header_1, header_2))

        return male_df, female_df

    def dfs_from_html(self):
        """
        Scrapes the HTML files found in this file's directory to generate 2
        DataFrames (one for males and one for females).

        Returns:
            tuple: A 2-tuple of non-empty DataFrames.
        """
        male_df, female_df = self.get_empty_dataframes()
        pandas_data = collections.deque()
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
            rows = table.find_all('tr', attrs={'align': 'right'})[1:]

            # The dictionary element's key will be the name.
            # The dictionary element's value will be the rank.
            male_names_dict = {}
            female_names_dict = {}

            for row in rows:
                # For most of the HTML files, the table rows are missing the
                # closing tr tags, so I am calling "next" until I get the
                # correct element.
                rank_el = row.next.next
                rank_num = int(str(rank_el))
                tag = rank_el.next
                male_name = tag.text.strip()
                male_names_dict[male_name] = rank_num
                female_name = tag.next_sibling.text.strip()
                female_names_dict[female_name] = rank_num

                pandas_data.extend(
                    [
                        ['m', year, male_name, rank_num],
                        ['f', year, female_name, rank_num],
                    ]
                )

            # Append a new row to the male's table.
            male_df.loc[len(male_df.index)] = \
                self.get_all_row_data(male_names_dict, [year])

            # Append a new row to the female's table.
            female_df.loc[len(female_df.index)] = \
                self.get_all_row_data(female_names_dict, [year])

            html_file.close()

        # Save the data in the current directory, so you won't have to scrape
        # the HTML again.
        self.save_pkl(pandas_data)
        return male_df, female_df

    def dfs_from_pkl(self):
        """
        Uses the PKL file (static data) found in this file's directory to
        generate 2 DataFrames (one for males and one for females).

        Much faster than the dfs_from_html method because it is not scraping
        data from HTML. Also faster because it is querying the PKL data file.

        Returns:
            tuple: A 2-tuple containing non-empty DataFrames.
        """
        male_df, female_df = self.get_empty_dataframes()
        pkl_path = self.get_pkl_path()

        # Filter and fetch the data from the PKL file.
        df_filter = f'name in {str(list(self.names_in_report))}'
        # "df" is a very short data set. It is only:
        # len(self.names_in_report) * available_years * 2.
        # In this example: 3 * 10 * 2 = 60
        df = pd.read_pickle(pkl_path).query(df_filter)
        nested_data = {
            'm': {},
            'f': {}
        }

        # Transform the queried data to a structure similar to what is in the
        # dfs_from_html method.
        for i in df.itertuples():
            try:
                # Accessing the year can raise a KeyError.
                nested_data[i.gender][i.year][i.name] = i.rank
            except KeyError:
                nested_data[i.gender][i.year] = {i.name: i.rank}

        for gender, value_dict in nested_data.items():
            if gender == 'm':
                for year, value_dict in value_dict.items():
                    # Append a new row to the male's table.
                    male_df.loc[len(male_df.index)] = \
                        self.get_all_row_data(value_dict, [year])
            else:
                for year, value_dict in value_dict.items():
                    # Append a new row to the female's table.
                    female_df.loc[len(female_df.index)] = \
                        self.get_all_row_data(value_dict, [year])

        return male_df, female_df

    def get_all_row_data(self, names: dict, new_row_data: list = []) -> list:
        """
        Creates and returns two empty dataframes.
        """
        for name in self.names_in_report:
            try:
                rank = names[name]
            except KeyError:
                rank = 'N/A'
            new_row_data.append(rank)
        return new_row_data

    def save_to_excel(self, dataframes: list):
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


script = Script(
    NAMES_IN_REPORT,
    excel_sheetname=EXCEL_SHEETNAME,
    generate_excel=True
)
script.execute_report()
