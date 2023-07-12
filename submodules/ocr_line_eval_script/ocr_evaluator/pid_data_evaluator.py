# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import datetime
import json
import os
import xml.etree.ElementTree as ET
from .page_evaluator import PageEvaluator


class PidDataEvaluator:
    def __init__(self, output_root_dir, pid_string, pred_xml, gt_xml, options):
        # prepare output directory
        output_dir = os.path.join(output_root_dir, pid_string)
        while(os.path.isdir(output_dir)):
            time_str = datetime.datetime.now().strftime('%y%m%d%H%M%S')
            output_dir += '_{0}'.format(time_str)
        os.makedirs(output_dir)
        self.output_dir = output_dir

        self.pid_string = pid_string
        self.pred_xml_file_path = pred_xml
        self.gt_xml_file_path = gt_xml
        self.options = options

        self.page_evaluator_list = []

    def load_page_evaluators(self):
        pred_page_block_list = self._extract_page_block_list(self.pred_xml_file_path)
        gt_page_block_list = self._extract_page_block_list(self.gt_xml_file_path)

        for pred_page_block in pred_page_block_list[:]:
            for gt_page_block in gt_page_block_list[:]:
                if gt_page_block.attrib['IMAGENAME'] == pred_page_block.attrib['IMAGENAME']:
                    page_evaluator = PageEvaluator(pred_page_block, gt_page_block, self.options)
                    self.page_evaluator_list.append(page_evaluator)
                    pred_page_block_list.remove(pred_page_block)
                    gt_page_block_list.remove(gt_page_block)
                    break
            else:
                print('Page block for {0} not found in'.format(pred_page_block.attrib['IMAGENAME'], self.gt_xml_file_path))

        if len(gt_page_block_list) > 0:
            for gt_page_block in gt_page_block_list:
                print('There is no corresponding page block for page {0} in {1}'.format(gt_page_block.attrib['IMAGENAME'], self.pred_xml_file_path))

    def do_evaluation(self):
        print('#### Start PID Data Evaluation : pid={0}####'.format(self.pid_string))
        for page_evaluator in self.page_evaluator_list:
            page_evaluator.load_line_evaluators()
            page_evaluator.do_evaluation()

        self._output_eval_log()

    def get_line_ocr_edit_distance_average(self):
        edit_distance_sum = 0
        for page_evaluator in self.page_evaluator_list:
            edit_distance_sum += page_evaluator.get_line_ocr_edit_distance_average()
        return edit_distance_sum / len(self.page_evaluator_list)

    def get_line_ocr_edit_distance_list(self):
        edit_distance_list = []
        for page_evaluator in self.page_evaluator_list:
            edit_distance_list.append(page_evaluator.get_line_ocr_edit_distance_average())
        return edit_distance_list

    def get_line_order_edit_distance_average(self):
        edit_distance_sum = 0
        for page_evaluator in self.page_evaluator_list:
            edit_distance_sum += page_evaluator.normalized_line_order_edit_distance
        return edit_distance_sum / len(self.page_evaluator_list)

    def get_line_order_edit_distance_list(self):
        edit_distance_list = []
        for page_evaluator in self.page_evaluator_list:
            edit_distance_list.append(page_evaluator.normalized_line_order_edit_distance)
        return edit_distance_list

    def _extract_page_block_list(self, xml_file_path):
        def remove_namespace(root, namespace):
            for block in root.getiterator():
                if block.tag.startswith(namespace):
                    block.tag = block.tag[len(namespace):]
        try:
            ET.register_namespace('', 'NDLOCRDATASET')
            full_xml_data = ET.parse(xml_file_path)
        except ET.ParseError as err:
            print(err)
            return []

        root = full_xml_data.getroot()
        remove_namespace(root, u'{NDLOCRDATASET}')

        page_block_list = []
        for page in root.iter('PAGE'):
            page_block_list.append(page)

        return page_block_list

    def _output_eval_log(self):
        json_file = os.path.join(self.output_dir, 'ocr_evaluation.log')
        page_log_dict = {}
        page_log_dict['line_ocr_edit_distance_average_for_pid'] = self.get_line_ocr_edit_distance_average()
        page_log_dict['normalized_line_order_edit_distance_for_pid'] = self.get_line_order_edit_distance_average()

        # dump line_ocr_edit_distance_average for each page
        page_log_dict['line_ocr_edit_distance_average_for_page'] = {}
        page_log_dict['normalized_line_order_edit_distance_for_page'] = {}
        for page_id, page_evaluator in enumerate(self.page_evaluator_list):
            line_ocr_edit_distance_average_for_page = page_evaluator.get_line_ocr_edit_distance_average()
            page_log_dict['line_ocr_edit_distance_average_for_page'][page_id] = line_ocr_edit_distance_average_for_page
            page_log_dict['normalized_line_order_edit_distance_for_page'][page_id] = page_evaluator.normalized_line_order_edit_distance

        with open(json_file, 'w') as fp:
            json.dump(page_log_dict, fp, indent=2)
