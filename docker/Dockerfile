FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

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

RUN set -x && apt -y install libgl1-mesa-dev libglib2.0-0 zip git python3-pip wget

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN set -x && pip3 install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1 torchtext==0.16.1 --index-url https://download.pytorch.org/whl/cu121


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
    && pip3 install mmdet==3.3.0\
    && pip3 install -r ${PROJECT_DIR}/submodules/ruby_prediction/requirements.txt

RUN set -x && pip3 install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.1/index.html

WORKDIR ${PROJECT_DIR}
