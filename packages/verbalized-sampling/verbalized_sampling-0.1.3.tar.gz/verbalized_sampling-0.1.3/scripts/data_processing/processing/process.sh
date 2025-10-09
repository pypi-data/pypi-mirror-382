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

MODELS=gemini-2.5-flash
MODELS=gpt-4.1
POSITIVE_DATASET=simonycl/gsm8k_training_positive_1k_transformed
# POSITIVE_DATASET=simonycl/gsm8k_training_positive_direct_1k_transformed

# python processing/process_synthetic_negative.py \
#     "method_synthetic_negative_test/${MODELS}_synthetic_negative/generation/direct (samples=1)/responses.jsonl" \
#     --positive_dataset $POSITIVE_DATASET \
#     --output_dataset gsm8k_training_negative_direct_1k_${MODELS}_transformed \
#     --verbose

# python processing/process_synthetic_negative.py \
#     "method_synthetic_negative_test/${MODELS}_synthetic_negative/generation/sequence [strict] (samples=5)/responses.jsonl" \
#     --positive_dataset $POSITIVE_DATASET \
#     --output_dataset gsm8k_training_negative_sequence_1k_${MODELS}_transformed \
#     --verbose

python processing/process_synthetic_negative.py \
    "method_synthetic_negative_test/gpt-4.1_synthetic_negative/generation/multi_turn (samples=5)/responses.jsonl" \
    --positive_dataset $POSITIVE_DATASET \
    --output_dataset gsm8k_training_negative_multi_turn_1k_${MODELS}_transformed \
    --verbose

# python processing/process_synthetic_negative.py \
#     "method_synthetic_negative_test/${MODELS}_synthetic_negative/generation/structure_with_prob [strict] (samples=5)/responses.jsonl" \
#     --positive_dataset $POSITIVE_DATASET \
#     --output_dataset gsm8k_training_negative_vs_standard_1k_${MODELS}_transformed \
#     --verbose
python processing/process_synthetic_negative.py \
    "method_synthetic_negative_test/gpt-4.1_synthetic_negative/generation/chain_of_thought [strict] (samples=5)/responses.jsonl" \
    --positive_dataset $POSITIVE_DATASET \
    --output_dataset gsm8k_training_negative_chain_of_thought_1k_${MODELS}_transformed \
    --verbose


# python processing/process_synthetic_negative.py \
#     "method_synthetic_negative_test/${MODELS}_synthetic_negative/generation/combined [strict] (samples=5)/responses.jsonl" \
#     --positive_dataset $POSITIVE_DATASET \
#     --output_dataset gsm8k_training_negative_combined_1k_${MODELS}_transformed \
#     --verbose