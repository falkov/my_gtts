import time
from text_to_video import TextOnImage, GoogleGtts, SubprocessFfmpeg


def main():
    images_dir = 'images/'
    sounds_dir = 'sounds/'
    videos_dir = 'videos/'
    text_file = 'english_text.txt'
    imagefile_extension = '.png'
    soundfile_extension = '.mp3'
    videofile_extension = '.mp4'

    start_time = time.time()  # ----------

    langs = ['en-us', 'en-in']

    with open(text_file, 'r') as file:
        strings_from_file = file.readlines()

    my_textonimage = TextOnImage(dir_name=images_dir)
    my_gtts = GoogleGtts(langs, dir_name=sounds_dir)
    my_subprocess_ffmpeg = SubprocessFfmpeg(
        images_dir=images_dir,
        sounds_dir=sounds_dir,
        videos_dir=videos_dir
    )

    last_file_index = 0

    for file_index, sentence in enumerate(strings_from_file, start=1):
        if len(sentence) > 5:
            my_textonimage.set_text_on_img(
                text=sentence,
                bg='bg.jpg',
                file_name='image_' + str(file_index) + imagefile_extension
            )

            my_gtts.save_sound(
                text=sentence,
                file_name='sound_' + str(file_index) + soundfile_extension
            )

            my_subprocess_ffmpeg.add_silence(
                soundfile_name='sound_' + str(file_index) + soundfile_extension,
                silence_duration_sec=1
            )

            # my_subprocess_ffmpeg.add_beep_to_soundfile(
            #     soundfile_name='sound_' + str(file_index) + soundfile_extension,
            #     beepfile_name='mybeep.mp3'
            # )

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
        outfile_name='outfile' + videofile_extension
    )

    # os.system(f'afplay short.mp3')
    print(f'{time.time() - start_time} sec')  # ----------


if __name__ == "__main__":
    main()
