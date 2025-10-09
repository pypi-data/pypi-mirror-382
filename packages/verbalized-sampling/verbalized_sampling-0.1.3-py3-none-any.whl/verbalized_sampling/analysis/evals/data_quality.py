# Copyright 2025 CHATS-Lab. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import numpy as np
from datasets import load_dataset
from tqdm import tqdm

from verbalized_sampling.llms import get_model

from .base import BaseEvaluator, EvalResult


# Templates for synthetic question quality evaluation
def get_system_prompt(k: int) -> str:
    return f"""You are an expert at evaluating question quality.
You will be shown {k} questions. All but one of them are from a high-quality dataset, while one of them is synthetically generated and may be of lower quality.
Your task is to identify which question (1, 2, ..., {k}) appears to be synthetically generated or of lower quality. Consider factors like:

1. Natural language patterns and flow
2. Question structure, clarity, and difficulty
3. Context and specificity
4. Any subtle artifacts or unnatural patterns
5. Question coherence and logical structure

Analyze each question carefully and explain your reasoning. End with 'Answer: [Question Number]' where Question Number is 1, 2, ..., {k}."""


def get_user_prompt(k: int, questions: str) -> str:
    return f"""Here are {k} questions. One of them is synthetically generated. Please identify which one:
{questions}

Analyze each question and explain which one you think is synthetically generated or of lower quality. End with 'Answer: [Question Number]'."""


class GSM8KEvaluator:
    def __init__(self):
        self.dataset = load_dataset("openai/gsm8k", name="main", split="train")
        self.candidate_questions = [q for q in self.dataset["question"]]

    def extract_question(self, raw_response: str, grounding: Dict = None) -> str:
        # Extract just the question part
        if "Question:" in raw_response:
            parsed = raw_response.split("Question:")[1]
            if "Answer:" in parsed:
                return parsed.split("Answer:")[0].strip()
            else:
                return parsed.strip()
        return raw_response.strip()

    def get_quality_prompt(
        self, data_point: str, ground_truth_placement: int = 1, num_examples_to_choose_from: int = 4
    ) -> Dict[str, str]:
        # Examples from same category as data point
        random.seed(hash(data_point) % 2**32)  # Deterministic randomness
        random_samples = random.sample(self.candidate_questions, num_examples_to_choose_from - 1)

        # Build the questions in the right order based on ground_truth_placement
        synthetic_question = self.extract_question(data_point)
        questions_compiled, real_example_idx = "", 0
        for i in range(1, num_examples_to_choose_from + 1):
            if i == ground_truth_placement:
                questions_compiled += f"Question {i}: {synthetic_question}\n"
            else:
                questions_compiled += f"Question {i}: {random_samples[real_example_idx]}\n"
                real_example_idx += 1

        return {
            "system": get_system_prompt(num_examples_to_choose_from),
            "user": get_user_prompt(num_examples_to_choose_from, questions_compiled),
        }


class LiveCodeBenchEvaluator:
    def __init__(self):
        self.dataset = load_dataset(
            "livecodebench/test_generation", split="test", trust_remote_code="True"
        )
        self.candidate_questions = [q for q in self.dataset["question_content"]]

    def extract_question(self, raw_response: str, grounding: Dict = None) -> str:
        # Extract just the question part
        if "Question:" in raw_response:
            parsed = raw_response.split("Question:")[1]
            if "Test Input:" in parsed:
                return parsed.split("Test Input:")[0].strip()
            elif "Answer:" in parsed:
                return parsed.split("Answer:")[0].strip()
            else:
                return parsed.strip()
        return raw_response.strip()

    def get_quality_prompt(
        self, data_point: str, ground_truth_placement: int = 1, num_examples_to_choose_from: int = 4
    ) -> Dict[str, str]:
        random.seed(hash(data_point) % 2**32)  # Deterministic randomness
        random_samples = random.sample(self.candidate_questions, num_examples_to_choose_from - 1)
        synthetic_question = self.extract_question(data_point)

        questions_compiled, real_example_idx = "", 0
        for i in range(1, num_examples_to_choose_from + 1):
            if i == ground_truth_placement:
                questions_compiled += f"Question {i}: {synthetic_question}\n"
            else:
                questions_compiled += f"Question {i}: {random_samples[real_example_idx]}\n"
                real_example_idx += 1

        return {
            "system": get_system_prompt(num_examples_to_choose_from),
            "user": get_user_prompt(num_examples_to_choose_from, questions_compiled),
        }


def check_lcb_dataset(datapoint: str) -> bool:
    """
    Check if the datapoint is from the LiveCodeBench (lcb) dataset.
    Returns True if 'Test Input' is present in the datapoint string, else False (assume gsm8k).
    """
    return "Test Input" in datapoint


class SyntheticQuestionQualityEvaluator(BaseEvaluator):
    instance_plot_metrics = [
        ("is_distinguishable", "histogram"),
        ("placement", "histogram"),
    ]
    aggregate_plot_metrics = [
        "avg_ir_rate",
    ]
    key_plot_metrics = [
        ("avg_ir_rate", "IR Rate (Identification Rate)"),
    ]

    def __init__(
        self,
        judge_model: str = "gpt-4.1",
        num_workers: int = 64,
        num_responses_per_prompt: int = 50,
        dataset_type: str = "auto",
    ):
        super().__init__("question_quality", num_workers=num_workers)
        self.judge_model_name = judge_model
        self.dataset_type = dataset_type
        self.num_responses_per_prompt = num_responses_per_prompt

        # Initialize dataset evaluators
        self.gsm8k_evaluator = GSM8KEvaluator()
        self.lcb_evaluator = LiveCodeBenchEvaluator()

        # Thread-local storage for judge models to avoid conflicts
        self._thread_local = threading.local()

    def parse_quality_response(self, response: str, ground_truth_placement: int = 0) -> bool:
        # Extract the model's guess from the response
        lines = response.lower().split("\n")
        # print(lines)
        for line in reversed(lines):
            if "answer:" in line:
                # Extract the number after "answer:"
                try:
                    # extract the number after "answer:"
                    after_answer = line[line.find("answer:") + len("answer:") :].strip()
                    match = re.search(r"\d+", after_answer)
                    if match:
                        model_guess = int(match.group())
                    # print(f"Model guess: {model_guess}")
                    # Is acceptable if model guess is not the ground truth
                    return model_guess, model_guess != ground_truth_placement
                except ValueError:
                    return None, False
        return None, False

    def _get_thread_judge_model(self):
        """Get a thread-local judge model instance to avoid conflicts in parallel execution."""
        if not hasattr(self._thread_local, "judge_model"):
            model_config = {"temperature": 0.1}
            self._thread_local.judge_model = get_model(
                self.judge_model_name, method="direct", config=model_config, strict_json=True
            )
        return self._thread_local.judge_model

    def compute_instance_metric(self, prompt: str, response: Dict) -> Dict[str, Any]:
        response_text = response.get("text", response)
        if isinstance(response_text, dict):
            response_text = str(response_text)

        # Determine dataset type
        if self.dataset_type == "auto":
            is_lcb = check_lcb_dataset(response_text)
            evaluator = self.lcb_evaluator if is_lcb else self.gsm8k_evaluator
        elif self.dataset_type == "gsm8k":
            evaluator = self.gsm8k_evaluator
        elif self.dataset_type == "livecodebench":
            evaluator = self.lcb_evaluator
        else:
            raise ValueError(f"Unknown dataset_type: {self.dataset_type}")

        # Randomly place the synthetic question among genuine ones
        placement = random.Random(hash(response_text)).randint(1, 4)  # 1-indexed position

        # Get judge model for this thread
        judge_model = self._get_thread_judge_model()

        # Get quality prompt from the appropriate evaluator
        try:
            prompt_data = evaluator.get_quality_prompt(response_text, placement)

            # Query the judge model
            prompt_messages = [
                {"role": "system", "content": prompt_data["system"]},
                {"role": "user", "content": prompt_data["user"]},
            ]
            judge_response = judge_model._chat(prompt_messages)

            # Parse the judge's response
            model_guess, is_distinguishable = self.parse_quality_response(judge_response, placement)

            return {
                "prompt": prompt,
                "synthetic_question": evaluator.extract_question(response_text),
                "placement": placement,
                "judge_response": judge_response,
                "model_guess": model_guess,
                "is_distinguishable": is_distinguishable,
                "dataset_type": evaluator.__class__.__name__,
                "probability": response.get("probability", np.nan),
            }

        except Exception as e:
            print(f"Error in judge evaluation: {e}")
            return {
                "prompt": prompt,
                "synthetic_question": evaluator.extract_question(response_text),
                "placement": placement,
                "judge_response": "",
                "model_guess": None,
                "is_distinguishable": False,
                "error": str(e),
                "probability": response.get("probability", np.nan),
            }

    def _process_prompt_group(self, prompt_group_tuple):
        """Process a single prompt group and calculate detection rate."""
        prompt, group = prompt_group_tuple

        # Calculate detection stats for this prompt group
        indistinguishable_count = sum(1 for m in group if m.get("is_distinguishable", False))
        total_count = len(group)

        # print("Total count: ", total_count, self.num_responses_per_prompt)
        ir_rate = indistinguishable_count / total_count if total_count > 0 else 0

        return {
            "prompt": prompt,
            "ir_rate": ir_rate,
            "group_size": total_count,
        }

    def aggregate_metrics(self, instance_metrics: List[Dict[str, float]]) -> Dict[str, Any]:
        if not instance_metrics:
            return {}

        # If input is nested, flatten
        if len(instance_metrics) > 0 and isinstance(instance_metrics[0], list):
            metrics = [m for sublist in instance_metrics for m in sublist if sublist]
        else:
            metrics = instance_metrics
        if not metrics:
            return {}

        # Group by prompt
        prompt_groups = {}
        for metric in metrics:
            prompt = metric["prompt"]
            if prompt not in prompt_groups:
                prompt_groups[prompt] = []
            prompt_groups[prompt].append(metric)

        # Process prompt groups in parallel using ThreadPoolExecutor
        per_prompt_stats = {}
        prompt_detection_rates = []
        total_responses = 0
        num_prompts = len(prompt_groups)

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            # Submit processing tasks for each prompt group
            future_to_prompt = {
                executor.submit(self._process_prompt_group, (prompt, group)): prompt
                for prompt, group in prompt_groups.items()
            }

            # Process results as they complete
            with tqdm(total=len(prompt_groups), desc="Processing prompt groups") as pbar:
                for future in as_completed(future_to_prompt):
                    result = future.result()
                    prompt = result["prompt"]

                    per_prompt_stats[prompt] = {
                        "prompt": prompt,
                        "ir_rate": result["ir_rate"],
                    }

                    prompt_detection_rates.append(result["ir_rate"])
                    total_responses += result["group_size"]
                    pbar.update(1)

        # Calculate overall totals
        total_indistinguishable = sum(metric.get("is_distinguishable", False) for metric in metrics)
        total_distinguishable = len(metrics) - total_indistinguishable

        # Calculate average detection rate (IR rate)
        avg_ir_rate = sum(prompt_detection_rates) / num_prompts if prompt_detection_rates else 0

        return {
            "per_prompt_stats": per_prompt_stats,
            "num_indistinguishable": total_indistinguishable,
            "num_distinguishable": total_distinguishable,
            "num_responses": total_responses,
            "num_prompts": num_prompts,
            "avg_ir_rate": avg_ir_rate,  # This is the IR rate
        }

    def evaluate(
        self, prompts: List[str], responses: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> EvalResult:
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "evaluation_framework": "SyntheticQuestionQuality",
                "judge_model": self.judge_model_name,
                "num_responses": len(responses),
                "num_workers": self.num_workers,
                "dataset_type": self.dataset_type,
                "evaluation_type": "synthetic_question_detection",
            }
        )

        return super().evaluate(prompts, responses, metadata)


# Backward compatibility alias
SyntheticDataQualityEvaluator = SyntheticQuestionQualityEvaluator
