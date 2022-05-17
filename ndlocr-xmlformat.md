# NDLOCRが出力するXMLの形式について

処理完了後、出力されるXMLは入力ページ毎に<PAGE>要素を持ち、この階層の下に、LINE要素及びBLOCK要素を持つ。

PAGE要素は「当該画像の高さ(HEIGHT)」及び「当該画像の幅(WIDTH)」のattributeを持つ。


LINE要素及びBLOCK要素は、「当該領域の高さ(HEIGHT)」「当該領域の幅(WIDTH)」「当該領域の左上x座標(X)」「当該領域の左上y座標(Y)」「予測の確信度(CONF)」「レイアウト種別(TYPE)」を属性に持つ。

領域の内部にOCRが読み取った文字列がある場合には、STRINGを属性に持ち、STRINGの属性値として出力する。

次に示すとおり、TYPEの属性値によってレイアウトの種類を表している。

* LINE要素

|TYPE|説明|
|----|----|
|本文|当該領域が本文であることを表す|
|割注|当該領域が割注（本文内で行を割って記述される注）であることを表す|
|頭注|当該領域が頭注（ページ上部に記述される注）であることを表す|
|キャプション|当該領域が図表の説明文であることを表す|

* BLOCK要素
  

|TYPE|説明|
|----|----|
|図版|当該領域が図版(広告も含む)であることを表す|
|表組|当該領域が表であることを表す|
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
        <LINE CONF="0.999" HEIGHT="2103" STRING="あいうえお" TYPE="本文" WIDTH="172" X="2751" Y="1070" />
        <LINE CONF="0.533" HEIGHT="2411" STRING="かきくけこ" TYPE="本文" WIDTH="416" X="844" Y="1987" />
        <LINE CONF="0.316" HEIGHT="245" STRING="さしすせそ" TYPE="本文" WIDTH="3106" X="349" Y="518" />
        <BLOCK CONF="0.702" HEIGHT="245" TYPE="図版" WIDTH="3105" X="346" Y="518" />
        <BLOCK CONF="0.420" HEIGHT="4240" TYPE="図版" WIDTH="3321" X="257" Y="581" />
        <BLOCK CONF="0.348" HEIGHT="28" STRING="2" TYPE="ノンブル" WIDTH="36" X="876" Y="396" />
        <BLOCK CONF="0.722" HEIGHT="176" STRING="柱の中身のテキスト" TYPE="柱" WIDTH="45" X="3516" Y="3316" />
    </PAGE>
    <PAGE HEIGHT="5173" WIDTH="3705" IMAGENAME="sampleimg-02.jpg">
        <LINE CONF="1.000" HEIGHT="3973" STRING="たちつてと" TYPE="本文" WIDTH="179" X="2683" Y="712" />
        <BLOCK CONF="0.993" HEIGHT="30" TYPE="数式" WIDTH="260" X="1167" Y="920" />
        <BLOCK CONF="0.997" HEIGHT="1216" TYPE="ルビ" WIDTH="37" X="1426" Y="681" />
    </PAGE>
    ...(ページ数分続く)
</OCRDATASET>
```
