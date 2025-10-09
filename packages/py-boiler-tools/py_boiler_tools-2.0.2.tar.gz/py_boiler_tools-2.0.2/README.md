# Py\_Boil 🔥

[![Tests](https://github.com/dfunani/py_boiler/workflows/Test%20Suite/badge.svg)](https://github.com/dfunani/py_boiler/actions)
[![Code Quality](https://github.com/dfunani/py_boiler/workflows/Code%20Quality/badge.svg)](https://github.com/dfunani/py_boiler/actions)
[![Security](https://github.com/dfunani/py_boiler/workflows/Security%20Scan/badge.svg)](https://github.com/dfunani/py_boiler/actions)
[![Coverage](https://codecov.io/gh/dfunani/py_boiler/branch/main/graph/badge.svg)](https://codecov.io/gh/dfunani/py_boiler)

A lightweight Python package that helps developers quickly bootstrap projects by generating ready-to-use boilerplate code. With **py\_boil**, you can scaffold Python applications in seconds — from simple scripts to full-featured project structures.

---

## 📋 Table of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Installing Dev Dependencies](#installing-dev-dependencies)
* [Usage](#usage)
* [Versioning](#versioning)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

---

## 📖 About The Project

Stop wasting time setting up the same boilerplate code for every project. **py\_boil** takes care of scaffolding your Python application, letting you focus on writing actual business logic.

### Features

* 📦 Generate project scaffolds instantly
* ⚡ Ready-to-use templates (from Hello World to package structures)
* 🛠️ Customizable templates planned in future versions
* 🚀 Helps maintain consistency across projects

---

## 🏗️ Built With

* [Python 3.10+](https://www.python.org/)
* [uv](https://github.com/astral-sh/uv) for dependency management and reproducible environments
* [bumpver](https://pypi.org/project/bumpver/) for automated semantic versioning
* [GitHub Actions](https://github.com/features/actions) for CI/CD pipeline
* [pytest](https://pytest.org/) for testing framework
* [Ruff](https://github.com/astral-sh/ruff) for linting and formatting

---

## 🚀 Getting Started

---

## 👤 For Users

### Installation

Install the latest release from PyPI:

```bash
pip install py-boiler-tools
```

### Quick Usage

After installation, you can use the CLI to scaffold a new project:

```bash
# Simple Hello World App
pyboiler new basic
```

This will create a new files in the current project folder, including starter files.

For more options, run:

```bash
pyboiler --help
```

---

### Prerequisites

Make sure you have Python 3.10+ and [uv](https://github.com/astral-sh/uv) installed:

```bash
python3 --version
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

Install dependencies and create a virtual environment with `uv`:

```bash
uv sync
```

This will:

* Create a `.venv/` automatically
* Install dependencies listed in `pyproject.toml`
* Pin them exactly via a local `uv.lock` file

### Installing Dev Dependencies

To install optional or development packages (like testing or formatting tools):

```bash
uv sync --dev
```

This will install your main dependencies **plus** all packages listed under `[project.optional-dependencies.dev]` in your `pyproject.toml`.

---

## 📝 Usage

Generate a simple Hello World project:

```bash
uv run py_boil new basic
```

Example output (placeholder):

```text
project/
├── main.py
└── README.md
```

---

## 🏷 Versioning

**py\_boil** uses [bumpver](https://pypi.org/project/bumpver/) for semantic versioning:

* Patch: bug fixes (0.1.0 → 0.1.1)
* Minor: new backward-compatible features (0.1.1 → 0.2.0)
* Major: breaking changes (0.2.0 → 1.0.0)

### Bumping a version

```bash
bumpver patch   # 0.1.0 -> 0.1.1
bumpver minor   # 0.1.1 -> 0.2.0
bumpver major   # 0.2.0 -> 1.0.0
```

This updates the version in both `pyproject.toml` and `src/py_boil/__init__.py` and optionally creates a Git commit and tag.

---

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### Automated Workflows

- **🧪 Test Suite**: Runs on Python 3.10, 3.11, 3.12 across Ubuntu, Windows, and macOS
- **🎨 Code Quality**: Linting and formatting with Ruff
- **📦 Build**: Automated package building and validation
- **🚀 Release**: Automated PyPI publishing when you create a GitHub release

### Quality Metrics

- **Test Coverage**: 97% code coverage
- **Code Quality**: Automated linting and formatting
- **Multi-Platform**: Tests on Ubuntu, Windows, and macOS
- **Multi-Version**: Tests on Python 3.10, 3.11, and 3.12

### Local Development

Run the same checks locally:

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest tests/ -v --cov=py_boiler

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Build package
python -m build
twine check dist/*
```

---

## 🗺️ Roadmap

* [x] Basic Hello World template
* [ ] Package scaffold with setup files
* [ ] CLI options for customization
* [ ] User-defined templates

See the [open issues](https://github.com/your-username/py_boil/issues) for a full list of proposed features (and known issues).

---

## 🤝 Contributing

We use [uv](https://github.com/astral-sh/uv) for dependency management. To set up the development environment:

```bash
uv sync --dev
```

To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **Apache 2.0 License**. See `LICENSE` for more information.

---

## 📬 Contact

Delali Funani – [dfunani@gmail.com](mailto:dfunani@gmail.com)

Project Link: [https://github.com/dfunani/py_boiler](https://github.com/dfunani/py_boiler)

## Notes - PYPI

To upload your package to PyPI, follow these steps:

Ensure your package is ready for distribution (source code, metadata, etc.).

Install Twine and Build if not already installed:

`pip install twine build`

Build your package:

`python -m build`

Upload to PyPI:

`twine upload --repository pypi dist/*`

After uploading, you can install your package from PyPI using:
`pip install --index-url https://test.pypi.org/simple/ your-package-name`
