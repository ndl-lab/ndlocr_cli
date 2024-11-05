# Copyright (c) 2023, National Diet Library, Japan
#
# This software is released under the CC BY 4.0.
# https://creativecommons.org/licenses/by/4.0/


from .inference import OcrInferrer
from .evaluate import OcrResultEvaluator

__all__ = ['OcrInferrer', 'OcrResultEvaluator']
