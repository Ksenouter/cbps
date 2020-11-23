from fake_useragent import settings
import parser_settings as settings
from pathlib import Path
import download_settings
import shutil
import pandas
import dbf
import os


class Parser:

    @staticmethod
    def dbf_get_column(table, col_num):
        print("Parsing %s column..." % str(col_num))
        return [row[col_num] for row in table]

    @staticmethod
    def dbf_get_column_by_name(table, col_name):
        return Parser.dbf_get_column(table, table.field_names.index(col_name))

    @staticmethod
    def dbf_to_dataframe(path):
        print('Parsing "%s"...' % path)
        table = dbf.Table(path, codepage='cp866')
        table.open()
        data = {col: Parser.dbf_get_column_by_name(table, col) for col in table.field_names}
        table.close()
        return pandas.DataFrame(data)

    @staticmethod
    def create_csv_folder():
        if os.path.exists(settings.CSV_PATH) and os.path.isdir(settings.CSV_PATH):
            shutil.rmtree(settings.CSV_PATH, ignore_errors=True)
        Path(settings.CSV_PATH).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_dataframe(dataframe, form_name):
        path = '{}/{}.csv'.format(settings.CSV_PATH, form_name)
        dataframe.to_csv(path, index=False)

    @staticmethod
    def excel_pars_reg_nums(dataframe):
        reg_nums_dataframe = pandas.read_excel(settings.EXCEL_REG_NUMS)
        reg_nums = reg_nums_dataframe[reg_nums_dataframe.keys()[0]].to_list()
        dataframe = dataframe[dataframe.REGN.isin(reg_nums)]
        return dataframe

    @staticmethod
    def pars_forms():
        Parser.create_csv_folder()
        for form_name in settings.FORMS:
            form = settings.FORMS[form_name]
            form_dir = '{}/{}'.format(download_settings.FILES_PATH, form_name)
            dataframes = []
            for date in os.listdir(form_dir):
                date_dir = '{}/{}'.format(form_dir, date)
                file = [file for file in os.listdir(date_dir) if form.pars_file.lower() in file.lower()][0]
                file_dir = '{}/{}'.format(date_dir, file)
                dataframes.append(Parser.dbf_to_dataframe(file_dir))
            dataframe = pandas.concat(dataframes)
            dataframe = Parser.excel_pars_reg_nums(dataframe)
            dataframe = form.processing_func(dataframe)
            Parser.save_dataframe(dataframe, form_name)