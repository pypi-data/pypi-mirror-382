# aind-codeocean-pipeline-monitor

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)
![Python](https://img.shields.io/badge/python->=3.9-blue?logo=python)

Package for starting a pipeline, waiting for it to finish, and optionally capturing the results as a data asset.

## Installation
The repo can be install from PyPI. To pip install all of the necessary dependencies to run the pipeline monitor, run:
```bash
pip install aind-codeocean-pipeline-monitor[full]
```

To install only the minimum dependencies required for model validation, run:
```bash
pip install aind-codeocean-pipeline-monitor
```

To install the package for development, clone this repo and run
```bash
pip install -e .[dev]
```

## Usage
- Define job using PipelineMonitorJobSettings class.
- Define a CodeOcean client.
- Construct a PipelineMonitorJob with these settings.
- Run the job with the run_job method.

```python
import os

from codeocean import CodeOcean
from codeocean.computation import DataAssetsRunParam, RunParams
from urllib3.util import Retry

from aind_codeocean_pipeline_monitor.job import PipelineMonitorJob
from aind_codeocean_pipeline_monitor.models import (
    CaptureSettings,
    PipelineMonitorSettings,
)

domain = os.getenv("CODEOCEAN_DOMAIN")
token = os.getenv("CODEOCEAN_TOKEN")
# Recommend adding retry strategy to requests session
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
)
client = CodeOcean(domain=domain, token=token, retries=retry)

# Please consult Code Ocean docs for info about RunParams and DataAssetParams
settings = PipelineMonitorSettings(
    run_params=RunParams(
        capsule_id="<your capsule id>",
        data_assets=[
            DataAssetsRunParam(
                id="<your input data asset id>",
                mount="<your input data mount>",
            )
        ],
    ),
    capture_settings=CaptureSettings(
        tags=["derived"]
    ),  # 'tags' is the only required field
)

job = PipelineMonitorJob(job_settings=settings, client=client)
job.run_job()
```

## Contributing

### Linters and testing

There are several libraries used to run linters, check documentation, and run tests.

- Please test your changes using the **coverage** library, which will run the tests and log a coverage report:

```bash
coverage run -m unittest discover && coverage report
```

- Use **interrogate** to check that modules, methods, etc. have been documented thoroughly:

```bash
interrogate .
```

- Use **flake8** to check that code is up to standards (no unused imports, etc.):
```bash
flake8 .
```

- Use **black** to automatically format the code into PEP standards:
```bash
black .
```

- Use **isort** to automatically sort import statements:
```bash
isort .
```

### Pull requests

For internal members, please create a branch. For external members, please fork the repository and open a pull request from the fork. We'll primarily use [Angular](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) style for commit messages. Roughly, they should follow the pattern:
```text
<type>(<scope>): <short summary>
```

where scope (optional) describes the packages affected by the code changes and type (mandatory) is one of:

- **build**: Changes that affect build tools or external dependencies (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bugfix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests

### Semantic Release

The table below, from [semantic release](https://github.com/semantic-release/semantic-release), shows which commit message gets you which release type when `semantic-release` runs (using the default configuration):

| Commit message                                                                                                                                                                                   | Release type                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `fix(pencil): stop graphite breaking when too much pressure applied`                                                                                                                             | ~~Patch~~ Fix Release, Default release                                                                          |
| `feat(pencil): add 'graphiteWidth' option`                                                                                                                                                       | ~~Minor~~ Feature Release                                                                                       |
| `perf(pencil): remove graphiteWidth option`<br><br>`BREAKING CHANGE: The graphiteWidth option has been removed.`<br>`The default graphite width of 10mm is always used for performance reasons.` | ~~Major~~ Breaking Release <br /> (Note that the `BREAKING CHANGE: ` token must be in the footer of the commit) |

### Documentation
To generate the rst files source files for documentation, run
```bash
sphinx-apidoc -o docs/source/ src
```
Then to create the documentation HTML files, run
```bash
sphinx-build -b html docs/source/ docs/build/html
```
More info on sphinx installation can be found [here](https://www.sphinx-doc.org/en/master/usage/installation.html).
