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

from datasets import Dataset, load_dataset

dataset = load_dataset("EleanorZzz/gsm8k_training_synthetic_positive_direct_cot", split="train")

transformed_data = []
for example in dataset:
    messages = [
        {"role": "system", "content": example["system"]},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]},
    ]
    transformed_data.append({"messages": messages})

new_dataset = Dataset.from_list(transformed_data)
new_dataset.push_to_hub("simonycl/gsm8k_training_positive_direct_cot_1k_transformed", split="train")
