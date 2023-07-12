# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/
import hydra
import numpy
import xml.etree.ElementTree as ET

from .base_proc import BaseInferenceProcess


class LineAttributeProcess(BaseInferenceProcess):
    """
    行属性認識推論を実行するプロセスのクラス。
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
        super().__init__(cfg, pid, '_line_attribute')
        if cfg['line_attribute']['classifier'] == 'rf':
            from submodules.text_recognition_lightning.src.tasks.infer_rf_task import infer, create_object_dict
        elif cfg['line_attribute']['classifier'] == 'bert':
            from submodules.text_recognition_lightning.src.tasks.infer_nlp_task import infer, create_object_dict
        else:
            raise Exception('Unsupported Line Attribute Classifier')
        self._run_submodule_inference = infer

        config_path = "../../submodules/text_recognition_lightning/configs"
        from hydra.core.global_hydra import GlobalHydra
        if not GlobalHydra.instance().is_initialized():
            hydra.initialize(version_base="1.2", config_path=config_path)
        if cfg['line_attribute']['classifier'] == 'rf':
            self._hydra_cfg = hydra.compose(config_name="infer_rf",
                                            overrides=[f"paths.output_dir={cfg['output_root']}"])
        else:
            self._hydra_cfg = hydra.compose(config_name="infer_nlp",
                                            overrides=[f"paths.output_dir={cfg['output_root']}"])
            self._hydra_cfg['ckpt_path'] = ''
            self._hydra_cfg['datamodule']['downsampling_rate'] = 20

        title_model_path = cfg['line_attribute']['title_model']
        author_model_path = cfg['line_attribute']['author_model']

        self._hydra_cfg['datamodule']['tree'] = None
        self._hydra_cfg['target'] = 'TITLE'

        self._object_dict = create_object_dict(self._hydra_cfg, title_model_path, author_model_path)

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
        if type(input_data['xml']) is not ET.ElementTree:
            print('LineAttributeProcess: input xml is not ElementTree')
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

        print('### Line Attribute Process ###')
        output_data = self._run_submodule_inference(self._object_dict, input_data)
        result.append(output_data)

        return result
