FROM nvcr.io/nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

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
RUN set -x && pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html
RUN set -x && cd ${PROJECT_DIR}/src/ndl_layout/mmdetection && python setup.py bdist_wheel && pip install dist/*.whl
ENV PYTHONPATH $PYTHONPATH:${PROJECT_DIR}/src/text_recognition/deep-text-recognition-benchmark
RUN set -x && pip install mmcv-full==1.4.0 -f https://download.openmmlab.com/mmcv/dist/cu111/torch1.8.0/index.html

WORKDIR ${PROJECT_DIR}
