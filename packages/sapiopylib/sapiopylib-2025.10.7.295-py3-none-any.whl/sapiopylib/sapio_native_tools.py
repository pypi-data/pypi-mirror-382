# Sapio Native Tools allows users to read in/out objects against native lib.
import pickle
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_pd_datetime

from sapiopylib.sapio_input_data import SapioInputData

sapio_input_data = SapioInputData()


def get_sapio_input():
    """
    Get the Sapio Input Data object. If it has not been retrieved yet, retrieve it.
    If it has been retrieved, then return what's in the cache.
    :return: The sapio input object fed from Sapio app into this script.
    """
    return sapio_input_data


def set_output_object(output_object):
    """
    Set the output object data, which will upload immediately to Sapio for consumption.
    However, Sapio will not consume it until the script terminates or times out.
    """
    if output_object is None:
        return
    input_data: SapioInputData = get_sapio_input()
    output_file = input_data.get_output_file()
    with open(output_file, "wb") as fp:
        # noinspection PyTypeChecker
        pickle.dump(output_object, fp, protocol=2)

def get_data_frame(src: dict[str, Any]) -> pd.DataFrame:
    """
    Convert Sapio's pandas data frame rep generated from PyScriptUtil class into pandas data frame.
    """
    df: pd.DataFrame = pd.DataFrame.from_records(src['data'])
    date_field_names: set[str] = set(src['dateFieldNameSet'])
    for date_field_name in date_field_names:
        df[date_field_name] = pd.to_datetime(df[date_field_name], unit='ms', origin='unix')
    index: list = src['index']
    if index:
        df.index = index
    else:
        df.reset_index(drop=True)
    return df

def to_java_data_frame(df: pd.DataFrame) -> dict:
    """
    Convert Pandas data frame to rep that can be used to convert into Java's field map list in Sapio.
    """
    modified_df: pd.DataFrame = df.copy()
    datetime_field_name_list: list[str] = list()
    dtype_list = [str(x) for x in df.dtypes.tolist()]
    dtype_dict = dict()
    for i, column in enumerate(df.columns):
        dtype_dict[column] = dtype_list[i]
    for col in df.columns:
        if is_pd_datetime(modified_df[col].dtype):
            modified_df[col] = modified_df[col].astype('int64') // 1e6
            datetime_field_name_list.append(str(col))
    field_map_list = modified_df.to_dict(orient="records")
    plain_index: bool = pd.Index(np.arange(0, len(modified_df))).equals(modified_df.index)
    ret: dict = {
        'data': field_map_list,
        'dateFieldNameSet': datetime_field_name_list,
        'column_data_types': dtype_dict
    }
    if not plain_index:
        ret['index'] = modified_df.index.tolist()
    return ret


