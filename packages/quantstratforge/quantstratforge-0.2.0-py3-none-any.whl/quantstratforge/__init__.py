# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Apache License, Version 2.0. See LICENSE file for details.

from .data_prep import DataFetcher
from .model import StrategyModel
from .generator import StrategyGenerator
from .backtester import Backtester
from .optimizer import Optimizer
from .utils import add_watermark, logger

__version__ = "0.2.0"
__author__ = "Venkata Vikhyat Choppa"
__license__ = "Apache-2.0"