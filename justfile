set shell := ["bash", "-euo", "pipefail", "-c"]

validate:
    python3 scripts/validate_plugin.py

test:
    python3 -m unittest discover -s tests -p 'test_*.py'

proof: validate test

agent-acceptance:
    bash scripts/run_local_acceptance_workcell.sh
