# ci-starter

Kickstarts the semantic release pipeline for your Python project on GitHub. It creates an opinionated configuration file for python-semantic-release, _semantic-release.toml_ and a pipeline with reusable workflows in _.github/workflows_.

## Usage

### Prerequisites

- Create your project:
    - Use uv to initialize your project (must be a package)
        - Fill it with some minimally meaningful content, I recommend:
            - set version to `0.0.0`
            - project urls
            - keywords
            - classifiers
            - license
        - Add a dependency group for running tests (group shall contain at least your test runner, e.g. pytest)
    - Create tests (CI/CD pipeline would fail if no tests are found)
    - Format and check everything with ruff
    - Set up a trusted publisher for your project on pypi.org:
        - Workflow: `continuous-delivery.yml`
        - Environment name: `pypi`
    - Set up a trusted publisher for your project on test.pypi.org:
        - Workflow: `continuous-delivery.yml`
        - Environment name: `testpypi`
    - Create a GitHub repository for your project
    - Add remote origin and its ssh address at your local clone

### Create CI/CD Pipeline

- run `ci-start` (not _ci-starter_) in the project directory:
```
ci-start \
    --module-name my_app \
    --package-name my-app \
    --workflow-file continuous_delivery.yml \
    --test-group test`
    --test-command "uv run -- pytest -v"
    .
```

That should create you a configuration file (_semantic-release.toml_) and some workflow files (.github/workflows/*.yml) to start with.
