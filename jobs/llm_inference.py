"""LLM Inference Job Execution"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Any
import structlog

from .base import BaseJob

log = structlog.get_logger()


class LLMInferenceJob(BaseJob):
    """Execute LLM inference jobs"""

    def __init__(self, job_data: Dict[str, Any]):
        super().__init__(job_data)
        self.model_name = self.input_data.get('model', 'Qwen/Qwen-7B')
        self.prompt = self.input_data.get('prompt', '')
        self.max_tokens = self.config.get('max_tokens', 512)
        self.temperature = self.config.get('temperature', 0.7)
        self.model = None
        self.tokenizer = None

    def validate(self) -> bool:
        if not super().validate():
            return False

        if not self.prompt:
            log.error("Prompt is required for LLM inference")
            return False

        return True

    def load_model(self):
        """Load model and tokenizer"""
        log.info("Loading model", model=self.model_name)

        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info("Using device", device=device)

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto",
            trust_remote_code=True
        )

        self.model.eval()
        log.info("Model loaded successfully")

    def execute(self) -> Dict[str, Any]:
        """Execute LLM inference"""
        try:
            if not self.validate():
                return {'success': False, 'error': 'Validation failed'}

            # Load model
            self.load_model()

            # Tokenize input
            inputs = self.tokenizer(self.prompt, return_tensors="pt")

            if torch.cuda.is_available():
                inputs = inputs.to("cuda")

            # Generate
            log.info("Generating response", max_tokens=self.max_tokens)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    top_p=0.95,
                    top_k=50,
                )

            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            log.info("Inference completed successfully")

            return {
                'success': True,
                'output': generated_text,
                'model': self.model_name,
                'tokens_generated': len(outputs[0])
            }

        except Exception as e:
            log.error("Inference failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }

    def cleanup(self):
        """Clean up model from memory"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        log.info("Cleanup completed")
