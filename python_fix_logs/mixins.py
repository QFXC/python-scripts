import os
import settings


class FixLogMixin:

    def output_path(self, file_dundar: str):
        excel_filename = (
            self.excel_filename or
            os.path.basename(file_dundar).replace('.py', '_report.xlsx')
        )
        output_path = (
            os.path.dirname(os.path.abspath(file_dundar)) + '\\' + excel_filename)
        return output_path

    def get_filenames(self) -> list:
        """
        Returns the filenames from the directory that are needed.

        Returns:
            list
        """
        filenames = []
        filename_prefix = settings.FILENAME_PREFIX
        file_type = settings.FILE_TYPE
        filenames_in_dir = os.listdir(settings.RELATIVE_PATH)
        for filename in filenames_in_dir:
            prefix2 = filename[:len(filename_prefix)]
            file_type2 = filename[-len(file_type):]
            if filename_prefix == prefix2 and file_type == file_type2:
                filenames.append(filename)
        return filenames
