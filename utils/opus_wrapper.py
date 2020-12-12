from ctypes import (
    cdll,
    c_int,
    POINTER,
    Structure,
    c_float,
    c_uint32,
    c_ushort,
    cast,
    pointer,
    c_char_p,
    c_int32,
    c_char,
    Array,
    c_ubyte,
    c_uint64,
    c_uint8,
    c_uint,
    c_uint16,
    c_ushort,
    c_short,
byref
)

OPUS_OK = 0

OPUS_BAD_ARG = -1
OPUS_BANDWIDTH_NARROWBAND = 1101  # 4kHz bandpass
OPUS_BANDWIDTH_MEDIUMBAND = 1102  # 6kHz bandpass
OPUS_BANDWIDTH_WIDEBAND = 1103  # 8kHz bandpass
OPUS_BANDWIDTH_SUPERWIDEBAND = 1104  # 12kHz bandpass
OPUS_BANDWIDTH_FULLBAND = 1105  # 20kHz bandpass
OPUS_INVALID_PACKET = -4
OPUS_BANDWIDTH = {OPUS_BANDWIDTH_NARROWBAND: 4000, OPUS_BANDWIDTH_MEDIUMBAND: 6000,
                  OPUS_BANDWIDTH_WIDEBAND: 8000, OPUS_BANDWIDTH_SUPERWIDEBAND: 12000,
                  OPUS_BANDWIDTH_FULLBAND: 20000}


class silk_DecControlStruct(Structure):
    _fields_ = [
        ('nChannelsAPI', c_int),
        ('nChannelsInternal', c_int),
        ('API_sampleRate', c_int),
        ('internalSampleRate', c_int),
        ('payloadSize_ms', c_int),
        ('prevPitchLag', c_int)
    ]


class OpusDecoderState(Structure):
    _fields_ = [
        ('celt_dec_offset', c_int),
        ('silk_dec_offset', c_int),
        ('channels', c_int),
        ('Fs', c_int),
        ('silk_DecControlStruct', silk_DecControlStruct),
        ('decode_gain', c_int),
        ('arch', c_int),
        ('stream_channels', c_int),
        ('bandwidth', c_int),
        ('mode', c_int),
        ('prev_mode', c_int),
        ('frame_size', c_int),
        ('prev_redundancy', c_int),
        ('last_packet_duration', c_int),
        ('softclip_mem', c_float * 2),
        ('rangeFinal', c_uint32)
    ]


class OpusDecoder:
    def __init__(self):
        self.lib = cdll.LoadLibrary('/home/vyacheslav/proj/project1/3rd/lib/libopus.so.0.8.0')

    def create_state(self, sample_rate: c_int, channels: c_int) -> POINTER(OpusDecoderState):
        error = pointer(c_int())
        decoder_state = cast(self.lib.opus_decoder_create(sample_rate, channels, error),
                             POINTER(OpusDecoderState))
        if error.contents.value != OPUS_OK:
            raise Exception(f'Decoder state  create error {error.contents.value}')
        return decoder_state

    def init_state(self, decoder_state: POINTER(OpusDecoderState), sample_rate: c_int, channels: c_int):
        result = self.lib.opus_decoder_init(decoder_state, sample_rate, channels)
        if result != OPUS_OK:
            raise Exception(f'Decoder state init error {result}')

    def destroy_state(self, decoder_state: POINTER(OpusDecoderState)):
        self.lib.opus_decoder_destroy(decoder_state)

    def packet_get_bandwidth(self, data: Array) -> int:
        result = self.lib.opus_packet_get_bandwidth(data)
        if result == OPUS_INVALID_PACKET:
            raise Exception('The compressed data passed is corrupted or of an unsupported type')
        return OPUS_BANDWIDTH.get(result)

    def packet_get_nb_channels(self, data: Array) -> int:
        result = self.lib.opus_packet_get_nb_channels(data)
        if result == OPUS_INVALID_PACKET:
            raise Exception('The compressed data passed is corrupted or of an unsupported type')
        return result

    def packet_get_nb_frames(self, data: Array, length: c_int) -> int:
        result = self.lib.opus_packet_get_nb_frames(data, length)
        if result == OPUS_BAD_ARG:
            raise Exception('Insufficient data was passed to the function')
        elif result == OPUS_INVALID_PACKET:
            raise Exception('The compressed data passed is corrupted or of an unsupported type')
        return result

    def packet_get_nb_samples(self, data: Array, length: c_int, sample_rate: c_int) -> int:
        result = self.lib.opus_packet_get_nb_samples(data, length, sample_rate)
        # if result == OPUS_BAD_ARG:
        #     raise Exception('Insufficient data was passed to the function')
        # elif result == OPUS_INVALID_PACKET:
        #     raise Exception('The compressed data passed is corrupted or of an unsupported type')
        return result

    def packet_get_samples_per_frame(self, data: Array, sample_rate: c_int) -> int:
        result = self.lib.opus_packet_get_samples_per_frame(data, sample_rate)
        return result

    def decode(self, decoder_state: POINTER(OpusDecoderState), data: Array, length: c_int,
               pcm: Array, frame_size: c_int, decode_fec: c_int) -> int:
        result = self.lib.opus_decode(decoder_state, data, length, pcm, frame_size, decode_fec)
        return result


if __name__ == '__main__':
    decoder = OpusDecoder()
    with open('/home/vyacheslav/proj/project1/data_set/public_lecture_1/0/0a/eb9e6faa1b5b.opus', 'rb') as data_file:
        data = data_file.read()
        length = c_int(len(data))
        data = (c_char * len(data))(*data)
    sample_rate = c_int(decoder.packet_get_bandwidth(data))
    channels = decoder.packet_get_nb_channels(data)
    print(f'Gets the number of channels from an Opus packet {channels}')
    print(f'Gets the number of frames in an Opus packet {decoder.packet_get_nb_frames(data, length)}')
    for i in range(400, 20400):
        result = decoder.packet_get_nb_samples(data, length, c_int(i))
        if result != -4:
            print(result)
    # print(f'Gets the number of samples of an Opus packet {decoder.packet_get_nb_samples(data, length, sample_rate)}')
    # frame_size = decoder.packet_get_samples_per_frame(data, sample_rate)
    # print(f'Gets the number of samples per frame from an Opus packet {frame_size}')
    # pcm = (c_short * (frame_size * channels * c_short().__sizeof__()))()
    # print(len(pcm))
    # decode_fec = c_int(0)
    # decoder_state = decoder.create_state(sample_rate, c_int(channels))
    # result = decoder.decode(decoder_state, data, length, pcm, frame_size, decode_fec)
    # print(result)
    # decoder.destroy_state(decoder_state)
    # print([i for i in pcm])

