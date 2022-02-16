import time
import os
import sys
import json
from run_encoders import run_encoder
from run_decoders import run_decoder
from cal_results import cal_results
from save_results import save_results


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


if __name__ == '__main__':
    # ----------------------------------------------------------------------------------
    # modify json file and parameter
    with open('test.json', 'r') as f:
        test_sequences = json.load(f)

    qps = [22, 27, 32, 37] # QP setting
    encoders = ['HM16_7', 'HPM9_0', 'x265', 'AV1', 'VTM10_0']  # set encoder
    cfg_type = 'I'  # I or LDP or RA
    save_rec_yuv_flag = False  # true : save reconstruction YUV
    save_deco_yuv_flag = False  # true : save decoded YUV
    # ----------------------------------------------------------------------------------
    results_path = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    os.mkdir(results_path)  # make folder to store results
    sys.stdout = Logger('command.log', sys.stdout)  # log for encode command
    print('\n-----------------------------------------------------------------------')
    print('--------------------------' + results_path + '--------------------------\n')
    results = {}
    for seq_name in test_sequences:
        # loop for all sequences
        curr_seq = test_sequences[seq_name]
        seq_result_path = results_path + '/' + seq_name
        os.mkdir(seq_result_path)  # make folder to store bitstream and encode information
        results[seq_name] = {}
        # loop for all encoders
        for encoder in encoders:
            results[seq_name][encoder] = {}
            # run encoder
            results[seq_name][encoder]['encode_time'] = run_encoder(curr_seq, encoder, qps, seq_result_path, cfg_type)
            # run decoder
            results[seq_name][encoder]['decode_time'] = run_decoder(encoder, qps, seq_result_path)
            # verify consistency and calculate PSNR, rate
            results[seq_name][encoder]['bits'], results[seq_name][encoder]['psnr'] = cal_results(curr_seq, encoder, qps, seq_result_path, save_rec_yuv_flag, save_deco_yuv_flag)
    # make folder to store results
    perf_result_path = results_path + '/figure_results'
    os.mkdir(perf_result_path)
    save_results(results, qps, perf_result_path, encoders)
