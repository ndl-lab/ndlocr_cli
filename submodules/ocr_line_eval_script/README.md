# OCR読み順推論評価スクリプト
## 機能概要
このスクリプトはOCRの読み順推論の結果に対して精度評価を行うスクリプトです。
評価の対象は①行内の読み順と②行間の読み順です。
本プログラムは、国立国会図書館が株式会社モルフォAIソリューションズに委託して作成したものです。
本プログラムは、国立国会図書館がCC BY 4.0ライセンスで公開するものです。詳細については LICENSEをご覧ください。

### 行内の読み順に対する評価
一つの行ブロック内に含まれる文字の読み順に対する評価を行います。
正解データと推論データの行矩形を比較し、IoUが設定されたしきい値以上かつ最も高いものを対応する行の組として評価を行います。
評価指標は正解文字列と推論結果の文字列の編集距離(Levenshtein distance)を用います。
各行の正解文字列数を文字列の長さで正規化し、正規化編集距離として定義します。

`(正規化編集距離) = LevenshteinDistance(line_true_k, line_pred_k) / Length(line_true_k) )`

最終的には各ページにおける各行の正規化編集距離を集計し、平均値を求めます。

### 行間の読み順に対する評価
各ページ内にある行ブロックの読み順に対する評価を行います。
正解データと推論データの行矩形を比較し、IoUが設定されたしきい値以上かつ最も高いものを対応する行の組として評価を行います。
評価指標は正解文字列と推論結果の文字列の編集距離(Levenshtein distance)を用います。
本文行の順序を文字列とみなし、正解の本文行の順序と推論結果の本文行の順序の正規化編集距離を算出します。

`(正規化編集距離) = LevenshteinDistance(line_order_true, line_order_pred) / n`

## 使い方
次のような形で入力ディレクトリを指定して実行します。
実行結果は標準出力に表示されます。
```
$ python eval_order_leven.py --pred_data_root_dir sample_data/pred_data --gt_data_root_dir sample_data/gt_data

[WARNING] xml file must be only one in each xml directory. : ['sample_data/pred_data/invalid_dir/xml/duplic.xml', 'sample_data/pred_data/invalid_dir/xml/2939815.xml']
[WARNING] xml directory not found in sample_data/pred_data/dummy_dir.
PID directory for sample_data/pred_data/sample_002 not found in sample_data/gt_data
### XML PAGE AVERAGE LINE LEVEN DISTANCE : 0.05154639175257732
### XML PAGE LINE ORDER LEVEN DISTANCE : 2
### SINGLE XML AVERAGE LINE LEVEN DISTANCE : 0.02577319587628866
### SINGLE XML LINE ORDER LEVEN DISTANCE : 4.0
### ALL XML AVERAGE LINE LEVEN DISTANCE : 0.02577319587628866
### ALL XML LINE ORDER LEVEN DISTANCE : 4.0
```

## 入力仕様
### ディレクトリ入力モード
入力として、推論結果のデータと正解データが収められたディレクトリを指定します。
入力データの各ディレクトリは以下のような構成となっている想定です。

```
pred_data_root_dir/
└── PID
    └── xml
        └── PID.xml
```

```
gt_data_root_dir/
└── PID
    ├── img
    |   ├── PID_R.jpg
    |   └── PID_L.jpg
    └── xml
        └── PID.xml
```

- コマンド実行例
```
$ python eval_order_leven.py --pred_data_root_dir sample_data/pred_data --gt_data_root_dir sample_data/gt_data
```
### シングルファイル入力モード
入力として、推論結果のXMLファイルと正解データのXMLファイルを一つずつ指定します。

- コマンド実行例
```
$ python eval_order_leven.py --pred_single_xml sample_data/pred_data/2939815/xml/2939815.xml --gt_single_xml sample_data/gt_data/2939815/xml/2939815.xml --output_root_dir single_file_test_output_dir
```

## 出力仕様
`output_root_dir`オプションで指定された出力ディレクトリの配下に評価実行時のオプション情報、評価ログ、評価結果等を保存したファイルが保存されます。
また、PIDごとの出力ディレクトリも生成されます。
PIDごとの各出力ディレクトリにはログファイル等のデバッグ用情報が出力されます。

## 評価オプションについて
- iou_thresh：正解データ・推論データの対応する行を決定する際に利用するIoUのしきい値
- correct_line_ocr_log：推論データにおける行内の読み順が正解データと完全に一致している場合でもその行の評価時のログを出力する
- eval_main_text_only：本文のLINEのみを評価の対象とする
- eval_annotation_line_order：頭注、割注のLINEを読み順評価の対象に含める
- ignore_inline_type_to_skip：正解データが〓のみのINLINEだった場合、INLINEの種類に関係なく読み順の評価対象から外す
- eval_all_valid_pred_line：正解データ側の行が読み順評価の対象外の場合でも、対応する推論データの行を読み順評価の対象から外さないようにする
