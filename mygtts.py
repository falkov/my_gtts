from gtts import gTTS
import os
import logging

logging.basicConfig(format="%(asctime)s  %(filename)s:%(lineno)d  %(message)s", datefmt="%Y-%m-%d  %H:%M.%S",
                    level=logging.DEBUG, filename=f'{os.path.dirname(__file__)}/_mylog.log')


class MyGTTS:
    def __init__(self):
        self.langs = ['en', 'en-au', 'en-ca', 'en-in', 'en-nz', 'en-us']

    # def save_pause(self, mp3_file):
    #     tts = gTTS(text='')
    #     tts.save_add(mp3_file)  # мой метод

    def save_audiofile_from_textfile(self, text_file, mp3_file, lang='en'):
        if not os.path.exists(text_file):
            logging.info(f'No file: "{text_file}"')
            exit(1)

        with open(text_file, 'r') as file:
            text_from_file = file.read()

        tts = gTTS(text=text_from_file, lang=lang)
        tts.save(mp3_file)

    def save_audiofile_from_textfile_all_lang(self, text_file, mp3_file):
        if not os.path.exists(text_file):
            logging.info(f'No file: "{text_file}"')
            exit(1)

        os.remove(f'{os.path.dirname(__file__)}/{mp3_file}')

        with open(text_file, 'r') as file:
            strings_from_file = file.readlines()

        for sentence in strings_from_file:
            if len(sentence) > 10:
                for lang in self.langs:
                    tts = gTTS(text=sentence, lang=lang)
                    tts.save_add(mp3_file)  # метод добавлен мной в библиотеку gtts (режим открытия файла 'a')

    def save_with_add(self, text, mp3_file, lang='en'):
        tts = gTTS(text=text, lang=lang)
        tts.save_add(mp3_file)

    def save_with_add_all_langs(self, text, mp3_file):
        for lang in self.langs:
            tts = gTTS(text=text, lang=lang)
            tts.save_add(mp3_file)      # метод добавлен мной в библиотеку gtts (режим открытия файла 'a')


def main():
    # import datetime
    # print(datetime.datetime.today().strftime("%d.%m.%Y  %H:%M"))

    mygtts = MyGTTS()
    mygtts.save_audiofile_from_textfile_all_lang(text_file="short_text.txt", mp3_file='short.mp3')

    # mygtts.save_with_add_all_langs(text='Hello! When would it be convenient for you?', mp3_file='add_1.mp3')

    # os.system(f'afplay short.mp3')

if __name__ == "__main__":
    main()
