# import tensorflow as tf
# import matplotlib.pyplot as plt
from pyAudioAnalysis import audioSegmentation as segmentation
from pyAudioAnalysis import audioBasicIO as aIO
# from pydub import AudioSegment
from itertools import product
from functools import partial
from multiprocessing import Pool


# def decode_audio(file_path):
#     audio_binary = tf.io.read_file(file_path)
#     audio, _ = tf.audio.decode_wav(audio_binary)
#     return tf.squeeze(audio, axis=-1)


def float_range(start, stop, step):
    while start <= stop:
        yield start
        start += step


def processing(st_win, st_step, smooth_window, weight, signal, sampling_rate):
    try:
        segments = segmentation.silence_removal(signal=signal, sampling_rate=sampling_rate,
                                                st_win=st_win, st_step=st_step,
                                                smooth_window=smooth_window, weight=weight, plot=False)
        if len(segments) == 2:
            if segments[0][0] <= 0.27 and 0.40 <= segments[0][1] <= 0.47 \
                    and 0.40 <= segments[1][0] <= 0.47 and 1.03 <= segments[1][1]:
                print(f'st_win {st_win}, st_step {st_step}, '
                      f'smooth_window {smooth_window}, weight {weight}')
                return (st_win, st_step, smooth_window, weight)
    except Exception:
        pass


if __name__ == '__main__':
    st_win_range = float_range(0.02, 0.09, 0.01)
    st_step_range = float_range(0.02, 0.09, 0.01)
    smooth_window_range = float_range(0, 1.2, 0.01)
    weight_range = float_range(0, 1, 0.1)
    args = product(st_win_range, st_step_range, smooth_window_range, weight_range)
    sampling_rate, signal = aIO.read_audio_file("/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/0c/55742ae9a671.wav")
    with Pool(3) as pool:
        result = set(pool.starmap(
            partial(processing, signal=signal, sampling_rate=sampling_rate),
            args
        ))
        with open('/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/0c/result.txt',
                  'wt') as result_file:
            if result:
                for i in result:
                    if i:
                        result_file.write(f'st_win {i[0]}, st_step {i[1]}, '
                                          f'smooth_window {i[2]}, weight {i[3]}\n')
    # t1 = segments[1][0]*1000
    # t2 = segments[1][1]*1000
    # newAudio = AudioSegment.from_wav("/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/0c/a82114d0301d.wav")
    # newAudio = newAudio[t1:t2]
    # newAudio.export('/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/0c/a82114d0301d_1.wav', format="wav")
    # waveform = decode_audio('/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/3e/1814d985e9c2.wav')
    # fig, ax = plt.subplots()
    # ax.plot(waveform)
    # plt.show()