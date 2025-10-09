import smartsheet
import pandas as pd
import gc

configs = {'api_key': 0000000,
           'value_cols': []}

class SmartsheetConnector:
    def __init__(self, configs):
        self._cfg = configs
        self.ss = smartsheet.Smartsheet(self._cfg['api_key'])
        self.ss.errors_as_exceptions(True)

    def get_sheet_as_dataframe(self, sheet_id):
        sheet = self.ss.Sheets.get_sheet(sheet_id)
        col_map = {col.id: col.title for col in sheet.columns}
        # rows = sheet id, row id, cell values or display values
        data_frame = pd.DataFrame([[sheet.id, row.id] +
                                   [cell.value if col_map[cell.column_id] in self._cfg['value_cols']
                                    else cell.display_value for cell in row.cells]
                                   for row in sheet.rows],
                                  columns=['Sheet ID', 'Row ID'] +
                                          [col.title for col in sheet.columns])
        del sheet, col_map
        gc.collect()  # force garbage collection
        return data_frame

    def get_report_as_dataframe(self, report_id):
        rprt = self.ss.Reports.get_report(report_id, page_size=0)
        page_count = int(rprt.total_row_count/10000) + 1
        col_map = {col.virtual_id: col.title for col in rprt.columns}
        data = []
        for page in range(1, page_count + 1):
            rprt = self.ss.Reports.get_report(report_id, page_size=10000, page=page)
            data += [[row.sheet_id, row.id] +
                     [cell.value if col_map[cell.virtual_column_id] in self._cfg['value_cols']
                      else cell.display_value for cell in row.cells] for row in rprt.rows]
            del rprt
        data_frame = pd.DataFrame(data, columns=['Sheet ID', 'Row ID']+list(col_map.values()))
        del col_map, page_count, data
        gc.collect()
        return data_frame