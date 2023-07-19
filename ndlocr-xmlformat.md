# NDLOCR ver.2が出力するXMLの形式について

処理完了後、出力されるXMLは入力ページ毎に<PAGE>要素を持ち、この階層の下に、TEXTBLOCK要素、LINE要素及びBLOCK要素を持つ。

PAGE要素は「当該画像の高さ(HEIGHT)」及び「当該画像の幅(WIDTH)」を属性に持つ。

TEXTBLOCK要素は記事のようにひとまとまりになった本文領域を指し、「予測の確信度(CONF)」を属性に持ち、この階層の下にLINE要素及びBLOCK要素を持つ。
TEXTBLOCK要素の階層の下にはSHAPE要素があり、SHAPE要素の階層の下にPOLYGONとしてTEXTBLOCK要素を囲むポリゴン座標を持つ。


LINE要素及びBLOCK要素は、「当該領域の高さ(HEIGHT)」「当該領域の幅(WIDTH)」「当該領域の左上x座標(X)」「当該領域の左上y座標(Y)」「予測の確信度(CONF)」「レイアウト種別(TYPE)」を共通して属性に持つ。

LINE要素は上記に追加して、「読み順序の通し番号（ORDER）」「見出し要素かどうか(TITLE)」「著者要素かどうか（AUTHOR）」を属性に持つ。

LINE要素及びBLOCK要素は必ずしもTEXTBLOCK要素の階層の下にある必要はなく、PAGE要素の直下に含まれる場合もある。

BLOCK要素のうち「広告」については、この階層の下にTEXTBLOCK要素、LINE要素及びBLOCK要素を持つことがある。

領域の内部にOCRが読み取った文字列がある場合には、STRINGを属性に持ち、STRINGの属性値として出力する。

次に示すとおり、TYPEの属性値によってレイアウトの種類を表している。

* LINE要素

|TYPE|説明|
|----|----|
|本文|当該領域が本文であることを表す|
|広告文字|当該領域が広告中の文字であることを表す|
|割注|当該領域が割注（本文内で行を割って記述される注）であることを表す|
|頭注|当該領域が頭注（ページ上部に記述される注）であることを表す|
|キャプション|当該領域が図表の説明文であることを表す|

* BLOCK要素
  

|TYPE|説明|
|----|----|
|図版|当該領域が図版(広告も含む)であることを表す|
|表組|当該領域が表であることを表す|
|広告|当該領域が広告であることを表す|
|柱|当該領域が柱であることを表す|
|ノンブル|当該領域がページ番号等であることを表す|
|ルビ|当該領域がフリガナであることを表す|
|組織図|当該領域が組織図や家系図であることを表す|
|数式|当該領域が数式であることを表す|
|化学式|当該領域が化学式であることを表す|
|欧文|当該領域が複数行にわたる欧文であることを表す|


* 出力XMLのイメージ
```
<?xml version='1.0' encoding='utf-8'?>
<OCRDATASET>
    <PAGE HEIGHT="5173"  WIDTH="3705" IMAGENAME="sampleimg-01.jpg">
        <TEXTBLOCK CONF="0.850">
            <LINE TYPE="本文" X="2067" Y="3266" WIDTH="45" HEIGHT="616" CONF="1.000" STRING="いろはに" ORDER="0" TITLE="FALSE" AUTHOR="FALSE" />
            <LINE TYPE="本文" X="1985" Y="3260" WIDTH="40" HEIGHT="159" CONF="0.998" STRING="ほへと" ORDER="1" TITLE="FALSE" AUTHOR="FALSE" />
            <SHAPE><POLYGON POINTS="2001,3273,1996,3287,1998,3418,2005,3444,2032,3466,2036,3480,2049,3736,2064,3759,2076,3802,2083,3869,2095,3878,2838,3878,2853,3870,2875,3827,2884,3790,2890,3582,2909,3565,2932,3578,2943,3635,2972,3690,2983,3874,2999,3881,3225,3880,3243,3870,3245,3264,3232,3256,2954,3254,2902,3276,2874,3298,2836,3301,2805,3296,2743,3258,2716,3254,2073,3255,2016,3259" /></SHAPE>
        </TEXTBLOCK>
  　    <BLOCK TYPE="広告" X="927" Y="3287" WIDTH="1057" HEIGHT="614" CONF="0.989">
    　　    <LINE TYPE="広告文字" X="1032" Y="3575" WIDTH="839" HEIGHT="39" CONF="0.946" STRING="広告の中の" ORDER="2" TITLE="FALSE" AUTHOR="FALSE" />
    　　    <LINE TYPE="広告文字" X="1270" Y="3839" WIDTH="442" HEIGHT="27" CONF="0.568" STRING="文字である" ORDER="3" TITLE="FALSE" AUTHOR="FALSE" />
        </BLOCK>
        <BLOCK TYPE="図版" X="994" Y="1147" WIDTH="591" HEIGHT="563" CONF="0.998" />
        <BLOCK TYPE="柱" X="2669" Y="292" WIDTH="550" HEIGHT="45" CONF="0.933" STRING="柱の中身" />
        <BLOCK TYPE="ノンブル" X="981" Y="296" WIDTH="76" HEIGHT="51" CONF="0.999" STRING="29" />
    </PAGE>
    <PAGE HEIGHT="5173" WIDTH="3705" IMAGENAME="sampleimg-02.jpg">
  　　　<TEXTBLOCK CONF="0.850">
    　　　　<LINE TYPE="本文" X="661" Y="2231" WIDTH="1197" HEIGHT="41" CONF="0.938" STRING="これは" ORDER="0" TITLE="FALSE" AUTHOR="FALSE" />
  　　　　　<LINE TYPE="本文" X="619" Y="2310" WIDTH="1222" HEIGHT="39" CONF="0.958" STRING="本文です。" ORDER="1" TITLE="FALSE" AUTHOR="FALSE" />
    　　　　<SHAPE><POLYGON POINTS="629,2308,629,2343,641,2348,1832,2349,1847,2344,1847,2236,1828,2231,693,2230,671,2235,670,2271,659,2279,635,2286" /></SHAPE>
    　　</TEXTBLOCK>
  　　　<BLOCK TYPE="図版" X="696" Y="472" WIDTH="1055" HEIGHT="536" CONF="0.994" />
  　　　<BLOCK TYPE="ノンブル" X="1181" Y="2399" WIDTH="119" HEIGHT="23" CONF="0.998" STRING="-2-" />
    </PAGE>
    ...(ページ数分続く)
</OCRDATASET>
```
