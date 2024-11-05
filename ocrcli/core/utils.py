# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import datetime
import glob
import os
import sys
import yaml


def parse_cfg(cfg_dict):
    """
    コマンドで入力された引数やオプションを内部関数が利用しやすい形にparseします。

    Parameters
    ----------
    cfg_dict : dict
        コマンドで入力された引数やオプションが保存された辞書型データ。

    Returns
    -------
    infer_cfg : dict
        推論処理を実行するための設定情報が保存された辞書型データ。
    """
    infer_cfg = copy.deepcopy(cfg_dict)

    # add inference config parameters from yml config file
    yml_config = None
    if not os.path.isfile(cfg_dict['config_file']):
        print('[ERROR] Config yml file not found.', file=sys.stderr)
        return None

    with open(cfg_dict['config_file'], 'r') as yml:
        yml_config = yaml.safe_load(yml)

    if type(yml_config) is not dict:
        print('[ERROR] Config yml file read error.', file=sys.stderr)
        return None

    infer_cfg.update(yml_config)

    # save_xml will be ignored when last proc does not output xml data
    if (infer_cfg['proc_range'] != '0..3') and (infer_cfg['save_xml'] or infer_cfg['save_image']):
        print('[WARNING] save_xml and save_image flags are ignored because this is partial execution.')
        print('          All output of last proc will be saved in output directory.')

    # parse start/end indices of inference process
    start = int(infer_cfg['proc_range'][0])
    end = int(infer_cfg['proc_range'][-1])
    if (start < 0) or (end > 3):
        print('[ERROR] Value of proc_range must be 0 ~ 3.', file=sys.stderr)
    if start > end:
        print('[ERROR] Value of proc_range must be [x..y : x <= y] .', file=sys.stderr)
        return None
    infer_cfg['proc_range'] = {
        'start': start,
        'end': end
    }
    if (start != 0) or (end != 3):
        infer_cfg['partial_infer'] = True
    else:
        infer_cfg['partial_infer'] = False

    # create input_dirs from input_root
    # input_dirs is list of dirs that contain img (and xml) dir
    infer_cfg['input_root'] = os.path.abspath(infer_cfg['input_root'])
    infer_cfg['output_root'] = os.path.abspath(infer_cfg['output_root'])
    if infer_cfg['input_structure'] in ['s']:
        # - Single input dir mode
        # input_root
        #  ├── xml
        #  │   └── R[7桁連番].xml※XMLデータ
        #  └── img
        #      └── R[7桁連番]_pp.jp2※画像データ

        # validation check for input dir structure
        if not os.path.isdir(os.path.join(infer_cfg['input_root'], 'img')):
            print('[ERROR] Input img diretctory not found in {}'.format(infer_cfg['input_root']), file=sys.stderr)
            return None
        if ((start > 2) or infer_cfg['ruby_only']) and (not os.path.isdir(os.path.join(infer_cfg['input_root'], 'xml'))):
            print('[ERROR] Input xml diretctory not found in {}'.format(infer_cfg['input_root']), file=sys.stderr)
            return None
        infer_cfg['input_dirs'] = [infer_cfg['input_root']]
    elif infer_cfg['input_structure'] in ['i']:
        # - Partial inference mode
        # input_root
        #  └── PID
        #      ├── xml
        #      │   └── R[7桁連番].xml※XMLデータ
        #      └── img
        #          └── R[7桁連番]_pp.jp2※画像データ
        infer_cfg['input_dirs'] = []
        for input_dir in glob.glob(os.path.join(infer_cfg['input_root'], '*')):
            if os.path.isdir(input_dir):
                if not os.path.isdir(os.path.join(input_dir, 'img')) and not infer_cfg['ruby_only']:
                    print('[WARNING] Input directory {0} is skipped(no img diretctory)'.format(input_dir))
                    continue
                if ((start > 2) or infer_cfg['ruby_only']) and (not os.path.isdir(os.path.join(input_dir, 'xml'))):
                    print('[WARNING] Input directory {0} is skipped(no xml diretctory)'.format(input_dir))
                    continue
                infer_cfg['input_dirs'].append(input_dir)
    elif infer_cfg['input_structure'] in ['t']:
        # - ToshoData mode
        # input_root
        #  └── tosho_19XX_bunkei
        #      └── R[7桁連番]_pp.jp2※画像データ
        if infer_cfg['ruby_only']:
            print('[ERROR] Ruby only mode is not supported when input structure is ToshoData mode')
            return None
        infer_cfg['input_dirs'] = []
        for input_dir in glob.glob(os.path.join(infer_cfg['input_root'], '*')):
            if os.path.isdir(input_dir):
                infer_cfg['input_dirs'].append(input_dir)
        if 'img' in [os.path.basename(d) for d in infer_cfg['input_dirs']]:
            print('[WARNING] This input structure might be single input(img diretctory found)')
    elif infer_cfg['input_structure'] in ['w']:
        # - Work station input mode
        # input_root
        #  └── workstation
        #      └── [collect(3桁数字)、またはdigital(3桁数字)]フォルダ
        #           └── [15桁連番]フォルダ※PID上1桁目
        #                └── [3桁連番]フォルダ※PID上2～4桁目
        #                     └── [3桁連番]フォルダ※PID上5～7桁目
        #                          └── R[7桁連番]_contents.jp2※画像データ

        # recursive function to get input_dirs in workstation mode
        def get_input_dirs(path, depth):
            depth += 1
            ret_list = []
            current_list = []
            for input_dir in glob.glob(os.path.join(path, '*')):
                if os.path.isdir(input_dir):
                    current_list.append(input_dir)
            if depth > 3:
                return current_list
            if (depth < 2) and (len(current_list) == 0):
                print('[ERROR] Input directory structure dose not match workstation mode', file=sys.stderr)
                return []
            for dir in current_list:
                tmp_list = get_input_dirs(dir, depth)
                ret_list.extend(tmp_list)
            return ret_list

        if infer_cfg['ruby_only']:
            print('[ERROR] Ruby only mode is not supported when input structure is Work station mode')
            return None

        # check if workstation directory exist
        work_dir = os.path.join(infer_cfg['input_root'], 'workstation')
        if not os.path.isdir(work_dir):
            print('[ERROR] \'workstation\' directory not found', file=sys.stderr)
            return None

        # get input dir list
        infer_cfg['input_dirs'] = get_input_dirs(work_dir, 0)
    elif infer_cfg['input_structure'] in ['f']:
        # - Image file input mode
        # input_root is equal to input image file path
        infer_cfg['input_dirs'] = [infer_cfg['input_root']]
    else:
        print('[ERROR] Unexpected input directory structure type: {0}.'.format(infer_cfg['input_structure']), file=sys.stderr)
        return None

    return infer_cfg


def parse_eval_cfg(cfg_dict):
    """
    コマンドで入力された引数やオプションをevaluationの内部関数が利用しやすい形にparseします。

    Parameters
    ----------
    cfg_dict : dict
        コマンドで入力された引数やオプションが保存された辞書型データ。

    Returns
    -------
    eval_cfg : dict
        評価処理を実行するための設定情報が保存された辞書型データ。
    """
    eval_cfg = copy.deepcopy(cfg_dict)

    # add inference config parameters from yml config file
    yml_config = None
    if not os.path.isfile(cfg_dict['config_file']):
        print('[ERROR] Config yml file not found.', file=sys.stderr)
        return None

    with open(cfg_dict['config_file'], 'r') as yml:
        yml_config = yaml.safe_load(yml)

    if type(yml_config) is not dict:
        print('[ERROR] Config yml file read error.', file=sys.stderr)
        return None

    eval_cfg.update(yml_config)

    # create input_dirs from input_root
    # input_dirs is list of dirs that contain img (and xml) dir
    eval_cfg['input_pred_data'] = os.path.abspath(eval_cfg['input_pred_data'])
    eval_cfg['input_gt_data'] = os.path.abspath(eval_cfg['input_gt_data'])
    eval_cfg['output_root_dir'] = os.path.abspath(eval_cfg['output_root_dir'])
    if eval_cfg['input_structure'] in ['s']:
        # - Sigle file input mode
        # validation check for input file
        for input_data in [eval_cfg['input_pred_data'], eval_cfg['input_gt_data']]:
            if not os.path.isfile(input_data):
                print('[ERROR] Input xml file not found in {}'.format(input_data), file=sys.stderr)
                return None
    elif eval_cfg['input_structure'] in ['d']:
        # - Directory input mode
        # input_data
        #  └── PID
        #      ├── xml
        #      │   └── R[7桁連番].xml※XMLデータ
        #      └── img
        #          └── R[7桁連番]_pp.jp2※画像データ
        for input_data in [eval_cfg['input_pred_data'], eval_cfg['input_gt_data']]:
            if not os.path.isdir(input_data):
                print('[ERROR] Input diretctory {} not found.'.format(input_data), file=sys.stderr)
                return None
    else:
        print('[ERROR] Unexpected input directory structure type: {0}.'.format(eval_cfg['input_structure']), file=sys.stderr)
        return None

    return eval_cfg


def save_xml(xml_to_save, path):
    """
    指定されたファイルパスにXMLファイル保存します。

    Parameters
    ----------
    path : str
        XMLファイルを保存するファイルパス。

    """
    print('### save xml : {}###'.format(path))
    try:
        xml_to_save.write(path, encoding='utf-8', xml_declaration=True)
    except OSError as err:
        print("[ERROR] XML save error : {0}".format(err), file=sys.stderr)
        raise OSError
    return


def mkdir_with_duplication_check(dir_path):
    dir_path_to_create = dir_path

    # prepare output root derectory
    while os.path.isdir(dir_path_to_create):
        print('[WARNING] Directory {0} already exist.'.format(dir_path))
        now = datetime.datetime.now()
        time_stamp = now.strftime('_%Y%m%d%H%M%S')
        dir_path_to_create += time_stamp

    if dir_path_to_create != dir_path:
        print('[WARNING] Directory is changed to {0}.'.format(dir_path_to_create))
    os.mkdir(dir_path_to_create)

    return dir_path_to_create
