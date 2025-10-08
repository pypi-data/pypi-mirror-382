# DSF AML SDK

Reduce ML training data requirements by 70–90% through adaptive evaluation and knowledge distillation. Train surrogate models ~10× faster and cut infra costs.

---

## Why DSF AML?

Traditional ML needs thousands of labeled examples and hours of training. DSF AML uses adaptive formula evaluation + knowledge distillation to create fast, lightweight models from domain expertise with minimal data.

---

## Core Concepts

Define weighted evaluation rules from domain knowledge. (Enterprise) adapts parameters over time and (Pro/Ent) can distill into an ultra-fast surrogate (linear) for large-scale or edge inference.

**Non-linear mode note**: the backend expects `data['adjustments_values'] = { field_name: { adj_name: value } }`.

---

## Installation

```bash
pip install dsf-aml-sdk
```

**Custom Backend URL (SDK):**

```python
import os
from dsf_aml_sdk import AMLSDK
sdk = AMLSDK(base_url=os.getenv("DSF_AML_BASE_URL"), tier="community")
```

---

## Quick Start

### Community Edition

```python
from dsf_aml_sdk import AMLSDK

sdk = AMLSDK()  # community

config = (sdk.create_config()
  .add_field('model_accuracy',  default=0.95, importance=2.5, sensitivity=2.0)
  .add_field('training_epochs', default=100,  importance=1.8, sensitivity=1.5)
  .add_field('validation_loss', default=0.05, importance=2.2, sensitivity=2.5)
  .add_field('model_name',      default='baseline', importance=1.0, string_floor=0.1)
)

experiment = {'model_accuracy': 0.96, 'training_epochs': 105, 'validation_loss': 0.048}
result = sdk.evaluate(experiment, config)
print(f"Score: {result.score:.3f}")
```

---

### Professional Edition

```python
sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# Bootstrap config from labeled examples (Professional+)
labeled_examples = [
    {'model_accuracy': 0.92, 'training_epochs': 50, 'label': 1},
    {'model_accuracy': 0.85, 'training_epochs': 30, 'label': 0},
    # ... minimum 20 examples
]
suggested_config = sdk.bootstrap_config(labeled_examples)

# Batch evaluation (limit per request = BATCH_MAX_ITEMS; default 1000)
experiments = [
  {'model_accuracy': 0.92, 'training_epochs': 50,  'validation_loss': 0.08},
  {'model_accuracy': 0.95, 'training_epochs': 100, 'validation_loss': 0.05},
  {'model_accuracy': 0.97, 'training_epochs': 150, 'validation_loss': 0.03},
]

results = sdk.batch_evaluate(experiments, config)
metrics = sdk.get_metrics()  # requires prior evaluate/batch_evaluate with config
```

---

### Enterprise: Pipeline + Distillation

```python
sdk = AMLSDK(license_key='ENT-2026-12-31-XXXX', tier='enterprise')

# 1) Seeds (all tiers)
seeds = sdk.pipeline_identify_seeds(dataset=training_data, config=config, top_k_percent=0.1)

# 2) Critical generation
# - Community: demo (1 variant)
# - Professional: rejected by backend (upgrade to Enterprise)
# - Enterprise: full generation
gen = sdk.pipeline_generate_critical(config=config, original_dataset=training_data)

# 3) Full cycle (Enterprise)
full = sdk.pipeline_full_cycle(dataset=training_data, config=config, max_iterations=3)

# 4) Distillation (train/predict Pro+; export Enterprise only)
sdk.distill_train(config, samples=1000, batch_size=100, seed=42)
fast_score = sdk.distill_predict(data=some_item, config=config)
artifact = sdk.distill_export()   # Enterprise only
```

---

## Rate Limits

| Tier         | Evaluations/Day | Batch Size                              | Seeds Preview                    |
|--------------|-----------------|-----------------------------------------|----------------------------------|
| Community    | 100             | ❌ Not available                         | Configurable (default: 10)      |
| Professional | 10,000          | ✅ Up to `BATCH_MAX_ITEMS` (default 1000) | Unlimited                      |
| Enterprise   | Unlimited       | ✅ Up to `BATCH_MAX_ITEMS` (default 1000) | Unlimited                      |

---

## Pipeline 2-in-1: Decision Boundary Focus

Reduce dataset 70–90% preserving information at decision boundaries.

```python
# Seeds (all tiers). Cache 1h.
seeds_result = sdk.pipeline_identify_seeds(dataset=training_data, config=config, top_k_percent=0.1)
print("Seeds:", seeds_result['seeds_count'])

variants_result = sdk.pipeline_generate_critical(
  config=config,
  original_dataset=training_data,
  k_variants=5,
  epsilon=0.05,            # auto-tune based on previous acceptance rate
  non_critical_ratio=0.15,
  diversity_threshold=0.95,
  max_seeds_to_process=100
)
print("Generated:", variants_result['total_generated'])
```

**Auto-tuning (Enterprise)**: epsilon adjusts based on previous acceptance rate (stored 1h in `acc_rate:{license}`).
- If rate < 1% → epsilon += 0.02 (≤ 0.25)
- If rate > 30% → epsilon -= 0.02 (≥ 0.02)

---

## Curriculum Learning (Enterprise)

```python
sdk = AMLSDK(license_key='ENT-...', tier='enterprise')

init  = sdk.curriculum_init(dataset=training_data,  config=config, top_k_percent=0.1)
step  = sdk.curriculum_step(dataset=current_batch, config=config, precomputed_metrics={'max_iterations': 5})
status = sdk.curriculum_status()
print(status.get('state', {}).get('status'))
```

State/iterations persist in Redis (TTL ~1 day).

---

## Bootstrap Configuration (Professional/Enterprise)

Generate initial configuration from labeled examples:

```python
sdk = AMLSDK(license_key='PRO-...', tier='professional')

# Minimum 20 labeled examples required
labeled_data = [
    {'accuracy': 0.92, 'epochs': 100, 'label': 1},  # success
    {'accuracy': 0.78, 'epochs': 50,  'label': 0},  # failure
    # ...
]

config = sdk.bootstrap_config(labeled_data)
# Returns optimized importance and sensitivity based on correlation with success
```

---

## Non-Linear Evaluation Mode (Professional/Enterprise)

```python
config = {'performance': {'default': 0.85, 'importance': 2.0},
          'latency':     {'default': 100,  'importance': 1.5}}

adjustments = {'new_customer_bonus': 0.5, 'peak_hours_penalty': 0.3}
adjustment_values = {'performance': {'new_customer_bonus': 0.1, 'peak_hours_penalty': -0.05}}

result = sdk.evaluate_nonlinear(
  data={'performance': 0.87, 'latency': 95},
  config=config,
  adjustments=adjustments,
  adjustment_values=adjustment_values  # sent as data['adjustments_values']
)
print("Adjusted score:", result.score)
```

---

## Error Handling

```python
from dsf_aml_sdk import AMLSDK, LicenseError, ValidationError, APIError

try:
  sdk = AMLSDK(license_key='invalid', tier='enterprise')
  sdk.distill_train(config, samples=1000)
except LicenseError:
  sdk = AMLSDK()  # fallback to community
except ValidationError as e:
  print("Invalid config:", e)
except APIError as e:
  print("API failure:", e)

# get_metrics requires prior evaluate/batch_evaluate with config
```

**Backend limits & statuses**:
- 413 for data_batch or dataset too large (defaults: BATCH_MAX_ITEMS=1000, DATASET_MAX_ITEMS=10000).
- 403 invalid license / tier not permitted
- 404 unknown action/state
- 502 export failure

---

## Tier Comparison

| Feature                       | Community         | Professional                      | Enterprise                       |
|------------------------------|--------------------|-----------------------------------|----------------------------------|
| Single evaluation            | ✅ (100/day)      | ✅ (10k/day)                      | ✅ (unlimited)                   |
| Batch evaluation             | ❌                | ✅ (up to BATCH_MAX_ITEMS)        | ✅ (up to BATCH_MAX_ITEMS)       |
| Performance metrics          | ❌                | ✅                                | ✅ (enhanced)                    |
| Adaptive learning            | ❌                | ✅ Light                          | ✅ Full                          |
| Bootstrap configuration      | ❌                | ✅                                | ✅                               |
| pipeline_identify_seeds      | ✅                | ✅                                | ✅                               |
| pipeline_generate_critical   | Demo (1)           | ❌                                | ✅ Full                          |
| pipeline_full_cycle          | ❌                | ❌                                | ✅                               |
| Curriculum learning          | ❌                | ❌                                | ✅                               |
| Non-linear evaluation        | ❌                | ✅                                | ✅                               |
| Distillation (train/predict) | ❌                | ✅                                | ✅                               |
| Model export (surrogate)     | ❌                | ❌                                | ✅                               |
| Redis hot store / caching    | ❌                | ✅                                | ✅                               |
| Auto-tuning                  | ❌                | ⚠️ (limited)                      | ✅                               |
| Support                      | Community          | Email                             | Priority SLA                     |

---

## Enterprise Features

### Full Adaptive Learning

```python
sdk = AMLSDK(license_key='ENT-...', tier='enterprise')
_ = sdk.batch_evaluate(batches[0], config)
metrics = sdk.get_metrics()
print(metrics.get('weight_changes'), metrics.get('adjusted_fields'))
```

---

### Knowledge Distillation Performance

```python
sdk = AMLSDK(license_key='PRO-...', tier='professional')

import time
t0 = time.time(); _ = sdk.evaluate(data, config); t_full = time.time() - t0

sdk.distill_train(config, samples=1000)
t1 = time.time(); _ = sdk.distill_predict(data, config); t_surr = time.time() - t1

print(f"Speedup: {t_full / max(t_surr, 1e-6):.1f}×")
```

---

## API Reference (SDK)

### Initialization

`AMLSDK(tier='community'|'professional'|'enterprise', license_key=None, base_url=None)`

---

### Evaluation

- `evaluate(data, config)` – single evaluation
- `batch_evaluate(data_points, config)` – Pro/Ent (tier limits apply)
- `evaluate_nonlinear(data, config, adjustments, adjustment_values)` – Pro/Ent
- `get_metrics()` – requires prior evaluate/batch_evaluate with config (not community)

---

### Configuration

- `bootstrap_config(labeled_examples)` – Pro/Ent (min 20 examples)

---

### Pipeline

- `pipeline_identify_seeds(dataset, config, top_k_percent=0.1, max_seeds_preview=10)`
- `pipeline_generate_critical(config, original_dataset, seeds=None, **kwargs)`
  - Params: `k_variants`, `epsilon`, `non_critical_ratio`, `diversity_threshold`, `max_seeds_to_process`, `vectors_for_dedup` (optional)
  - If seeds not provided, retrieved from cache
- `pipeline_full_cycle(dataset, config, max_iterations=5, **kwargs)` – Enterprise

---

### Curriculum (Enterprise)

- `curriculum_init(dataset, config, **params)`
- `curriculum_step(dataset, config, precomputed_metrics=None)`
- `curriculum_status()`

---

### Distillation (Professional/Enterprise)

- `distill_train(config, samples=1000, batch_size=100, seed=42, adjustments=None)`
- `distill_predict(data, config)` → float score
- `distill_predict_batch(data_batch, config)` → List[float]
- `distill_export()` – Enterprise (export to Supabase)

---

### Configuration parameters (per field)

- `default` – reference value
- `importance` – field relevance (0.0–5.0)
- `sensitivity` – sensitivity factor (0.0–5.0)
- `string_floor` – minimum match for string mismatch (0.0–1.0; default 0.1)

---

## Use Cases

### Experiment Scoring

```python
config = {
  'train_acc': {'default': 0.92, 'importance': 2.0},
  'val_acc':   {'default': 0.88, 'importance': 2.5},
  'train_loss':{'default': 0.1,  'importance': 1.8},
  'gap':       {'default': 0.04, 'importance': 2.2},
}
result = sdk.evaluate(experiment_metrics, config)
```

---

### Boundary-Focused Reduction

```python
result = sdk.pipeline_full_cycle(dataset=full_training_data, config=config, max_iterations=3)
print(result['final_size'])
```

---

## Performance Benefits

- **Data efficiency**: 100–1,000 examples + rules (vs 10k+)
- **Training speed**: surrogate ≈ 10× faster
- **Pipeline processing**: 70–90% reduction maintaining accuracy
- **Deployment size**: surrogate artifacts are tiny

---

## FAQ

**Q: How accurate are surrogate models?**  
A: Typical MAE of 0.01-0.05 on normalized scores.

**Q: What is Pipeline 2-in-1?**  
A: Combines filtering and generation at decision boundaries.

**Q: Why does get_metrics() fail?**  
A: You must first call evaluate() or batch_evaluate() with a valid config.

**Q: How does epsilon auto-tuning work?**  
A: Adjusts based on previous acceptance rate (stored 1h in Redis).

**Q: Do I need to generate vectors for deduplication?**  
A: No, auto-generated if not provided.

**Q: How long are pipeline seeds cached?**  
A: 3600 seconds (1 hour) in Redis.

**Q: Can Community tier use pipeline_identify_seeds?**  
A: Yes. Preview size is configurable (default 10 via max_seeds_preview).

**Q: Does Professional tier have access to distillation?**  
A: Yes, both Professional and Enterprise tiers.

---

## Support

- **Docs**: https://docs.dsf-aml.ai
- **Issues**: https://github.com/dsf-aml/sdk/issues
- **Enterprise**: contacto@softwarefinanzas.com.co

---

## License

MIT for Community. Professional/Enterprise under commercial terms.  
© 2025 DSF AML SDK. Adaptive ML powered by Knowledge Distillation.