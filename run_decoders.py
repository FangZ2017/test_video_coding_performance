import os
import time


def run_hm_deocder(encoder, qps, seq_result_path):
    decode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = 'HM16_7_decoder' + \
            ' -b ' + tmp_path + '.265' + \
            ' -o ' + tmp_path + '_deco.yuv' + \
            ' > ' + tmp_path + '_deco.txt'
        start = time.clock()
        os.system(cmd)
        decode_time.append(time.clock() - start)

    return decode_time


def run_vtm_deocder(encoder, qps, seq_result_path):
    decode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = 'VTM10_0_decoder' + \
            ' -b ' + tmp_path + '.266' + \
            ' -o ' + tmp_path + '_deco.yuv' + \
            ' > ' + tmp_path + '_deco.txt'
        start = time.clock()
        os.system(cmd)
        decode_time.append(time.clock() - start)

    return decode_time


def run_av1_deocder(encoder, qps, seq_result_path):
    decode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = 'AV1_decoder --i420  -o ' + tmp_path + '_deco.yuv ' + tmp_path + '.ivf' + ' > ' + tmp_path + '_deco.txt'
        start = time.clock()
        os.system(cmd)
        decode_time.append(time.clock() - start)

    return decode_time


def run_hpm_deocder(encoder, qps, seq_result_path):
    decode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = 'HPM9_0_decoder' + \
            ' -i ' + tmp_path + '.bin' + \
            ' -o ' + tmp_path + '_deco.yuv' + \
            ' > ' + tmp_path + '_deco.txt'
        start = time.clock()
        os.system(cmd)
        decode_time.append(time.clock() - start)

    return decode_time


def run_decoder(encoder, qps, seq_result_path):
    if encoder.startswith('HM') | encoder.startswith('x265'):
        decode_time = run_hm_deocder(encoder, qps, seq_result_path)
    elif encoder.startswith('VTM'):
        decode_time = run_vtm_deocder(encoder, qps, seq_result_path)
    elif encoder.startswith('AV1'):
        decode_time = run_av1_deocder(encoder, qps, seq_result_path)
    elif encoder.startswith('HPM'):
        decode_time = run_hpm_deocder(encoder, qps, seq_result_path)
    else:
        raise Exception('no function to run ' + encoder + 'decoder')

    return decode_time
