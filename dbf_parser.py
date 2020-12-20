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
        print('Completed csv folder recreated!\n')

    @staticmethod
    def save_dataframe(dataframe, form_name, as_source=False):
        path = '{}/{}.csv'.format(settings.SOURCE_CSV_PATH if as_source else settings.CSV_PATH, form_name)
        dataframe.to_csv(path, index=False, encoding='cp866')

    @staticmethod
    def excel_pars_reg_nums(dataframe):
        reg_nums_dataframe = pandas.read_excel(settings.EXCEL_REG_NUMS, engine='openpyxl')
        reg_nums = reg_nums_dataframe[reg_nums_dataframe.keys()[0]].to_list()
        dataframe = dataframe[dataframe.REGN.isin(reg_nums)]
        return dataframe

    @staticmethod
    def check_source_csv_folder():
        if os.path.exists(settings.SOURCE_CSV_PATH) and os.path.isdir(settings.SOURCE_CSV_PATH):
            files = [file for file in os.listdir(settings.SOURCE_CSV_PATH)]
            result = sorted(files) == sorted([key + '.csv' for key in settings.FORMS.keys()])
            return True if result else shutil.rmtree(settings.SOURCE_CSV_PATH, ignore_errors=True)
        Path(settings.SOURCE_CSV_PATH).mkdir(parents=True, exist_ok=True)
        return False

    @staticmethod
    def create_source_csv_files(processing_forms=True):
        for form_name in settings.FORMS:
            print('Parsing dataframe form dbf for form %s...' % form_name)
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
            Parser.save_dataframe(dataframe, form_name, as_source=True)
            print('Parsing for form %s from dbf completed and saved!\n' % form_name)
            if processing_forms:
                print('Processing %s form...' % form_name)
                dataframe = form.processing_func(dataframe)
                Parser.save_dataframe(dataframe, form_name)
                print('Processing completed and saved to csv!\n')

    @staticmethod
    def pars_forms(recreate_sources=False):
        if recreate_sources:
            if os.path.exists(settings.SOURCE_CSV_PATH) and os.path.isdir(settings.SOURCE_CSV_PATH):
                shutil.rmtree(settings.SOURCE_CSV_PATH, ignore_errors=True)
            print('Sources folder deleted!\n')

        Parser.create_csv_folder()

        if not Parser.check_source_csv_folder():
            print('Sources csv files not found...\n')
            Parser.create_source_csv_files(processing_forms=True)
            return
        print('Sources csv files found!\n')

        for form_name in settings.FORMS:
            print('Reading dataframe from csv for form %s...' % form_name)
            csv_path = '{}/{}.csv'.format(settings.SOURCE_CSV_PATH, form_name)
            dataframe = pandas.read_csv(csv_path, encoding='cp866')
            print('Reading dataframe completed!\n')
            print('Processing %s form...' % form_name)
            dataframe = settings.FORMS[form_name].processing_func(dataframe)
            Parser.save_dataframe(dataframe, form_name)
            print('Processing completed and saved to csv!\n')
