# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import argparse
from submodules.ocr_line_eval_script.ocr_evaluator import OcrEvaluator
from submodules.ocr_line_eval_script.eval_order_leven import validate_options


class OcrResultEvaluator:
    """
    行文字認識・読み順認識の推論結果を評価する機能を提供します。

    Attributes
    ----------
    cfg : dict
        本実行処理における設定情報です。
    """

    def __init__(self, eval_cfg):
        """
        Parameters
        ----------
        eval_cfg : dict
            本実行処理における設定情報です。
        """
        # convert config dict to options
        p = argparse.ArgumentParser()
        options = p.parse_args([])
        for k, v in eval_cfg.items():
            if k == 'input_pred_data':
                if eval_cfg['input_structure'] == 's':
                    options.__setattr__('pred_single_xml', v)
                    options.__setattr__('pred_data_root_dir', None)
                elif eval_cfg['input_structure'] == 'd':
                    options.__setattr__('pred_single_xml', None)
                    options.__setattr__('pred_data_root_dir', v)
            elif k == 'input_gt_data':
                if eval_cfg['input_structure'] == 's':
                    options.__setattr__('gt_single_xml', v)
                    options.__setattr__('gt_data_root_dir', None)
                elif eval_cfg['input_structure'] == 'd':
                    options.__setattr__('gt_single_xml', None)
                    options.__setattr__('gt_data_root_dir', v)
            else:
                options.__setattr__(k, v)
        validate_options(options)
        self.options = options
        self.time_statistics = []

    def run(self):
        """
        self.cfgに保存された設定に基づいた評価処理を実行します。
        """
        ocr_evaluator = OcrEvaluator(self.options)
        ocr_evaluator.do_evaluation()

        ocr_edit_distance_average = ocr_evaluator.get_ocr_edit_distance_average()
        line_order_edit_distance_average = ocr_evaluator.get_line_order_edit_distance_average()
        print('### AVERAGE OF LINE OCR LEVEN DISTANCE : {0}'.format(ocr_edit_distance_average))
        print('### AVERAGE OF LINE ORDER LEVEN DISTANCE : {0}'.format(line_order_edit_distance_average))
        median_pid_list, ocr_edit_distance_median = ocr_evaluator.get_ocr_edit_distance_median()
        if len(median_pid_list) >= 2:
            print('### MEDIAN OF LINE OCR LEVEN DISTANCE : {0} (pid={1}, {2})'.format(ocr_edit_distance_median, median_pid_list[0], median_pid_list[1]))
        else:
            print('### MEDIAN OF LINE OCR LEVEN DISTANCE : {0} (pid={1})'.format(ocr_edit_distance_median, median_pid_list[0]))

        median_pid_list, line_order_edit_distance_median = ocr_evaluator.get_line_order_edit_distance_median()
        if len(median_pid_list) >= 2:
            print('### MEDIAN OF LINE ORDER LEVEN DISTANCE : {0} (pid={1}, {2})'.format(line_order_edit_distance_median, median_pid_list[0], median_pid_list[1]))
        else:
            print('### MEDIAN OF LINE ORDER LEVEN DISTANCE : {0} (pid={1})'.format(line_order_edit_distance_median, median_pid_list[0]))
