from __future__ import annotations

import pandas as pd
from pandas._typing import Axes, Dtype

from catwalk_common import CommonCaseFormat, OpenCase


class CCFDataFrame(pd.DataFrame):
    def __init__(
        self,
        data: list[CommonCaseFormat] | list[OpenCase] | None = None,
        index: Axes | None = None,
        columns: Axes | None = None,
        dtype: Dtype | None = None,
        copy: bool | None = None,
    ):
        if data:
            self.__setup(data, index, columns, dtype, copy)
        else:
            super().__init__(data, index, columns, dtype, copy)

    def __setup(
        self,
        data: list[CommonCaseFormat] | list[OpenCase],
        index: Axes | None = None,
        columns: Axes | None = None,
        dtype: Dtype | None = None,
        copy: bool | None = None,
    ):
        is_not_empty_list = isinstance(data, list) and len(data) > 0

        if not is_not_empty_list:
            self.__raise_type_error()

        _columns = self.__columns(data)

        super().__init__(
            [case.to_df_row() for case in data],
            index,
            columns or _columns,
            dtype,
            copy,
        )

    def __columns(self, data: list[CommonCaseFormat] | list[OpenCase]):
        if all(isinstance(case, OpenCase) for case in data):
            return OpenCase.df_columns()
        elif all(isinstance(case, CommonCaseFormat) for case in data):
            return CommonCaseFormat.df_columns()
        else:
            self.__raise_type_error()

    def __raise_type_error(self):
        raise TypeError(
            "Argument 'data' has to be either of type list[CommonCaseFormat] or list[OpenCase]"
        )
