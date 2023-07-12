# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import glob
import os
import statistics
from .pid_data_evaluator import PidDataEvaluator


class OcrEvaluator:
    def __init__(self, options):
        # set properties
        self.correct_line_ocr_log = options.correct_line_ocr_log
        self.eval_main_text_only = options.eval_main_text_only
        self.eval_annotation_line_order = options.eval_annotation_line_order
        self.ocr_edit_distance_list = []
        self.line_order_edit_distance_list = []
        self.output_root_dir = options.output_root_dir

        # create list of PidDataEvaluator
        self.pid_data_evaluator_list = []
        if (options.pred_single_xml is not None) and (options.gt_single_xml is not None):
            pid_string, _ = os.path.splitext(os.path.basename(options.gt_single_xml))
            single_pid_evaluator = PidDataEvaluator(self.output_root_dir, pid_string, options.pred_single_xml, options.gt_single_xml, options)
            self.pid_data_evaluator_list.append(single_pid_evaluator)
        else:
            self.pid_data_evaluator_list = self._create_pid_evaluator_list(options)

    def do_evaluation(self):
        # create PID dir pair list
        for pid_data_evaluator in self.pid_data_evaluator_list:
            pid_data_evaluator.load_page_evaluators()
            pid_data_evaluator.do_evaluation()
            self.ocr_edit_distance_list.append(pid_data_evaluator.get_line_ocr_edit_distance_average())
            self.line_order_edit_distance_list.append(pid_data_evaluator.get_line_order_edit_distance_average())

    def get_ocr_edit_distance_average(self):
        if len(self.ocr_edit_distance_list) <= 0:
            print('ocr_edit_distance_list is empty')
            return -1
        return sum(self.ocr_edit_distance_list) / len(self.ocr_edit_distance_list)

    def get_ocr_edit_distance_median(self):
        line_ocr_edit_distance_list = []
        line_ocr_edit_distance_dict = {}
        for pid_data_evaluator in self.pid_data_evaluator_list:
            line_ocr_edit_distance_dict[pid_data_evaluator.pid_string] = pid_data_evaluator.get_line_ocr_edit_distance_list()
            line_ocr_edit_distance_list.extend(pid_data_evaluator.get_line_ocr_edit_distance_list())
        ocr_edit_distance_median_low = statistics.median_low(line_ocr_edit_distance_list)
        ocr_edit_distance_median_high = statistics.median_high(line_ocr_edit_distance_list)
        ocr_edit_distance_median = (ocr_edit_distance_median_low + ocr_edit_distance_median_high) / 2

        median_pid_list = []
        for pid, single_edit_distance_list in line_ocr_edit_distance_dict.items():
            if ocr_edit_distance_median_low in single_edit_distance_list:
                median_pid_list.append(pid)
                break
        for pid, single_edit_distance_list in line_ocr_edit_distance_dict.items():
            if ocr_edit_distance_median_high in single_edit_distance_list:
                median_pid_list.append(pid)
                break

        if median_pid_list[0] == median_pid_list[1]:
            median_pid_list.pop()
        return median_pid_list, ocr_edit_distance_median

    def get_line_order_edit_distance_average(self):
        if len(self.line_order_edit_distance_list) <= 0:
            print('line_order_edit_distance_list is empty')
            return -1
        return sum(self.line_order_edit_distance_list) / len(self.line_order_edit_distance_list)

    def get_line_order_edit_distance_median(self):
        line_order_edit_distance_list = []
        line_order_edit_distance_dict = {}
        for pid_data_evaluator in self.pid_data_evaluator_list:
            line_order_edit_distance_dict[pid_data_evaluator.pid_string] = pid_data_evaluator.get_line_order_edit_distance_list()
            line_order_edit_distance_list.extend(pid_data_evaluator.get_line_order_edit_distance_list())
        line_order_edit_distance_median_low = statistics.median_low(line_order_edit_distance_list)
        line_order_edit_distance_median_high = statistics.median_high(line_order_edit_distance_list)
        line_order_edit_distance_median = (line_order_edit_distance_median_low + line_order_edit_distance_median_high) / 2

        median_pid_list = []
        for pid, single_edit_distance_list in line_order_edit_distance_dict.items():
            if line_order_edit_distance_median_low in single_edit_distance_list:
                median_pid_list.append(pid)
                break

        for pid, single_edit_distance_list in line_order_edit_distance_dict.items():
            if line_order_edit_distance_median_high in single_edit_distance_list:
                median_pid_list.append(pid)
                break

        if median_pid_list[0] == median_pid_list[1]:
            median_pid_list.pop()
        return median_pid_list, line_order_edit_distance_median

    def _create_pid_evaluator_list(self, options):
        pid_evaluator_list = []

        # get full PID directory list
        pred_pid_data_dir_list = [pid_dir for pid_dir in glob.glob(os.path.join(options.pred_data_root_dir, '*')) if os.path.isdir(pid_dir)]

        # check if there is xml directory in PID directory, and there is only 1 xml file inside
        for pred_pid_data_dir in pred_pid_data_dir_list:
            pid_string = os.path.basename(pred_pid_data_dir)
            gt_pid_data_dir = os.path.join(options.gt_data_root_dir, pid_string)
            try:
                # input data validation check
                for id, pid_dir in enumerate([pred_pid_data_dir, gt_pid_data_dir]):
                    # input directory check
                    if not os.path.isdir(pid_dir):
                        raise FileNotFoundError('pid directory {0} not found.'.format(pid_dir))
                    # xml file check
                    xml_dir = os.path.join(pid_dir, 'xml')
                    if not os.path.isdir(xml_dir):
                        raise FileNotFoundError('xml directory not found in {0}.'.format(pid_dir))
                    if id == 0:
                        xml_file_list = glob.glob(os.path.join(xml_dir, '*.sorted.xml'))
                    else:
                        xml_file_list = glob.glob(os.path.join(xml_dir, '*.xml'))
                    if len(xml_file_list) != 1:
                        raise FileNotFoundError('xml file must be only one in each xml directory. : {0}'.format(xml_file_list))

                # set instance properties
                pred_xml_dir = os.path.join(pred_pid_data_dir, 'xml')
                pred_xml_file_list = glob.glob(os.path.join(pred_xml_dir, '*.sorted.xml'))
                pred_xml_file_path = pred_xml_file_list[0]

                gt_xml_dir = os.path.join(gt_pid_data_dir, 'xml')
                gt_xml_file_list = glob.glob(os.path.join(gt_xml_dir, '*.xml'))
                gt_xml_file_path = gt_xml_file_list[0]

                pid_data_evaluator = PidDataEvaluator(self.output_root_dir, pid_string, pred_xml_file_path, gt_xml_file_path, options)
            except FileNotFoundError as err:
                print(err)
                continue
            pid_evaluator_list.append(pid_data_evaluator)

        return pid_evaluator_list
