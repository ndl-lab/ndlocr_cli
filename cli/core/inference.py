# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


import copy
import cv2
import glob
import os
import pathlib
import sys
import time
import xml
import xml.etree.ElementTree as ET

from . import utils
from .. import procs

# Add import path for submodules
currentdir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(currentdir) + "/../../submodules/separate_pages_ssd")
sys.path.append(str(currentdir) + "/../../submodules/ndl_layout")
sys.path.append(str(currentdir) + "/../../submodules/deskew_HT")
sys.path.append(str(currentdir) + "/../../submodules/text_recognition_lightning")
sys.path.append(str(currentdir) + "/../../submodules/reading_order")

# supported image type list
supported_img_ext = ['.jpg', '.jpeg', '.jp2','.png','.tiff','.bmp','.tif','.JPG','.PNG']

class OcrInferrer:
    """
    推論実行時の関数や推論の設定値を保持します。

    Attributes
    ----------
    full_proc_list : list
        全推論処理のリストです。
    proc_list : list
        本実行処理における推論処理のリストです。
    cfg : dict
        本実行処理における設定情報です。
    """

    def __init__(self, cfg):
        """
        Parameters
        ----------
        cfg : dict
            本実行処理における設定情報です。
        """
        # inference process class list in order
        self.full_proc_list = [
            procs.PageSeparation,           # 0: ノド元分割               出力：（画像：あり、XML：なし、TXT：なし）
            procs.PageDeskewProcess,        # 1: 傾き補正                 出力：（画像：あり、XML：なし、TXT：なし）
            procs.LayoutExtractionProcess,  # 2: レイアウト抽出           出力：（画像：あり、XML：あり、TXT：なし）
            procs.LineOcrProcess,           # 3: 文字認識(OCR)            出力：（画像：あり、XML：あり、TXT：あり）
        ]
        self.proc_list = self._create_proc_list(cfg)
        self.cfg = cfg
        self.total_time_statistics = []
        self.proc_time_statistics = {}
        for proc in self.proc_list:
            self.proc_time_statistics[proc.proc_name] = []
        self.xml_template = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<OCRDATASET></OCRDATASET>'

    def run(self):
        """
        self.cfgに保存された設定に基づいた推論処理を実行します。
        """
        if len(self.cfg['input_dirs']) == 0:
            print('[ERROR] Input directory list is empty', file=sys.stderr)
            return

        # input dir loop
        for input_dir in self.cfg['input_dirs']:
            if self.cfg['input_structure'] in ['t']:
                single_outputdir_data_list = self._get_single_dir_data_from_tosho_data(input_dir)
            else:
                single_outputdir_data_list = self._get_single_dir_data(input_dir)

            if single_outputdir_data_list is None:
                print('[ERROR] Input data list is empty', file=sys.stderr)
                continue
            print(single_outputdir_data_list)
            # do infer with input data for single output data dir
            for single_outputdir_data in single_outputdir_data_list:
                if single_outputdir_data is None:
                    continue
                if self.cfg['ruby_only']:
                    pred_list = self._infer_ruby_only(single_outputdir_data)
                else:
                    pred_list = self._infer(single_outputdir_data)

                # save inferenced xml in xml directory
                if (self.cfg['save_xml'] or self.cfg['partial_infer']) and (self.cfg['proc_range']['end'] > 1):
                    self._save_pred_xml(single_outputdir_data['output_dir'], [single_data['xml'] for single_data in pred_list], self.cfg['line_order'])
        if len(self.total_time_statistics) == 0:
            print('================== NO VALID INFERENCE ==================')
        else:
            print('================== PROCESSING TIME ==================')
            for proc_name, proc_time_list in self.proc_time_statistics.items():
                proc_averaege = sum(proc_time_list) / len(proc_time_list)
                print(f'Average processing time ({proc_name})'.ljust(45, ' ') + f': {proc_averaege:8.4f} sec / image file ')
            total_average = sum(self.total_time_statistics) / len(self.total_time_statistics)
            print(f'Average processing time (total)'.ljust(45, ' ') + f': {total_average:8.4f} sec / image file ')
        return

    def _infer_ruby_only(self, single_outputdir_data):
        """
        self.cfgに保存された設定に基づき、XML一つ分のデータに対するルビ推定処理を実行します。

        Parameters
        ----------
        single_outputdir_data : dict
            XML一つ分のデータ（基本的に1書籍分を想定）の入力データ情報。
            入力となるXMLデータを含みます。

        Returns
        -------
        pred_list : list
            1ページ分の推論結果を要素に持つ推論結果のリスト。
            各結果は辞書型で保持されています。
        """
        # single_outputdir_data dictionary include [key, value] pairs as below
        # [key, value]: ['img', None], ['xml', xml_tree]
        pred_list = []
        pred_xml_dict_for_dump = {}

        for page_idx, page_xml in enumerate(single_outputdir_data['xml'].findall('PAGE')):
            single_image_file_data = self._get_single_image_file_data(page_idx, single_outputdir_data)
            if single_image_file_data is None:
                print('[ERROR] Failed to get single page input data.')
                continue

            print('######## START PAGE INFERENCE PROCESS ########')
            start_page = time.time()

            for proc in self.proc_list:
                start_proc = time.time()
                single_page_output = []
                for idx, single_data_input in enumerate(single_image_file_data):
                    single_data_output = proc.do(idx, single_data_input)
                    single_page_output.extend(single_data_output)

                single_image_file_data = single_page_output
                self.proc_time_statistics[proc.proc_name].append(time.time() - start_proc)

            single_image_file_output = single_image_file_data
            self.total_time_statistics.append(time.time() - start_page)

            # save inferenced result text for this page
            sum_main_txt = ''
            sum_cap_txt = ''
            sum_ruby_txt = ''

            # check if xml output for this image is vertical text
            vertical_text_page = 0
            for single_data_output in single_image_file_output:
                if self._is_vertical_text_xml(single_data_output['xml']):
                    vertical_text_page += 1

            # reverse order of page if all pages are vertical text
            single_image_file_output_for_txt = single_image_file_output
            if vertical_text_page >= len(single_image_file_output):
                single_image_file_output_for_txt = list(reversed(single_image_file_output))

            for single_data_output in single_image_file_output_for_txt:
                main_txt, cap_txt = self._create_result_txt(single_data_output['xml'])
                sum_main_txt += main_txt + '\n'
                sum_cap_txt += sum_cap_txt + '\n'
                sum_ruby_txt += single_data_output['ruby_txt'] + '\n'

                self._save_pred_txt(sum_main_txt, sum_cap_txt, sum_ruby_txt, page_xml.attrib['IMAGENAME'], single_outputdir_data['output_dir'])

            # add inference result for single image file data to pred_list, including XML data
            pred_list.extend(single_image_file_output)
            print('########  END PAGE INFERENCE PROCESS  ########')

        return pred_list

    def _infer(self, single_outputdir_data):
        """
        self.cfgに保存された設定に基づき、XML一つ分のデータに対する推論処理を実行します。

        Parameters
        ----------
        single_outputdir_data : dict
            XML一つ分のデータ（基本的に1書籍分を想定）の入力データ情報。
            画像ファイルパスのリスト、それらに対応するXMLデータを含みます。

        Returns
        -------
        pred_list : list
            1ページ分の推論結果を要素に持つ推論結果のリスト。
            各結果は辞書型で保持されています。
        """
        # single_outputdir_data dictionary include [key, value] pairs as below
        # (xml is not always included)
        #   [key, value]: ['img', numpy.ndarray], ['xml', xml_tree]
        pred_list = []
        pred_xml_dict_for_dump = {}
        if self.cfg['dump']:
            dump_dir = os.path.join(single_outputdir_data['output_dir'], 'dump')
            os.makedirs(dump_dir, exist_ok=True)

            for proc in self.proc_list:
                pred_xml_dict_for_dump[proc.proc_name] = []
                proc_dump_dir = os.path.join(dump_dir, proc.proc_name)
                os.makedirs(proc_dump_dir, exist_ok=True)

        for img_path in single_outputdir_data['img_list']:
            single_image_file_data = self._get_single_image_file_data(img_path, single_outputdir_data)
            output_dir = single_outputdir_data['output_dir']
            if single_image_file_data is None:
                print('[ERROR] Failed to get single page input data for image:{0}'.format(img_path), file=sys.stderr)
                continue

            print('######## START PAGE INFERENCE PROCESS ########')
            start_page = time.time()

            for proc in self.proc_list:
                start_proc = time.time()
                single_page_output = []
                for idx, single_data_input in enumerate(single_image_file_data):
                    single_data_output = proc.do(idx, single_data_input)
                    single_page_output.extend(single_data_output)
                # save inference result data to dump
                if self.cfg['dump'] and 'xml' in single_image_file_data[0].keys():
                    pred_xml_dict_for_dump[proc.proc_name].append(single_image_file_data[0]['xml'])

                single_image_file_data = single_page_output
                self.proc_time_statistics[proc.proc_name].append(time.time() - start_proc)

            single_image_file_output = single_image_file_data
            self.total_time_statistics.append(time.time() - start_page)

            if self.cfg['save_image'] or self.cfg['partial_infer']:
                # save inferenced result drawn image in pred_img directory
                for single_data_output in single_image_file_output:
                    # save input image while partial inference
                    if self.cfg['partial_infer']:
                        img_output_dir = os.path.join(output_dir, 'img')
                        self._save_image(single_data_output['img'], single_data_output['img_file_name'], img_output_dir)

                    pred_img = self._create_result_image(single_data_output, self.proc_list[-1].proc_name)
                    img_output_dir = os.path.join(output_dir, 'pred_img')
                    self._save_image(pred_img, single_data_output['img_file_name'], img_output_dir)

            # save inferenced result text for this page
            if self.cfg['proc_range']['end'] > 2:
                sum_main_txt = ''
                sum_cap_txt = ''
                sum_ruby_txt = None
                if self.cfg['ruby_read']:
                    sum_ruby_txt = ''

                # check if xml output for this image is vertical text
                vertical_text_page = 0
                for single_data_output in single_image_file_output:
                    if self._is_vertical_text_xml(single_data_output['xml']):
                        vertical_text_page += 1

                # reverse order of page if it's vertical text
                single_image_file_output_for_txt = single_image_file_output
                if vertical_text_page >= len(single_image_file_output):
                    single_image_file_output_for_txt = list(reversed(single_image_file_output))

                for single_data_output in single_image_file_output_for_txt:
                    main_txt, cap_txt = self._create_result_txt(single_data_output['xml'])
                    sum_main_txt += main_txt + '\n'
                    sum_cap_txt += sum_cap_txt + '\n'
                    if self.cfg['ruby_read']:
                        sum_ruby_txt += single_data_output['ruby_txt'] + '\n'

                self._save_pred_txt(sum_main_txt, sum_cap_txt, sum_ruby_txt, os.path.basename(img_path), single_outputdir_data['output_dir'])

            # add inference result for single image file data to pred_list, including XML data
            pred_list.extend(single_image_file_output)
            print('########  END PAGE INFERENCE PROCESS  ########')

        return pred_list

    def _get_single_dir_data(self, input_dir):
        """
        XML一つ分の入力データに関する情報を整理して取得します。

        Parameters
        ----------
        input_dir : str
            XML一つ分の入力データが保存されているディレクトリパスです。

        Returns
        -------
        # Fixme
        single_dir_data : dict
            XML一つ分のデータ（基本的に1PID分を想定）の入力データ情報です。
            画像ファイルパスのリスト、それらに対応するXMLデータを含みます。
        """
        single_dir_data = {'input_dir': os.path.abspath(input_dir)}
        single_dir_data['img_list'] = []

        # get img list of input directory
        if not self.cfg['ruby_only']:
            if self.cfg['input_structure'] in ['w']:
                for ext in supported_img_ext:
                    single_dir_data['img_list'].extend(sorted(glob.glob(os.path.join(input_dir, '*{0}'.format(ext)))))
            elif self.cfg['input_structure'] in ['f']:
                stem, ext = os.path.splitext(os.path.basename(input_dir))
                if ext in supported_img_ext:
                    single_dir_data['img_list'] = [input_dir]
                else:
                    print('[ERROR] This file is not supported type : {0}'.format(input_dir), file=sys.stderr)
            elif not os.path.isdir(os.path.join(input_dir, 'img')):
                print('[ERROR] Input img diretctory not found in {}'.format(input_dir), file=sys.stderr)
                return None
            else:
                for ext in supported_img_ext:
                    single_dir_data['img_list'].extend(sorted(glob.glob(os.path.join(input_dir, 'img/*{0}'.format(ext)))))

        # check xml file number and load xml data if needed
        if (self.cfg['proc_range']['start'] > 2) or self.cfg['ruby_only']:
            if self.cfg['input_structure'] in ['f']:
                print('[ERROR] Single image file input mode does not support partial inference wich need xml file input.', file=sys.stderr)
                return None
            input_xml = None
            xml_file_list = glob.glob(os.path.join(input_dir, 'xml/*.xml'))
            if len(xml_file_list) > 1:
                print('[ERROR] Input xml file must be only one, but there is {0} xml files in {1}.'.format(
                    len(xml_file_list), os.path.join(self.cfg['input_root'], 'xml')), file=sys.stderr)
                return None
            elif len(xml_file_list) == 0:
                print('[ERROR] There is no input xml files in {0}.'.format(os.path.join(input_dir, 'xml')), file=sys.stderr)
                return None
            else:
                input_xml = xml_file_list[0]
            try:
                single_dir_data['xml'] = ET.parse(input_xml)
            except xml.etree.ElementTree.ParseError as err:
                print("[ERROR] XML parse error : {0}".format(input_xml), file=sys.stderr)
                return None

        # prepare output dir for inferensce result with this input dir
        if self.cfg['input_structure'] in ['f']:
            stem, ext = os.path.splitext(os.path.basename(input_dir))
            output_dir = os.path.join(self.cfg['output_root'], stem)
        elif self.cfg['input_structure'] in ['i', 's']:
            dir_name = os.path.basename(input_dir)
            output_dir = os.path.join(self.cfg['output_root'], dir_name)
        elif self.cfg['input_structure'] in ['w']:
            input_dir_names = input_dir.split('/')
            dir_name = input_dir_names[-3][0] + input_dir_names[-2] + input_dir_names[-1]
            output_dir = os.path.join(self.cfg['output_root'], dir_name)
        else:
            print('[ERROR] Unexpected input directory structure type: {}.'.format(self.cfg['input_structure']), file=sys.stderr)
            return None

        # output directory existence check
        output_dir = utils.mkdir_with_duplication_check(output_dir)
        single_dir_data['output_dir'] = output_dir

        return [single_dir_data]

    def _get_single_dir_data_from_tosho_data(self, input_dir):
        """
        XML一つ分の入力データに関する情報を整理して取得します。

        Parameters
        ----------
        input_dir : str
            tosho data形式のセクションごとのディレクトリパスです。

        Returns
        -------
        single_dir_data_list : list
            XML一つ分のデータ（基本的に1PID分を想定）の入力データ情報のリストです。
            1つの要素に画像ファイルパスのリスト、それらに対応するXMLデータを含みます。
        """

        if self.cfg['ruby_only']:
            print("[ERROR] tosho_data input mode doesn't support ruby_only mode.", file=sys.stderr)
            return None

        single_dir_data_list = []

        # get img list of input directory
        tmp_img_list = sorted(glob.glob(os.path.join(input_dir, '*.jp2')))
        tmp_img_list.extend(sorted(glob.glob(os.path.join(input_dir, '*.jpg'))))

        pid_list = []
        for img in tmp_img_list:
            pid = os.path.basename(img).split('_')[0]
            if pid not in pid_list:
                pid_list.append(pid)

        for pid in pid_list:
            single_dir_data = {'input_dir': os.path.abspath(input_dir),
                               'img_list': [img for img in tmp_img_list if os.path.basename(img).startswith(pid)]}

            # prepare output dir for inferensce result with this input dir
            output_dir = os.path.join(self.cfg['output_root'], pid)

            # output directory existance check
            os.makedirs(output_dir, exist_ok=True)
            single_dir_data['output_dir'] = output_dir
            single_dir_data_list.append(single_dir_data)

        return single_dir_data_list

    def _get_single_image_file_data(self, img_path, single_dir_data):
        """
        1ページ分の入力データに関する情報を整理して取得します。

        Parameters
        ----------
        img_path : str
            入力画像データのパスです。
        single_dir_data : dict
            1書籍分の入力データに関する情報を保持する辞書型データです。
            xmlファイルへのパス、結果を出力するディレクトリのパスなどを含みます。

        Returns
        -------
        single_image_file_data : dict
            1ページ分のデータの入力データ情報です。
            画像ファイルのパスとnumpy.ndarray形式の画像データ、その画像に対応するXMLデータを含みます。
        """
        single_image_file_data = [{
            'img_path': img_path,
            'img_file_name': os.path.basename(img_path) if isinstance(img_path, str) else None,
            'output_dir': single_dir_data['output_dir']
        }]

        full_xml = None
        if 'xml' in single_dir_data.keys():
            full_xml = single_dir_data['xml']

        # get img data for single page
        if isinstance(img_path, str):
            orig_img = cv2.imread(img_path)
            if orig_img is None:
                print('[ERROR] Image read error : {0}'.format(img_path), file=sys.stderr)
                return None
            single_image_file_data[0]['img'] = orig_img

        # return if this proc needs only img data for input
        if full_xml is None:
            return single_image_file_data

        if self.cfg['ruby_only']:
            tmp_idx = 0
            for page in full_xml.getroot().iter('PAGE'):
                if tmp_idx == img_path:
                    node = ET.fromstring(self.xml_template)
                    node.append(page)
                    tree = ET.ElementTree(node)
                    single_image_file_data[0]['xml'] = tree
                    break
                tmp_idx += 1
            return single_image_file_data

        # get xml data for single page
        image_name = os.path.basename(img_path)
        for page in full_xml.getroot().iter('PAGE'):
            if page.attrib['IMAGENAME'] == image_name:
                node = ET.fromstring(self.xml_template)
                node.append(page)
                tree = ET.ElementTree(node)
                single_image_file_data[0]['xml'] = tree
                break

        if 'xml' not in single_image_file_data[0].keys():
            print('[ERROR] Input PAGE data for page {} not found in XML data.'.format(img_path), file=sys.stderr)
            return None

        return single_image_file_data

    def _create_proc_list(self, cfg):
        """
        推論の設定情報に基づき、実行する推論処理のリストを作成します。

        Parameters
        ----------
        cfg : dict
            推論実行時の設定情報を保存した辞書型データ。
        """
        if cfg['ruby_only']:
            return [procs.RubyReadingProcess(cfg, 'ex2')]

        proc_list = []
        for i in range(cfg['proc_range']['start'], cfg['proc_range']['end'] + 1):
            proc_list.append(self.full_proc_list[i](cfg, i))
        if cfg['line_order']:
            if cfg['proc_range']['end'] <= 2:
                print('[WARNING] LineOrderProcess will be skipped(this process needs LineOcrProcess output).')
            else:
                proc_list.append(procs.LineOrderProcess(cfg, 'ex1'))
        if cfg['ruby_read']:
            if cfg['proc_range']['end'] <= 2 or not cfg['line_order']:
                print('[WARNING] RubyReadingProcess will be skipped(this process needs LineOrderProcess output).')
            else:
                proc_list.append(procs.RubyReadingProcess(cfg, 'ex2'))
        if cfg['line_attribute']['add_title_author']:
            if cfg['proc_range']['end'] <= 2:
                print('[WARNING] LineAttributeProcess will be skipped(this process needs LineOcrProcess output).')
            else:
                proc_list.append(procs.LineAttributeProcess(cfg, 'ex3'))

        return proc_list

    def _save_pred_xml(self, output_dir, pred_list, sorted):
        """
        推論結果のXMLデータをまとめたXMLファイルを生成して保存します。

        Parameters
        ----------
        output_dir : str
            推論結果を保存するディレクトリのパスです。
        pred_list : list
            1ページ分の推論結果を要素に持つ推論結果のリスト。
            各結果は辞書型で保持されています。
        sorted : bool
            読み順認識が実行されたかどうかのフラグ。
        """
        xml_dir = os.path.join(output_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)

        # basically, output_dir is supposed to be PID, so it used as xml filename
        if sorted:
            xml_path = os.path.join(xml_dir, '{}.sorted.xml'.format(os.path.basename(output_dir)))
        else:
            xml_path = os.path.join(xml_dir, '{}.xml'.format(os.path.basename(output_dir)))
        pred_xml = self._parse_pred_list_to_save(pred_list)
        utils.save_xml(pred_xml, xml_path)
        return

    def _save_image(self, pred_img, orig_img_name, img_output_dir, id=''):
        """
        指定されたディレクトリに画像データを保存します。
        画像データは入力に使用したものと推論結果を重畳したものの２種類が想定されています。

        Parameters
        ----------
        pred_img : numpy.ndarray
            保存する画像データ。
        orig_img_name : str
            もともとの入力画像のファイル名。
            基本的にはこのファイル名と同名で保存します。
        img_output_dir : str
            画像ファイルの保存先のディレクトリパス。
        id : str
            もともとの入力画像のファイル名に追加する処理結果ごとのidです。
            一つの入力画像から複数の画像データが出力される処理がある場合に必要になります。
        """
        os.makedirs(img_output_dir, exist_ok=True)
        stem, ext = os.path.splitext(orig_img_name)
        orig_img_name = stem + '.jpg'

        if id != '':
            stem, ext = os.path.splitext(orig_img_name)
            orig_img_name = stem + '_' + id + ext

        img_path = os.path.join(img_output_dir, orig_img_name)
        try:
            cv2.imwrite(img_path, pred_img)
        except OSError as err:
            print("[ERROR] Image save error: {0}".format(err), file=sys.stderr)
            raise OSError

        return

    def _save_pred_txt(self, main_txt, cap_txt, ruby_txt, orig_img_name, output_dir):
        """
        指定されたディレクトリに推論結果のテキストデータを保存します。

        Parameters
        ----------
        main_txt : str
            本文＋キャプションの推論結果のテキストデータです
        cap_txt : str
            キャプションのみの推論結果のテキストデータです
        ruby_txt : str
            ルビのみの推論結果のテキストデータです
        orig_img_name : str
            もともとの入力画像ファイル名。
            基本的にはこのファイル名と同名で保存します。
        img_output_dir : str
            画像ファイルの保存先のディレクトリパス。
        """
        txt_dir = os.path.join(output_dir, 'txt')
        os.makedirs(txt_dir, exist_ok=True)

        stem, _ = os.path.splitext(orig_img_name)
        txt_path = os.path.join(txt_dir, stem + '_cap.txt')
        try:
            with open(txt_path, 'w') as f:
                f.write(cap_txt)
        except OSError as err:
            print("[ERROR] Caption text save error: {0}".format(err), file=sys.stderr)
            raise OSError

        stem, _ = os.path.splitext(orig_img_name)
        txt_path = os.path.join(txt_dir, stem + '_main.txt')
        try:
            with open(txt_path, 'w') as f:
                f.write(main_txt)
        except OSError as err:
            print("[ERROR] Main text save error: {0}".format(err), file=sys.stderr)
            raise OSError

        if ruby_txt is not None:
            stem, _ = os.path.splitext(orig_img_name)
            txt_path = os.path.join(txt_dir, stem + '_ruby.txt')
            try:
                with open(txt_path, 'w') as f:
                    f.write(ruby_txt)
            except OSError as err:
                print("[ERROR] Ruby text save error: {0}".format(err), file=sys.stderr)
                raise OSError

        return

    def _parse_pred_list_to_save(self, pred_list):
        """
        推論結果のXMLを要素に持つリストから、ファイルに保存するための一つのXMLデータを生成します。

        Parameters
        ----------
        pred_list : list
            推論結果のXMLを要素に持つリスト。
        """
        ET.register_namespace('', 'NDLOCRDATASET')
        node = ET.fromstring(self.xml_template)
        for single_xml_tree in pred_list:
            root = single_xml_tree.getroot()
            for element in root:
                node.append(element)

        tree = ET.ElementTree(node)
        return tree

    def _create_result_image(self, result, proc_name):
        """
        推論結果を入力画像に重畳した画像データを生成します。

        Parameters
        ----------
        result : dict
            1ページ分の推論結果を持つ辞書型データ。
        proc_name : str
            重畳を行う結果を出力した推論処理の名前。
        """
        if 'dump_img' in result.keys():
            dump_img = copy.deepcopy(result['dump_img'])
        else:
            dump_img = copy.deepcopy(result['img'])
        if 'xml' in result.keys() and result['xml'] is not None:
            # draw inference result on input image
            cv2.putText(dump_img, proc_name, (0, 50),
                        cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 5, cv2.LINE_AA)
            pass
        else:
            cv2.putText(dump_img, proc_name, (0, 50),
                        cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 5, cv2.LINE_AA)
        return dump_img

    def _create_result_txt(self, xml_data):
        """
        推論結果のxmlデータからテキストデータを生成します。

        Parameters
        ----------
        xml_data :
            1ページ分の推論結果を持つxmlデータ。
        """
        main_txt = ''
        cap_txt = ''
        for page_xml in xml_data.iter('PAGE'):
            for line_xml in page_xml.iter('LINE'):
                main_txt += line_xml.attrib['STRING']
                main_txt += '\n'
                if line_xml.attrib['TYPE'] == 'キャプション':
                    cap_txt += line_xml.attrib['STRING']
                    cap_txt += '\n'

        return main_txt, cap_txt

    def _is_vertical_text_xml(self, xml_data):
        """
        与えられたxmlデータが縦書きテキストかどうか判定します

        Parameters
        ----------
        xml_data :
            1ページ分の推論結果を持つxmlデータ。
        """
        all_line_num = 0
        vertical_line_num = 0
        for page_xml in xml_data.iter('PAGE'):
            for line_xml in page_xml.iter('LINE'):
                w = int(line_xml.attrib['WIDTH'])
                h = int(line_xml.attrib['HEIGHT'])
                if w < h:
                    vertical_line_num += 1
                all_line_num += 1
        return (all_line_num / 2) < vertical_line_num
