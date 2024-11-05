# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/
import numpy
import xml.etree.ElementTree as ET

from .base_proc import BaseInferenceProcess


class LineOrderProcess(BaseInferenceProcess):
    """
    読み順認識推論を実行するプロセスのクラス。
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
        super().__init__(cfg, pid, '_line_order')
        from submodules.reading_order.tools.eval import infer_with_cli
        self._run_submodule_inference = infer_with_cli

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

        print('### Line Order Process ###')
        output_data = self._run_submodule_inference(input_data)
        result.append(output_data)

        return result
