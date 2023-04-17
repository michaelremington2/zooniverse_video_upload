import os
import ffmpeg
import glob
import time
import subprocess
from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

#sudo apt-get install ffmpeg
# cite https://gist.github.com/ESWZY/a420a308d3118f21274a0bc3a6feb1ff
# https://panoptes-python-client.readthedocs.io/en/latest/
# https://www.zooniverse.org/talk/18/1439900
#https://stackoverflow.com/questions/65570944/how-to-split-a-video-in-parts-using-python
#https://stackoverflow.com/questions/63631973/how-can-i-use-python-to-speed-up-a-video-without-dropping-frames


def compress_video(video_full_path, size_upper_bound, output_file_folder=None, two_pass=True, filename_suffix='cps_'):
    """
    Compress video file to max-supported size.
    :param video_full_path: the video you want to compress.
    :param size_upper_bound: Max video size in KB.
    :param two_pass: Set to True to enable two-pass calculation.
    :param filename_suffix: Add a suffix for new video.
    :return: out_put_name or error
    """
    filename, extension = os.path.splitext(video_full_path)
    extension = '.mp4'
    if output_file_folder is None:
        output_file_name = filename + filename_suffix + extension
    else:
        video_file_name = filename.split(os.sep)[-1]
        output_file_name = output_file_folder + video_file_name + filename_suffix + extension
        print(output_file_name)


    # Adjust them to meet your minimum requirements (in bps), or maybe this function will refuse your video!
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        probe = ffmpeg.probe(video_full_path)
        # Video duration, in s.
        duration = float(probe['format']['duration'])
        # Audio bitrate, in bps.
        audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
        # Target total bitrate, in bps.
        target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print('Bitrate is extremely low! Stop compress!')
            return False

        # Best min size, in kB.
        best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
        if size_upper_bound < best_min_size:
            print('Quality not good! Recommended minimum size:', '{:,}'.format(int(best_min_size)), 'KB.')
            # return False

        # Target audio bitrate, in bps.
        audio_bitrate = audio_bitrate

        # target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
            return False

        i = ffmpeg.input(video_full_path)
        if two_pass:
            ffmpeg.output(i, os.devnull,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                          ).overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()
        else:
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
            return output_file_name
        elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):  # Do it again
            return compress_video(output_file_name, size_upper_bound)
        else:
            return False
    except FileNotFoundError as e:
        print('You do not have ffmpeg installed!', e)
        print('You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251')
        return False

# def video_speed_change(input_file, output_file, speed_multiplier):
#     # FFmpeg command to speed up video
#     ffmpeg_cmd = f'ffmpeg -i {input_file} -filter:v "setpts={1/speed_multiplier}*PTS" {output_file}'

#     # run FFmpeg command
#     subprocess.call(ffmpeg_cmd, shell=True)

def video_speed(input_file, speed_multiplier,output_file_folder=None):
    # Import video clip
    filename, extension = os.path.splitext(input_file)
    extension = '.mp4'
    filename_suffix = 'speed_{}x'.format(speed_multiplier)
    if output_file_folder is None:
        output_file_name = filename + filename_suffix + extension
    else:
        video_file_name = filename.split(os.sep)[-1]
        output_file_name = output_file_folder + video_file_name + filename_suffix + extension
        print(output_file_name)

    clip = VideoFileClip(input_file)
    print("fps: {}".format(clip.fps))

    # Modify the FPS
    clip = clip.set_fps(clip.fps * speed_multiplier)

    # Apply speed up
    final = clip.fx(vfx.speedx, speed_multiplier)
    print("fps: {}".format(final.fps))

    # Save video clip
    final.write_videofile(output_file_name)
    print('fps increase complete')
    return output_file_name


# Compress input.mp4 to 50MB and save as output.mp4
#compress_video('input.mp4', 'output.mp4', 50 * 1000)

def main():
    start = time.time()
    input_file = 'Full_videos/Bonnie07222021.mp4'
    cur_dir = os.getcwd()
    #input_file = os.path.join(cur_dir,input_file)
    #output = os.path.join(cur_dir,'compressed_video/test.mp4')
    input_file = os.path.join(cur_dir,'compressed_video/test.mp4')
    output = os.path.join(cur_dir,'compressed_video/test_compressed.mp4')
    print(output)
    file_name = compress_video(video_full_path=input_file, size_upper_bound = 50 * 1000, output_file_folder=output, filename_suffix='speed3_')
    #video_speed(input_file=input_file, output_file = output, speed_multiplier=3)
    #print(file_name)
    end = time.time()
    print(end - start)


if __name__=="__main__":
    main()