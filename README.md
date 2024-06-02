# ndlocr_cli(NDLOCR(ver.2.1)アプリケーションのリポジトリ)

NDLOCR(ver.2)を利用してテキスト化を実行するためのアプリケーションを提供するリポジトリです。 

本プログラムは、令和4年度NDLOCR追加開発事業の成果物である[ver.2.0](https://github.com/ndl-lab/ndlocr_cli/tree/ver.2.0)に対して、国立国会図書館が改善作業を行ったプログラムです。

事業の詳細については、[令和4年度NDLOCR追加開発事業及び同事業成果に対する改善作業](https://lab.ndl.go.jp/data_set/r4ocr/r4_software/)をご覧ください。

本プログラムは、国立国会図書館がCC BY 4.0ライセンスで公開するものです。詳細については LICENSEをご覧ください。

**2023年6月まで公開していたバージョンを継続して利用したい場合には、[ver.1](https://github.com/ndl-lab/ndlocr_cli/tree/ver.1)をご利用ください。**
```
git clone --recursive https://github.com/ndl-lab/ndlocr_cli -b ver.1
```
のようにソースコード取得部分を書き換えることで継続してお使いいただけます。


## 環境構築

### 1. リポジトリのクローン
本リポジトリはNDLOCRの処理を統合する機能のみを有しています。

OCRを実現するための各機能はhttps://github.com/ndl-lab
に存在する複数のリポジトリに切り分けられており、

本リポジトリとの間をsubmoduleで紐づけています。

リポジトリをclone する際は、次のコマンドを実行すると、関連リポジトリを一度に取得することができます。
```
git clone --recursive https://github.com/ndl-lab/ndlocr_cli
```
### 2. ホストマシンのNVIDIA Driverのアップデート
コンテナ内でCUDA 11.1を利用します。

ホストマシンのNVIDIA Driverが

Linuxの場合: 450.36.06以上 

Windowsの場合:520.06以上

のバージョンを満たさない場合は、ご利用のGPUに対応するドライバの更新を行ってください。

（参考情報）

以下のホストマシン環境（AWS g5.xlargeインスタンス）上で動作確認を行っています。

OS: Ubuntu 18.04.6 LTS

GPU: NVIDIA A10G

NVIDIA Driver: 470.182.03



### 3. dockerのインストール
https://docs.docker.com/engine/install/
に従って、OS及びディストリビューションにあった方法でdockerをインストールしてください。

### 4. dockerコンテナのビルド
Linux:
```
cd ndlocr_cli
sh ./docker/dockerbuild.sh
```

Windows:
```
cd ndlocr_cli
docker\dockerbuild.bat
```

### 5. 処理したい画像の入ったディレクトリのマウント方法

[./docker/run_docker.sh](./docker/run_docker.sh)を書き換えて、-vを追加してホストマシンのディレクトリを指定することでホストマシンのディレクトリをマウントすることができます。
（※-vオプションは-iオプションよりも手前で指定してください。）

Linux:

例：/home/user/tmpdirの直下に画像ファイルがある場合
```
docker run --gpus all -d --rm --name ocr_cli_runner -v /home/user/tmpdir:/root/tmpdir/img -i ocr-v2-cli-py38:latest
```


### 6. dockerコンテナの起動
Linux:
```
cd ndlocr_cli
sh ./docker/run_docker.sh
```

Windows:
```
cd ndlocr_cli
docker\run_docker.bat
```


## 環境構築後のディレクトリ構成（参考）
```
ndlocr_cli
├── main.py : CLIコマンドを実行するためのPythonスクリプト
├── cli : CLIコマンドの利用するPythonコード
├── submodules : 各推論・評価処理のソースコード用ディレクトリ(※Dockerビルド前に作成するディレクトリ)
│   ├── separate_pages_mmdet : ノド元分割のソースコード
│   ├── deskew_HT : 傾き補正のソースコード
│   ├── ndl_layout : レイアウト抽出処理のソースコード
│   ├── text_recognition_lightning : 文字認識・見出し著者認識処理のソースコード
│   ├── reading_order : 読み順認識処理のソースコード
│   ├── ruby_prediction : ルビ推定処理のソースコード
│   └── ocr_line_eval_script : 推論結果の評価処理のソースコード
├── config.yml : サンプルの推論設定ファイル
├── eval_config.yml : サンプルの評価設定ファイル
├── docker : Dockerによる環境作成のスクリプト類
├── README.md : このファイル
├── requirements.txt : Python の必要パッケージリスト
├── LICENSE : 本リポジトリのライセンスファイル
└── LICENSE_DEPENDENCIES : 本リポジトリのプログラムが利用するパッケージのライセンスファイル
```

## チュートリアル
### Dockerの生成と実行  
起動後は以下のような`docker exec`コマンドを利用してコンテナにログインできます。

```
docker exec -it ocr_cli_runner bash
```

### 推論処理の実行

single形式(inputディレクトリ直下にimgディレクトリが存在する)のinputディレクトリ構成であれば、以下のコマンドで実行することができます。
```
python main.py infer input_data_dir output_dir -s s
```


## 各種実行時オプションについて
### 推論処理の実行時オプション
#### `-d`/`--dump`オプション
各サブ機能中間出力を全てdumpする場合は`-d`オプションを追加してください。
中間出力結果のファイルは出力ディレクトリ配下の`dump`ディレクトリに保存されます。
- `-d`オプション有効時の出力例

```
output_dir/
├── PID
│   ├── dump
│   │   ├── 0_page_sep
│   │   │   └── pred_img
│   │   ├── 1_page_deskew
│   │   │   ├── pred_img
│   │   │   └── xml
│   │   ├── 2_layer_ext
│   │   │   ├── pred_img
│   │   │   └── xml
│   │   ├── 3_line_ocr
│   │   │   ├── pred_img
│   │   │   └── xml
│   │   ├── ex1_line_order
│   │   │   ├── pred_img
│   │   │   └── xml
│   │   ├── ex2_ruby_read
│   │   │   ├── pred_img
│   │   │   └── xml
│   │   └── ex3_line_attribute
│   │       ├── pred_img
│   │       ├── txt
│   │       └── xml
│   └── txt
└── opt.json
```

#### `-p, --proc_range`オプション
入力形式によらず、推論処理の部分実行を行うときは`-p`オプションを利用します。
例えば[ノド元分割]〜[レイアウト抽出]を実行する場合は以下のようなコマンドとなります。
```
python main.py infer input_data_dir output_dir -p 0..2
```

`-p`オプションに与えるサブ機能番号に対応する各機能は以下のとおりです。

- 0: ノド元分割
- 1: 傾き補正
- 2: レイアウト抽出
- 3: 文字認識(OCR)

以下の機能はコマンド引数ではなく設定ファイルの`config.yml`で実行するかどうかを設定します。

- ex1: 読み順認識(設定ファイルの変数名：line_order)
- ex2: 漢字ルビ推定(設定ファイルの変数名：ruby_read)
- ex3: 見出し・著者認識(設定ファイルの変数名：add_title_author)

#### `-s, --input_structure`オプション
入力形式を指定するためのオプションです。
入力形式のパターンについては後述の入出力形式（推論処理）をご覧ください。

#### `-i, --save_image`オプション
推論処理の際にテキストデータだけでなく、画像データも出力するようにするためのオプションです。
本オプションが有効な場合、出力ディレクトリ内の`pred_img`ディレクトリに最後のサブ機能による処理が
実行された後の画像ファイルが出力されます。  
例えば、`-p`オプションによって[ノド元分割]〜[傾き補正]の部分実行が行われた場合、
傾き補正が行われた後の画像がファイルとして保存されます。

#### `-x, --save_xml`オプション
推論処理の際にテキストデータだけでなく、XMLデータも出力するようにするためのオプションです。
本オプションが有効な場合、出力ディレクトリ内の`xml`ディレクトリに最後のサブ機能による処理が
実行された後のXMLファイルが出力されます。
例えば全てのサブ機能による処理が実行された場合、
本オプションが有効であればテキストファイルだけでなくXMLファイルも出力ディレクトリ内に保存されます。  
ただし、推論処理がXMLデータの出力が無い範囲の部分実行である場合にはXMLファイルは出力されません。  

#### `-r, --ruby_only`オプション
ルビ推定機能のみを利用する場合に利用するためのオプションです。
本オプションが有効な場合、推論処理はルビ推定機能のみを実行し、他のサブ機能の全てをスキップします。
ただし、入力ディレクトリ内にルビ推定機能の入力となるXMLデータが存在しない場合は動作しません。

#### `-c, --config_file`オプション
推論処理の設定ファイルのパスを指定するためのオプションです。

## 入出力仕様(推論処理)
### 入力ディレクトリについて
入力ディレクトリの形式は以下の4パターンを想定しており、
それぞれ`-s`オプションで指定することができます。
(デフォルトはSigle input dir modeです)

- Sigle input dir mode(`-s s`)
```
input_root
 ├── xml
 │   └── R[7桁連番].xml※XMLデータ
 └── img
     └── R[7桁連番]_pp.jp2※画像データ
```

- Partial inference mode(`-s i`)
(過去に実行した部分実行の結果を入力とする場合はこちら)
```
input_root
 └── PID
     ├── xml
     │   └── R[7桁連番].xml※XMLデータ
     └── img
         └── R[7桁連番]_pp.jp2※画像データ
```

- Image file mode(`-s f`)
(単体の画像ファイルを入力として与える場合はこちら)
```
input_root(※画像データファイル)
```

### 出力ディレクトリ例
```
output_dir
├── PID
│   ├── dump
│   │   ├── 0_page_sep
│   │   ├── 1_page_deskew
│   │   ├── 2_layer_ext
│   │   ├── 3_line_ocr
│   │   ├── ex1_line_order
│   │   ├── ex2_ruby_read
│   │   └── ex3_line_attribute
│   ├── img
│   ├── pred_img
│   ├── txt
│   └── xml
└── opt.json
```

#### オプション情報の保存
出力ディレクトリには、パース済みの実行オプションが`opt.json`に保存されています。

#### 推論結果(画像、XML)の保存
推論結果の画像やXMLファイルを保存するように`-s`, `-x`オプションが有効な状態で実行した場合、
それぞれ`pred_img`, `xml`ディレクトリに保存されます。

#### 部分実行時の仕様
`-p`オプションを指定していた場合、`-i`, `-x`オプションの有無と関係なく`pred_img`, `xml`ディレクトリのデータは保存され、
更に最後の推論プロセスで入力として使用した画像が`img`ディレクトリに保存されます。
つまり、推論結果を重畳した画像が`pred_img`, 前処理のみ行われた画像が`img`ディレクトリに保存されます。
前処理のみ行われた画像を保存するのは、この出力ディレクトリを別の部分実行の入力ディレクトリとして利用できるようにするためです。

### 推論処理のデータフロー
```mermaid
graph TD
  subgraph メインフロー
    st0[(入力画像ファイル)];
    e0[(出力本文+キャプションテキストファイル)];
    e2[(出力ルビテキストファイル)];
    e3[(出力テキストXMLファイル)];
    A[ノド元分割];
    B[傾き補正];
    C[レイアウト抽出];
    D["文字認識(OCR)"];
    E["読み順認識"];
    F["ルビ推定"];
    G["見出し著者認識"];
    st0 --入力画像--> A;
    A --ノド元分割画像--> B;
    B --傾き補正画像--> C & D;
    C --前処理済み画像+レイアウト情報--> D;
    D --"推論テキスト(XML)"--> E;
    E --"読み順訂正済み推論テキスト(XML)"--> F;
    E --"読み順訂正済み推論テキスト(XML)"--> G;
    E --"読み順訂正済み推論テキスト(txt)"--> e0;
    F --"推定ルビテキスト(txt)"--> e2;
    G --"推定ルビテキスト(txt)"--> e3;
  end
  subgraph 部分実行フロー
    st1[(中間入力データファイル)]
    e1[(中間結果出力ファイル)];
    A --ノド元分割画像--> e1;
    B --傾き補正画像--> e1;
    C --レイアウト情報--> e1;
    D --"推論テキスト(XML)"--> e1;
    E --"読み順訂正済み推論テキスト(XML)"--> e1;
    F --"推定ルビテキスト(txt)"--> e1;
    st1 --"ノド元分割画像"--> B;
    st1 --"傾き補正画像"--> C;
    st1 --"前処理済み画像+レイアウト情報"--> D;
    st1 --"推論テキスト(XML)"--> E;
    st1 --"推論テキスト(XML)"--> F;
  end
```


## GPUメモリに関する設定
本モジュールは`mmdetection`を利用しており、実行環境に応じて`mmdetection`のGPUメモリ使用量に関する設定の調整が必要になることがあります。  
具体的には推論実行時にGPUのメモリ不足エラーが発生した場合、またはGPUメモリが十分に活用されていない場合に
コンテナ内で以下のファイルで定義されている`GPU_MEM_LIMIT`という定数を変更することで状況が改善する場合があります。

`/usr/local/lib/python3.8/dist-packages/mmdet/models/roi_heads/mask_heads/fcn_mask_head.py`

例えば`RuntimeError: CUDA out of memory.`というエラーが発生した場合、
`GPU_MEM_LIMIT`の行を次のように編集してGPUメモリの使用量を半減させることで
エラーの発生が抑えられることがあります

[編集前]
```
GPU_MEM_LIMIT = 1024**3 # 1 GB memory limit
```

[編集後]
```
GPU_MEM_LIMIT = (1024**3) // 2 # 500 MB memory limit
```
