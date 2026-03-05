import ttkbootstrap as ttk
from typing import List, Optional

from ops.ecris.analysis.model import CSD

_FONT = "TkDefaultFont"
_TITLE_FONT = (_FONT, 14)
_SUBTITLE_FONT = (_FONT, 12)
_COLUMN_FONT = (_FONT, 10)

class CSDInfoRow:
    def __init__(self, csd_settings: str | List[str], formats: str | List[str], info_label: str = ''):
        if isinstance(csd_settings, str):
            if not info_label:
                info_label = csd_settings
            csd_settings = [csd_settings]
        if isinstance(formats, str):
            formats = [formats]
        if len(formats) != len(csd_settings):
            raise RuntimeError('Length of formats and csd settings must be the same')
        self.csd_settings = csd_settings
        self.formats = formats
        self.info_label = info_label

class _CSDInfoBlock(ttk.Label):
    def __init__(self, owner: ttk.Frame, csd_setting: str, format: str):
        super().__init__(owner)
        self.csd_setting = csd_setting
        self.format = format
    
    def update(self, csd: Optional[CSD] = None):
        text = 'No CSD Data'
        if csd is not None:
            text = f'{csd.settings[self.csd_setting]:{self.format}}'
        self.config(text=text)

class CSDInfoFrame(ttk.Frame):
    def __init__(self, owner, frame_title: str, 
                 csd_info_rows: CSDInfoRow | List[CSDInfoRow], 
                 column_titles: List[str] | None):
        super().__init__(owner)
        self.frame_title = frame_title
        if not isinstance(csd_info_rows, list):
            csd_info_rows = [csd_info_rows]
        if column_titles is None:
            column_titles = []
        self.info_rows = csd_info_rows
        self.column_titles = column_titles
        self.info_blocks = []
        self.create_widgets()
        self.update_csd_info()

    def create_widgets(self):
        grid_width = 1 + max(len(row.csd_settings) for row in self.info_rows)
        row_start = 1 if self.column_titles is None else 2
        self.columnconfigure(0, weight=1)
        self.columnconfigure(list(range(1, grid_width)), weight=10)
        ttk.Label(self, text=self.frame_title, font=_SUBTITLE_FONT).grid(row=0, column=0,
                                                                         columnspan=grid_width)
        for i, title in enumerate(self.column_titles):
            ttk.Label(self, text=title, font=_COLUMN_FONT).grid(row=1, column=1 + i, sticky='e')

        for i, row in enumerate(self.info_rows):
            n_row = row_start + i
            ttk.Label(self, text=row.info_label).grid(row=n_row, column=0, 
                                                      sticky='w')
            for j, setting in enumerate(row.csd_settings):
                self.info_blocks.append(_CSDInfoBlock(self, setting, row.formats[j]))
                self.info_blocks[-1].grid(row=n_row, column = j + 1, 
                                          sticky='e')

    def update_csd_info(self, csd: CSD | None = None):
        for info_block in self.info_blocks:
            info_block.update(csd)
