# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/

import click
import json
import os
import sys

from ocrcli.core import OcrInferrer, OcrResultEvaluator
from ocrcli.core import utils


@click.group()
@click.pass_context
def cmd(ctx):
    pass


@cmd.command()
@click.pass_context
@click.argument('input_root')
@click.argument('output_root')
@click.option('-s', '--input_structure', type=click.Choice(['s', 'i', 't', 'w', 'f'], case_sensitive=True), default='s', help='Input directory structure type. s(single), i(intermediate_output), t(tosho_data), w(workstation), and f(image_file).')
@click.option('-p', '--proc_range', type=str, default='0..3', help='Inference process range to run. Default is "0..3".')
@click.option('-c', '--config_file', type=str, default='config.yml', help='Configuration yml file for inference. Default is "config.yml".')
@click.option('-i', '--save_image', type=bool, default=False, is_flag=True, help='Output result image file with text file.')
@click.option('-x', '--save_xml', type=bool, default=False, is_flag=True, help='Output result XML file with text file.')
@click.option('-d', '--dump', type=bool, default=False, is_flag=True, help='Dump all intermediate process output.')
@click.option('-r', '--ruby_only', type=bool, default=False, is_flag=True, help='Do ruby_read inference only.')
def infer(ctx, input_root, output_root, config_file, proc_range, save_image, save_xml, input_structure, dump, ruby_only):
    """
    \b
    INPUT_ROOT   \t: Input data directory for inference.
    OUTPUT_ROOT   \t: Output directory for inference result.
    """
    click.echo('start inference !')
    click.echo('input_root : {0}'.format(input_root))
    click.echo('output_root : {0}'.format(output_root))
    click.echo('config_file : {0}'.format(config_file))

    cfg = {
        'input_root': input_root,
        'output_root': output_root,
        'config_file': config_file,
        'proc_range': proc_range,
        'save_image': save_image,
        'save_xml': save_xml,
        'dump': dump,
        'input_structure': input_structure,
        'ruby_only': ruby_only
    }

    # check if input_root exists
    if not os.path.exists(input_root):
        print('INPUT_ROOT not found :{0}'.format(input_root), file=sys.stderr)
        exit(0)

    # parse command line option
    infer_cfg = utils.parse_cfg(cfg)
    if infer_cfg is None:
        print('[ERROR] Config parse error :{0}'.format(input_root), file=sys.stderr)
        exit(1)

    # prepare output root derectory
    infer_cfg['output_root'] = utils.mkdir_with_duplication_check(infer_cfg['output_root'])

    # save inference option
    with open(os.path.join(infer_cfg['output_root'], 'opt.json'), 'w') as fp:
        json.dump(infer_cfg, fp, ensure_ascii=False, indent=4,
                  sort_keys=True, separators=(',', ': '))

    # do inference
    inferrer = OcrInferrer(infer_cfg)
    inferrer.run()


@cmd.command()
@click.pass_context
@click.argument('input_pred_data')
@click.argument('input_gt_data')
@click.argument('output_root')
@click.option('-s', '--input_structure', type=click.Choice(['d', 's'], case_sensitive=True), default='d', help='Input data structure type. s(single) and d(directory).')
@click.option('-c', '--config_file', type=str, default='eval_config.yml', help='Configuration yml file for evaluation. Default is "eval_config.yml".')
def evaluate(ctx, input_pred_data, input_gt_data, output_root, input_structure, config_file):
    """
    \b
    INPUT_PRED_DATA   \t: Input inference result data path for evaluation.
    INPUT_GT_DATA   \t: Input grand truth data path for evaluation.
    OUTPUT_ROOT   \t: Output directory for evaluation result.
    """
    click.echo('start evaluation !')
    click.echo('input_pred_data : {0}'.format(input_pred_data))
    click.echo('input_gt_data : {0}'.format(input_gt_data))
    click.echo('output_root : {0}'.format(output_root))
    click.echo('input_structure : {0}'.format(input_structure))
    click.echo('config_file : {0}'.format(config_file))

    cfg = {
        'input_pred_data': input_pred_data,
        'input_gt_data': input_gt_data,
        'output_root_dir': output_root,
        'input_structure': input_structure,
        'config_file': config_file
    }

    # check if input_pred_data exists
    if not os.path.exists(input_pred_data):
        print('INPUT_PRED_DATA not found :{0}'.format(input_pred_data), file=sys.stderr)
        exit(0)

    # check if input_gt_data exists
    if not os.path.exists(input_gt_data):
        print('INPUT_PRED_DATA not found :{0}'.format(input_gt_data), file=sys.stderr)
        exit(0)

    # parse command line option
    eval_cfg = utils.parse_eval_cfg(cfg)
    if eval_cfg is None:
        print('[ERROR] Config parse error.', file=sys.stderr)
        exit(1)

    # prepare output root derectory
    eval_cfg['output_root_dir'] = utils.mkdir_with_duplication_check(eval_cfg['output_root_dir'])

    # save inference option
    with open(os.path.join(eval_cfg['output_root_dir'], 'opt.json'), 'w') as fp:
        json.dump(eval_cfg, fp, ensure_ascii=False, indent=4,
                  sort_keys=True, separators=(',', ': '))

    # do evaluation
    evaluator = OcrResultEvaluator(eval_cfg)
    evaluator.run()


def main():
    cmd(obj={})


if __name__ == '__main__':
    main()
