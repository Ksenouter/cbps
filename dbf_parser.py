import parser_settings as settings
import parser_processing
from pathlib import Path
import download_settings
import datetime
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
    def dbf_to_dataframe(path, form_date):
        print('Parsing "%s"...' % path)
        table = dbf.Table(path, codepage='cp866')
        table.open()
        data = {col: Parser.dbf_get_column_by_name(table, col) for col in table.field_names}
        if form_date[:3] in settings.FORMS_WITH_DATE and table.field_names[-1] != settings.FORMS_DATE_COLUMN:
            year = int(form_date[4:8])
            month = int(form_date[8:10])
            day = int(form_date[10:])
            date = datetime.date(year, month, day)
            rows_num = len(data[next(iter(data))])
            data[settings.FORMS_DATE_COLUMN] = [date for i in range(rows_num)]
        table.close()

        return pandas.DataFrame(data)

    @staticmethod
    def create_output_folder():
        if os.path.exists(settings.OUTPUT_PATH) and os.path.isdir(settings.OUTPUT_PATH):
            shutil.rmtree(settings.OUTPUT_PATH, ignore_errors=True)
        Path(settings.OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
        print('Completed output folder recreated!\n')

    @staticmethod
    def save_dataframe(dataframe, form_name, as_source=False):
        path = '{}/{}.csv'.format(settings.SOURCE_CSV_PATH if as_source else settings.CSV_PATH, form_name)
        dataframe.to_csv(path, index=False, encoding='ansi')

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
            result = sorted(files) == sorted([key + '.csv' for key in download_settings.FORMS])
            return True if result else shutil.rmtree(settings.SOURCE_CSV_PATH, ignore_errors=True)
        Path(settings.SOURCE_CSV_PATH).mkdir(parents=True, exist_ok=True)
        return False

    @staticmethod
    def create_source_csv_files(processing_forms=True):
        forms_df = {}
        for form_name in download_settings.FORMS:
            print('Parsing dataframe form dbf for form %s...' % form_name)
            form = settings.FORMS[form_name]
            form_dir = '{}/{}'.format(download_settings.FILES_PATH, form_name)
            dataframes = []
            for date in os.listdir(form_dir):
                date_dir = '{}/{}'.format(form_dir, date)
                file = [file for file in os.listdir(date_dir) if form.lower() in file.lower()][0]
                file_dir = '{}/{}'.format(date_dir, file)
                dataframes.append(Parser.dbf_to_dataframe(file_dir, date))
            dataframe = pandas.concat(dataframes)
            dataframe = Parser.excel_pars_reg_nums(dataframe)
            Parser.save_dataframe(dataframe, form_name, as_source=True)
            print('Parsing for form %s from dbf completed and saved!\n' % form_name)
            if processing_forms:
                forms_df[form_name] = dataframe
        if processing_forms:
            print('Processing forms dataframes...')
            parser_processing.processing_forms(forms_df)
            print('Processing forms dataframes completed!')

    @staticmethod
    def load_dataframe_from_input(csv_path):
        return pandas.read_csv(settings.INPUT_PATH + csv_path, encoding='ansi')

    @staticmethod
    def save_dataframe_to_output(dataframe, csv_path):
        dataframe.to_csv(settings.OUTPUT_PATH + csv_path, index=False, encoding='ansi')

    @staticmethod
    def pars_forms(recreate_sources=False):
        if recreate_sources:
            if os.path.exists(settings.SOURCE_CSV_PATH) and os.path.isdir(settings.SOURCE_CSV_PATH):
                shutil.rmtree(settings.SOURCE_CSV_PATH, ignore_errors=True)
            print('Sources folder deleted!\n')

        Parser.create_output_folder()

        if not Parser.check_source_csv_folder():
            print('Sources csv files not found...\n')
            Parser.create_source_csv_files(processing_forms=True)
            return
        print('Sources csv files found!\n')

        forms_df = {}
        for form_name in download_settings.FORMS:
            print('Reading dataframe from csv for form %s...' % form_name)
            csv_path = '{}/{}.csv'.format(settings.SOURCE_CSV_PATH, form_name)
            dataframe = pandas.read_csv(csv_path, encoding='ansi')
            print('Reading dataframe completed!\n')
            forms_df[form_name] = dataframe
        print('Processing forms dataframes...')
        parser_processing.processing_forms(forms_df)
        print('Processing forms dataframes completed!')
