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

import json
import random

from datasets import load_dataset

# Load the dataset
dataset = load_dataset("EleanorZzz/gsm8k_training_positive_1k")
seed = 42
random.seed(seed)
max_samples = 100

# Process the data
processed_data = []
for item in dataset["train"]:
    instruction = item["instruction"]
    output = item["output"]

    # Remove the trailing instruction text
    trailing_text = "Think step by step then provide the numerical answer at the end after the delimiter '####', like '#### 24'."
    if instruction.endswith(trailing_text):
        instruction = instruction[: -len(trailing_text)].strip()
    # Remove "Question: " prefix if it exists
    if instruction.startswith("Question: "):
        instruction = instruction[len("Question: ") :].strip()
    # Format the new prompt
    formatted_prompt = f"Here's the math problem: {instruction}\nGolden answer: {output}"
    processed_data.append(formatted_prompt)

subset_data = random.sample(processed_data, max_samples)
# Save to file
with open("data/synthetic_negative_new.jsonl", "w") as f:
    for prompt in subset_data:
        f.write(json.dumps({"prompt": prompt}) + "\n")

print(f"Processed {len(subset_data)} items and saved to synthetic_negative_new.jsonl")
