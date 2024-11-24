# spinners.json from https://github.com/sindresorhus/cli-spinners used under MIT License:
# MIT License
# Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https://sindresorhus.com)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json, sys

from os import path

from utils.dict_utils import get_value_if_key_exists

def get_spinners_from_json_file(spinners_json_filename: str = 'spinners.json') -> dict:
    utils_dir_path: str = path.abspath(path.dirname(__file__))
    spinners_file_path: str =  path.join(utils_dir_path, 'spinners.json')
    with open (spinners_file_path, 'r') as spinners_json:
        spinners: dict = json.load(spinners_json)

    return spinners

def get_spinner(config: dict) -> dict:
    spinners = get_spinners_from_json_file('spinners.json')
    unicode_is_supported: bool = bool(sys.stdout.encoding.lower().startswith('utf'))
    selected_spinner_name: str | bool = get_value_if_key_exists(config, 'spinner')
    valid_spinner_names: list[str] = [ spinner_name for spinner_name in spinners.keys() ]
    selected_spinner_is_valid: bool = bool(selected_spinner_name in valid_spinner_names and unicode_is_supported)
    spinner_name: str | bool = selected_spinner_name if selected_spinner_is_valid  else 'line'

    return spinners[spinner_name]
