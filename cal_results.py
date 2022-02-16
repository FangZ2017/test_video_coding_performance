import numpy as np
import os


def cal_results(curr_seq, encoder, qps, seq_result_path, save_rec_yuv_flag, save_deco_yuv_flag):
    # only for yuv420 format
    luma_size = int(curr_seq['width']) * int(curr_seq['height'])
    bit_depth = int(curr_seq["bit_depth"])
    max_value = 2 ** bit_depth - 1
    if bit_depth > 8:
        bufsize = int(luma_size * 2)
    else:
        bufsize = int(luma_size * 1.5)
    frame_num = int(curr_seq['frame_num'])

    psnr = []
    bits = []
    for qp in qps:
        tmp_path = seq_result_path + '/' + encoder + '-QP' + str(qp)
        rec_yuv_path = tmp_path + '.yuv'
        deco_yuv_path = tmp_path + '_deco.yuv'
        if encoder.startswith('HM') | encoder.startswith('x265'):
            bs_path = tmp_path + '.265'
        elif encoder.startswith('VTM'):
            bs_path = tmp_path + '.266'
        elif encoder.startswith('AV1'):
            bs_path = tmp_path + '.ivf'
        elif encoder.startswith('HPM'):
            bs_path = tmp_path + '.bin'

        # calculate rate
        bits.append(os.stat(bs_path).st_size * 8 * int(curr_seq['frame_rate']) / frame_num / 1000)
        # verify consistency and calculate psnr
        frame_psnr = np.zeros(frame_num)
        with open(rec_yuv_path, 'rb') as fp1, open(deco_yuv_path, 'rb') as fp2, open(curr_seq['seq_dir'], 'rb') as fp3:
            for i in range(0, frame_num):
                b1 = fp1.read(bufsize)
                b2 = fp2.read(bufsize)
                b3 = fp3.read(bufsize)
                if b1 != b2:
                    raise Exception(str(i) + 'th is not identical')

                rec_luma = np.fromstring(b1, 'B')
                orig_luma = np.fromstring(b3, 'B')
                resi = rec_luma[0: luma_size].astype(np.float) - orig_luma[0: luma_size].astype(np.float)
                mse = np.mean(resi ** 2)
                frame_psnr[i] = 10 * np.log10(max_value * max_value / mse)

        psnr.append(frame_psnr.mean())
        # delete reconstruction and decoded YUV
        if not save_rec_yuv_flag:
            os.remove(rec_yuv_path)
        if not save_deco_yuv_flag:
            os.remove(deco_yuv_path)

    return bits, psnr


def cal_BDrate(results):
    for seq_name in results:
        is_first_encoder = True
        for encoder in results[seq_name]:
            if is_first_encoder:
                anchor_psnr = np.array(results[seq_name][encoder]['psnr'])
                anchor_bits = np.log(np.array(results[seq_name][encoder]['bits']))
                anchor_encode_time = np.array(results[seq_name][encoder]['encode_time'])
                anchor_psnr_max = anchor_psnr.max()
                anchor_psnr_min = anchor_psnr.min()
                anchor_function = np.polyfit(anchor_psnr, anchor_bits, 3)
                anchor_integral = np.polyint(anchor_function)
                is_first_encoder = False
                continue
            else:
                current_encoder_psnr = np.array(results[seq_name][encoder]['psnr'])
                current_encoder_bits = np.log(np.array(results[seq_name][encoder]['bits']))
                current_encode_time = np.array(results[seq_name][encoder]['encode_time'])
                current_encoder_psnr_max = current_encoder_psnr.max()
                current_encoder_psnr_min = current_encoder_psnr.min()
                current_encoder_function = np.polyfit(current_encoder_psnr, current_encoder_bits, 3)
                current_encoder_integral = np.polyint(current_encoder_function)

            psnr_min = np.max([anchor_psnr_min, current_encoder_psnr_min])
            psnr_max = np.min([anchor_psnr_max, current_encoder_psnr_max])
            anchor_area = np.polyval(anchor_integral, psnr_max) - np.polyval(anchor_integral, psnr_min)
            current_encoder_area = np.polyval(current_encoder_integral, psnr_max) - np.polyval(current_encoder_integral, psnr_min)
            results[seq_name][encoder]['BDrate'] = np.exp((current_encoder_area - anchor_area) / (psnr_max - psnr_min)) - 1
            diff_encode_time = np.divide(current_encode_time - anchor_encode_time, anchor_encode_time)
            results[seq_name][encoder]['time_saving'] = np.average(diff_encode_time)
