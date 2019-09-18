import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
from gtts import gTTS
import ffmpeg


class TextOnImage:
    def __init__(self, dir_name: str, delim: str):
        if not os.path.exists(dir_name):
            try:
                os.mkdir(dir_name)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {dir_name}')
                exit(1)

        self.delim = delim
        self.dir_name = dir_name

        for file in os.listdir(dir_name):
            os.remove(os.path.join(dir_name, file))

    def set_text_on_img(self, text: str, bg: str, file_name: str, translate: str):
        bg = Image.open(bg)
        bg_width, bg_height = bg.size
        bg_width -= 100  # для полей по краям картинки

        text_font = ImageFont.truetype('Arial.ttf', 60)
        text_font_color = (0, 0, 50)

        draw_img = ImageDraw.Draw(bg)
        text_x, text_y, split_text = self.split_text_to_string(bg_width, bg_height, text, text_font)
        draw_img.text(xy=(text_x, text_y), text=split_text, fill=text_font_color, align='center', font=text_font)

        if len(translate) > 0:
            transl_font = ImageFont.truetype('Arial.ttf', 45)
            transl_font_color = (50, 50, 50)

            transl_x, transl_y, split_text = self.split_text_to_string(bg_width, bg_height, translate, transl_font)
            draw_img.text(xy=(transl_x, transl_y+300), text=split_text, fill=transl_font_color, align='center', font=transl_font)

        bg.save(self.dir_name + file_name)

    @staticmethod
    def split_text_to_string(bg_width: int, bg_height: int, text: str, font):
        """разбивает текст на строки, чтобы они входили в ширину картинки"""
        split_text = ''
        # strings = []

        text_width, text_height = font.getsize(text=text)

        if text_width < bg_width:
            text_x = (bg_width - text_width) / 2
            text_y = (bg_height - text_height * 2) / 2
            split_text = text
        else:
            letter_width = int(text_width / len(text))
            letters_in_bgwidth = int(bg_width / letter_width) - 6

            string_tail = text
            strings = []
            last_letter = 0

            while len(string_tail) >= letters_in_bgwidth:
                last_letter = string_tail.rfind(' ', 0, letters_in_bgwidth)
                strings.append(string_tail[:last_letter])
                string_tail = string_tail[last_letter:]

            strings.append(string_tail[:last_letter])  # append last string_tail after while

            for string in strings:
                split_text += string.strip() + '\n'

            # found max_text_width of strings for aligning
            max_text_width, _ = font.getsize(text=strings[0])
            for string in strings:
                next_text_width, _ = font.getsize(text=string)
                max_text_width = max_text_width if max_text_width > next_text_width else next_text_width

            text_x = ((bg_width - max_text_width) / 2) + 50
            text_y = (bg_height - text_height * len(strings)) / 2

        return text_x, text_y, split_text


class GoogleGtts:
    def __init__(self, langs: list, dir_name: str, slow: bool):
        self.dir_name = dir_name
        self.langs = langs
        self.slow = slow

        self.check_and_clear_dir()

    def check_and_clear_dir(self):
        if not os.path.exists(self.dir_name):
            try:
                os.mkdir(self.dir_name)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {self.dir_name}')
                exit(1)

        for file in os.listdir(self.dir_name):
            os.remove(os.path.join(self.dir_name, file))

    def save_sound_with_gtts(self, text: str, file_name: str):
        for lang in self.langs:
            tts = gTTS(text=text, lang=lang, slow=self.slow)
            tts.save_add(self.dir_name + file_name)  # мой метод (режим файла 'a')

    def save_sound_with_cli(self, text: str, file_name: str):
        for lang in self.langs:
            process = subprocess.run([
                'gtts-cli',
                f'"{text}"',
                # '--file', f'{self.file_for_gtts}',
                '--output', self.dir_name + file_name,
                '--lang', lang,
                # '--slow' if self.slow else '',
        ])
        # print(process.args)

class SubprocessFfmpeg:
    def __init__(self, dir_output: str):
        if not os.path.exists(dir_output):
            try:
                os.mkdir(dir_output)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {dir_output}')
                exit(1)

        for file in os.listdir(dir_output):
            os.remove(os.path.join(dir_output, file))

        self.dir_output = dir_output

    def create_video_from_image_and_sound(self, image_file, sound_file, video_file):
        subprocess.run([
            'ffmpeg',
            '-loop', '1', '-framerate', '10',
            '-i', f'{self.dir_output}{image_file}',
            '-i', f'{self.dir_output}{sound_file}',
            # '-c:v', 'libx264',  # из-за этого кодека видео отстает от звука
            # '-tune', 'stillimage',
            '-c:a', 'aac',
            # '-pix_fmt', 'yuv420p',
            '-shortest', f'{self.dir_output}{video_file}',
            '-hide_banner'
        ])

    def concat_video(self, file_name: str, file_extension: str, last_file_index: int, outfile_name: str):
        # создать файл со списком файлов для склейки
        with open(f'{self.dir_output}concat.txt', 'w') as file_for_join:
            for index in range(1, last_file_index + 1):
                file_for_join.write(f"file '{file_name}{index}.ts'\n")

        # склеить файлы
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-i', f'{self.dir_output}concat.txt',
            # '-c', 'copy', f'{self.dir_output}{outfile_name}'
            f'{self.dir_output}{outfile_name}',
            '-hide_banner'
        ])

    def add_silence(self, soundfile_name: str, silence_duration_sec):
        if not os.path.exists(f'{self.dir_output}my_silence.mp3'):
            # создать файл тишины фильтром
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc', '-ac', '1',
                '-t', f'{silence_duration_sec}', '-y', f'{self.dir_output}my_silence.mp3',
                '-hide_banner'
            ])

        subprocess.run([
            'ffmpeg', '-i',
            f'concat:{self.dir_output}{soundfile_name}|{self.dir_output}my_silence.mp3',
            '-y', f'{self.dir_output}temp_file.mp3',
            '-hide_banner'
        ])

        os.renames(f'{self.dir_output}temp_file.mp3', f'{self.dir_output}{soundfile_name}')
