# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Apache License, Version 2.0. See LICENSE file for details.

import pandas as pd
import yfinance as  yfi
import random
from datasets import load_dataset, Dataset, concatenate_datasets
from .utils import logger

# Try to import pandas_ta, but provide fallback
try:
    import pandas_ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False
    

def calculate_rsi(series, period=14):
    """Calculate RSI indicator without pandas_ta"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


class DataFetcher:
    def __init__(self, dataset="financial_phrasebank", split="sentences_allagree", synthetic_count=200):
        self.dataset = dataset
        self.split = split
        self.synthetic_count = synthetic_count
        self.final_dataset = None
        self._cached_time_series = None  # Cache for time series data

    def fetch_base_dataset(self):
        """Load base dataset."""
        try:
            dataset = load_dataset(self.dataset, self.split)
            logger.info("Base dataset loaded.")
            return dataset
        except Exception as e:
            logger.error(f"Dataset load failed: {e}")
            raise

    def get_time_series(self, ticker="AAPL", use_cache=True):
        """Fetch time-series data with indicators."""
        try:
            # Use cached data if available (for training data preparation)
            if use_cache and self._cached_time_series is not None:
                return self._cached_time_series
            
            data = yfi.download(ticker, period="1y", progress=False)
            if HAS_PANDAS_TA:
                data['RSI'] = pandas_ta.rsi(data['Close'])
            else:
                data['RSI'] = calculate_rsi(data['Close'])
            
            result = data.tail(50).to_csv(index=True)
            
            # Cache the result if caching is enabled
            if use_cache:
                self._cached_time_series = result
            
            return result
        except Exception as e:
            logger.error(f"Time-series fetch failed for {ticker}: {e}")
            return "Error fetching data"

    def generate_synthetic_strategy(self, risk_level):
        """Generate synthetic strategy code."""
        try:
            if risk_level == "low":
                code = "def low_risk_strategy(df):\n    return df['Close'] > df['Close'].rolling(20).mean()"
                explanation = "Low-risk mean-reversion with low drawdown."
            elif risk_level == "medium":
                code = "def medium_strategy(df):\n    if df['RSI'] < 30:\n        return 'Buy'"
                explanation = "Medium-risk momentum with balanced returns."
            else:
                code = "def high_strategy(df):\n    vol = df['Close'].pct_change().std()\n    if vol > 0.02:\n        return 'Sell'"
                explanation = "High-risk HFT for volatile markets."
            return {"code": code, "explanation": explanation, "risk": risk_level}
        except Exception as e:
            logger.error(f"Synthetic strategy generation failed: {e}")
            raise

    def format_example(self, example, add_strategy=False):
        """Format prompt for training."""
        try:
            label_map = {0: "low", 1: "medium", 2: "high"}
            risk = label_map[example["label"]]
            time_series = self.get_time_series()
            
            # Get sentence or create synthetic one
            sentence = example.get("sentence", "Market analysis shows positive momentum.")
            
            text = f"Analyze quant data for strategy: Statement: {sentence}\nTime-Series: {time_series}\nRisk Level: {risk}\nGenerate Strategy Code: "
            if add_strategy:
                strat = self.generate_synthetic_strategy(risk)
                text += f"\n{strat['code']}\nBacktest Results: Simulated Sharpe 1.2\nOptimization Explanation: {strat['explanation']}"
            # Return only text, remove label to avoid schema conflicts
            return {"text": text}
        except Exception as e:
            logger.error(f"Example formatting failed: {e}")
            raise

    def prepare_data(self):
        """Prepare and save dataset."""
        try:
            dataset = self.fetch_base_dataset()
            formatted_dataset = dataset.map(self.format_example)
            synthetic = [self.format_example({"label": random.choice([0,1,2])}, add_strategy=True) for _ in range(self.synthetic_count)]
            synthetic_ds = Dataset.from_list(synthetic)
            self.final_dataset = concatenate_datasets([formatted_dataset["train"], synthetic_ds])
            self.final_dataset.save_to_disk("./formatted_data")
            logger.info("Data prepared!")
            return self.final_dataset
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise



