# Integration Plan V2: Smart Integration with Existing Codebase

**Goal**: Add simple `verbalize()` API by **smartly reusing** existing `llms/`, `methods/`, and `parser` infrastructure.

---

## Key Insight: Reuse, Don't Rebuild!

Looking at the existing code, we already have:
- ✅ **`llms/`** - Excellent provider abstractions (`BaseLLM`, `OpenAILLM`, `LiteLLM`, etc.)
- ✅ **`methods/parser.py`** - JSON extraction, repair, and parsing logic
- ✅ **`methods/schema.py`** - Pydantic schemas for structured outputs
- ✅ **`methods/factory.py`** - Method enum and prompt templates

**New approach**: Build the simple API as a **thin wrapper** over existing components.

---

## Revised Architecture

```
User Code
    ↓
verbalize()  ← NEW (thin wrapper in api.py)
    ↓
┌─────────────────────────────────────┐
│ Existing Infrastructure (reuse!)   │
│                                     │
│  llms.get_model()                  │ ← Reuse provider selection
│  methods.ResponseParser            │ ← Reuse JSON parsing/repair
│  methods.schema                     │ ← Reuse Pydantic schemas
│  core.transforms                    │ ← NEW (filter/normalize/order)
└─────────────────────────────────────┘
    ↓
DiscreteDist[Item]  ← NEW (simple data structures)
```

---

## Minimal New Code Required

### New Files (Only 3!)

```
verbalized_sampling/
├── api.py                   # NEW: verbalize() function (100 lines)
├── core/                    # NEW: Data structures
│   ├── __init__.py
│   ├── item.py             # NEW: Item dataclass (30 lines)
│   ├── dist.py             # NEW: DiscreteDist class (150 lines)
│   └── transforms.py       # NEW: filter/normalize/order (100 lines)
└── [everything else unchanged]
```

### Modified Files (Only 2!)

```
verbalized_sampling/
├── __init__.py              # MODIFIED: Add new exports
└── methods/
    └── parser.py            # MODIFIED: Add helper for weight extraction
```

**Total new code**: ~400 lines
**Total modified code**: ~20 lines

---

## Phase-by-Phase Implementation

### Phase 1: Core Data Structures (Week 1, Days 1-2)

#### 1.1 Create `core/item.py`

```python
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(frozen=True)
class Item:
    """A single candidate with normalized probability and metadata."""
    text: str
    p: float  # Normalized probability [0,1]
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, 'meta', dict(self.meta))  # Copy to allow frozen
        if not (0 <= self.p <= 1 + 1e-9):  # Small tolerance
            raise ValueError(f"p must be in [0,1], got {self.p}")
```

**Meta fields** (populated by transforms):
- `p_raw`: original elicited weight
- `p_clipped`: after repair/clipping
- `repairs`: list of repair operations
- `idx_orig`: original index
- `provider_meta`: from existing LLM response

#### 1.2 Create `core/dist.py`

**Smart reuse**: The `DiscreteDist` class just holds `Item` objects and provides ergonomic methods.

```python
from collections.abc import Sequence
from typing import Any, Callable, Dict, List, Optional
import random

from .item import Item


class DiscreteDist(Sequence[Item]):
    """A discrete distribution over text candidates."""

    def __init__(self, items: List[Item], trace: Dict[str, Any]):
        """Items must already be sorted descending by p."""
        self._items = list(items)  # Defensive copy
        self._trace = dict(trace)
        self._validate()

    def _validate(self):
        """Ensure Σp=1.0±ε and descending order."""
        total = sum(it.p for it in self._items)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Probabilities must sum to 1, got {total:.6f}")

        # Check descending order
        for i in range(len(self._items) - 1):
            if self._items[i].p < self._items[i+1].p - 1e-9:
                raise ValueError("Items must be sorted descending by p")

    # Sequence protocol
    def __getitem__(self, i: int) -> Item:
        return self._items[i]

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"DiscreteDist(k={len(self)}, Σp={sum(self.p):.3f})"

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
        if not self._items:
            raise ValueError("Cannot argmax on empty distribution")
        return self._items[0]

    def sample(self, seed: Optional[int] = None) -> Item:
        """Sample an item weighted by probability."""
        if not self._items:
            raise ValueError("Cannot sample from empty distribution")

        rng = random.Random(seed) if seed is not None else random
        return rng.choices(self._items, weights=self.p, k=1)[0]

    # Functional transforms
    def map(self, fn: Callable[[Item], str]) -> "DiscreteDist":
        """Map over item texts, preserve probabilities."""
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
            Item(
                text=it.text,
                p=it.p / total,
                meta={**it.meta, "renormalized": True}
            )
            for it in filtered
        ]
        return DiscreteDist(renormed, self._trace)

    def reweight(self, fn: Callable[[Item], float]) -> "DiscreteDist":
        """Recompute weights and renormalize."""
        new_weights = [fn(it) for it in self._items]
        total = sum(new_weights)
        if total <= 1e-12:
            raise ValueError("All new weights are zero or negative")

        renormed = [
            Item(
                text=it.text,
                p=w / total,
                meta={**it.meta, "reweighted": True}
            )
            for it, w in zip(self._items, new_weights)
        ]

        # Re-sort descending
        renormed.sort(key=lambda it: -it.p)
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiscreteDist":
        """Reconstruct from dict."""
        items = [
            Item(text=it["text"], p=it["p"], meta=it["meta"])
            for it in data["items"]
        ]
        return cls(items, data["trace"])

    def to_markdown(self, max_items: Optional[int] = None) -> str:
        """Pretty markdown table."""
        lines = ["# verbalized-sampling"]

        t = self._trace
        header_parts = [
            f"k={len(self)}",
            f"τ={t.get('tau_final', 'N/A')}",
            f"Σp={sum(self.p):.3f}",
            f"model={t.get('model', 'unknown')}",
        ]
        if t.get('tau_relaxed'):
            header_parts.insert(1, f"τ_relaxed=True")

        lines.append("  ".join(header_parts))
        lines.append("")

        items_to_show = self._items[:max_items] if max_items else self._items
        for i, it in enumerate(items_to_show, 1):
            repairs_str = str(it.meta.get("repairs", []))
            text_preview = it.text[:70] + "..." if len(it.text) > 70 else it.text
            lines.append(f'{i}. {it.p:.3f}  "{text_preview}"  {repairs_str}')

        if max_items and len(self._items) > max_items:
            lines.append(f"... ({len(self._items) - max_items} more)")

        return "\n".join(lines)

    @property
    def trace(self) -> Dict[str, Any]:
        """Metadata: model, tokens, repairs, etc."""
        return self._trace
```

#### 1.3 Create `core/transforms.py`

**Smart reuse**: Use existing `ResponseParser` for weight extraction, then add filter/normalize logic.

```python
"""Core postprocessing: filter → normalize → order."""
from typing import Any, Dict, List, Literal, Optional, Tuple
import math

from .item import Item


def postprocess(
    parsed_responses: List[Dict[str, Any]],  # From existing ResponseParser
    tau: float,
    min_k_survivors: int,
    weight_mode: Literal["elicited", "softmax", "uniform"],
    seed: Optional[int],
) -> Tuple[List[Item], Dict[str, Any]]:
    """
    Apply filter → clip/repair → normalize → sort.

    Args:
        parsed_responses: Output from methods.ResponseParser.parse_structure_with_probability()
                         Format: [{"text": ..., "probability": ...}, ...]

    Returns:
        (items, metadata)
    """
    # 1) Extract and repair weights
    parsed = []
    for idx, resp in enumerate(parsed_responses):
        text = resp.get("text", "")
        weight_raw = resp.get("probability", resp.get("weight", 0.0))

        # Repair weight to [0, 1]
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
        if min_k_survivors <= len(sorted_by_raw):
            tau_final = sorted_by_raw[min_k_survivors - 1]["p_raw"]
            survivors = [it for it in parsed if it["p_raw"] >= tau_final]
            tau_relaxed = True

    if not survivors:
        survivors = parsed  # Keep all if filter too aggressive

    # 3) Normalize weights
    survivors = _normalize_weights(survivors, weight_mode)

    # 4) Stable sort: descending by p_norm, then idx_orig, then text hash
    survivors.sort(
        key=lambda x: (-x["p_norm"], x["idx_orig"], hash(x["text"]))
    )

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
        "weight_mode": weight_mode,
    }

    return items, metadata


def _normalize_weights(
    items: List[Dict[str, Any]],
    mode: Literal["elicited", "softmax", "uniform"],
) -> List[Dict[str, Any]]:
    """Normalize weights according to mode."""
    if mode == "uniform":
        for it in items:
            it["p_norm"] = 1.0 / len(items)

    elif mode == "softmax":
        exps = [math.exp(it["p_clipped"]) for it in items]
        Z = sum(exps) or 1.0
        for it, e in zip(items, exps):
            it["p_norm"] = e / Z

    else:  # "elicited"
        Z = sum(it["p_clipped"] for it in items)
        if Z <= 1e-12:
            # Fallback to uniform if all weights are zero
            for it in items:
                it["p_norm"] = 1.0 / len(items)
                it["repairs"].append("zero_sum_uniform_fallback")
        else:
            for it in items:
                it["p_norm"] = it["p_clipped"] / Z

    return items


def repair_weight(raw: Any) -> Tuple[float, List[str]]:
    """
    Repair a raw weight value to [0, 1].

    Returns: (clipped_value, repairs_applied)
    """
    repairs = []

    # Handle string inputs
    if isinstance(raw, str):
        raw = raw.strip()

        # Percentage to unit
        if raw.endswith("%"):
            repairs.append("percent_to_unit")
            raw = float(raw[:-1]) / 100.0
        else:
            try:
                raw = float(raw)
            except ValueError:
                repairs.append("invalid_to_zero")
                return 0.0, repairs

    try:
        value = float(raw)
    except (ValueError, TypeError):
        repairs.append("invalid_to_zero")
        return 0.0, repairs

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

### Phase 2: Main API (Week 1, Days 3-4)

#### 2.1 Create `api.py`

**Smart reuse**: Leverage existing `llms.get_model()`, `methods.ResponseParser`, and `methods.schema`.

```python
"""Main verbalize() API - thin wrapper over existing infrastructure."""
from typing import Any, Dict, List, Literal, Optional, Sequence
import time

from .core import Item, DiscreteDist
from .core.transforms import postprocess
from .llms import get_model
from .methods import Method, ResponseParser
from .methods.schema import _create_structured_response_with_field_schema


def verbalize(
    prompt: Optional[str] = None,
    *,
    messages: Optional[Sequence[Dict[str, Any]]] = None,

    # Core knobs
    k: int = 5,
    tau: float = 0.12,
    temperature: float = 0.9,

    # Provider/model
    provider: Literal["auto", "openai", "anthropic", "google"] = "auto",
    model: Optional[str] = None,

    # Robustness
    min_k_survivors: int = 3,
    retries: int = 2,

    # Weight handling
    weight_mode: Literal["elicited", "softmax", "uniform"] = "elicited",
    probability_definition: str = "explicit",

    # Determinism
    seed: Optional[int] = None,

    # Advanced
    use_strict_json: bool = True,
    num_workers: int = 1,
    **provider_kwargs,
) -> DiscreteDist:
    """
    Elicit k weighted candidates → DiscreteDist (filtered, normalized, ordered).

    **REUSES EXISTING INFRASTRUCTURE**:
    - llms.get_model() for provider selection
    - methods.ResponseParser for JSON parsing
    - methods.schema for Pydantic schemas
    """
    # Input validation
    if (prompt is None) == (messages is None):
        raise ValueError("Exactly one of 'prompt' or 'messages' must be provided")

    if prompt is not None:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = list(messages)

    # Auto-select model if not provided
    if model is None:
        model = _auto_select_model(provider)

    # Build config
    config = {
        "temperature": temperature,
        "seed": seed,
        "max_tokens": provider_kwargs.get("max_tokens", 8192),
        **{k: v for k, v in provider_kwargs.items() if k != "max_tokens"},
    }

    # Get LLM instance (REUSE existing infrastructure!)
    llm = get_model(
        model_name=model,
        method=Method.VS_STANDARD,
        config=config,
        num_workers=num_workers,
        strict_json=use_strict_json,
    )

    # Build VS prompt using existing prompt logic
    vs_prompt = _build_vs_prompt(k, probability_definition)
    full_messages = [
        {"role": "system", "content": vs_prompt},
        *messages,
    ]

    # Get schema (REUSE existing schema builder!)
    schema = _create_structured_response_with_field_schema(probability_definition)

    # Generate with retries
    for attempt in range(retries + 1):
        try:
            start_time = time.time()

            # Call LLM (REUSE existing LLM interface!)
            if use_strict_json:
                responses = llm._chat_with_format(full_messages, schema)
            else:
                response_str = llm._chat(full_messages)
                # Parse (REUSE existing parser!)
                responses = ResponseParser.parse_structure_with_probability(response_str)

            latency_ms = (time.time() - start_time) * 1000

            # Validate we got k items
            if len(responses) < k and attempt < retries:
                raise ValueError(f"Expected {k} items, got {len(responses)}")

            break  # Success

        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"Failed after {retries} retries: {e}")
            # Simplify prompt for retry
            vs_prompt = _build_vs_prompt(k, probability_definition, simplified=True)
            full_messages[0]["content"] = vs_prompt

    # Postprocess (NEW: filter/normalize/order)
    items, transform_meta = postprocess(
        responses,
        tau=tau,
        min_k_survivors=min_k_survivors,
        weight_mode=weight_mode,
        seed=seed,
    )

    # Build trace
    trace = {
        "model": llm.model_name,
        "provider": _infer_provider(model),
        "latency_ms": latency_ms,
        "k": k,
        "tau": tau,
        "temperature": temperature,
        "seed": seed,
        "use_strict_json": use_strict_json,
        **transform_meta,
    }

    return DiscreteDist(items, trace)


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


def _auto_select_model(provider: str) -> str:
    """Auto-select default model for provider."""
    import os

    if provider == "openai" or (provider == "auto" and os.getenv("OPENAI_API_KEY")):
        return "gpt-4o"
    elif provider == "anthropic" or (provider == "auto" and os.getenv("ANTHROPIC_API_KEY")):
        return "claude-3-5-sonnet-20241022"
    elif provider == "google" or (provider == "auto" and os.getenv("GOOGLE_API_KEY")):
        return "gemini-2.0-flash-exp"
    elif provider == "auto":
        raise ValueError(
            "No API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
        )
    else:
        return "gpt-4o"  # Default fallback


def _infer_provider(model: str) -> str:
    """Infer provider from model name."""
    if "gpt" in model.lower() or "o3" in model.lower():
        return "openai"
    elif "claude" in model.lower():
        return "anthropic"
    elif "gemini" in model.lower():
        return "google"
    else:
        return "unknown"


def _build_vs_prompt(k: int, probability_definition: str, simplified: bool = False) -> str:
    """Build VS-Standard prompt."""
    # Get field info
    from .methods.schema import _get_probability_field_info
    field_name, field_desc = _get_probability_field_info(probability_definition)

    if simplified:
        return f"""Generate exactly {k} responses as JSON.
Each item: {{"text": "...", "{field_name}": 0.0-1.0}}
Output JSON only."""

    return f"""Generate exactly {k} responses to the user query.

Return as JSON: {{
  "responses": [
    {{"text": "response 1", "{field_name}": 0.0-1.0}},
    {{"text": "response 2", "{field_name}": 0.0-1.0}},
    ...
  ]
}}

- `{field_name}`: {field_desc}
- Sample randomly from the full distribution
- Output ONLY the JSON object, no explanations"""
```

---

### Phase 3: Update Exports (Week 1, Day 5)

#### 3.1 Update `verbalized_sampling/__init__.py`

```python
# Copyright 2025 CHATS-Lab. All Rights Reserved.
# ... (keep existing copyright)

# NEW: Simple API (v0.2)
from .api import verbalize, select
from .core import Item, DiscreteDist

# EXISTING: Research API (unchanged)
from .cli import app as cli_app
from .methods import Method, PromptFactory
from .tasks import Task
from .pipeline import Pipeline, ExperimentConfig

__all__ = [
    # Simple API (NEW)
    "verbalize",
    "select",
    "Item",
    "DiscreteDist",

    # Research API (EXISTING)
    "cli_app",
    "Method",
    "PromptFactory",
    "Task",
    "Pipeline",
    "ExperimentConfig",
]

__version__ = "0.2.0"
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_core.py
def test_item_validation():
    """Test Item probability validation."""
    Item("hello", p=0.5, meta={})  # OK

    with pytest.raises(ValueError):
        Item("hello", p=1.5, meta={})  # p > 1


def test_discrete_dist_invariants():
    """Test DiscreteDist validates invariants."""
    items = [
        Item("a", p=0.5, meta={}),
        Item("b", p=0.3, meta={}),
        Item("c", p=0.2, meta={}),
    ]
    dist = DiscreteDist(items, trace={})

    assert len(dist) == 3
    assert sum(dist.p) == pytest.approx(1.0)
    assert dist.argmax().text == "a"


def test_transforms():
    """Test filter/normalize/order."""
    from verbalized_sampling.core.transforms import postprocess

    parsed = [
        {"text": "a", "probability": 0.5},
        {"text": "b", "probability": 0.3},
        {"text": "c", "probability": 0.2},
    ]

    items, meta = postprocess(
        parsed, tau=0.25, min_k_survivors=2,
        weight_mode="elicited", seed=42
    )

    assert len(items) >= 2
    assert sum(it.p for it in items) == pytest.approx(1.0)


# tests/test_api.py (integration test)
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
def test_verbalize_basic():
    """Test basic verbalize() call."""
    dist = verbalize(
        "Say hello in 3 ways",
        k=3,
        provider="openai",
        seed=42,
    )

    assert len(dist) == 3
    assert sum(dist.p) == pytest.approx(1.0)
    assert dist.argmax() is not None
```

---

## Migration & Compatibility

### ✅ No Breaking Changes

1. **Existing code unaffected**: All research scripts, experiments, CLI continue to work
2. **New imports opt-in**: Users choose `from verbalized_sampling import verbalize`
3. **Shared infrastructure**: New API reuses `llms/`, `methods/` → no duplication
4. **Version bump**: 0.1.x → 0.2.0 (minor, backwards compatible)

### File Tree (Final State)

```
verbalized_sampling/
├── __init__.py              # MODIFIED: +4 exports
├── api.py                   # NEW: ~150 lines
├── core/                    # NEW: ~300 lines total
│   ├── __init__.py
│   ├── item.py
│   ├── dist.py
│   └── transforms.py
├── methods/                 # EXISTING (reused)
│   ├── parser.py           # (unchanged, reused as-is)
│   ├── schema.py           # (unchanged, reused as-is)
│   └── factory.py
├── llms/                    # EXISTING (reused)
└── [all other existing files unchanged]
```

**Total impact**: ~450 new lines, ~20 modified lines, 0 breaking changes.

---

## Implementation Checklist

### Week 1: Core Implementation

**Days 1-2: Core Structures**
- [ ] Create `core/item.py` (~30 lines)
- [ ] Create `core/dist.py` (~150 lines)
- [ ] Create `core/transforms.py` (~100 lines)
- [ ] Unit tests for core (~100 lines)

**Days 3-4: Main API**
- [ ] Create `api.py` with `verbalize()` (~150 lines)
- [ ] Integration with existing `llms.get_model()`
- [ ] Integration with existing `methods.ResponseParser`
- [ ] Integration tests (~50 lines)

**Day 5: Documentation**
- [ ] Update `__init__.py` exports
- [ ] Create `examples/simple_api.py`
- [ ] Update main README.md Quick Start
- [ ] Docstrings for all public APIs

### Week 2: Polish & Release

- [ ] Version bump to 0.2.0
- [ ] Full test suite (>80% coverage)
- [ ] Update PyPI package
- [ ] Blog post/announcement

---

## Success Criteria

1. ✅ **One-liner works**: `verbalize("prompt", k=5)` returns valid `DiscreteDist`
2. ✅ **Reuses existing code**: No duplicate LLM/parsing logic
3. ✅ **No breaking changes**: All existing tests pass
4. ✅ **Clean integration**: New code fits naturally into existing structure
5. ✅ **Minimal footprint**: <500 new lines of code

---

## Why This Approach is Better

| Aspect | Old Plan | New Plan ✅ |
|--------|----------|------------|
| **New code** | ~2000 lines | ~450 lines |
| **Duplication** | Separate providers, parsers | Reuse existing |
| **Breaking changes** | Risk of conflicts | Zero |
| **Maintenance** | Two parallel systems | One unified system |
| **Time to implement** | 3 weeks | 1 week |

---

## Next Steps

Ready to implement! Should I start with Phase 1 (core structures)?

The key insight: **Your existing codebase is excellent** - we just need a thin ergonomic layer on top.
