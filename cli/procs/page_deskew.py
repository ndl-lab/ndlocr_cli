# Copyright (c) 2022, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import numpy

from .base_proc import BaseInferenceProcess


class PageDeskewProcess(BaseInferenceProcess):
    """
    傾き補正を実行するプロセスのクラス。
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
        super().__init__(cfg, pid, '_page_deskew')
        from src.deskew_HT.alyn3.deskew import Deskew
        self.deskewer = Deskew('', '',
                               r_angle=cfg['page_deskew']['r_angle'],
                               skew_max=cfg['page_deskew']['skew_max'],
                               acc_deg=cfg['page_deskew']['acc_deg'],
                               method=cfg['page_deskew']['method'],
                               gray=cfg['page_deskew']['gray'],
                               quality=cfg['page_deskew']['quality'],
                               short=cfg['page_deskew']['short'],
                               roi_w=cfg['page_deskew']['roi_w'],
                               roi_h=cfg['page_deskew']['roi_h'])
        self._run_src_inference = self.deskewer.deskew_on_memory


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
            print('PageDeskewProcess: input img is not numpy.ndarray')
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
        print('### Page Deskew Process ###')
        inference_output = self._run_src_inference(input_data['img'])

        # Create result to pass img_path and img data
        result = []
        output_data = copy.deepcopy(input_data)
        output_data['img'] = inference_output
        result.append(output_data)

        return result
