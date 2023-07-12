# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import nltk
from operator import itemgetter
from .line_evaluator import LineEvaluator, LineData


class PageEvaluator:
    # character code number for the first character
    # which is used when generating a string represents reading order
    BASE_CHR_NUM = 40

    def __init__(self, pred_page_block, gt_page_block, options):
        # input data
        self.pred_page_block = pred_page_block
        self.gt_page_block = gt_page_block

        # output data
        self.line_order_edit_distance = None
        self.normalized_line_order_edit_distance = None
        self.line_ocr_edit_distance_average = None

        # config
        self.iou_thresh = options.iou_thresh
        self.correct_line_ocr_log = options.correct_line_ocr_log
        self.eval_main_text_only = options.eval_main_text_only
        self.eval_annotation_line_order = options.eval_annotation_line_order
        self.ignore_inline_type_to_skip = options.ignore_inline_type_to_skip
        self.eval_all_valid_pred_line = options.eval_all_valid_pred_line

        # internal variables
        self._line_evaluator_list = []

    def load_line_evaluators(self):
        gt_idx = 0
        for gt_line_block in self.gt_page_block.iter('LINE'):
            # use only '本文' LINE blocks when eval_main_text_only is enabled
            if gt_line_block.attrib['TYPE'] != '本文' and self.eval_main_text_only:
                continue

            skip_ocr_evaluation = False
            gt_skip_line_order_evaluation = False

            # skip line blocks not for line ocr evaluation/line order evaluation
            if gt_line_block.attrib['TYPE'] not in ['本文', '頭注', '割注', '広告文字']:
                skip_ocr_evaluation = True
                gt_skip_line_order_evaluation = True

            # enable skip_ocr_evaluation flag to skip line
            # which its string is empty and inline type is '手書き' or '数式' or '化学式' or '縦中横'
            gt_inline_block = gt_line_block.find('INLINE')
            if (gt_line_block.attrib['STRING'] == '〓') and (gt_inline_block is not None):
                inline_type = gt_inline_block.attrib['TYPE']
                # inline_type is ignored if ignore_inline_type_to_skip is True
                if (self.ignore_inline_type_to_skip) or (inline_type in ['手書き', '数式', '化学式', '縦中横']):
                    skip_ocr_evaluation = True

            if gt_line_block.attrib['TYPE'] in ['頭注', '割注']:
                skip_ocr_evaluation = True
                if not self.eval_annotation_line_order:
                    gt_skip_line_order_evaluation = True

            if gt_line_block.attrib['TYPE'] in ['広告文字']:
                gt_skip_line_order_evaluation = True

            pred_skip_line_order_evaluation = False
            # search pair of pred/gt line data
            iou_line_tuple_list = []
            pred_idx = -1
            for pred_line_block in self.pred_page_block.iter('LINE'):
                # use only '本文' LINE blocks when eval_main_text_only is enabled
                if pred_line_block.attrib['TYPE'] != '本文' and self.eval_main_text_only:
                    continue

                if pred_line_block.attrib['TYPE'] not in ['本文', '頭注', '割注', '広告文字']:
                    pred_skip_line_order_evaluation = True
                elif (pred_line_block.attrib['TYPE'] in ['頭注', '割注']) and (not self.eval_annotation_line_order):
                    pred_skip_line_order_evaluation = True
                elif (pred_line_block.attrib['TYPE'] in ['広告文字']):
                    pred_skip_line_order_evaluation = True
                else:
                    pred_skip_line_order_evaluation = False

                if gt_skip_line_order_evaluation and (not pred_skip_line_order_evaluation) and (not self.eval_all_valid_pred_line):
                    pred_skip_line_order_evaluation = True

                if not pred_skip_line_order_evaluation:
                    pred_idx += 1

                line_iou = self._get_line_iou(pred_line_block, gt_line_block)
                if line_iou >= self.iou_thresh:
                    if pred_skip_line_order_evaluation:
                        pred_line_data = LineData(pred_line_block.attrib['STRING'], None)
                    else:
                        pred_line_data = LineData(pred_line_block.attrib['STRING'], pred_idx)
                    iou_line_tuple_list.append((line_iou, pred_line_data))

            if len(iou_line_tuple_list) > 0:
                sorted_tuple_list = sorted(iou_line_tuple_list, key=itemgetter(0))
                pred_line_data_to_add = sorted_tuple_list[-1][1]
                if gt_skip_line_order_evaluation:
                    gt_line_data = LineData(gt_line_block.attrib['STRING'], None)
                else:
                    gt_line_data = LineData(gt_line_block.attrib['STRING'], gt_idx)
                    gt_idx += 1
                line_evaluator = LineEvaluator(pred_line_data_to_add, gt_line_data, self.correct_line_ocr_log, skip_ocr_evaluation)
                self._line_evaluator_list.append(line_evaluator)
            else:
                # if pair not found, add empty line data as pred line data
                if gt_skip_line_order_evaluation:
                    gt_line_data = LineData(gt_line_block.attrib['STRING'], None)
                else:
                    gt_line_data = LineData(gt_line_block.attrib['STRING'], gt_idx)
                pred_line_data = LineData('', None)
                line_evaluator = LineEvaluator(pred_line_data, gt_line_data, self.correct_line_ocr_log, skip_ocr_evaluation)
                self._line_evaluator_list.append(line_evaluator)
                print('Predicted line block for gt line "{0}" not found in {1}'.format(gt_line_block.attrib['STRING'], self.gt_page_block.attrib['IMAGENAME']))
                if not gt_skip_line_order_evaluation:
                    gt_idx += 1

    def do_evaluation(self):
        print('#### Start Page Evaluation ####')
        gt_line_order_string = ''
        pred_line_order_string = ''
        gt_line_order_counter = 0
        for line_evaluator in self._line_evaluator_list:
            line_evaluator.do_evaluation()
            pred_idx = line_evaluator.get_pred_line_idx()
            if pred_idx is not None:
                pred_line_order_string += chr(pred_idx + PageEvaluator.BASE_CHR_NUM)
            gt_idx = line_evaluator.get_gt_line_idx()
            if gt_idx is not None:
                gt_line_order_string += chr(gt_idx + PageEvaluator.BASE_CHR_NUM)
                gt_line_order_counter += 1

        print('pred line order :{}'.format(pred_line_order_string))
        print('  gt line order :{}'.format(gt_line_order_string))

        if len(self._line_evaluator_list) == 0:
            print('No Line Block in this image:{0}'.format(self.gt_page_block.attrib['IMAGENAME']))
            self.normalized_line_order_edit_distance = 0
            self.line_ocr_edit_distance_average = 0
            return

        # calculate line order edit_distance
        line_order_edit_distance = nltk.edit_distance(pred_line_order_string, gt_line_order_string)
        self.line_order_edit_distance = line_order_edit_distance
        if (len(self._line_evaluator_list) <= 0) or (gt_line_order_counter <= 0):
            print('valid _line_evaluator_list length is 0.')
            self.normalized_line_order_edit_distance = line_order_edit_distance
        else:
            self.normalized_line_order_edit_distance = line_order_edit_distance / gt_line_order_counter

        # calculate ocr edit_distance average
        edit_distance_sum = 0
        skipped_line_evaluation_num = 0
        for line_evaluator in self._line_evaluator_list:
            if isinstance(line_evaluator.edit_distance, int):
                edit_distance_sum += line_evaluator.normalized_edit_distance
            elif line_evaluator.edit_distance is None:
                skipped_line_evaluation_num += 1
            else:
                raise ValueError('Edit distance in {0} is invalid')
        if (len(self._line_evaluator_list) <= 0) or (len(self._line_evaluator_list) - skipped_line_evaluation_num <= 0):
            print('valid _line_evaluator_list length is 0.')
            self.line_ocr_edit_distance_average = edit_distance_sum
        else:
            self.line_ocr_edit_distance_average = edit_distance_sum / (len(self._line_evaluator_list) - skipped_line_evaluation_num)

    def get_line_ocr_edit_distance_average(self):
        return self.line_ocr_edit_distance_average

    def _get_line_iou(self, line_a, line_b):
        # get each bbox coordinate
        box_a = (int(line_a.attrib['X']), int(line_a.attrib['Y']), int(line_a.attrib['WIDTH']), int(line_a.attrib['HEIGHT']))
        box_b = (int(line_b.attrib['X']), int(line_b.attrib['Y']), int(line_b.attrib['WIDTH']), int(line_b.attrib['HEIGHT']))

        # compute the overlapping area
        x_a = max(box_a[0], box_b[0])
        y_a = max(box_a[1], box_b[1])
        x_b = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
        y_b = min(box_a[1] + box_a[3], box_b[1] + box_b[3])
        overlap_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)

        # compute IoU
        box_a_area = (box_a[2] + 1) * (box_a[3] + 1)
        box_b_area = (box_b[2] + 1) * (box_b[3] + 1)
        iou = overlap_area / float(box_a_area + box_b_area - overlap_area + 1e-6)

        return iou
