# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import nltk


class LineData:
    def __init__(self, string: str, line_order_idx: int):
        self.string = string
        self.line_order_idx = line_order_idx


class LineEvaluator:
    def __init__(self, pred_line_data: LineData, gt_line_data: LineData, correct_line_ocr_log: bool, skip_ocr_evaluation: bool):
        # input data
        self.pred_line_data = pred_line_data
        self.gt_line_data = gt_line_data

        # output data
        self.edit_distance = None
        self.normalized_edit_distance = None

        # config
        self.correct_line_ocr_log = correct_line_ocr_log
        self.skip_ocr_evaluation = skip_ocr_evaluation

    def do_evaluation(self):
        if self.skip_ocr_evaluation:
            print('Line evalutation skipped')
            print('pred line: {0}'.format(self.pred_line_data.string))
            print('  gt line: {0}'.format(self.gt_line_data.string))
            return
        distance = nltk.edit_distance(self.pred_line_data.string, self.gt_line_data.string)
        if distance != 0 or self.correct_line_ocr_log:
            print('### EDIT DIS : {0}'.format(distance))
            print('pred line: {0}'.format(self.pred_line_data.string))
            print('  gt line: {0}'.format(self.gt_line_data.string))
        self.edit_distance = distance
        if len(self.gt_line_data.string) <= 0:
            print('gt string length is 0.')
            self.normalized_edit_distance = distance
        else:
            self.normalized_edit_distance = distance / len(self.gt_line_data.string)

    def get_pred_line_idx(self):
        return self.pred_line_data.line_order_idx

    def get_gt_line_idx(self):
        return self.gt_line_data.line_order_idx
