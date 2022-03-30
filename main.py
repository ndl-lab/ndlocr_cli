# Copyright (c) 2022, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import click
import json
import os
import sys

from cli.core import OcrInferencer
from cli.core import utils


@click.group()
@click.option('--debug', is_flag=True)
@click.pass_context
def cmd(ctx, debug):
    ctx.obj['DEBUG'] = debug


@cmd.command()
@click.pass_context
def help(ctx):
    if ctx.obj['DEBUG']:
        click.echo('DEBUG MODE!')
    click.echo('help!')


@cmd.command()
@click.pass_context
@click.argument('input_root')
@click.argument('output_root')
@click.option('-s', '--input_structure', type=click.Choice(['s', 'i', 't', 'w', 'f'], case_sensitive=True), default='w', help='Input directory structure type. s(single), i(intermediate_output), t(tosho_data), w(workstatin), and f(image_file).')
@click.option('-p', '--proc_range', type=str, default='0..3', help='Inference process range to run. Default is "0..3".')
@click.option('-c', '--config_file', type=str, default='config.yml', help='Configuration yml file for inference. Default is "config.yml".')
@click.option('-i', '--save_image', type=bool, default=False, is_flag=True, help='Output result image file with text file.')
@click.option('-x', '--save_xml', type=bool, default=False, is_flag=True, help='Output result XML file with text file.')
@click.option('-d', '--dump', type=bool, default=False, is_flag=True, help='Dump all intermediate process output.')
def infer(ctx, input_root, output_root, config_file, proc_range, save_image, save_xml, input_structure, dump):
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
        'input_structure': input_structure
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
    inferencer = OcrInferencer(infer_cfg)
    inferencer.run()


def main():
    cmd(obj={})


if __name__ == '__main__':
    main()
