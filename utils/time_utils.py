from os.path import getmtime
from time import localtime, strftime, struct_time

def get_file_modification_time(file_path: str, time_format = '%Y-%m-%d %H:%M:%S') -> str:
    file_modification_time_utc_timestamp: float = getmtime(file_path)
    file_modification_time_local: struct_time = localtime(file_modification_time_utc_timestamp)
    file_modification_time_local_formatted: str = strftime(time_format, file_modification_time_local)
    
    return file_modification_time_local_formatted