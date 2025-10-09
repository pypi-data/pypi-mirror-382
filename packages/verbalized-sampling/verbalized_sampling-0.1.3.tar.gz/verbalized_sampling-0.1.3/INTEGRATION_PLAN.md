# Integration Plan: New `verbalize()` API for verbalized-sampling

**Goal**: Add a clean, simple `verbalize()` interface on top of the existing research codebase without breaking existing experiments and scripts.

---

## Overview

The new API will live alongside the existing `methods`, `tasks`, `pipeline`, and `llms` modules. Users can choose:
- **New simple API**: `verbalize()` for quick one-liners (§0-10 from plan.md)
- **Existing research API**: `Pipeline`, `ExperimentConfig`, etc. for paper reproduction

---

## Phase 1: Core Data Structures (§2-4 from plan.md)

### 1.1 Create `verbalized_sampling/core/` module

**New files:**
```
verbalized_sampling/core/
├── __init__.py          # Export: Item, DiscreteDist
├── item.py              # Item dataclass
├── dist.py              # DiscreteDist class
└── transforms.py        # Filter/normalize/order logic
```

**Implementation:**

#### `core/item.py`
```python
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class Item:
    """A single candidate with normalized probability and metadata."""
    text: str                 # The candidate response
    p: float                  # Normalized probability [0,1]
    meta: Dict[str, Any]      # Provenance & repairs

    def __post_init__(self):
        assert 0 <= self.p <= 1, f"p must be in [0,1], got {self.p}"
```

**Meta fields:**
- `p_raw`: elicited weight (may be %, >1, malformed)
- `p_clipped`: coerced to [0,1] pre-normalize
- `repairs`: list[str] of repair operations
- `idx_orig`: original index
- `tau_relaxed`, `tau_final`: filtering info
- `provider_meta`: {tokens_in, tokens_out, latency_ms, model, mode_used}

#### `core/dist.py`
```python
from collections.abc import Sequence
from typing import Any, Callable, Dict, List, Optional
import random
from .item import Item

class DiscreteDist(Sequence[Item]):
    """A discrete distribution over text candidates."""

    def __init__(self, items: List[Item], trace: Dict[str, Any]):
        self._items = items  # Already sorted descending by p
        self._trace = trace
        self._validate()

    def _validate(self):
        """Ensure invariants: Σp=1.0±ε, descending order."""
        total = sum(it.p for it in self._items)
        assert abs(total - 1.0) < 1e-9, f"Probabilities must sum to 1, got {total}"
        # Check descending order
        for i in range(len(self._items) - 1):
            assert self._items[i].p >= self._items[i+1].p

    # Sequence protocol
    def __getitem__(self, i: int) -> Item:
        return self._items[i]

    def __len__(self) -> int:
        return len(self._items)

    @property
    def items(self) -> List[Item]:
        """All items (sorted descending by p)."""
        return self._items

    @property
    def p(self) -> List[float]:
        """List of probabilities."""
        return [it.p for it in self._items]

    # Selection
    def argmax(self) -> Item:
        """Return highest-probability item (deterministic)."""
        return self._items[0] if self._items else None

    def sample(self, seed: Optional[int] = None) -> Item:
        """Sample an item weighted by probability."""
        if not self._items:
            return None
        rng = random.Random(seed)
        return rng.choices(self._items, weights=self.p, k=1)[0]

    # Transforms (functional, return new DiscreteDist)
    def map(self, fn: Callable[[Item], str]) -> "DiscreteDist":
        """Map over item texts, preserve weights."""
        new_items = [
            Item(text=fn(it), p=it.p, meta=it.meta)
            for it in self._items
        ]
        return DiscreteDist(new_items, self._trace)

    def filter_items(self, pred: Callable[[Item], bool]) -> "DiscreteDist":
        """Filter items and renormalize."""
        filtered = [it for it in self._items if pred(it)]
        if not filtered:
            raise ValueError("Filter removed all items")
        # Renormalize
        total = sum(it.p for it in filtered)
        renormed = [
            Item(text=it.text, p=it.p/total, meta={**it.meta, "renormalized": True})
            for it in filtered
        ]
        return DiscreteDist(renormed, self._trace)

    def reweight(self, fn: Callable[[Item], float]) -> "DiscreteDist":
        """Recompute weights and renormalize."""
        new_weights = [fn(it) for it in self._items]
        total = sum(new_weights)
        if total <= 0:
            raise ValueError("All weights are zero or negative")
        renormed = [
            Item(text=it.text, p=w/total, meta={**it.meta, "reweighted": True})
            for it, w in zip(self._items, new_weights)
        ]
        # Re-sort descending
        renormed.sort(key=lambda it: it.p, reverse=True)
        return DiscreteDist(renormed, self._trace)

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "items": [
                {"text": it.text, "p": it.p, "meta": it.meta}
                for it in self._items
            ],
            "trace": self._trace,
        }

    def to_markdown(self, max_items: Optional[int] = None) -> str:
        """Pretty markdown table."""
        lines = ["# verbalized-sampling"]
        t = self._trace
        header = f"k={len(self._items)}  τ={t.get('tau_final', 'N/A')} (relaxed: {t.get('tau_relaxed', False)})  Σp={sum(self.p):.3f}  model={t.get('model', 'unknown')}"
        lines.append(header)
        lines.append("")

        items_to_show = self._items[:max_items] if max_items else self._items
        for i, it in enumerate(items_to_show, 1):
            repairs_str = str(it.meta.get("repairs", []))
            lines.append(f'{i}. {it.p:.2f}  "{it.text}"  {repairs_str}')

        if max_items and len(self._items) > max_items:
            lines.append(f"... ({len(self._items) - max_items} more)")

        return "\n".join(lines)

    @property
    def trace(self) -> Dict[str, Any]:
        """Metadata: model, tokens, repairs, etc."""
        return self._trace
```

#### `core/transforms.py`
```python
"""Core postprocessing: filter → normalize → order."""
from typing import List, Dict, Any, Literal
import math
from .item import Item

def postprocess(
    raw_items: List[Dict[str, Any]],  # [{"text": ..., "weight": ...}, ...]
    tau: float,
    min_k_survivors: int,
    weight_mode: Literal["elicited", "softmax", "uniform"],
    seed: Optional[int],
) -> tuple[List[Item], Dict[str, Any]]:
    """
    Apply filter → clip/repair → normalize → sort.

    Returns: (items, metadata)
    """
    # 1) Parse and repair raw weights
    parsed = []
    for idx, raw in enumerate(raw_items):
        text = raw.get("text", "")
        weight_raw = raw.get("weight", raw.get("prob", raw.get("probability", 0.0)))

        # Repair weight
        weight_clipped, repairs = repair_weight(weight_raw)

        parsed.append({
            "text": text,
            "p_raw": weight_raw,
            "p_clipped": weight_clipped,
            "repairs": repairs,
            "idx_orig": idx,
        })

    # 2) Filter by tau
    survivors = [it for it in parsed if it["p_raw"] >= tau]
    tau_relaxed = False
    tau_final = tau

    if len(survivors) < min_k_survivors and parsed:
        # Relax tau to keep exactly min_k_survivors
        sorted_by_raw = sorted(parsed, key=lambda x: x["p_raw"], reverse=True)
        tau_final = sorted_by_raw[min_k_survivors - 1]["p_raw"]
        survivors = [it for it in parsed if it["p_raw"] >= tau_final]
        tau_relaxed = True

    if not survivors:
        survivors = parsed  # Keep all if filter too aggressive

    # 3) Normalize weights
    if weight_mode == "uniform":
        for it in survivors:
            it["p_norm"] = 1.0 / len(survivors)
    elif weight_mode == "softmax":
        exps = [math.exp(it["p_clipped"]) for it in survivors]
        Z = sum(exps) or 1.0
        for it, e in zip(survivors, exps):
            it["p_norm"] = e / Z
    else:  # "elicited"
        Z = sum(it["p_clipped"] for it in survivors)
        if Z <= 1e-12:
            for it in survivors:
                it["p_norm"] = 1.0 / len(survivors)
        else:
            for it in survivors:
                it["p_norm"] = it["p_clipped"] / Z

    # 4) Stable sort: descending by p_norm, then idx_orig, then text hash
    survivors.sort(key=lambda x: (-x["p_norm"], x["idx_orig"], hash(x["text"])))

    # 5) Create Item objects
    items = [
        Item(
            text=it["text"],
            p=it["p_norm"],
            meta={
                "p_raw": it["p_raw"],
                "p_clipped": it["p_clipped"],
                "repairs": it["repairs"],
                "idx_orig": it["idx_orig"],
            }
        )
        for it in survivors
    ]

    metadata = {
        "tau_relaxed": tau_relaxed,
        "tau_final": tau_final,
        "seed": seed,
    }

    return items, metadata


def repair_weight(raw: Any) -> tuple[float, List[str]]:
    """
    Repair a raw weight value to [0, 1].

    Returns: (clipped_value, repairs_applied)
    """
    repairs = []

    # Convert to float
    if isinstance(raw, str):
        raw = raw.strip()
        if raw.endswith("%"):
            repairs.append("percent_to_unit")
            raw = float(raw[:-1]) / 100.0
        else:
            raw = float(raw)

    value = float(raw)

    # Clip negatives
    if value < 0:
        repairs.append("negative_to_zero")
        value = 0.0

    # Clip > 1
    if value > 1.0:
        repairs.append("clipped>1")
        value = 1.0

    return value, repairs
```

---

## Phase 2: Provider Abstraction (§5-6 from plan.md)

### 2.1 Create `verbalized_sampling/providers/` module

**Leverage existing `llms/` module but create a simpler adapter layer:**

```
verbalized_sampling/providers/
├── __init__.py          # Export: get_provider, Provider
├── base.py              # Abstract Provider interface
├── openai_provider.py   # Wrap existing OpenAILLM
├── anthropic_provider.py # Wrap existing LiteLLM for Anthropic
└── auto.py              # Auto-detect provider
```

#### `providers/base.py`
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class Provider(ABC):
    """Abstract interface for LLM providers."""

    supports_json_schema: bool = False
    supports_tools: bool = False

    @abstractmethod
    def generate_json(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float,
        seed: Optional[int],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate structured JSON output.

        Returns: (parsed_json, metadata)
        metadata includes: {tokens_in, tokens_out, latency_ms, mode_used}
        """
        pass
```

#### `providers/openai_provider.py`
```python
from typing import Any, Dict, List, Optional
import time
from verbalized_sampling.llms.openai import OpenAILLM
from .base import Provider

class OpenAIProvider(Provider):
    supports_json_schema = True
    supports_tools = False

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self._llm = None  # Lazy init

    def generate_json(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float,
        seed: Optional[int],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        # Wrap existing OpenAILLM
        if self._llm is None:
            self._llm = OpenAILLM(
                model_name=self.model,
                config={"temperature": temperature, "seed": seed},
                num_workers=1,
                strict_json=True,
            )

        start = time.time()
        # Use existing _chat_with_format method
        response = self._llm._chat_with_format(messages, schema)
        latency_ms = (time.time() - start) * 1000

        # Parse JSON from response
        import json
        parsed = json.loads(response)

        metadata = {
            "tokens_in": None,  # Not easily accessible
            "tokens_out": None,
            "latency_ms": latency_ms,
            "mode_used": "json_schema",
            "model": self.model,
        }

        return parsed, metadata
```

#### `providers/auto.py`
```python
import os
from typing import Optional
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

def get_provider(provider: str = "auto", model: Optional[str] = None):
    """Auto-select provider based on API keys and model name."""

    if provider == "openai" or (provider == "auto" and os.getenv("OPENAI_API_KEY")):
        return OpenAIProvider(model or "gpt-4o")

    elif provider == "anthropic" or (provider == "auto" and os.getenv("ANTHROPIC_API_KEY")):
        return AnthropicProvider(model or "claude-3-5-sonnet-20241022")

    elif provider == "auto":
        raise ValueError(
            "No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY, "
            "or explicitly specify provider='openai' or provider='anthropic'"
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")
```

---

## Phase 3: Main `verbalize()` API (§2.1 from plan.md)

### 3.1 Create `verbalized_sampling/api.py`

```python
"""Main verbalize() function."""
from typing import Any, Dict, List, Literal, Optional, Sequence
import time

from .core import Item, DiscreteDist
from .core.transforms import postprocess
from .providers.auto import get_provider
from .parsing import extract_and_repair_json


def verbalize(
    prompt: Optional[str] = None,
    *,
    messages: Optional[Sequence[Dict[str, Any]]] = None,

    # Core knobs
    k: int = 5,
    tau: float = 0.12,
    temperature: float = 0.9,

    # Provider/model
    provider: Literal["auto", "openai", "anthropic"] = "auto",
    model: Optional[str] = None,
    provider_kwargs: Optional[Dict[str, Any]] = None,

    # Robustness
    json_repair: bool = True,
    min_k_survivors: int = 3,
    retries: int = 2,

    # Weight handling
    weight_mode: Literal["elicited", "softmax", "uniform"] = "elicited",

    # Determinism
    seed: Optional[int] = None,

    # Introspection
    with_meta: bool = False,
) -> DiscreteDist:
    """
    Elicit k weighted candidates → DiscreteDist (filtered, normalized, ordered).

    Args:
        prompt: User prompt string (mutually exclusive with messages)
        messages: Chat messages format (mutually exclusive with prompt)
        k: Number of candidates to generate
        tau: Probability threshold for filtering
        temperature: LLM sampling temperature
        provider: "auto" | "openai" | "anthropic"
        model: Model name (auto-selected if None)
        json_repair: Enable robust JSON parsing
        min_k_survivors: Minimum items after filtering (relaxes tau if needed)
        retries: Number of retry attempts on failure
        weight_mode: "elicited" | "softmax" | "uniform"
        seed: Random seed for determinism

    Returns:
        DiscreteDist with filtered, normalized, sorted items
    """
    # Input validation
    if (prompt is None) == (messages is None):
        raise ValueError("Exactly one of 'prompt' or 'messages' must be provided")

    if prompt is not None:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = list(messages)

    # Get provider
    prov = get_provider(provider, model)

    # Build VS prompt
    vs_prompt = _build_vs_prompt(k)
    full_messages = [
        {"role": "system", "content": vs_prompt},
        *messages,
    ]

    # Schema for JSON validation
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "weight": {"type": "number"},
            },
            "required": ["text", "weight"],
        },
        "minItems": k,
        "maxItems": k,
    }

    # Generate with retries
    for attempt in range(retries + 1):
        try:
            raw_json, provider_meta = prov.generate_json(
                full_messages, schema, temperature, seed
            )

            # Validate structure
            if isinstance(raw_json, dict) and "responses" in raw_json:
                raw_items = raw_json["responses"]
            elif isinstance(raw_json, list):
                raw_items = raw_json
            else:
                raise ValueError(f"Unexpected JSON structure: {type(raw_json)}")

            if len(raw_items) != k:
                raise ValueError(f"Expected {k} items, got {len(raw_items)}")

            break  # Success

        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"Failed after {retries} retries: {e}")
            # Simplify prompt for retry
            full_messages = [
                {"role": "system", "content": _build_vs_prompt(k, simplified=True)},
                *messages,
            ]

    # Postprocess: filter → normalize → order
    items, transform_meta = postprocess(
        raw_items, tau, min_k_survivors, weight_mode, seed
    )

    # Build trace
    trace = {
        **provider_meta,
        **transform_meta,
        "k": k,
        "tau": tau,
        "weight_mode": weight_mode,
    }

    # Add provider_meta to each item
    for item in items:
        item.meta["provider_meta"] = provider_meta

    return DiscreteDist(items, trace)


def _build_vs_prompt(k: int, simplified: bool = False) -> str:
    """Build the VS-Standard prompt."""
    if simplified:
        return f"""Generate exactly {k} responses as JSON array.
Each item: {{"text": "...", "weight": 0.0-1.0}}
Output JSON only."""

    return f"""Generate exactly {k} responses to the user query.

Return as JSON array: [
  {{"text": "response 1", "weight": 0.0-1.0}},
  {{"text": "response 2", "weight": 0.0-1.0}},
  ...
]

- `weight` is the probability/likelihood of each response in [0, 1]
- Sample randomly from the full distribution
- Output ONLY the JSON array, no explanations"""
```

### 3.2 Create `verbalized_sampling/parsing.py`

```python
"""JSON extraction and repair utilities."""
import json
import re
from typing import Any, Dict, List, Tuple


def extract_and_repair_json(text: str) -> Tuple[Any, List[str]]:
    """
    Extract JSON from text, with repairs.

    Returns: (parsed_json, repairs_applied)
    """
    repairs = []

    # Try direct parse first
    try:
        return json.loads(text), repairs
    except json.JSONDecodeError:
        pass

    # Extract from fenced block
    match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
    if match:
        repairs.append("extracted_from_fence")
        text = match.group(1)
    else:
        # Find first balanced JSON
        text = _extract_balanced_json(text)
        if text:
            repairs.append("extracted_balanced")

    # Repair common issues
    text = _repair_json_text(text, repairs)

    # Parse
    try:
        return json.loads(text), repairs
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON after repairs: {e}")


def _extract_balanced_json(text: str) -> str:
    """Find first balanced {...} or [...]."""
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue

        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == start_char:
                depth += 1
            elif char == end_char:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
    return ""


def _repair_json_text(text: str, repairs: List[str]) -> str:
    """Apply common JSON repairs."""
    # Remove trailing commas
    if ',]' in text or ',}' in text:
        repairs.append("removed_trailing_comma")
        text = re.sub(r',\s*([}\]])', r'\1', text)

    # Fix single quotes (risky, only if no double quotes in values)
    if "'" in text and text.count("'") > text.count('"'):
        repairs.append("single_to_double_quotes")
        text = text.replace("'", '"')

    return text
```

---

## Phase 4: Update `__init__.py` and Integration

### 4.1 Update `verbalized_sampling/__init__.py`

```python
# New simple API (v1)
from .api import verbalize
from .core import Item, DiscreteDist

# Optional helper
from .api import select

# Existing research API (unchanged)
from .cli import app as cli_app
from .methods import Method, PromptFactory
from .tasks import Task
from .pipeline import Pipeline, ExperimentConfig

__all__ = [
    # New simple API
    "verbalize",
    "Item",
    "DiscreteDist",
    "select",

    # Existing research API
    "cli_app",
    "Method",
    "PromptFactory",
    "Task",
    "Pipeline",
    "ExperimentConfig",
]

__version__ = "0.2.0"  # Bump minor version
```

### 4.2 Optional: Add helper function

Add to `api.py`:
```python
def select(
    dist: DiscreteDist,
    strategy: Literal["argmax", "sample"] = "sample",
    seed: Optional[int] = None,
) -> Item:
    """Neutral helper for selecting from a distribution."""
    if strategy == "argmax":
        return dist.argmax()
    else:
        return dist.sample(seed=seed)
```

---

## Phase 5: Examples and Documentation

### 5.1 Create `examples/simple_api.py`

```python
"""Simple API examples matching plan.md §0."""
from verbalized_sampling import verbalize

# Example 1: Basic usage
dist = verbalize(
    "Write an opening line for a mystery novel",
    k=5,
    tau=0.12,
    temperature=0.9,
    seed=42,
)

print(dist.to_markdown())

best = dist.argmax()
choice = dist.sample(seed=7)

print(f"\nBest: {best.text}")
print(f"Sampled: {choice.text}")

# Example 2: Transform
short_dist = dist.filter_items(lambda it: len(it.text) < 50)
print(f"\nFiltered to {len(short_dist)} short items")

# Example 3: Inspect trace
print(f"\nModel: {dist.trace['model']}")
print(f"Tokens: {dist.trace.get('tokens_in', 'N/A')}")
print(f"Latency: {dist.trace['latency_ms']:.0f}ms")
```

### 5.2 Update main README.md

Add a new "Quick Start" section at the top:

```markdown
## Quick Start (New in v0.2!)

Install:
```bash
pip install verbalized-sampling
```

Get started in one line:
```python
from verbalized_sampling import verbalize

# Ask for a distribution, not a sample
dist = verbalize(
    "Write five opening lines for a mystery novel",
    k=5, tau=0.12, temperature=0.9
)

# Inspect
print(dist.to_markdown())

# Select
best = dist.argmax()        # deterministic top
choice = dist.sample(seed=7) # seeded sample

print(best.text)
```

For research/paper reproduction, see [EXPERIMENTS.md](scripts/EXPERIMENTS.md).
```

---

## Phase 6: Testing

### 6.1 Create `tests/test_simple_api.py`

```python
"""Tests for the new simple API."""
import pytest
from verbalized_sampling import verbalize, Item, DiscreteDist


def test_verbalize_basic():
    """Test basic verbalize() call."""
    dist = verbalize(
        "Say hello",
        k=3,
        provider="openai",  # Requires API key
        seed=42,
    )

    assert len(dist) == 3
    assert sum(dist.p) == pytest.approx(1.0)
    assert dist.argmax() is not None


def test_discrete_dist_invariants():
    """Test DiscreteDist invariants."""
    items = [
        Item(text="a", p=0.5, meta={}),
        Item(text="b", p=0.3, meta={}),
        Item(text="c", p=0.2, meta={}),
    ]
    dist = DiscreteDist(items, trace={})

    # Probabilities sum to 1
    assert sum(dist.p) == pytest.approx(1.0)

    # Descending order
    assert dist.p == sorted(dist.p, reverse=True)

    # Argmax is first
    assert dist.argmax() == items[0]


def test_discrete_dist_transforms():
    """Test functional transforms."""
    items = [
        Item(text="hello", p=0.6, meta={}),
        Item(text="hi", p=0.4, meta={}),
    ]
    dist = DiscreteDist(items, trace={})

    # Map
    upper_dist = dist.map(str.upper)
    assert upper_dist[0].text == "HELLO"
    assert upper_dist[0].p == 0.6  # weights preserved

    # Filter
    long_dist = dist.filter_items(lambda it: len(it.text) > 3)
    assert len(long_dist) == 1
    assert long_dist[0].text == "hello"
    assert long_dist[0].p == pytest.approx(1.0)  # renormalized


def test_postprocess_tau_relaxation():
    """Test tau relaxation when too few survivors."""
    from verbalized_sampling.core.transforms import postprocess

    raw_items = [
        {"text": "a", "weight": 0.5},
        {"text": "b", "weight": 0.3},
        {"text": "c", "weight": 0.2},
    ]

    items, meta = postprocess(
        raw_items,
        tau=0.4,  # Would only keep 1 item
        min_k_survivors=2,
        weight_mode="elicited",
        seed=None,
    )

    assert len(items) >= 2
    assert meta["tau_relaxed"] == True
    assert meta["tau_final"] == 0.3  # Relaxed to keep 2 items
```

---

## Migration Path & Backwards Compatibility

### Coexistence Strategy

1. **No breaking changes**: Existing code continues to work
2. **New imports**: Users opt-in to new API via `from verbalized_sampling import verbalize`
3. **Shared infrastructure**: New API reuses `llms/`, `methods/` modules where possible
4. **Version bump**: 0.1.x → 0.2.0 (minor version)

### File Organization

```
verbalized_sampling/
├── __init__.py              # Exports both old & new APIs
├── api.py                   # NEW: verbalize() function
├── core/                    # NEW: Item, DiscreteDist, transforms
│   ├── __init__.py
│   ├── item.py
│   ├── dist.py
│   └── transforms.py
├── providers/               # NEW: Provider abstraction
│   ├── __init__.py
│   ├── base.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── auto.py
├── parsing.py               # NEW: JSON extraction/repair
├── methods/                 # EXISTING: Keep for research API
├── tasks/                   # EXISTING: Keep for research API
├── llms/                    # EXISTING: Reused by providers
├── pipeline.py              # EXISTING: Keep for research API
└── cli.py                   # EXISTING: Keep unchanged
```

---

## Implementation Checklist

### Phase 1: Core (Week 1)
- [ ] Create `core/` module structure
- [ ] Implement `Item` dataclass
- [ ] Implement `DiscreteDist` class with all methods
- [ ] Implement `transforms.py` (postprocess, repair_weight)
- [ ] Unit tests for core

### Phase 2: Providers (Week 1-2)
- [ ] Create `providers/` module structure
- [ ] Implement `Provider` base class
- [ ] Implement `OpenAIProvider` (wrap existing `OpenAILLM`)
- [ ] Implement `AnthropicProvider` (wrap existing `LiteLLM`)
- [ ] Implement `get_provider()` auto-detection
- [ ] Unit tests for providers

### Phase 3: Main API (Week 2)
- [ ] Implement `verbalize()` function
- [ ] Implement VS prompt generation
- [ ] Implement retry logic
- [ ] Implement `select()` helper
- [ ] Integration tests

### Phase 4: Parsing & Robustness (Week 2)
- [ ] Implement `parsing.py` (JSON extraction/repair)
- [ ] Add repair tracking to metadata
- [ ] Tests for edge cases

### Phase 5: Documentation & Examples (Week 3)
- [ ] Update main README.md with Quick Start
- [ ] Create `examples/simple_api.py`
- [ ] Create `examples/advanced_transforms.py`
- [ ] Add docstrings to all public APIs

### Phase 6: Polish & Release (Week 3)
- [ ] Version bump to 0.2.0
- [ ] Update `__init__.py` exports
- [ ] Run full test suite
- [ ] Update PyPI package
- [ ] Blog post / announcement

---

## Success Criteria

1. ✅ **One-liner works**: `verbalize("prompt", k=5)` returns valid `DiscreteDist`
2. ✅ **Invariants hold**: Σp=1.0, descending order, deterministic
3. ✅ **No breaking changes**: Existing scripts/experiments run unchanged
4. ✅ **Good UX**: `dist.to_markdown()` is readable and useful
5. ✅ **Documented**: README has clear Quick Start section
6. ✅ **Tested**: >80% coverage on new code

---

## Open Questions

1. **Should we support batch mode?** `verbalize([prompt1, prompt2, ...])` returns `List[DiscreteDist]`
2. **Streaming support?** For very large k, stream items as they're generated
3. **Caching?** Add optional disk cache for (prompt, k, model) → DiscreteDist
4. **CLI integration?** Add `verbalize` subcommand to existing CLI

---

## Next Steps

Please review this plan and let me know:
1. Which phase should we start with?
2. Any changes to the design?
3. Should we implement in this repo or create a separate `verbalized-sampling-v2` branch first?

I'm ready to start coding once you approve the plan!
