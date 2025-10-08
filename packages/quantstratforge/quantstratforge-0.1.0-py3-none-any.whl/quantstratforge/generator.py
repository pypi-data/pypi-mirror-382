# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Proprietary License. See LICENSE file for details.

from transformers import pipeline
import torch
from .utils import logger, add_watermark

class StrategyGenerator:
    def __init__(self, model_path="./quant-strat-forge"):
        try:
            self.generator = pipeline("text-generation", model=model_path, device=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            logger.error(f"Generator initialization failure: {e}")
            raise

    def generate(self, input_data: str):
        try:
            prompt = f"Generate quant strategy from data: {input_data}\nRisk Level: \nStrategy Code: \nBacktest Results: \nOptimization Explanation: "
            output = self.generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]["generated_text"]
            try:
                parts = output.split("Optimization Explanation:")
                strategy = parts[0].split("Strategy Code:")[-1].strip()
                explanation = parts[1].strip()
            except:
                strategy = "Default strategy"
                explanation = output.split(prompt)[-1].strip()
            logger.info("Strategy generated")
            return {"strategy_code": strategy, "explanation": add_watermark(explanation)}
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise