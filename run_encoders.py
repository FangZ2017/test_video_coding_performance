import os
import time


def run_x265(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if cfg_type == 'I':
        intra_period = '1'
        gop_size = '1'
        scenecut = ' '
    elif cfg_type == 'LDP':
        intra_period = '-1'
        gop_size = '0'
        scenecut = ' --no-scenecut '
    elif cfg_type == 'RA':
        intra_period = '32'
        gop_size = '9'
        scenecut = ' '
    else:
        raise Exception('cfg is not defined')

    if curr_seq['rate_control'] == '0':
        encode_time = []
        for qp in qps:
            tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
            cmd = encoder + \
                  ' --input ' + curr_seq['seq_dir'] + \
                  ' --fps ' + curr_seq['frame_rate'] + \
                  ' --frames ' + curr_seq['frame_num'] + \
                  ' --input-res ' + curr_seq['width'] + 'x' + curr_seq['height'] + \
                  ' --input-depth ' + curr_seq['bit_depth'] + \
                  ' --recon ' + tmp_path + '.yuv' + \
                  ' --output ' + tmp_path + '.265' + \
                  ' --qp ' + str(qp) + \
                  ' --b-adapt 0' + \
                  ' --keyint ' + intra_period + \
                  ' --min-keyint ' + intra_period + \
                  scenecut + \
                  ' --bframes ' + gop_size + \
                  ' > ' + tmp_path + '.txt'
            print(cmd)
            start = time.clock()
            os.system(cmd)
            encode_time.append(time.clock() - start)

    return encode_time


def run_hm(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if cfg_type == 'I':
        cfg = 'encoder_intra_main.cfg'
    elif cfg_type == 'LDP':
        cfg = 'encoder_lowdelay_P_main.cfg'
    elif cfg_type == 'RA':
        cfg = 'encoder_randomaccess_main.cfg'
    else:
        raise Exception('cfg is not defined')

    i = 0
    encode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = encoder + \
              ' -c ' + cfg + \
              ' -i ' + curr_seq['seq_dir'] + \
              ' -fr ' + curr_seq['frame_rate'] + \
              ' -wdt ' + curr_seq['width'] + \
              ' -hgt ' + curr_seq['height'] + \
              ' -f ' + curr_seq['frame_num'] + \
              ' --InputBitDepth=' + curr_seq['bit_depth'] + \
              ' -b ' + tmp_path + '.265' + \
              ' -o ' + tmp_path + '.yuv' + \
              ' -q ' + str(qp) + \
              ' --RateControl=' + curr_seq['rate_control'] + \
              ' --TargetBitrate=' + curr_seq['target_bits'][i] + \
              ' > ' + tmp_path + '.txt'
        print(cmd)
        start = time.clock()
        os.system(cmd)
        encode_time.append(time.clock() - start)
        i = i + 1

    return encode_time


def run_vtm(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if cfg_type == 'I':
        cfg = 'encoder_intra_vtm.cfg'
    elif cfg_type == 'LDP':
        cfg = 'encoder_lowdelay_P_vtm.cfg'
    elif cfg_type == 'RA':
        cfg = 'encoder_randomaccess_vtm.cfg'
    else:
        raise Exception('cfg is not defined')

    i = 0
    encode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = encoder + \
              ' -c ' + cfg + \
              ' -i ' + curr_seq['seq_dir'] + \
              ' -fr ' + curr_seq['frame_rate'] + \
              ' -wdt ' + curr_seq['width'] + \
              ' -hgt ' + curr_seq['height'] + \
              ' -f ' + curr_seq['frame_num'] + \
              ' -b ' + tmp_path + '.266' + \
              ' -o ' + tmp_path + '.yuv' + \
              ' -q ' + str(qp) + \
              ' --TemporalSubsampleRatio=1' + \
              ' --InputBitDepth=' + curr_seq['bit_depth'] + \
              ' --InternalBitDepth=' + curr_seq['bit_depth'] + \
              ' --RateControl=' + curr_seq['rate_control'] + \
              ' --TargetBitrate=' + curr_seq['target_bits'][i] + \
              ' > ' + tmp_path + '.txt'
        print(cmd)
        start = time.clock()
        os.system(cmd)
        encode_time.append(time.clock() - start)
        i = i + 1

    return encode_time


def run_av1(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if cfg_type == 'I':
        kf_min = '1'
        kf_max = '1'
    else:
        raise Exception('cfg is not defined')

    i = 0
    encode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = encoder + \
              ' --fps=' + curr_seq['frame_rate'] + '/1' + \
              ' --width=' + curr_seq['width'] + \
              ' --height=' + curr_seq['height'] + \
              ' --limit=' + curr_seq['frame_num'] + \
              ' --kf-max-dist=' + kf_max + \
              ' --kf-min-dist=' + kf_min + \
              ' --max-q=' + str(qp) + \
              ' --min-q=' + str(qp) + \
              ' --bit-depth=' + curr_seq['bit_depth'] + \
              ' --psnr --obu -y ' + \
              ' -o ' + tmp_path + '.ivf' + \
              ' ' + curr_seq['seq_dir'] + \
              ' > ' + tmp_path + '.txt'
        print(cmd)
        start = time.clock()
        os.system(cmd)
        encode_time.append(time.clock() - start)
        decoder_cmd = 'AV1_decoder --i420  -o ' + tmp_path + '.yuv ' + tmp_path + '.ivf'
        os.system(decoder_cmd)
        i = i + 1

    return encode_time


def run_hpm(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if cfg_type == 'I':
        cfg = 'encode_AI.cfg'
    elif cfg_type == 'LDP':
        cfg = 'encode_LDP.cfg'
    elif cfg_type == 'RA':
        cfg = 'encode_RA.cfg'
    else:
        raise Exception('cfg is not defined')

    if curr_seq['bit_depth'] == '8':
        profile_id = '32'
    elif curr_seq['bit_depth'] == '10':
        profile_id = '50'

    i = 0
    encode_time = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        cmd = encoder + \
              ' --config ' + cfg + \
              ' -i ' + curr_seq['seq_dir'] + \
              ' -z ' + curr_seq['frame_rate'] + \
              ' -w ' + curr_seq['width'] + \
              ' -h ' + curr_seq['height'] + \
              ' -f ' + curr_seq['frame_num'] + \
              ' -o ' + tmp_path + '.bin' + \
              ' -r ' + tmp_path + '.yuv' + \
              ' -q ' + str(qp) + \
              ' -d ' + curr_seq['bit_depth'] + \
              ' --profile ' + profile_id + \
              ' --internal_bit_depth ' + curr_seq['bit_depth'] + \
              ' --TemporalSubsampleRatio 1 -v 1' + \
              ' > ' + tmp_path + '.txt'
        print(cmd)
        start = time.clock()
        os.system(cmd)
        encode_time.append(time.clock() - start)
        i = i + 1

    return encode_time


def run_encoder(curr_seq, encoder, qps, seq_result_path, cfg_type):
    if encoder.startswith('HM'):
        encode_time = run_hm(curr_seq, encoder, qps, seq_result_path, cfg_type)
    elif encoder.startswith('x265'):
        encode_time = run_x265(curr_seq, encoder, qps, seq_result_path, cfg_type)
    elif encoder.startswith('VTM'):
        encode_time = run_vtm(curr_seq, encoder, qps, seq_result_path, cfg_type)
    elif encoder.startswith('AV1'):
        encode_time = run_av1(curr_seq, encoder, qps, seq_result_path, cfg_type)
    elif encoder.startswith('HPM'):
        encode_time = run_hpm(curr_seq, encoder, qps, seq_result_path, cfg_type)
    else:
        raise Exception('no function to run ' + encoder + 'encoder')

    return encode_time
