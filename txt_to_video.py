import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
from gtts import gTTS


class Gtts:
    def __init__(self, file_txt: str, output_dir: str, lang: str, slow: bool, delim: str = '-:-'):
        self.file_txt = file_txt
        self.output_dir = output_dir
        self.lang = lang
        self.slow = slow

        self.check_dir_file()

        self.delim = delim
        self.file_for_gtts = f'{self.output_dir}/file_for_gtts.txt'
        self.file_translates = f'{self.output_dir}/translates.txt'

    def check_dir_file(self):
        if not os.path.exists(self.file_txt):
            print(f'{self.__class__.__name__}: error! not exist file: {self.file_txt}')
            exit(1)

        if not os.path.exists(self.output_dir):
            try:
                os.mkdir(self.output_dir)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {self.output_dir}')
                exit(1)

        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))

    def gtts_cli(self):
        self.divide_filetxt_to_text_and_translate()

        subprocess.run([
            'gtts-cli',
            '--file', f'{self.file_for_gtts}',
            '--output', f'{self.output_dir}/from_gtts.mp3',
            '--lang', f'{self.lang}',
            '--slow' if self.slow else ''
        ])

    def divide_filetxt_to_text_and_translate(self):
        sentences = []
        translates = []

        with open(self.file_txt, 'r') as file:
            strings_from_file = file.readlines()

        for string in strings_from_file:
            if len(string) > 2:
                delim_index = string.find(self.delim)

                if delim_index > 0:  # есть перевод
                    translates.append(string[delim_index + len(self.delim)+1:].strip())
                    sentences.append(string[:delim_index].strip())
                else:
                    sentences.append(string)

        with open(self.file_for_gtts, "w") as file:
            file.writelines(map(lambda x: x+'\n', sentences))

        with open(self.file_translates, "w") as file:
            file.writelines(map(lambda x: x+'\n', translates))



