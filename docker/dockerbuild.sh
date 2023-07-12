TAG=ocr-v2-cli-py38
DOCKERIGNORE=docker/dockerignore
DOCKERFILE=docker/Dockerfile
wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/resnet-orient2.ckpt -P ./submodules/text_recognition_lightning/models
wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_author/model.pkl -P ./submodules/text_recognition_lightning/models/rf_author/
wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_title/model.pkl -P ./submodules/text_recognition_lightning/models/rf_title/
wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/ndl_layout/ndl_retrainmodel.pth -P ./submodules/ndl_layout/models
wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/separate_pages_mmdet/epoch_180.pth -P ./submodules/separate_pages_mmdet/models
cp ${DOCKERIGNORE} .dockerignore
docker build -t ${TAG} -f ${DOCKERFILE} .
rm .dockerignore
