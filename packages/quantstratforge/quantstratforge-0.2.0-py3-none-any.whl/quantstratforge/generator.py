# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Apache License, Version 2.0. See LICENSE file for details.

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import os
from pathlib import Path
from .utils import logger, add_watermark

class StrategyGenerator:
    def __init__(self, model_path=None):
        """
        Initialize StrategyGenerator with ONLY your custom trained model.
        
        Args:
            model_path: Path to your custom trained model (default: ./quant-strat-forge)
        
        Note: This will ONLY use your custom SLM model, never external LLMs.
        """
        try:
            # Use custom model path - search in multiple locations
            if model_path is None:
                # Try multiple locations to find the model
                possible_paths = [
                    "./quant-strat-forge",  # Current directory
                    "../quant-strat-forge",  # Parent directory (for demos/ folder)
                    os.path.expanduser("~/PycharmProjects/YadVansh/StratForge/quant-strat-forge"),  # Absolute path
                    "/home/v/PycharmProjects/YadVansh/StratForge/quant-strat-forge"  # Absolute path
                ]
                
                model_path = None
                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        model_path = abs_path
                        break
                
                if model_path is None:
                    model_path = "./quant-strat-forge"  # Fallback for error message
            
            # Convert to absolute path for clarity
            model_path = os.path.abspath(model_path)
            
            # Check if custom model exists
            if not os.path.exists(model_path):
                error_msg = (
                    f"❌ Custom model not found at '{model_path}'.\n"
                    f"\n"
                    f"QuantStratForge uses ONLY your custom trained model.\n"
                    f"No external LLMs will be used.\n"
                    f"\n"
                    f"To train your model:\n"
                    f"  1. quantstratforge prepare     # Prepare training data\n"
                    f"  2. quantstratforge train       # Train model locally\n"
                    f"\n"
                    f"Or for federated learning:\n"
                    f"  2. quantstratforge train --federated  # Train with privacy-preserving FL\n"
                    f"\n"
                    f"After training, your model will be saved to: {model_path}"
                )
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Load your custom trained model
            logger.info(f"🔄 Loading YOUR custom SLM model from: {model_path}")
            self.model_path = model_path
            
            # Load model and tokenizer explicitly
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                
                # Use 4-bit quantization for inference to save memory on 6GB GPU
                if torch.cuda.is_available():
                    from transformers import BitsAndBytesConfig
                    
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        quantization_config=quantization_config,
                        device_map="auto",
                        low_cpu_mem_usage=True
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        torch_dtype=torch.float32,
                        device_map=None
                    )
                
                # Create pipeline - don't specify device when using device_map="auto"
                self.generator = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer
                )
                
                logger.info(f"✅ Custom SLM model loaded successfully from: {model_path}")
                logger.info(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
                
            except Exception as e:
                logger.error(f"Failed to load model from {model_path}: {e}")
                logger.error(f"Make sure the model was trained and saved correctly.")
                raise
                
                
        except Exception as e:
            logger.error(f"Generator initialization failure: {e}")
            raise

    def generate(self, input_data: str):
        try:
            # Clear GPU cache before generation to free memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Truncate input to fit in context window (leave room for prompt and generation)
            # Max context is 2048, use ~1500 for input data to be safe
            max_input_tokens = 1500
            tokens = self.tokenizer.encode(input_data, add_special_tokens=False)
            if len(tokens) > max_input_tokens:
                logger.warning(f"Input too long ({len(tokens)} tokens), truncating to {max_input_tokens}")
                tokens = tokens[:max_input_tokens]
                input_data = self.tokenizer.decode(tokens, skip_special_tokens=True)
            
            # Create a better structured prompt for code generation
            prompt = f"""### Instruction:
Generate a Python quantitative trading strategy function.

### Input Data:
{input_data[:500]}

### Required Output Format:
def strategy(df):
    # Your strategy code here
    # df has columns: Open, High, Low, Close, Volume
    # Return signals as: 1 (buy), 0 (hold), -1 (sell)
    return signals

### Strategy Code:
"""
            
            # Generate with reduced parameters for 6GB GPU
            output = self.generator(
                prompt, 
                max_new_tokens=150,  # Reduced from 200
                do_sample=True, 
                temperature=0.7,
                truncation=True,
                max_length=2048  # Enforce max length
            )[0]["generated_text"]
            
            # Extract the generated code
            try:
                # Try to extract Python code
                generated = output.split("### Strategy Code:")[-1].strip()
                
                # Look for def function
                if "def " in generated:
                    # Extract everything from def to the end or next ###
                    code_start = generated.find("def ")
                    code_end = generated.find("###", code_start)
                    if code_end == -1:
                        code_end = len(generated)
                    strategy = generated[code_start:code_end].strip()
                    explanation = "AI-generated quantitative trading strategy"
                else:
                    # Fallback to simple extraction
                    strategy = generated[:500].strip()
                    explanation = "Strategy code generated by AI model"
            except Exception as e:
                logger.warning(f"Code extraction failed: {e}")
                strategy = "# Default strategy\ndef strategy(df):\n    return (df['Close'] > df['Close'].rolling(20).mean()).astype(int)"
                explanation = "Fallback to simple moving average strategy"
            logger.info("Strategy generated successfully")
            return {"strategy_code": strategy, "explanation": add_watermark(explanation)}
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
        finally:
            # Clean up GPU memory after generation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()