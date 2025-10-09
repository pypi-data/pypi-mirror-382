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

from pathlib import Path
from typing import Any, Dict, List

from verbalized_sampling.methods import Method
from verbalized_sampling.pipeline import (
    EvaluationConfig,
    ExperimentConfig,
    Pipeline,
    PipelineConfig,
)
from verbalized_sampling.tasks import Task


def create_method_experiments(
    task: Task,
    model_name: str,
    temperature: float,
    top_p: float,
    methods: List[Dict[str, Any]],
) -> List[ExperimentConfig]:
    """Create experiments for testing specific method variations."""

    # Base configuration
    base = {
        "task": task,
        "model_name": model_name,
        "num_responses": 10,
        "num_prompts": 50,  # maximum 100
        "target_words": 0,
        "temperature": temperature,
        "top_p": top_p,
        "random_seed": 42,
        "use_vllm": False,
    }

    experiments = []
    for method_config in methods:
        # Create name
        name = f"{method_config['method'].value}"
        if method_config.get("strict_json"):
            name += " [strict]"
        if method_config.get("num_samples"):
            name += f" (samples={method_config['num_samples']})"

        experiments.append(ExperimentConfig(name=name, **base, **method_config))

    return experiments


def run_method_tests(
    task: Task,
    model_name: str,
    methods: List[Dict[str, Any]],
    metrics: List[str],  # "ngram"
    temperature: float,
    top_p: float,
    output_dir: str,
    num_workers: int = 16,
) -> None:
    """Run tests for specific method variations."""
    print("🔬 Running Method Tests")

    experiments = create_method_experiments(task, model_name, temperature, top_p, methods)
    print(f"📊 {len(experiments)} methods to test")

    for i, exp in enumerate(experiments, 1):
        print(f"  {i}. {exp.name}")

    model_basename = model_name.replace("/", "_")
    config = PipelineConfig(
        experiments=experiments,
        evaluation=EvaluationConfig(metrics=metrics),
        output_base_dir=Path(f"{output_dir}/{model_basename}_{task.value}"),
        skip_existing=True,
    )

    pipeline = Pipeline(config)
    pipeline.run_complete_pipeline()
    print(f"✅ Done! Check {output_dir}/{model_basename}_{task.value}/pipeline_report.html")


if __name__ == "__main__":
    # Example usage for testing different method variations

    # Test multi-turn and JSON mode variations
    num_samples = 5
    methods = [
        # {
        #     'method': Method.DIRECT,
        #     'strict_json': False,
        #     'num_samples': 1,
        # },
        # {
        #     'method': Method.DIRECT_COT,
        #     'strict_json': True,
        #     'num_samples': 1,
        # },
        {
            "method": Method.MULTI_TURN,
            "strict_json": False,
            "num_samples": num_samples,
        },
        # {
        #     'method': Method.SEQUENCE,
        #     'strict_json': True,
        #     'num_samples': num_samples,
        # },
        # {
        #     'method': Method.VS_STANDARD,
        #     'strict_json': True,
        #     'num_samples': num_samples,
        # },
        {
            "method": Method.SEQUENCE,
            "strict_json": True,
            "num_samples": num_samples,
        },
        # {
        #     'method': Method.VS_STANDARD,
        #     'strict_json': True,
        #     'num_samples': num_samples,
        # },
        # {
        #     'method': Method.VS_MULTI,
        #     'strict_json': True,
        #     'num_samples': num_samples,
        #     'num_samples_per_prompt': 2,
        # }
    ]

    models = [
        # "gpt-4.1-mini",
        "gpt-4.1",
        # "gemini-2.5-flash",
        # "gemini-2.5-pro",
        # "llama-3.1-70b-instruct",
        # "claude-4-sonnet",
        # "meta-llama/Llama-3.1-70B-Instruct",
        # "meta-llama/Llama-3.1-70B",
        # "anthropic/claude-4-sonnet",
        # "deepseek-r1",
        # "o3",
    ]
    for model in models:
        model_basename = model.replace("/", "_")
        run_method_tests(
            task=Task.SYNTHETIC_NEGATIVE,
            model_name=model,
            methods=methods,
            metrics=["diversity"],
            temperature=0.7,
            top_p=1.0,
            output_dir="method_synthetic_negative_test",
            num_workers=16 if any(x in model_basename for x in ["claude", "gemini"]) else 32,
        )
