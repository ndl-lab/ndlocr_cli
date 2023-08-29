SET TAG=ocr-v2-cli-py38
SET DOCKERIGNORE=docker\dockerignore
SET DOCKERFILE=docker\Dockerfile

set DIRNAME=submodules\text_recognition_lightning\models\models\
set FILENAME=resnet-orient2.ckpt
set URL="https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/resnet-orient2.ckpt"
set FULLPATH=%DIRNAME%%FILENAME%
if not exist %DIRNAME%%FILENAME% (
mkdir %DIRNAME%
curl -o %FULLPATH% %URL%
)

set DIRNAME=submodules\text_recognition_lightning\models\models\rf_author\
set FILENAME=model.pkl
set URL="https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_author/model.pkl"
set FULLPATH=%DIRNAME%%FILENAME%
if not exist %DIRNAME%%FILENAME% (
mkdir %DIRNAME%
curl -o %FULLPATH% %URL%
)

set DIRNAME=submodules\text_recognition_lightning\models\models\rf_title\
set FILENAME=model.pkl
set URL="https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_title/model.pkl"
set FULLPATH=%DIRNAME%%FILENAME%
if not exist %DIRNAME%%FILENAME% (
mkdir %DIRNAME%
curl -o %FULLPATH% %URL%
)

set DIRNAME=submodules\ndl_layout\models\
set FILENAME=ndl_retrainmodel.pth
set URL="https://lab.ndl.go.jp/dataset/ndlocr_v2/ndl_layout/ndl_retrainmodel.pth"
set FULLPATH=%DIRNAME%%FILENAME%
if not exist %DIRNAME%%FILENAME% (
mkdir %DIRNAME%
curl -o %FULLPATH% %URL%
)

set DIRNAME=submodules\separate_pages_mmdet\models\
set FILENAME=epoch_180.pth
set URL="https://lab.ndl.go.jp/dataset/ndlocr_v2/separate_pages_mmdet/epoch_180.pth"
set FULLPATH=%DIRNAME%%FILENAME%
if not exist %DIRNAME%%FILENAME% (
mkdir %DIRNAME%
curl -o %FULLPATH% %URL%
)

copy %DOCKERIGNORE% .dockerignore
docker build -t %TAG% -f %DOCKERFILE% .
del .dockerignore
