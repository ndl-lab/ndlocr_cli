FROM nvcr.io/nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

ENV PROJECT_DIR=/root/ocr_cli
ENV FORCE_CUDA="1"
ENV TORCH_CUDA_ARCH_LIST="7.5+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV DEBIAN_FRONTEND=noninteractive

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

RUN set -x && apt -y install libgl1-mesa-dev libglib2.0-0 git
RUN set -x \
    && apt -y install python3.8 python3.8-dev \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && apt -y install wget python3-distutils && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py

COPY . ${PROJECT_DIR}

RUN set -x \
    && pip install -r ${PROJECT_DIR}/requirements.txt
RUN set -x && pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 torchaudio==2.0.1 --index-url https://download.pytorch.org/whl/cu118

RUN set -x \
    && cd ${PROJECT_DIR}/src/ndl_layout \
    && git clone https://github.com/open-mmlab/mmdetection.git -b v3.0.0 \
    && cd ${PROJECT_DIR}/src/ndl_layout/mmdetection \
    && python setup.py bdist_wheel \
    && pip install dist/*.whl
ENV PYTHONPATH $PYTHONPATH:${PROJECT_DIR}/src/text_recognition/deep-text-recognition-benchmark

RUN set -x && pip install mmcv==2.0.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html

WORKDIR ${PROJECT_DIR}
