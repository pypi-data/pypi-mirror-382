PRODUCTION_REPO="git@github.com:codec-lab/flippy.git"
RELEASE_TAG=v$(shell cat version.txt | tr -d '\n')
LOGO_URL="https://raw.githubusercontent.com/codec-lab/flippy/refs/heads/main/flippy.svg"

test:
	python -m pytest $(ARGS)

lint:
	# Copied from .github/workflows
	flake8 flippy --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 flippy --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

docs:
	pdoc --math flippy

docs_build:
	pdoc --math flippy -o docs --logo $(LOGO_URL)

pypi_build:
	python -m build

release_dev_main:
	git checkout main

	# create tag for version
	git tag $(RELEASE_TAG)
	# set dev/production to dev/main
	git checkout -B production
	# push to dev
	git push origin main
	git push origin production
	git push origin tag $(RELEASE_TAG)

	# push dev/production to flippy/main
	git push $(PRODUCTION_REPO) production:main
	# push tag to flippy/main
	git push $(PRODUCTION_REPO) tag $(RELEASE_TAG)

	# Go back to main after released
	git checkout main
