import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
from gtts import gTTS


class TextOnImage:
    def __init__(self, dir_name: str):
        if not os.path.exists(dir_name):
            try:
                os.mkdir(dir_name)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {dir_name}')
                exit(1)

        self.dir_name = dir_name

        for file in os.listdir(dir_name):
            os.remove(os.path.join(dir_name, file))

    def set_text_on_img(self, text: str, bg: str, file_name: str):
        bg = Image.open(bg)
        bg_width, bg_height = bg.size

        font = ImageFont.truetype('Arial.ttf', 60)
        font_color = (0, 50, 0)

        draw_img = ImageDraw.Draw(bg)
        text_x, text_y, split_text = self.split_text_to_string(bg_width, bg_height, text, font)
        draw_img.text(xy=(text_x, text_y), text=split_text, fill=font_color, align='center', font=font)

        bg.save(self.dir_name + file_name)

    @staticmethod
    def split_text_to_string(bg_width: int, bg_height: int, text: str, font):
        """разбивает текст на строки, чтобы они входили в ширину"""
        split_text = ''

        text_width, text_height = font.getsize(text=text)

        if text_width < bg_width:
            text_x = (bg_width - text_width) / 2
            text_y = (bg_height - text_height * 2) / 2
            split_text = text
        else:
            letter_width = int(text_width / len(text))
            letters_in_bgwidth = int(bg_width / letter_width)

            string_tail = text
            strings = []
            last_letter = 0

            while len(string_tail) > letters_in_bgwidth - 10:
                last_letter = string_tail.rfind(' ', 0, letters_in_bgwidth)
                strings.append(string_tail[:last_letter])
                string_tail = string_tail[last_letter:]

            strings.append(string_tail[:last_letter])  # append last string_tail after while

            for string in strings:
                split_text += string.strip() + '\n'

            # found max_len of strings for aligning
            max_len = len(strings[0])
            for string in strings:
                max_len = max_len if max_len > len(string) else len(string)

            text_x = (bg_width - max_len * letter_width) / 2
            text_y = (bg_height - text_height * len(strings)) / 2

        return text_x, text_y, split_text


class GoogleGtts:
    def __init__(self, langs: list, dir_name: str):
        if not os.path.exists(dir_name):
            try:
                os.mkdir(dir_name)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {dir_name}')
                exit(1)

        self.dir_name = dir_name
        for file in os.listdir(dir_name):
            os.remove(os.path.join(dir_name, file))

        self.langs = langs

    def save_sound(self, text: str, file_name: str):
        for lang in self.langs:
            tts = gTTS(text=text, lang=lang)
            tts.save_add(self.dir_name + file_name)  # мой метод (режим файла 'a')


class SubprocessFfmpeg:
    def __init__(self, images_dir: str, sounds_dir: str, videos_dir: str):
        if not os.path.exists(videos_dir):
            try:
                os.mkdir(videos_dir)
            except OSError:
                print(f'{self.__class__.__name__}: error! do not create dir {videos_dir}')
                exit(1)

        for file in os.listdir(videos_dir):
            os.remove(os.path.join(videos_dir, file))

        self.images_dir = images_dir
        self.sounds_dir = sounds_dir
        self.videos_dir = videos_dir

    def create_video_from_image_and_sound(self, image_file, sound_file, video_file):
        tempvideofile_name = f'{self.videos_dir}temp_1sec.mp4'

        # create 1 sec video from image
        cmd = [
            'ffmpeg', '-loop', '1',
            '-i', f'{self.images_dir}{image_file}',
            '-c:v', 'libx264', '-t', '1',
            '-pix_fmt', 'yuv420p',
            '-y', tempvideofile_name
        ]
        process = subprocess.call(cmd)

        # load sound on 1sec video
        cmd = [
            'ffmpeg',
            '-i', f'{self.sounds_dir}{sound_file}',
            '-i', tempvideofile_name,
            f'{self.videos_dir}{video_file}'
        ]
        process = subprocess.call(cmd)

    def concat_video(self, file_name: str, file_extension: str, last_file_index: int, outfile_name: str):
        with open('concat.txt', 'w') as file_for_join:
            for index in range(1, last_file_index + 1):
                file_for_join.write(f"file '{self.videos_dir}{file_name}{index}{file_extension}'\n")

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-i', 'concat.txt',
            '-c', 'copy',
            f'{self.videos_dir}{outfile_name}'
        ]
        process = subprocess.call(cmd)

    def add_silence(self, soundfile_name: str, silence_duration_sec):
        silencefile_name = 'my_silence.mp3'

        cmd = [
            'ffmpeg', '-i', f'{self.sounds_dir}{soundfile_name}',
            '-ss', '00:00:00', '-t', f'{silence_duration_sec}',
            '-af', 'volume=0',
            '-y', f'{silencefile_name}'
        ]
        process = subprocess.call(cmd)

        # cmd = [
        #     'ffmpeg',
        #     '-f', 'lavfi', '-i', 'anullsrc',
        #     '-i', 'videos/video_1.avi',
        #     '-c:v', 'copy', '-c:a', 'aac',
        #     'output.avi'
        # ]
        # process = subprocess.call(cmd)

        cmd = [
            'ffmpeg', '-y', '-i',
            f'concat:{self.sounds_dir}{soundfile_name}|{silencefile_name}',
            # '-c',
            '-acodec', 'copy', '-ab', '32000', '-ac', '1',
            f'{self.sounds_dir}{soundfile_name}'
        ]
        process = subprocess.call(cmd)

    def add_beep_to_soundfile(self, soundfile_name: str, beepfile_name: str):
        cmd = [
            'ffmpeg', '-i',
            f'concat:{self.sounds_dir}{soundfile_name}|{beepfile_name}',
            # '-c', 'copy',
            # '-c:a', 'aac', '-b:a', '32k',
            '-y',
            f'{self.sounds_dir}{soundfile_name}'
        ]
        process = subprocess.call(cmd)
