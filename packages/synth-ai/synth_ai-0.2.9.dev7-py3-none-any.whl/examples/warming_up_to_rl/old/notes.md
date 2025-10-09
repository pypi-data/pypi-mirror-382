# Crafter Task App Ops Cheatsheet

## Discover available task apps
- `uvx synth-ai task-app list`
  - Lists the registered apps plus any aliases (e.g. `grpo-crafter`, `crafter`).

## Run locally with uvicorn
- Launch the FastAPI server:
  - `uvx synth-ai serve grpo-crafter --port 8010 --force`
    - `--force` frees the port if a previous run is still bound.
    - Add `--reload` while iterating on code.
- Enable tracing + SFT dumps while serving:
  - `uvx synth-ai serve grpo-crafter --port 8010 --force --trace ./traces --trace-db ./traces/v3/synth_ai.db`
    - `--trace` writes JSONL trajectories into the folder.
    - `--trace-db` points the sqlite/Turso-compatible tracing DB (defaults to `traces/v3/synth_ai.db`).

## Modal hot-reload (`modal serve`)
- Run the hosted app locally inside Modal’s hot-reload loop:
  - `uvx synth-ai task-app modal-serve grpo-crafter --env-file .env`
    - CLI will prompt for a `.env` file if not supplied; secrets are loaded via `Secret.from_dotenv`.
    - Keeps watching the repo for changes and streams logs in your terminal.

## Modal deploy (persistent endpoint)
- Build + deploy to the `modal deploy` target:
  - `uvx synth-ai task-app deploy grpo-crafter --env-file .env`
    - Use `--dry-run` first to inspect the generated `modal deploy …` command.
    - `--modal-cli` lets you point at a non-default Modal binary if needed.

## Collecting traces & rollouts
- Local rollouts against a running server with full trace payloads:
  - `uv run python examples/warming_up_to_rl/run_local_rollout_traced.py --api-key "$ENVIRONMENT_API_KEY" --base-url http://localhost:8010 --model gpt-4o-mini --trace-format full --trace-path ./trace_full.json`
    - This script prints a reward summary, dumps the trace JSON, and warns if episode returns don’t line up with event rewards.
- Remote rollouts against a deployed Modal endpoint:
  - `uv run python examples/warming_up_to_rl/run_rollout_remote.py --base-url https://<modal-app-url> --api-key "$ENVIRONMENT_API_KEY" --model gpt-4o-mini --max-llm-calls 10`

## Trace analytics
- Summarise model usage, reward breakdowns, and achievement histograms:
  - `uv run python examples/warming_up_to_rl/analyze_trace_db.py --db traces/v3/synth_ai.db`
    - Output includes per-model achievement tallies and episode reward stats.

## Exporting behavioural-cloning datasets
- Filter sessions via model, achievements, rewards, etc., then export JSONL:
  - `uv run python examples/warming_up_to_rl/export_trace_sft.py \`
    `  --db traces/v3/synth_ai.db \`
    `  --output traces/qwen32b_filtered.jsonl \`
    `  --model qwen/qwen3-32b \`
    `  --exclude-achievement collect_sapling \`
    `  --exclude-achievement collect_drink \`
    `  --min-unique 3 \`
    `  --event-reward unique_achievement_delta:1.0 \`
    `  --limit 100`
    - `--exclude-achievement` makes it easy to ignore easier unlocks when enforcing `--min-unique`.
    - Combine `--require-achievement`, `--min-outcome-reward`, or provider filters as needed.

## Training jobs (RL + SFT)
- `uvx synth-ai train` is the consolidated entry point for RL or SFT launches.
  - Omit `--config` to let the CLI enumerate candidate TOMLs (RL + FFT) and pick interactively.
  - Omit `--env-file` to browse available `.env` files; the CLI never auto-selects.
  - Missing secrets trigger an interactive loop: enter manually, switch `.env`, or fetch from Modal (secrets/apps) before proceeding.
- RL run (local backend + local task app):
  - `uvx synth-ai train --type rl --config examples/warming_up_to_rl/configs/crafter_cluster.toml --backend http://localhost:8000/api --task-url http://localhost:8010`
    - Performs task-app health checks using the resolved `ENVIRONMENT_API_KEY` before posting to `/rl/jobs`.
    - Polls job status until terminal unless `--no-poll` is supplied.
- SFT run (FFT fine-tune):
  - `uvx synth-ai train --type sft --config examples/warming_up_to_rl/configs/fft_crafter.toml --dataset traces/crafter_sft.jsonl`
    - Uploads training/validation JSONL to `/learning/files` and starts the job.
    - Poll output mirrors the legacy `run_fft_and_save.py` script.
- Common flags:
  - `--dry-run` previews payloads/uploads without making requests.
  - `--idempotency` sets the `Idempotency-Key` header for RL submissions.
  - `--poll-timeout` / `--poll-interval` tune the backend polling cadence.

> Tip: all `uvx synth-ai …` subcommands accept `--help` if you need to inspect additional options on the fly.
