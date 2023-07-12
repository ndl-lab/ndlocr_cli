# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import argparse
import datetime
import logging
import os
import sys


def validate_options(options):
    # args validation
    if options.gt_data_root_dir is not None and not os.path.isdir(options.gt_data_root_dir):
        raise FileNotFoundError('Ground truth data root directory not found : {0}'.format(options.gt_data_root_dir))
    if options.pred_data_root_dir is not None and not os.path.isdir(options.pred_data_root_dir):
        raise FileNotFoundError('Prediction data root directory not found : {0}'.format(options.pred_data_root_dir))
    if options.pred_single_xml is not None:
        if options.gt_data_root_dir is not None:
            logging.warning('gt_data_root_dir will be ignored when pred_single_xml is set')
        if not os.path.isfile(options.pred_single_xml):
            raise FileNotFoundError('Prediction data xml file not found : {0}'.format(options.pred_single_xml))
        elif options.gt_single_xml is None:
            raise ValueError('gt_single_xml must be set if pred_single_xml is set')
        elif not os.path.isfile(options.gt_single_xml):
            raise FileNotFoundError('Ground truth data xml file not found : {0}'.format(options.gt_single_xml))
    elif options.pred_data_root_dir is not None:
        if options.gt_single_xml is not None:
            logging.warning('gt_single_xml will be ignored when pred_single_xml is set')
        if not os.path.isdir(options.pred_data_root_dir):
            raise FileNotFoundError('Prediction data root directory not found : {0}'.format(options.pred_data_root_dir))
        elif options.gt_data_root_dir is None:
            raise ValueError('gt_data_root_dir must be set if pred_data_root_dir is set')
        elif not os.path.isdir(options.gt_data_root_dir):
            raise FileNotFoundError('Ground truth data root directory not found : {0}'.format(options.gt_data_root_dir))


def get_cli_options(args):
    # parse options
    parser = argparse.ArgumentParser()
    pred_group = parser.add_mutually_exclusive_group(required=True)
    pred_group.add_argument('--pred_single_xml', help='path to single inference result xml file')
    pred_group.add_argument('--pred_data_root_dir', help='path to output dir which contains PID output dirs')
    gt_group = parser.add_mutually_exclusive_group(required=True)
    gt_group.add_argument('--gt_single_xml', type=str, required=False, help='path to single ground truth xml file')
    gt_group.add_argument('--gt_data_root_dir', type=str, required=False, help='path to input dir which contains ground truth PID dirs')
    parser.add_argument('--iou_thresh', type=float, default=0.5, help='iou threshold to find corresponding bbox')
    parser.add_argument('--output_root_dir', type=str, required=True, default='.output_dir', help='output root dir')
    parser.add_argument('--correct_line_ocr_log', action='store_true', help='enable line ocr log which leven distace is 0')
    parser.add_argument('--eval_main_text_only', action='store_true', help='evaluate only main text')
    parser.add_argument('--eval_annotation_line_order', action='store_true', help='evaluate only main text')
    parser.add_argument('--ignore_inline_type_to_skip', action='store_true', help='check inline type when gt string is empty')
    parser.add_argument('--eval_all_valid_pred_line', action='store_true', help='evaluate all valid predicted line in line order evaluation')
    options = parser.parse_args(args)
    validate_options(options)

    return options


def main():
    try:
        options = get_cli_options(sys.argv[1:])
    except FileNotFoundError as err:
        print(err)
        sys.exit()

    from ocr_evaluator import OcrEvaluator
    output_root_dir = options.output_root_dir
    while(os.path.isdir(output_root_dir)):
        time_str = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        output_root_dir += '_{0}'.format(time_str)
    os.makedirs(output_root_dir)
    ocr_evaluator = OcrEvaluator(options)
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


if __name__ == '__main__':
    main()
