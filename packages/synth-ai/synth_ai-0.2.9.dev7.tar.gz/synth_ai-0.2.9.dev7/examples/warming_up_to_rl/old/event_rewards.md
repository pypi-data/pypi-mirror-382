# Crafter Event-Level Rewards (NOTES)

This note outlines how to support event-level reward layering for Crafter across the warming_up_to_rl task app and the monorepo clustered_training RL pipeline.

## Goals
- Attribute reward at decision/step level (per tool call) instead of only using a single trajectory outcome reward.
- Make this behavior controllable via TOML config flags (enable/disable and choose the source/kind of event reward).
- Keep compatibility with existing trajectory-outcome paths; when disabled, the system behaves exactly as before.

## Definitions
- "Decision": one LM tool call (e.g., `interact_many`) and the sequence of environment steps it triggers.
- "Absolute achievement delta" (AchΔ): count of achievements that became true during a decision.
- "Unique achievement delta" (UniqueΔ): count of achievements first unlocked in the episode by a decision.
- "Env sparse reward": the environment’s own per-step reward (e.g., `reward_last_step`).

## What to compute per decision
- From observation before and after the decision:
  - `turned_true = achievements_after − achievements_before`
  - `new_unique = episode_achievements_after − episode_achievements_before`
- Scalars:
  - `ach_delta = len(turned_true)`
  - `unique_delta = len(new_unique)`
- Optional: per-achievement markers for each `a ∈ new_unique` (reward 1.0) for fine-grained shaping.

## Switches/Flags in TOML
Prefer reusing existing RL trainer flags in clustered_training (already present in code):

```
[training]
# Stepwise/event rewards
step_rewards_enabled = true                # master switch
step_rewards_mode = "decision_stepwise"      # "off" | "decision_stepwise" | "env_sparse"
step_rewards_beta = 0.0                    # optional coefficient for time weighting
step_rewards_indicator_lambda = 0.0        # optional coefficient for indicator-based flips

# Crafter-specific selection (proposed extension, optional)
# event_rewards_kind = "unique"              # "unique" | "absolute" (if omitted, default to "unique")
```

- `step_rewards_enabled`: enables all event-level aggregation.
- `step_rewards_mode`:
  - `off`: use only trajectory outcome reward (status quo).
  - `decision_stepwise`: use per-decision computed deltas (from policy app or collector), aggregate as returns.
  - `env_sparse`: use the environment’s `reward_last_step` per step.
- `event_rewards_kind` (optional): if present, selects `unique_delta` (default) vs `ach_delta` for `decision_stepwise`.

Warmup task TOML may place these under a `training` or `rollout` section; the launcher just forwards the full TOML blob to the backend, so the monorepo side should read the same keys.

## Warming_up_to_rl task app – producing decision rewards
- In the Crafter policy (or rollout coordinator), for each decision:
  - Compute `ach_delta` and `unique_delta` as above.
  - Attach a compact record to the step metadata, e.g.:
    ```json
    {
      "decision_rewards": {
        "turn": 5,
        "ach_delta": 1,
        "unique_delta": 1,
        "all": ["collect_wood"],
        "unique": ["collect_wood"]
      }
    }
    ```
  - When `step_rewards_enabled=false`, omit this block.
  - When `step_rewards_mode="env_sparse"`, rely on `reward_last_step` (no decision block required).

Notes:
- The app already records previous tool calls and environment results; this simply adds a small, structured payload per decision (turn).
- If per-step `reward_last_step` is unavailable, `decision_stepwise` remains effective as long as achievements maps are present.

## Monorepo clustered_training – consuming event rewards
Integration points (based on existing config structure):
- `ClusteredTrainerConfig` already includes:
  - `step_rewards_enabled: bool`
  - `step_rewards_mode: str` (off | decision_stepwise)
  - `step_rewards_beta: float`
  - `step_rewards_indicator_lambda: float`

Collector changes (conceptual):
1. During trajectory collection, build a vector `r_t` of per-time-step rewards:
   - If `step_rewards_mode == "decision_stepwise"`:
     - For time step `t` corresponding to a decision, set:
       - `r_t = unique_delta` if `event_rewards_kind=="unique"` (default), else `r_t = ach_delta`.
     - For non-decision steps, `r_t = 0.0` (unless you prefer to spread rewards over sub-steps; keep simple attribution by default).
   - If `step_rewards_mode == "env_sparse"`:
     - For each environment step, set `r_t = reward_last_step`.
   - Else (`off`):
     - Use a single scalar outcome reward at the end (status quo).

2. Compute returns/advantages as usual, summing event rewards:
   - For GRPO/GRPO-Ludic, the typical group-based advantage calculation remains unchanged; only the reward signal changes from a single scalar to a sequence `[r_1, …, r_T]`.
   - Optional time weighting: `r_t ← r_t + beta * (T − t) * indicator_flip_t`, where `indicator_flip_t` is 1 if any unique achievement flipped at `t`, else 0. Use `step_rewards_indicator_lambda` as a coefficient if needed.

Pseudo-code (collector side):
```python
r = [0.0] * T
if cfg.step_rewards_enabled:
    if cfg.step_rewards_mode == "decision_stepwise":
        for ev in decision_events:  # each with fields {turn, ach_delta, unique_delta}
            idx = ev["turn"] - 1  # 0-based
            base = ev["unique_delta"] if event_kind == "unique" else ev["ach_delta"]
            r[idx] += float(base)
            if cfg.step_rewards_indicator_lambda > 0 and ev["unique_delta"] > 0:
                r[idx] += float(cfg.step_rewards_indicator_lambda)
    elif cfg.step_rewards_mode == "env_sparse":
        for t, step in enumerate(env_steps):
            r[t] += float(step.get("reward_last_step", 0.0))
else:
    r[-1] += float(trajectory_outcome_reward)
```

## Respecting the TOML switch
- warming_up_to_rl launcher (`run_rl_and_save.py`) forwards the entire TOML to the backend.
- clustered_training should read `[training].step_rewards_enabled` and `[training].step_rewards_mode` (and optionally `event_rewards_kind`) inside its config loader (already present fields in `ClusteredTrainerConfig`).
- When disabled, the collector must not attempt to parse or rely on any per-decision metadata.

## Debugging & metrics
- Log per-trajectory aggregates: `ΣAchΔ`, `ΣUniqueΔ`, and a breakdown by decision turn (already added to the Groq rollout table in research). These can be mirrored in the backend logs for quick checks.
- Add simple counters to training logs:
  - number of decisions with `unique_delta>0`
  - sum of deltas per batch
  - share of batches with nonzero event rewards

## Backward compatibility
- When flags are off, the pipeline uses trajectory outcome rewards only.
- No schema migrations are required; event-level metadata is optional.

## Recommended defaults
- `step_rewards_enabled = true`
- `step_rewards_mode = "decision_stepwise"`
- Prefer `unique` deltas for better credit assignment; set `event_rewards_kind = "unique"` (if adopted) or implicitly default to unique deltas.

Here’s the exact file-by-file implementation checklist, scoped so another engineer can implement from this alone.

Warming_up_to_rl (task app) – record decision rewards and honor flags
- Config examples (ensure flags present and documented)
  - `examples/warming_up_to_rl/configs/*.toml`
    - Add under [training]:
      - `step_rewards_enabled = true|false`
      - `step_rewards_mode = "off" | "decision_stepwise" | "env_sparse"`
      - Optional: `event_rewards_kind = "unique" | "absolute"`
      - Optional shaping: `step_rewards_beta`, `step_rewards_indicator_lambda`

- Policy (compute ach/unique deltas per decision; emit into step metadata when enabled)
  - `examples/warming_up_to_rl/task_app/synth_envs_hosted/envs/crafter/policy.py`
    - Before/after each tool call sequence, compute:
      - `ach_delta = len(achievements_after − achievements_before)`
      - `unique_delta = len((episode_achievements_after) − (episode_achievements_before))`
    - When `[training].step_rewards_enabled` and `step_rewards_mode == "decision_stepwise"`:
      - Attach to the step’s returned metadata:
        - `decision_rewards = { turn, ach_delta, unique_delta, all: [...], unique: [...] }`
    - If `step_rewards_mode == "env_sparse"`, do not emit `decision_rewards` (leave environment’s `reward_last_step` as the only per-step reward).
    - Respect clipping for long “Previous tool calls” context (already added; keep).

- Policy routes (surface flags to policy; store on policy instance or in request metadata)
  - `examples/warming_up_to_rl/task_app/synth_envs_hosted/policy_routes.py`
    - Accept training flags from create/init endpoints (if provided via config).
    - Pass through/attach the flags into the policy or per-step metadata so `policy.step(...)` can read them.

- Rollout coordinator (guarantee metadata flows out with each step)
  - `examples/warming_up_to_rl/task_app/synth_envs_hosted/rollout.py`
    - Ensure the step response returned to the caller includes `decision_rewards` when set by the policy.
    - No compute here; just propagate metadata.

- Environment adapter (ensure observation has fields needed by the deltas)
  - `examples/warming_up_to_rl/task_app/synth_envs_hosted/envs/crafter/environment.py`
    - Confirm each step response includes `observation.achievements_status` and `observation.reward_last_step`.
    - No reward computation changes here; just guarantee the fields exist.

Monorepo (clustered training, GSPO/GRPO) – use decision/env-sparse rewards to build per-step returns
- Config loader (read flags; default behavior preserved)
  - `backend/app/routes/clustered_training/core/algorithms/gspo/training/clustered_trainer.py`
    - In `ClusteredTrainerConfig.from_dict(...)`:
      - Already present: `step_rewards_enabled`, `step_rewards_mode`, `step_rewards_beta`, `step_rewards_indicator_lambda`.
      - Add (optional) read: `event_rewards_kind` with default `"unique"` if not present.

- Collector/rollout trajectory builder (construct r_t per episode)
  - The module that converts environment/policy step records into trajectories (collector). If it’s split, cover the point where step arrays are built just before advantage computation.
    - New logic:
      - Initialize `r = [0.0] * T`.
      - If `step_rewards_enabled`:
        - If `step_rewards_mode == "decision_stepwise"`:
          - For each step metadata with `decision_rewards`:
            - `idx = turn - 1`
            - `base = unique_delta` if `event_rewards_kind == "unique"` else `ach_delta`
            - `r[idx] += float(base)`
            - If `step_rewards_indicator_lambda > 0` and `unique_delta > 0`, `r[idx] += step_rewards_indicator_lambda`
        - Else if `step_rewards_mode == "env_sparse"`:
          - For each step, `r[t] += float(observation.reward_last_step or 0.0)`
      - Else (`off`): `r[-1] += float(outcome_reward)`
      - Optional shaping: `r[t] += step_rewards_beta * (T - t) * indicator_flip_t` where `indicator_flip_t = 1` if the step had `unique_delta > 0`, else 0.
    - Ensure this path does not run when flags are off; old outcome-only behavior remains.

- Advantage/returns computation (no API change; just consume r)
  - The function/module that currently builds returns/advantages from rewards.
    - No interface changes; ensure it takes `r` from the collector path above instead of a single scalar outcome reward when event rewards are enabled.

- Logging/metrics (help ops confirm it’s working)
  - Add counters in the training loop logs:
    - Sum of `r` per batch (stepwise mode).
    - Count of decisions with `unique_delta > 0`.
    - Mode/flags echoed on startup.

- RL configs (dev example TOMLs with flags)
  - `backend/app/routes/clustered_training/dev/configs/crafter_online.toml`
    - Add the `[training]` keys above with comments showing choices.
  - Any job start scripts that inline TOML (e.g. `tests/applications/crafter/rl/start_qwen_full_clustered.py` if used)
    - Ensure they don’t strip the new keys; no code change needed if they pass through the TOML.

Research (optional reference; not required for GSPO)
- Reference rollout script demonstrating decision-delta computation
  - `research/testing/crafter/eval_rollout_table_groq.py`
    - Already computes/prints per-decision deltas; use as validation aid (no further changes required for GSPO).

Docs/notes (keep implementers aligned)
- Warming up to RL notes
  - `examples/warming_up_to_rl/event_rewards.md`
    - Already describes flags and expectations; keep this in sync if any naming changes happen.

- Research spec
  - `research/testing/crafter/event_rewards.txt`
    - Already contains the full design and the “recording AND using stepwise rewards” plan.

Sanity checklist (engineer can validate with these)
- With `[training].step_rewards_enabled=false`: identical behavior to today (only outcome reward used).
- With `decision_stepwise`:
  - The task app emits `decision_rewards` per decision (check one trajectory).
  - The collector constructs `r_t` from `unique_delta` (or `ach_delta` if configured).
  - Training logs show nonzero stepwise batch reward sums.
- With `env_sparse`:
  - No decision payload; rewards come strictly from `reward_last_step`.
- Switching `event_rewards_kind` between `"unique"` and `"absolute"` changes which scalar lands in r at a decision turn.

If you want, I can generate minimal code diffs for each target file after you confirm these paths and flag names.