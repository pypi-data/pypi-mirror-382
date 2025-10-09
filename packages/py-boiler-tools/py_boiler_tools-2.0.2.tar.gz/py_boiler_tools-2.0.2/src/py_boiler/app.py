import click
from pathlib import Path
from py_boiler.templates import README_CODE, MAIN_CODE, GITIGNORE_CODE


@click.group()
def main():
    """Py-Boiler: Generate boilerplate Python apps."""
    pass


@main.group()
def new():
    """Scaffold new boilerplate projects."""
    pass


@new.command("basic")
def basic():
    """Generate a Hello World app.py file."""
    target_files = ["README.md", "app.py", ".gitignore", "__init__.py"]
    for file in target_files:
        target_file = Path(f"./{file}")

        if target_file.exists():
            click.echo(f"⚠️  {file} already exists, not overwriting.")
            continue

        match file:
            case "README.md":
                app_code = README_CODE
            case "app.py":
                app_code = MAIN_CODE
            case ".gitignore":
                app_code = GITIGNORE_CODE
            case _:
                app_code = ""
        try:
            target_file.write_text(app_code, encoding="utf-8")
        except UnicodeEncodeError:
            # Fallback for systems with encoding issues
            target_file.write_text(app_code, encoding="utf-8", errors="replace")
        click.echo(f"✅ Created {file} with Hello World template.")


if __name__ == "__main__":
    main()
