.PHONY: test validate eval zip

test:        ## unit tests + SKILL.md authoring rules
	python3 -m pytest -q
	python3 tests/validate_skill.py

validate:    ## Claude Code plugin + marketplace schema
	claude plugin validate --strict .

eval:        ## behavior evals vs a no-plugin baseline (uses your Claude plan/API usage)
	claude plugin eval . --allow-tools Bash

zip:         ## build phaselens.zip for upload in the Claude apps
	cd skills && zip -r ../phaselens.zip phaselens -x '*/__pycache__/*' '*.pyc'
