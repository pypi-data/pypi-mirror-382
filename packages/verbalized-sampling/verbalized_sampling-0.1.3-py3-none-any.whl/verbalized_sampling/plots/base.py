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

from dataclasses import dataclass
from typing import Optional

from ..analysis.evals.base import EvalResult


@dataclass
class ComparisonData:
    """Container for comparison data."""

    name: str  # Format name (e.g., "direct", "cot", "verbalized")
    result: EvalResult
    color: Optional[str] = None


class MetricExtractor:
    """Handles extraction of metric values from evaluation results."""

    @staticmethod
    def extract_metric_values(data: ComparisonData, metric_name: str) -> list[float]:
        """Extract metric values from either instance_metrics or overall_metrics."""
        values = []

        # First, try to find in instance_metrics
        for instance in data.result.instance_metrics:
            value = instance
            for key in metric_name.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                if isinstance(value, (list, tuple)):
                    values.extend([float(v) for v in value if v is not None])
                else:
                    values.append(float(value))

        # If no values found in instance_metrics, try overall_metrics
        if not values:
            overall_value = data.result.overall_metrics
            for key in metric_name.split("."):
                if isinstance(overall_value, dict) and key in overall_value.keys():
                    overall_value = overall_value[key]
                else:
                    overall_value = None
                    break

            if overall_value is not None:
                if isinstance(overall_value, (list, tuple)):
                    values = [float(v) for v in overall_value if v is not None]
                elif isinstance(overall_value, (int, float)):
                    values = [float(overall_value)]
                elif isinstance(overall_value, dict):
                    values = [float(v) for v in overall_value.values() if v is not None]

        return values
