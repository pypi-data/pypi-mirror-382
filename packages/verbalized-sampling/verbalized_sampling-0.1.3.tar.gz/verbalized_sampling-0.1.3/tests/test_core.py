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

"""Tests for core module (Item, DiscreteDist, transforms)."""

import pytest

from verbalized_sampling.selection import DiscreteDist, Item, postprocess_responses, repair_weight


class TestItem:
    """Tests for Item dataclass."""

    def test_item_creation(self):
        """Test basic Item creation."""
        item = Item("hello", p=0.5, meta={"test": "value"})
        assert item.text == "hello"
        assert item.p == 0.5
        assert item.meta["test"] == "value"

    def test_item_probability_validation(self):
        """Test Item validates probability in [0, 1]."""
        # Valid probabilities
        Item("test", p=0.0, meta={})
        Item("test", p=0.5, meta={})
        Item("test", p=1.0, meta={})

        # Invalid probabilities
        with pytest.raises(ValueError, match="Probability must be in"):
            Item("test", p=-0.1, meta={})

        with pytest.raises(ValueError, match="Probability must be in"):
            Item("test", p=1.5, meta={})

    def test_item_repr(self):
        """Test Item string representation."""
        item = Item("hello world", p=0.75, meta={})
        repr_str = repr(item)
        assert "0.750" in repr_str
        assert "hello world" in repr_str


class TestDiscreteDist:
    """Tests for DiscreteDist class."""

    def test_discrete_dist_creation(self):
        """Test basic DiscreteDist creation."""
        items = [
            Item("a", p=0.5, meta={}),
            Item("b", p=0.3, meta={}),
            Item("c", p=0.2, meta={}),
        ]
        dist = DiscreteDist(items, trace={"model": "test"})

        assert len(dist) == 3
        assert dist[0].text == "a"
        assert sum(dist.p) == pytest.approx(1.0)

    def test_discrete_dist_validates_sum(self):
        """Test DiscreteDist validates probabilities sum to 1."""
        items = [
            Item("a", p=0.5, meta={}),
            Item("b", p=0.5, meta={}),
        ]
        dist = DiscreteDist(items, trace={})
        assert sum(dist.p) == pytest.approx(1.0)

        # Invalid sum
        bad_items = [
            Item("a", p=0.5, meta={}),
            Item("b", p=0.3, meta={}),
        ]
        with pytest.raises(ValueError, match="must sum to 1"):
            DiscreteDist(bad_items, trace={})

    def test_discrete_dist_validates_order(self):
        """Test DiscreteDist validates descending order."""
        # Valid (descending)
        items = [
            Item("a", p=0.5, meta={}),
            Item("b", p=0.3, meta={}),
            Item("c", p=0.2, meta={}),
        ]
        dist = DiscreteDist(items, trace={})
        assert dist.p == [0.5, 0.3, 0.2]

        # Invalid (not descending)
        bad_items = [
            Item("a", p=0.2, meta={}),
            Item("b", p=0.5, meta={}),  # Out of order
            Item("c", p=0.3, meta={}),
        ]
        with pytest.raises(ValueError, match="must be sorted descending"):
            DiscreteDist(bad_items, trace={})

    def test_argmax(self):
        """Test argmax returns highest probability item."""
        items = [
            Item("best", p=0.6, meta={}),
            Item("second", p=0.3, meta={}),
            Item("third", p=0.1, meta={}),
        ]
        dist = DiscreteDist(items, trace={})
        assert dist.argmax().text == "best"

    def test_argmax_empty(self):
        """Test argmax raises on empty distribution."""
        dist = DiscreteDist([], trace={})
        with pytest.raises(ValueError, match="empty distribution"):
            dist.argmax()

    def test_sample(self):
        """Test sample with seed is deterministic."""
        items = [
            Item("a", p=0.5, meta={}),
            Item("b", p=0.3, meta={}),
            Item("c", p=0.2, meta={}),
        ]
        dist = DiscreteDist(items, trace={})

        # Sample with same seed should give same result
        result1 = dist.sample(seed=42)
        result2 = dist.sample(seed=42)
        assert result1.text == result2.text

    def test_map(self):
        """Test map preserves probabilities."""
        items = [
            Item("hello", p=0.6, meta={}),
            Item("world", p=0.4, meta={}),
        ]
        dist = DiscreteDist(items, trace={})

        upper_dist = dist.map(str.upper)
        assert upper_dist[0].text == "HELLO"
        assert upper_dist[1].text == "WORLD"
        assert upper_dist[0].p == 0.6
        assert upper_dist[1].p == 0.4

    def test_filter_items(self):
        """Test filter_items renormalizes."""
        items = [
            Item("hello world", p=0.5, meta={}),
            Item("hi", p=0.3, meta={}),
            Item("greetings", p=0.2, meta={}),
        ]
        dist = DiscreteDist(items, trace={})

        # Filter to items with length > 5
        long_dist = dist.filter_items(lambda it: len(it.text) > 5)
        assert len(long_dist) == 2  # "hello world" and "greetings"
        assert sum(long_dist.p) == pytest.approx(1.0)  # Renormalized

    def test_filter_items_empty(self):
        """Test filter_items raises if all removed."""
        items = [
            Item("a", p=0.6, meta={}),
            Item("b", p=0.4, meta={}),
        ]
        dist = DiscreteDist(items, trace={})

        with pytest.raises(ValueError, match="Filter removed all items"):
            dist.filter_items(lambda it: False)

    def test_reweight(self):
        """Test reweight renormalizes and re-sorts."""
        items = [
            Item("short", p=0.6, meta={}),
            Item("medium text", p=0.3, meta={}),
            Item("very long text here", p=0.1, meta={}),
        ]
        dist = DiscreteDist(items, trace={})

        # Reweight by inverse length (longer = higher weight)
        rewighted = dist.reweight(lambda it: 1.0 / (len(it.text) + 1))
        assert sum(rewighted.p) == pytest.approx(1.0)
        # After reweighting, order may change

    def test_serialization(self):
        """Test to_dict and from_dict roundtrip."""
        items = [
            Item("a", p=0.6, meta={"test": "value"}),
            Item("b", p=0.4, meta={}),
        ]
        dist = DiscreteDist(items, trace={"model": "test-model"})

        # Serialize
        data = dist.to_dict()
        assert len(data["items"]) == 2
        assert data["trace"]["model"] == "test-model"

        # Deserialize
        dist2 = DiscreteDist.from_dict(data)
        assert len(dist2) == 2
        assert dist2[0].text == "a"
        assert dist2[0].p == 0.6
        assert dist2.trace["model"] == "test-model"

    def test_to_markdown(self):
        """Test to_markdown formatting."""
        items = [
            Item("first", p=0.5, meta={"repairs": []}),
            Item("second", p=0.3, meta={"repairs": ["clipped>1"]}),
            Item("third", p=0.2, meta={"repairs": []}),
        ]
        dist = DiscreteDist(items, trace={"model": "test", "tau_final": 0.12})

        markdown = dist.to_markdown()
        assert "k=3" in markdown
        assert "τ=0.12" in markdown
        assert "first" in markdown
        assert "clipped>1" in markdown


class TestTransforms:
    """Tests for transforms module."""

    def test_repair_weight_percent(self):
        """Test repair_weight handles percentages."""
        value, repairs = repair_weight("70%")
        assert value == pytest.approx(0.70)
        assert "percent_to_unit" in repairs

    def test_repair_weight_negative(self):
        """Test repair_weight clips negatives."""
        value, repairs = repair_weight(-0.5)
        assert value == 0.0
        assert "negative_to_zero" in repairs

    def test_repair_weight_gt_one(self):
        """Test repair_weight clips > 1."""
        value, repairs = repair_weight(1.5)
        assert value == 1.0
        assert "clipped>1" in repairs

    def test_repair_weight_invalid(self):
        """Test repair_weight handles invalid inputs."""
        value, repairs = repair_weight("not_a_number")
        assert value == 0.0
        assert "invalid_to_zero" in repairs

    def test_postprocess_basic(self):
        """Test postprocess with basic input."""
        parsed = [
            {"text": "a", "probability": 0.5},
            {"text": "b", "probability": 0.3},
            {"text": "c", "probability": 0.2},
        ]

        items, meta = postprocess_responses(parsed, tau=0.15, min_k_survivors=2, weight_mode="elicited", seed=42)

        assert len(items) >= 2
        assert sum(it.p for it in items) == pytest.approx(1.0)
        assert items[0].p >= items[1].p  # Descending order

    def test_postprocess_tau_relaxation(self):
        """Test postprocess relaxes tau when needed."""
        parsed = [
            {"text": "a", "probability": 0.5},
            {"text": "b", "probability": 0.3},
            {"text": "c", "probability": 0.05},  # Below tau
        ]

        items, meta = postprocess_responses(
            parsed, tau=0.4, min_k_survivors=2, weight_mode="elicited", seed=42
        )

        assert len(items) >= 2
        assert meta["tau_relaxed"] is True
        assert meta["tau_final"] == 0.3  # Relaxed to include "b"

    def test_postprocess_weight_modes(self):
        """Test different weight normalization modes."""
        parsed = [
            {"text": "a", "probability": 0.5},
            {"text": "b", "probability": 0.3},
            {"text": "c", "probability": 0.2},
        ]

        # Elicited mode
        items_elicited, _ = postprocess_responses(
            parsed, tau=0.0, min_k_survivors=1, weight_mode="elicited", seed=42
        )
        assert sum(it.p for it in items_elicited) == pytest.approx(1.0)

        # Uniform mode
        items_uniform, _ = postprocess_responses(
            parsed, tau=0.0, min_k_survivors=1, weight_mode="uniform", seed=42
        )
        assert all(
            it.p == pytest.approx(1.0 / 3) for it in items_uniform
        )  # All equal

        # Softmax mode
        items_softmax, _ = postprocess_responses(
            parsed, tau=0.0, min_k_survivors=1, weight_mode="softmax", seed=42
        )
        assert sum(it.p for it in items_softmax) == pytest.approx(1.0)
