# Spinners: sindresorhus Sindre Sorhus (https://github.com/sindresorhus/cli-spinners/)
#
# MIT License
# Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https://sindresorhus.com)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from utils.format_utils import format_red, format_green
from json import load as json_from_file
from os import path
from threading import Thread
from time import sleep

def hide_cursor() -> None:
    print('\033[?25l', end = '')

def show_cursor() -> None:
    print('\033[?25h', end = '')

def clear_line() -> None:
    print('\x1b[2K', end = '\r')

class Spinner():
    def __init__(self, text: str = '', spinner: str = ''):
        utils_dir_path: str = path.dirname(__file__)
        spinners_file_path: str = path.join(utils_dir_path, 'spinners.json')
        with open(spinners_file_path, 'r') as spinners_file: spinners: dict = json_from_file(spinners_file)
        avalable_spinners: list[str] = [ key for key in spinners.keys() ]
        selected_spinner_name: str = spinner if spinner in avalable_spinners else 'dots'
        self.selected_spinner: dict = spinners[selected_spinner_name]
        self.refresh_interval: float = self.selected_spinner['interval'] / 1000
        self.continue_spinner: bool = True
        self.text = text

    def get_spinner_status(self):
        return bool(self.continue_spinner)

    def print_spinner(self):
        hide_cursor()
        while self.continue_spinner:
            for frame in self.selected_spinner['frames']:
                print(f'{frame} {self.text}', end = '\r')
                sleep(self.refresh_interval)
                if not self.continue_spinner: break
        

    def succeed(self, text: str = ''):
        self.continue_spinner = False
        clear_line()
        show_cursor()
        print(f'{format_green('✔')} {text}')

    def fail(self, text: str = ''):
        self.continue_spinner = False
        clear_line()
        show_cursor()
        print(f'{format_red('🗙')} {text}')

    def start(self, text: str = ''):
        self.continue_spinner = True
        self.text = text if bool(text) else self.text
        spinner_thread = Thread(target = self.print_spinner, daemon = True)
        spinner_thread.start()