# azpipeline

[![PyPI](https://img.shields.io/pypi/v/azpipeline?style=flat-square)](https://pypi.python.org/pypi/azpipeline/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/azpipeline?style=flat-square)](https://pypi.python.org/pypi/azpipeline/)
[![PyPI - License](https://img.shields.io/pypi/l/azpipeline?style=flat-square)](https://github.com/nidhaloff/azpipeline/blob/main/LICENCE)


---

**Documentation**: [https://azpipeline.readthedocs.io/en/latest/](https://azpipeline.readthedocs.io/en/latest/)

**Source Code**: [https://github.com/nidhaloff/azpipeline](https://github.com/nidhaloff/azpipeline)

**PyPI**: [https://pypi.org/project/azpipeline/](https://pypi.org/project/azpipeline/)

---

The easiest way to interact with azure pipelines using python!

The azure-devops library is very confusing to use and wrap your head around. Furthermore, it is not documented <b>at all</b>!!. Anyway, that is the reason I implemented this small wrapper to easily interact with azure pipeline.

## Installation

```sh
pip install azpipeline
```

## Usage

```py

from azpipeline import AzurePipeline

# Create the pipeline class
pipeline = AzurePipeline(
  organization_url=<your_organization_url>,
  project=<your_project>,
  build_id=<your_pipeline_build_id>,
  token=<your_access_token>
)

# Access a summary of the pipeline run
summary = pipeline.summary

# Get the timeline of the current pipeline run
timeline = pipeline.get_timeline()

# Get tasks/steps that failed on the pipeline
failed_tasks = pipeline.get_failed_tasks(timeline)

# Get failed tasks logs
logs = pipeline.get_failed_tasks_logs(timeline)

# Get failed jobs
jobs = pipeline.failed_jobs()

# Get a list of previous builds
builds = pipeline.get_previous_builds()

# Compare current with previous build
pipeline.compare_with_prev_build()


```


## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.7+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings
 of the public signatures of the source code.

### Releasing

Trigger the [Draft release workflow](https://github.com/nidhaloff/azpipeline/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/nidhaloff/azpipeline/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/nidhaloff/azpipeline/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Pre-commit

Pre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```
