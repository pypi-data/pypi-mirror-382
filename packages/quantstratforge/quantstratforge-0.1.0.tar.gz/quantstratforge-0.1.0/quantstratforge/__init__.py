# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Proprietary License. See LICENSE file for details.

from .data_prep import DataFetcher
from .model import StrategyModel
from .generator import StrategyGenerator
from .backtester import Backtester
from .optimizer import Optimizer
from .utils import add_watermark, logger

__version__ = "0.1.0"
__author__ = "Venkata Vikhyat Choppa"
__license__ = "Proprietary"