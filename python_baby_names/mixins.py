import os

from bs4 import Tag

import settings


class BabyNamesMixin:

    header_tags = settings.HEADER_TAGS
    excel_filename = ''

    def get_output_path(self, file_dunder: str) -> str:
        """
        Returns the path of the file that will be created (including the
        filename within the path).

        Args:
            file_dunder (str):
                The __file__ value that's available in every Python file.

        Returns:
            str: The path of the output.
        """
        excel_filename = (
            self.excel_filename or
            os.path.basename(file_dunder).replace('.py', '_report.xlsx')
        )
        output_path = (
            os.path.dirname(os.path.abspath(file_dunder)) + '\\' + excel_filename)
        return output_path

    def get_filename_info(self) -> tuple:
        """
        Returns a 2-tuple of filenames within the directory and the years that
        are within those filenames.

        Returns:
            tuple: filenames, available_years
        """
        available_years = []

        # Put the HTML filenames into a list.
        filenames = []
        filenames_in_dir = os.listdir(settings.RELATIVE_PATH)
        prefix_len = len(settings.FILENAME_PREFIX)
        file_type_len = len(settings.FILE_TYPE)

        for filename in filenames_in_dir:
            prefix2 = filename[:prefix_len]
            file_type2 = filename[-file_type_len:]
            # Make sure the files are actually the ones we need.
            if settings.FILENAME_PREFIX == prefix2 and settings.FILE_TYPE == file_type2:
                # Get the year from the middle of the string.
                year = filename[prefix_len: -file_type_len]
                # If there are any non-digit characters, it means that the
                # filename is not in the correct format.
                assert year.isdigit(), (
                    f'File "{filename}" is not in a valid format.')
                assert len(year) == 4
                available_years.append(year)
                filenames.append(filename)

        return filenames, available_years

    def validate_year(self, year: int, soup):
        """
        Validates that the year in the HTML file is the same as the year in the
        file's name.

        Args:
            year (int)
            soup (BeautifulSoup)
        """
        for tag in self.header_tags:
            title_el = soup.select_one(tag)
            try:
                title_text = title_el.text
                break
            except AttributeError:
                continue

        year_in_title = title_text[-4:]
        assert year_in_title.isdigit() and len(year_in_title) == 4, (
            f'Did not extract a valid year from the HTML. Instead got ({year_in_title}).')
        assert year_in_title == year, (
            f'Year "{year_in_title}" != "{year}"')

    def get_table(self, soup, filename: str):
        """
        Finds the correct table within BeautifulSoup object and validates it
        before it is returned.

        Args:
            soup (BeautifulSoup): The soup of the entire page.
            filename (str): The name of the file.

        Returns:
            BeautifulSoup: The HTML table element within the soup.
        """
        # In all cases, the data we need is in the 3rd table.
        table = soup.find_all('table')[2]
        self.validate_table_columns(table, filename)
        return table

    def validate_table_columns(self, table, filename: str):
        """
        Validates that the table's columns are in the expected order.

        Args:
            table (BeautifulSoup): The table object found in the HTML file.
            filename (str): The name of the file.
        """
        table_header = table.select_one('tr')
        actual_column_order = []
        for th in table_header:
            if isinstance(th, Tag):
                actual_column_order.append(th.text.lower())
        assert settings.EXPECTED_COLUMN_ORDER == actual_column_order, (
            f'File "{filename}" does not have the expected column order.')
