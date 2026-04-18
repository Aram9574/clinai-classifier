"""One-shot script to pre-compute demo classifications.

Runs the full pipeline (Claude agent + rules engine) on each example in
`backend/data/demo_examples.json` and writes the final ClassificationResult
to `backend/data/demo_classifications.json`.

Run locally with a populated .env:
    export $(grep -v '^#' .env | xargs) && PYTHONPATH=. python scripts/precompute_demo.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.models.requests import ClassificationRequest  # noqa: E402
from backend.services.classification_agent import ClassificationAgent  # noqa: E402
from backend.services.rules_engine import RulesEngine  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("precompute_demo")

DATA_DIR = REPO_ROOT / "backend" / "data"
EXAMPLES_PATH = DATA_DIR / "demo_examples.json"
OUTPUT_PATH = DATA_DIR / "demo_classifications.json"


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY missing. Populate .env and export it.")
        sys.exit(1)

    examples_doc = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    agent = ClassificationAgent(api_key=api_key)
    rules = RulesEngine()

    results: dict[str, dict] = {}
    for example in examples_doc["examples"]:
        example_id = example["id"]
        log.info("Classifying %s…", example_id)
        request = ClassificationRequest(
            system_name=example["system_name"],
            description=example["description"],
            intended_purpose=example["intended_purpose"],
            data_inputs=example["data_inputs"],
            outputs_produced=example["outputs_produced"],
            deployment_context=example["deployment_context"],
            affects_clinical_decision=example["affects_clinical_decision"],
            anthropic_api_key=api_key,
        )
        agent_result = agent.classify(request)
        final = rules.validate_and_enrich(
            agent_result,
            request_description=request.description,
            request_intended_purpose=request.intended_purpose,
        )
        results[example_id] = final.model_dump()
        log.info(
            "  %s -> %s (SaMD=%s, conf=%.2f, %d compliance items)",
            example_id,
            final.risk_level,
            final.samd_flag,
            final.confidence_score,
            len(final.compliance_requirements),
        )

    OUTPUT_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log.info("Wrote %s (%d entries)", OUTPUT_PATH, len(results))


if __name__ == "__main__":
    main()
