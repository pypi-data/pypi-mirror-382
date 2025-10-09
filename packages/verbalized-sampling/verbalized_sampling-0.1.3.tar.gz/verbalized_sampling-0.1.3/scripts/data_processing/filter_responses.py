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

input_file = "story_experiments_final/anthropic_claude-3.7-sonnet/anthropic_claude-3.7-sonnet_book/generation/vs_multi [strict] (samples=5)/responses.jsonl"
output_file = input_file.replace(".jsonl", "_filtered.jsonl")


def is_list_of_dicts(obj):
    return isinstance(obj, list) and all(isinstance(item, dict) for item in obj)


with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        try:
            data = json.loads(line)
            if is_list_of_dicts(data.get("responses", [])):
                outfile.write(line)
        except Exception:
            continue  # skip lines that aren't valid JSON

print(f"Filtered lines written to {output_file}")
