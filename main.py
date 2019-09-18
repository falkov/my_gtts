import time
from text_to_video import TextOnImage, GoogleGtts, SubprocessFfmpeg


def main(langs: list, textfile_name: str, dir_output: str, delim: str, slow: bool):
    imagefile_extension = '.png'
    soundfile_extension = '.mp3'
    videofile_extension = '.ts'  # '.mp4'

    start_time = time.time()  # ----------

    langs = langs

    with open('texts_for_transform/'+textfile_name, 'r') as file:
        strings_from_file = file.readlines()

    my_textonimage = TextOnImage(dir_name=dir_output, delim=delim)
    my_gtts = GoogleGtts(langs, dir_name=dir_output, slow=slow)
    my_subprocess_ffmpeg = SubprocessFfmpeg(dir_output=dir_output)

    last_file_index = 0

    for file_index, sentence in enumerate(strings_from_file, start=1):
        if len(sentence) > 1:
            translate = ''
            delim_index = sentence.find(delim)

            if delim_index > 0:  # есть перевод, который нужно вывести внизу картинки
                translate = sentence[delim_index + 4:]
                sentence = sentence[:delim_index]

            my_textonimage.set_text_on_img(
                text=sentence,
                bg='bg.jpg',
                file_name='image_' + str(file_index) + imagefile_extension,
                translate=translate
            )

            my_gtts.save_sound_with_gtts(
                text=sentence,
                file_name='sound_' + str(file_index) + soundfile_extension,
            )

            # my_gtts.save_sound_with_cli(
            #     text=sentence,
            #     file_name='sound_' + str(file_index) + soundfile_extension
            # )

            my_subprocess_ffmpeg.add_silence(
                soundfile_name='sound_' + str(file_index) + soundfile_extension,
                silence_duration_sec=1
            )

            my_subprocess_ffmpeg.create_video_from_image_and_sound(
                image_file='image_' + str(file_index) + imagefile_extension,
                sound_file='sound_' + str(file_index) + soundfile_extension,
                video_file='video_' + str(file_index) + videofile_extension
            )
            last_file_index = file_index

    my_subprocess_ffmpeg.concat_video(
        file_name='video_',
        file_extension=videofile_extension,
        last_file_index=last_file_index,
        outfile_name='_outfile' + videofile_extension
    )

    # my_subprocess_ffmpeg.print_information('my_silence.mp3')

    # os.system(f'afplay short.mp3')
    print(f'{time.time() - start_time} sec')  # ----------


def main_cli(file_txt: str, output_dir: str, lang: str, slow: bool = False):
    gtts = Gtts(file_txt, output_dir, lang, slow)
    gtts.gtts_cli()


if __name__ == "__main__":
    # main(langs=['en-us', 'en-in'], textfile_name='english_ted.txt', dir_output='ted_1/', delim='-:-')
    main(langs=['no'], textfile_name='norveg.txt', dir_output='norveg/', delim='-:-', slow=False)
    # main(langs=['no'], textfile_name='norveg_short.txt', dir_output='norveg/', delim='-:-')

    # main_cli(file_txt='texts_for_transform/proba.txt', output_dir='proba_1', lang='en-us', slow=False)
    # main_cli(file_txt='texts_for_transform/norveg.txt', output_dir='norveg_1', lang='no', slow=True)
