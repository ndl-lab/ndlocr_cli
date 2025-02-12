FROM nvcr.io/nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

ENV PROJECT_DIR=/root/ocr_cli
ENV FORCE_CUDA="1"
ENV TORCH_CUDA_ARCH_LIST="7.5+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"

RUN set -x \
    && apt update \
    && apt upgrade -y

RUN set -x \
    && apt update \
    && apt -y install locales \
    && locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
RUN localedef -f UTF-8 -i ja_JP ja_JP.utf8

RUN set -x \
    && apt -y install python3.8 python3.8-dev \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && apt -y install wget python3-distutils \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN set -x && apt -y install libglib2.0-0
RUN set -x && apt -y install libgl1-mesa-dev
RUN set -x && apt -y install vim git

RUN set -x && pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 torchaudio==2.0.1 --index-url https://download.pytorch.org/whl/cu118

RUN set -x \
    && pip install yaspin tqdm SudachiPy==0.6.9 \
    && pip install setuptools==59.5.0 \
    && pip install transformers['ja']

RUN set -x \
    && wget http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz \
    && tar xzvf kytea-0.4.7.tar.gz \
    && cd kytea-0.4.7 \
    && ./configure \
    && make \
    && make install \
    && ldconfig

COPY cli ${PROJECT_DIR}/cli
COPY main.py ${PROJECT_DIR}
COPY README.md ${PROJECT_DIR}
COPY requirements.txt ${PROJECT_DIR}
COPY config.yml ${PROJECT_DIR}
COPY eval_config.yml ${PROJECT_DIR}
RUN set -x \
    && pip install -r ${PROJECT_DIR}/requirements.txt

COPY submodules/deskew_HT ${PROJECT_DIR}/submodules/deskew_HT
COPY submodules/ndl_layout ${PROJECT_DIR}/submodules/ndl_layout
COPY submodules/ocr_line_eval_script ${PROJECT_DIR}/submodules/ocr_line_eval_script
COPY submodules/reading_order ${PROJECT_DIR}/submodules/reading_order
COPY submodules/ruby_prediction ${PROJECT_DIR}/submodules/ruby_prediction
COPY submodules/separate_pages_mmdet ${PROJECT_DIR}/submodules/separate_pages_mmdet
COPY submodules/text_recognition_lightning ${PROJECT_DIR}/submodules/text_recognition_lightning

RUN set -x \
    && pip install -r ${PROJECT_DIR}/submodules/ruby_prediction/requirements.txt


RUN set -x \
    && cd ${PROJECT_DIR}/submodules/ndl_layout \
    && git clone https://github.com/open-mmlab/mmdetection.git -b v3.0.0 \
    && cd ${PROJECT_DIR}/submodules/ndl_layout/mmdetection \
    && sed -i -e 's/GPU_MEM_LIMIT = 1024\*\*3/GPU_MEM_LIMIT = 1024\*\*3\/\/5/' mmdet/models/roi_heads/mask_heads/fcn_mask_head.py \
    && python setup.py bdist_wheel \
    && pip install dist/*.whl


RUN set -x && pip install mmcv==2.0.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html

WORKDIR ${PROJECT_DIR}
