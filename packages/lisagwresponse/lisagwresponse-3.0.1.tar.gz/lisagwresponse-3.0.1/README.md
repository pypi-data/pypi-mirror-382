# LISA GW Response

LISA GW Response is a Python package computing the instrumental response to
gravitational-waves, and produce a gravitational-wave (GW) file compatible with
[LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument) and
[LISANode](https://gitlab.in2p3.fr/j2b.bayle/LISANode).

## Contributing

### Report an issue

We use the issue-tracking management system associated with the project provided
by Gitlab. If you want to report a bug or request a feature, open an issue at
<https://gitlab.in2p3.fr/lisa-simulation/gw-response/-/issues>. You may also
thumb-up or comment on existing issues.

### Development environment

Start by cloning the project repository,

```bash
git clone git@gitlab.in2p3.fr:lisa-simulation/gw-response.git
cd gw-response
```

This project uses [Poetry 2](https://python-poetry.org/) to manage dependencies
and packaging. Poetry can prepare a virtual environment for developement, and is
used to build the package.

To run a command inside the project development environement, use

```bash
poetry run <YOUR-COMMAND>
```

You can also explicitely create a virtual environement with

```bash
poetry install
```

You can then activate your environement or setup VS Code to use it.

Remember to synchronize your environement whenever the dependencies change,
using the command

```bash
poetry sync
```

Refer to the [Poetry documentation](https://python-poetry.org/docs/) for more
information.

### Pre-commit hooks

We recommend you install pre-commit hooks to detect errors before you even
commit.

```bash
poetry run pre-commit install
```

You can then run the pre-commit hooks manually with

```bash
poetry run pre-commit run --all-files
```

### Syntax

We enforce PEP 8 (Style Guide for Python Code) with Pylint syntax checking, and
code formatting with Black. Both are implemented in the continuous integration
system, and merge requests cannot be merged if it fails. Pre-commit hooks will
also run Black before you commit.

You can run them locally with

```bash
poetry run pylint lisaorbits
poetry run mypy lolipops
poetry run black --check .
```

Note that VS Code can be configured to run Black when saving a file, and to
display Pylint errors in the editor.

### Unit tests

Correction of the code is checked by the pytest testing framework. It is
implemented in the continuous integration system, but we recommend you run the
tests locally before you commit, with

```bash
poetry run pytest
```

Note that VS Code can be configured to run the tests easily.

### VS Code tasks

Convenient scripts are available to run in VS Code for common developement or
maintenance tasks, such as running the pre-commit hooks, formatting with Black,
building the documentation or building the package.

They are located in ".vscode/tasks.json". In VS Code, you can run them by
opening the command palette (Cmd + Shift + P) and choosing "Tasks: Run Task...".

### Workflow

The project's development workflow is based on the issue-tracking system
provided by Gitlab, as well as peer-reviewed merge requests. This ensures
high-quality standards.

Issues are solved by creating branches and opening merge requests. Only the
assignee of the related issue and merge request can push commits on the branch.
Once all the changes have been pushed, the "draft" specifier on the merge
request is removed, and the merge request is assigned to a reviewer. He can push
new changes to the branch, or request changes to the original author by
re-assigning the merge request to them. When the merge request is accepted, the
branch is merged onto master, deleted, and the associated issue is closed.

## Use policy

The project is distributed under the 3-Clause BSD open-source license to foster
open science in our community and share common tools. Please keep in mind that
developing and maintaining such a tool takes time and effort. Therefore, we
kindly ask you to

* Cite the DOI (see badge above) in any publication
* Acknowledge the authors (below)
* Acknowledge the LISA Simulation Expert Group in any publication

Do not hesitate to send an email to the authors for support. We always
appreciate being associated with research projects.

## Authors

* Jean-Baptiste Bayle (<j2b.bayle@gmail.com>)
* Quentin Baghi (<quentin.baghi@cea.fr>)
* Arianna Renzini (<arenzini@caltech.edu>)
* Maude Le Jeune (<lejeune@apc.in2p3.fr>)
