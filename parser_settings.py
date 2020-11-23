from collections import namedtuple
import parser_processing


Form = namedtuple('Form', 'pars_file processing_func')
FORMS = {
    '101': Form('B1.DBF', parser_processing.processing_form_101),
    '102': Form('_P1.DBF', parser_processing.processing_form_102),
    '135': Form('_135B.DBF', parser_processing.processing_form_135),
}

CSV_PATH = './csv'

EXCEL_REG_NUMS = './reg_nums.xlsx'
