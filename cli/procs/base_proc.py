# Copyright (c) 2022, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import cv2
import os


class BaseInferenceProcess:
    """
    各推論処理を実行するプロセスクラスを作るためのメタクラス。

    Attributes
    ----------
    proc_name : str
        推論処理を実行するインスタンスが持つプロセス名。
        [実行される順序を表す数字＋クラスごとの処理名]で構成されます。
    cfg : dict
        本推論実行における設定情報です。
    """
    def __init__(self, cfg, pid, proc_type='_base_prep'):
        """
        Parameters
        ----------
        cfg : dict
            本実行処理における設定情報です。
        pid : int
            実行される順序を表す数値。
        proc_type : str
            クラスごとに定義されている処理名。
        """
        self.proc_name = str(pid) + proc_type

        if not self._is_valid_cfg(cfg):
            raise ValueError('Configuration validation error.')
        else:
            self.cfg = cfg

        self.process_dump_dir = None

        return True

    def do(self, data_idx, input_data):
        """
        推論処理を実行する際にOcrInferencerクラスから呼び出される推論実行関数。
        入力データのバリデーションや推論処理、推論結果の保存などが含まれます。
        本処理は基本的に継承先では変更されないことを想定しています。

        Parameters
        ----------
        data_idx : int
            入力データのインデックス。
            画像ファイル１つごとに入力データのリストが構成されます。
        input_data : dict
            推論処理を実行すつ対象の入力データ。

        Returns
        -------
        result : dict
            推論処理の結果を保持する辞書型データ。
            基本的にinput_dataと同じ構造です。
        """
        # input data valudation check
        if not self._is_valid_input(input_data):
            raise ValueError('Input data validation error.')

        # run main inference process
        result = self._run_process(input_data)
        if result is None:
            raise ValueError('Inference output error in {0}.'.format(self.proc_name))

        # dump inference result
        if self.cfg['dump']:
            self._dump_result(input_data, result, data_idx)

        return result

    def _run_process(self, input_data):
        """
        推論処理の本体部分。
        処理内容は継承先のクラスで実装されることを想定しています。

        Parameters
        ----------
        input_data : dict
            推論処理を実行する対象の入力データ。

        Returns
        -------
        result : dict
            推論処理の結果を保持する辞書型データ。
            基本的にinput_dataと同じ構造です。
        """
        print('### Base Inference Process ###')
        result = copy.deepcopy(input_data)
        return result

    def _is_valid_cfg(self, cfg):
        """
        推論処理全体の設定情報ではなく、クラス単位の設定情報に対するバリデーション。
        バリデーションの内容は継承先のクラスで実装されることを想定しています。

        Parameters
        ----------
        cfg : dict
            本推論実行における設定情報です。

        Returns
        -------
        [変数なし] : bool
            設定情報が正しければTrue, そうでなければFalseを返します。
        """
        if cfg is None:
            print('Given configuration data is None.')
            return False
        return True

    def _is_valid_input(self, input_data):
        """
        本クラスの推論処理における入力データのバリデーション。
        バリデーションの内容は継承先のクラスで実装されることを想定しています。

        Parameters
        ----------
        input_data : dict
            推論処理を実行する対象の入力データ。

        Returns
        -------
        [変数なし] : bool
            　入力データが正しければTrue, そうでなければFalseを返します。
        """
        return True

    def _dump_result(self, input_data, result, data_idx):
        """
        本クラスの推論処理結果をファイルに保存します。
        dumpフラグが有効の場合にのみ実行されます。

        Parameters
        ----------
        input_data : dict
            推論処理に利用した入力データ。
        result : list
            推論処理の結果を保持するリスト型データ。
            各要素は基本的にinput_dataと同じ構造の辞書型データです。
        data_idx : int
            入力データのインデックス。
            画像ファイル１つごとに入力データのリストが構成されます。
        """

        self.process_dump_dir = os.path.join(os.path.join(input_data['output_dir'], 'dump'), self.proc_name)

        for i, single_result in enumerate(result):
            if 'img' in single_result.keys() and single_result['img'] is not None:
                dump_img_name = os.path.basename(input_data['img_path']).split('.')[0] + '_' + str(data_idx) + '_' + str(i) + '.jpg'
                self._dump_img_result(single_result, input_data['output_dir'], dump_img_name)
            if 'xml' in single_result.keys() and single_result['xml'] is not None:
                dump_xml_name = os.path.basename(input_data['img_path']).split('.')[0] + '_' + str(data_idx) + '_' + str(i) + '.xml'
                self._dump_xml_result(single_result, input_data['output_dir'], dump_xml_name)
            if 'txt' in single_result.keys() and single_result['txt'] is not None:
                dump_txt_name = os.path.basename(input_data['img_path']).split('.')[0] + '_' + str(data_idx) + '_' + str(i) + '.txt'
                self._dump_txt_result(single_result, input_data['output_dir'], dump_txt_name)
        return

    def _dump_img_result(self, single_result, output_dir, img_name):
        """
        本クラスの推論処理結果(画像)をファイルに保存します。
        dumpフラグが有効の場合にのみ実行されます。

        Parameters
        ----------
        single_result : dict
            推論処理の結果を保持する辞書型データ。
        output_dir : str
            推論結果が保存されるディレクトリのパス。
        img_name : str
            入力データの画像ファイル名。
            dumpされる画像ファイルのファイル名は入力のファイル名と同名(複数ある場合は連番を付与)となります。
        """
        pred_img_dir = os.path.join(self.process_dump_dir, 'pred_img')
        os.makedirs(pred_img_dir, exist_ok=True)
        image_file_path = os.path.join(pred_img_dir, img_name)
        dump_image = self._create_result_image(single_result)
        try:
            cv2.imwrite(image_file_path, dump_image)
        except OSError as err:
            print("Dump image save error: {0}".format(err))
            raise OSError

        return

    def _dump_xml_result(self, single_result, output_dir, img_name):
        """
        本クラスの推論処理結果(XML)をファイルに保存します。
        dumpフラグが有効の場合にのみ実行されます。

        Parameters
        ----------
        single_result : dict
            推論処理の結果を保持する辞書型データ。
        output_dir : str
            推論結果が保存されるディレクトリのパス。
        img_name : str
            入力データの画像ファイル名。
            dumpされるXMLファイルのファイル名は入力のファイル名とほぼ同名（拡張子の変更、サフィックスや連番の追加のみ）となります。
        """
        xml_dir = os.path.join(self.process_dump_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)
        trum, _ = os.path.splitext(img_name)
        xml_path = os.path.join(xml_dir, trum + '.xml')
        try:
            single_result['xml'].write(xml_path, encoding='utf-8', xml_declaration=True)
        except OSError as err:
            print("Dump xml save error: {0}".format(err))
            raise OSError

        return

    def _dump_txt_result(self, single_result, output_dir, img_name):
        """
        本クラスの推論処理結果(テキスト)をファイルに保存します。
        dumpフラグが有効の場合にのみ実行されます。

        Parameters
        ----------
        single_result : dict
            推論処理の結果を保持する辞書型データ。
        output_dir : str
            推論結果が保存されるディレクトリのパス。
        img_name : str
            入力データの画像ファイル名。
            dumpされるテキストファイルのファイル名は入力のファイル名とほぼ同名（拡張子の変更、サフィックスや連番の追加のみ）となります。
        """
        txt_dir = os.path.join(self.process_dump_dir, 'txt')
        os.makedirs(txt_dir, exist_ok=True)

        trum, _ = os.path.splitext(img_name)
        txt_path = os.path.join(txt_dir, trum + '_main.txt')
        try:
            with open(txt_path, 'w') as f:
                f.write(single_result['txt'])
        except OSError as err:
            print("Dump text save error: {0}".format(err))
            raise OSError

        return

    def _create_result_image(self, single_result):
        """
        推論結果を入力の画像に重畳した画像データを生成します。

        Parameters
        ----------
        single_result : dict
            推論処理の結果を保持する辞書型データ。
        """
        dump_img = None
        if 'dump_img' in single_result.keys():
            dump_img = copy.deepcopy(single_result['dump_img'])
        else:
            dump_img = copy.deepcopy(single_result['img'])
        if 'xml' in single_result.keys() and single_result['xml'] is not None:
            # draw single inferenceresult on input image
            # this should be implemeted in each child class
            cv2.putText(dump_img, 'dump' + self.proc_name, (0, 50),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 5, cv2.LINE_AA)
            pass
        else:
            cv2.putText(dump_img, 'dump' + self.proc_name, (0, 50),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 0), 5, cv2.LINE_AA)
        return dump_img
