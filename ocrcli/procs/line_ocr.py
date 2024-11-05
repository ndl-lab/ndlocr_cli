# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/
import hydra
import numpy
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
        from submodules.text_recognition_lightning.src.tasks.infer_task import infer, create_object_dict
        self._run_submodule_inference = infer

        config_path = "../../submodules/text_recognition_lightning/configs"
        hydra.initialize(version_base="1.2", config_path=config_path)
        self._hydra_cfg = hydra.compose(config_name="infer", overrides=[f"paths.output_dir={cfg['output_root']}"])
        self._hydra_cfg['model']['character_file'] = cfg['line_ocr']['char_list']
        self._hydra_cfg['ckpt_path'] = cfg['line_ocr']['saved_model']
        self._hydra_cfg = self._remove_noise_elements(self._hydra_cfg)
        for element_type, add_flag in cfg['line_ocr']['additional_elements'].items():
            if add_flag:
                add_block_string = f'BLOCK[@TYPE="{element_type}"]'
                self._hydra_cfg['datamodule']['additional_elements'].append(add_block_string)
        from pathlib import Path
        hydra.core.utils._save_config(self._hydra_cfg, "config.yaml", Path(cfg['output_root'])/".text_recognition")

        self._object_dict = create_object_dict(self._hydra_cfg)

    def _remove_noise_elements(self, hydra_cfg):
        NOISE_ELEMENT_TYPE = ['ノンブル', '柱']

        for element_type in NOISE_ELEMENT_TYPE:
            for idx, value in enumerate(hydra_cfg['datamodule']['additional_elements']):
                if value == f'BLOCK[@TYPE="{element_type}"]':
                    hydra_cfg['datamodule']['additional_elements'].pop(idx)
                    break
        return hydra_cfg

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
        output_data = self._run_submodule_inference(self._object_dict, input_data)
        result.append(output_data)

        return result
