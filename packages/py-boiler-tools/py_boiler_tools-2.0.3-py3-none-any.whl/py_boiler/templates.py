README_CODE = """# py_boiler 🚀

A simple boilerplate generator for Python projects.

## Features
- Generate a `Hello, World!` app with one command
- Modern Python packaging (`pyproject.toml`)
- Extensible for future boilerplates

## Quickstart
```bash
python app.py # Run the app

or

python3 app.py # Depending on your system, you may need to use python3
"""

MAIN_CODE = """\
def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
"""

GITIGNORE_CODE = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.log

# Virtual envs
.venv/
.env/
.py_boiler_env/

# Build
build/
dist/
*.egg-info/
"""

PYPROJECT_TOML = """
[project]
name = "py-boiler"
version = "1.0.0-alpha"
description = "A boilerplate generator for Python apps"
authors = [
    { name = "Your Name", email = "your@email.com" }
]
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"

dependencies = [
    "click>=8.0",
]

[project.scripts]
py-boiler = "app:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

VERSION_CODE = """__version__ = \"1.0.0-alpha\"
"""
