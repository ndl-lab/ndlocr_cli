# Copyright (c) 2022, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import numpy
import subprocess
import xml.etree.ElementTree as ET

from .base_proc import BaseInferenceProcess


class LineOcrProcess(BaseInferenceProcess):
    """
    行文字認識推論を実行するプロセスのクラス。
    BaseInferenceProcessを継承しています。
    """
    def __init__(self, cfg, pid):
        """
        Parameters
        ----------
        cfg : dict
            本推論処理における設定情報です。
        pid : int
            実行される順序を表す数値。
        """
        super().__init__(cfg, pid, '_line_ocr')
        process1 = subprocess.Popen(['cat', self.cfg['line_ocr']['char_list']], stdout=subprocess.PIPE)
        process2 = subprocess.Popen(['tr', '-d', '\\n'], stdin=process1.stdout, stdout=subprocess.PIPE)
        self.character = '〓' + process2.stdout.read().decode()

        from src.text_recognition.text_recognition import InferencerWithCLI
        self._inferencer = InferencerWithCLI(self.cfg['line_ocr'], self.character)
        self._run_src_inference = self._inferencer.inference_wich_cli

    def _is_valid_input(self, input_data):
        """
        本クラスの推論処理における入力データのバリデーション。

        Parameters
        ----------
        input_data : dict
            推論処理を実行する対象の入力データ。

        Returns
        -------
        [変数なし] : bool
            入力データが正しければTrue, そうでなければFalseを返します。
        """
        if type(input_data['img']) is not numpy.ndarray:
            print('LineOcrProcess: input img is not numpy.ndarray')
            return False
        if type(input_data['xml']) is not ET.ElementTree:
            print('LineOcrProcess: input xml is not ElementTree')
            return False
        return True

    def _run_process(self, input_data):
        """
        推論処理の本体部分。

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
        result = []
        print('### Line OCR Process ###')
        result_xml = self._run_src_inference(input_data['img'], input_data['xml'],
                                             accept_empty=self.cfg['line_ocr']['accept_empty'],
                                             yield_block_page_num=self.cfg['line_ocr']['yield_block_page_num'],
                                             yield_block_pillar=self.cfg['line_ocr']['yield_block_pillar'])

        output_data = copy.deepcopy(input_data)
        output_data['xml'] = result_xml
        result.append(output_data)

        return result
