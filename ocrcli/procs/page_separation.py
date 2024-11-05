# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import numpy
import os

from .base_proc import BaseInferenceProcess


class PageSeparation(BaseInferenceProcess):
    """
    ノド元分割処理を実行するプロセスのクラス。
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
        super().__init__(cfg, pid, '_page_sep')

        from submodules.separate_pages_mmdet.inference_divide import divide_facing_page_with_cli, GutterDetector

        config_path = self.cfg['page_separation']['config_path']
        checkpoint = self.cfg['page_separation']['weight_path']
        device = 'cuda:0'
        self._detector = GutterDetector(config_path, checkpoint, device)
        self._run_submodule_inference = divide_facing_page_with_cli

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
            print('PageSeparation: input img is not numpy.ndarray')
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
        print('### Page Separation ###')
        log_file_path = None
        if self.process_dump_dir is not None:
            log_file_path = os.path.join(
                self.process_dump_dir,
                self.cfg['page_separation']['log']
            )
        inference_output = self._run_submodule_inference(
            input_data['img'],
            self._detector,
            log=log_file_path,
        )
        if (not self.cfg['page_separation']['allow_invalid_num_output']) and (not len(inference_output) in range(1, 3)):
            print('ERROR: Output from page separation must be 1 or 2 pages.')
            return None

        # Create result to pass img_path and img data
        result = []
        for id, single_output_img in enumerate(inference_output):
            output_data = copy.deepcopy(input_data)
            output_data['img'] = single_output_img
            output_data['orig_img_path'] = input_data['img_path']

            # make and save separated img file name
            if id == 0:
                id = 'L'
            else:
                id = 'R'
            orig_img_name = os.path.basename(input_data['img_path'])
            stem, ext = os.path.splitext(orig_img_name)
            output_data['img_file_name'] = stem + '_' + id + '.jpg'

            result.append(output_data)

        return result
