# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Proprietary License. See LICENSE file for details.

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
import flwr as fl
from datasets import load_from_disk
from .utils import logger

class StrategyModel:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2", lora_r=16):
        self.model_name = model_name
        self.lora_r = lora_r
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = None
        self.dataset = None

    def load_model(self):
        try:
            model = AutoModelForCausalLM.from_pretrained(self.model_name, load_in_8bit=True, device_map="auto")
            lora_config = LoraConfig(r=self.lora_r, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
            return get_peft_model(model, lora_config)
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise

    def tokenize_function(self, examples):
        return self.tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

    def prepare_for_training(self, data_path="./formatted_data"):
        try:
            self.dataset = load_from_disk(data_path)
            tokenized_dataset = self.dataset.map(self.tokenize_function, batched=True)
            tokenized_dataset = tokenized_dataset.remove_columns(["text", "label"])
            tokenized_dataset.set_format("torch")
            return tokenized_dataset
        except Exception as e:
            logger.error(f"Training preparation failed: {e}")
            raise

    def get_training_args(self, output_dir="./quant-strat-forge", epochs=3):
        return TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=2 if torch.cuda.is_available() else 1,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            learning_rate=2e-4,
            fp16=True if torch.cuda.is_available() else False,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",
            remove_unused_columns=False,
        )

    def train_local(self, data_path="./formatted_data", epochs=3):
        try:
            tokenized_dataset = self.prepare_for_training(data_path)
            self.model = self.load_model()
            args = self.get_training_args()
            trainer = Trainer(model=self.model, args=args, train_dataset=tokenized_dataset)
            trainer.train()
            self.model.save_pretrained("./quant-strat-forge")
            self.tokenizer.save_pretrained("./quant-strat-forge")
            logger.info("Local training done!")
        except Exception as e:
            logger.error(f"Local training failed: {e}")
            raise

    def federated_train(self, num_clients=3, num_rounds=3, data_path="./formatted_data"):
        try:
            tokenized_dataset = self.prepare_for_training(data_path)
            client_datasets = [tokenized_dataset.shard(num_clients, i) for i in range(num_clients)]

            class QuantClient(fl.client.NumPyClient):
                def __init__(self, cid, trainset, model_loader, args_getter):
                    self.model = model_loader()
                    self.trainset = trainset
                    self.training_args = args_getter()
                    self.trainer = Trainer(model=self.model, args=self.training_args, train_dataset=self.trainset)

                def get_parameters(self, config):
                    return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

                def set_parameters(self, parameters):
                    params_dict = zip(self.model.state_dict().keys(), parameters)
                    state_dict = {k: torch.tensor(v) for k, v in params_dict}
                    self.model.load_state_dict(state_dict, strict=False)

                def fit(self, parameters, config):
                    self.set_parameters(parameters)
                    self.trainer.train()
                    return self.get_parameters(config={}), len(self.trainset), {}

            def client_fn(cid: str):
                return QuantClient(cid, client_datasets[int(cid)], self.load_model, self.get_training_args)

            fl.simulation.start_simulation(
                client_fn=client_fn,
                num_clients=num_clients,
                client_resources={"num_cpus": 2, "num_gpus": 0.5 if torch.cuda.is_available() else 0},
                strategy=fl.server.strategy.FedAvg(),
                num_rounds=num_rounds
            )

            self.model = self.load_model()
            self.model.save_pretrained("./quant-strat-forge")
            self.tokenizer.save_pretrained("./quant-strat-forge")
            logger.info("Federated training completed!")
        except Exception as e:
            logger.error(f"Federated training failed: {e}")
            raise