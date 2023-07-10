# NDLOCRアプリケーション(NDLOCR ver.1)
NDLOCRを利用してテキスト化を実行するためのアプリケーションを提供するリポジトリです。 

本プログラムは、令和3年度に国立国会図書館が株式会社モルフォAIソリューションズに委託して作成したものです。

本プログラムは、国立国会図書館がCC BY 4.0ライセンスで公開するものです。詳細については
[LICENSE](./LICENSE
)をご覧ください。

**令和4年度NDLOCR追加開発事業の成果物である[ver.2.0](https://github.com/ndl-lab/ndlocr_cli_r4/tree/ver.2.0)**

及び

**ver.2.0をもとに国立国会図書館が更に改善を行ったプログラム[ver.2.1](https://github.com/ndl-lab/ndlocr_cli_r4/tree/ver.2.1)があります**

 
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

Linuxの場合: 455.23以上 

Windowsの場合:456.38以上

のバージョンを満たさない場合は、ご利用のGPUに対応するドライバの更新を行ってください。

（参考情報）

以下の環境で動作確認を行っています。

OS: Ubuntu 18.04.5 LTS

GPU: GeForce RTX 2080Ti

NVIDIA Driver: 455.23.05


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
docker run --gpus all -d --rm --name ocr_cli_runner -v /home/user/tmpdir:/root/tmpdir/img -i ocr-cli-py37:latest
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

### 環境構築後のディレクトリ構成（参考）
```
ndlocr_cli
├── main.py : メインとなるPythonスクリプト
├── cli : CLIコマンド的に利用するPythonスクリプトの格納されたディレクトリ
├── src : 各推論処理のソースコード用ディレクトリ
│   ├── separate_pages_ssd : ノド元分割のソースコードの格納されたディレクトリ
│   ├── deskew_HT : 傾き補正のソースコードの格納されたディレクトリ
│   ├── ndl_layout : レイアウト抽出処理のソースコードの格納されたディレクトリ
│   └── text_recognition : 文字認識処理のソースコードの格納されたディレクトリ
├── config.yml : サンプルの推論設定ファイル
├── docker : Dockerによる環境作成のスクリプトの格納されたディレクトリ
├── README.md : このファイル
└── requirements.txt : 必要なPythonパッケージリスト
```


## チュートリアル
起動後は以下のような`docker exec`コマンドを利用してコンテナにログインできます。

```
docker exec -i -t --user root ocr_cli_runner bash
```

### 推論処理の実行
single形式(inputディレクトリ直下にimgディレクトリが存在する)のinputディレクトリ構成であれば、以下のコマンドで実行することができます。
```
python main.py infer input_root output_dir
```
各部分の推論結果による中間出力を全てdumpする場合は`-d`オプションを追加してください。
中間出力結果のファイルは出力ディレクトリ配下の`dump`ディレクトリに保存されます。
(行認識のdumpでは認識された文字列の重畳は行われず、レイアウト認識と同じものが出力されます)
- `-d`オプション実行後の出力例
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
│   │   └── 3_line_ocr
│   │       ├── pred_img
│   │       ├── txt
│   │       └── xml
│   ├── pred_img
│   ├── txt
│   └── xml
└── opt.json
```

入力形式によらず、推論処理の部分実行を行うときは`-p`オプションを利用します。
例えば[ノド元分割]から[レイアウト抽出]までを実行する場合は次のコマンドとなります。
```
python main.py infer input_root output_dir -p 0..2 -s s
```

**既にページ単位の画像になっている等、ノド元分割が不要の場合は[傾き補正]から[文字認識(OCR)]までを実行すればよく、次のコマンドとなります。**
```
python main.py infer input_root output_dir -p 1..3 -s s
```

`-p`の番号と処理の内容の対応関係は次の通りです。
* '-p 0': ノド元分割
* '-p 1': 傾き補正
* '-p 2': レイアウト抽出
* '-p 3': 文字認識(OCR)


重みファイルのパス等、各モジュールで利用する設定値は`config.yml`の内容を修正することで変更することができます。


## 【Google Colaboratoryを利用する場合の参考事例】
国立国会図書館非常勤調査員・東京大学史料編纂所の中村覚助教がGoogle Colaboratory上での実行例をまとめたブログ記事とノートブックを公開しています。

https://zenn.dev/nakamura196/articles/b6712981af3384


## 【Google Cloud Platformを利用する場合の参考事例】
国立国会図書館非常勤調査員・東京大学史料編纂所の中村覚助教がGoogle Cloud Platform上での構築例と実行例をまとめたブログ記事を公開しています。

https://zenn.dev/nakamura196/articles/1313a746826c36




## 入出力仕様
### 入力ディレクトリについて
入力ディレクトリの形式は以下の3パターンを想定しており、
それぞれ`-s`オプションで指定することができます。

- Sigle input dir mode（`-s s`で指定）※デフォルト
```
input_root
 ├── xml
 │   └── R[7桁連番].xml※XMLデータ
 └── img
     └── R[7桁連番]_pp.jpg※画像データ
```

- Image file mode（`-s f`で指定）
(単体の画像ファイルを入力として与える場合はこちら)
```
input_root(※画像データファイル)
```

- intermediate output mode（`-s i`で指定）
(過去に実行した部分実行の結果を入力とする場合はこちら)
```
input_root
 └── PID
     ├── xml
     │   └── R[7桁連番].xml※XMLデータ
     └── img
         └── R[7桁連番]_pp.jpg※画像データ   
```



### 出力ディレクトリについて
```
output_dir/
├── PID
│   ├── dump
│   │   ├── 0_page_sep
│   │   ├── 1_page_deskew
│   │   ├── 2_layer_ext
│   │   └── 3_line_ocr
│   ├── img
│   ├── pred_img
│   ├── txt
│   └── xml
└── opt.json
```

#### オプション情報の保存
出力ディレクトリでは、実行時に指定したオプション情報が`opt.json`に保存されています。

#### 認識結果(画像、XML)の保存
認識結果の画像を保存するには、`-i`オプションを指定します。この場合、出力ディレクトリ以下の`pred_img`に画像が出力されます。
認識結果を構造化したXMLファイルを保存するには, `-x`オプションを指定します。この場合、**実行中の全ての処理が完了した後に**　`xml`ディレクトリに結果が保存されます。

#### 部分実行時の仕様
`-p`オプションを指定していた場合、`-i`, `-x`オプションの有無と関係なく認識結果の画像が`pred_img`ディレクトリに、認識結果を構造化したXMLファイルが`xml`ディレクトリにそれぞれ保存されます。

更に最後の推論プロセスで入力として使用した画像が`img`ディレクトリに保存されます。
つまり、認識結果を重畳した画像が`pred_img`, 前処理のみ行われた画像が`img`ディレクトリに保存されます。

前処理のみ行われた画像を別途保存するのは、この出力ディレクトリを別の部分実行の入力情報として利用できるようにするためです。

### 推論処理のデータフロー
```mermaid
graph TD
  subgraph メインフロー
    st0[(入力画像ファイル)];
    e0[(出力テキストファイル)];
    A[ノド元分割];
    B[傾き補正];
    C[レイアウト抽出];
    D["文字認識(OCR)"];
    st0 --入力画像--> A;
    A --ノド元分割画像--> B & C & D;
    B --傾き補正画像--> C;
    C --前処理済み画像+レイアウト情報--> D;
    D --推論テキスト--> e0;
  end
  subgraph 部分実行フロー
    st1[(中間入力データファイル)]
    e1[(中間結果出力ファイル)];
    A --ノド元分割画像--> e1;
    B --傾き補正画像--> e1;
    C --レイアウト情報--> e1;
    D --推論テキスト--> e1;
    st1 --"ノド元分割画像"--> B;
    st1 --"傾き補正画像"--> C;
    st1 --"前処理済み画像+レイアウト情報"--> D;
  end
```





