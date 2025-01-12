# main.py

from typing import Optional

import typer
import os
import markdown
import tomllib
import sys

__version__ = "0.1.0"
__help__ = """Usage: main.py [OPTIONS] DIR \n
  Convert .txt or .md files to .html files.\n
Arguments:
  DIR  [required]\n
Options:
  --version, -v  Print the current version of Tiller.
  --help, -h     Show this message and exit.
  --config, -c   Specify the path to a TOML config file to be used.
  --output, -o   Specify the name of the folder which the generated files will appear.
  --lang, -l    Specify the language of the generated HTML file.\n"""

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"Tiller Version: {__version__}")
        raise typer.Exit()


def help_callback(value: bool):
    if value:
        print(f"Help: {__help__}")
        raise typer.Exit(code=0)


@app.command()
def main(
    dir: str,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Print the current version of Tiller.",
    ),
    help: Optional[bool] = typer.Option(
        None, "--help", "-h", callback=help_callback, help="Print the help message."
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Change the output directory of the .html files."
    ),
    lang: Optional[str] = typer.Option(
        None, "--lang", "-l", help="Specify the language of the generated HTML file."
    ),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Specify the path to a TOML config file."
    ),
):
    """Convert .txt or .md files to .html files."""
    if config is not None:
        print("Using config file: " + config)
        try:
            with open(config, "rb") as configFile:
                data = tomllib.load(configFile)
                output = data.get("o") or data.get("output")
                lang = data.get("l") or data.get("lang")
        except tomllib.TOMLDecodeError as error:
            print("Error: Please provide a valid config TOML file.")
            print(error)
            sys.exit(1)
    output = output or "til"
    lang = lang or "en-CA"
    if dir is not None:
        try:
            os.makedirs(output, exist_ok=True)
        except OSError as error:
            print(error)
            exit(-1)
        if os.path.isdir(dir):
            for file in os.listdir(dir):
                # Added a condition to check for markdown file
                if CheckFileExtension(file):
                    with open(dir + "/" + file, "r") as text_file:
                        text_file = text_file.read()
                        WriteHTML(text_file, file.split(".")[0], output, lang)
                else:
                    # Added an output to indicate if a file was not .md in addition to not being a .txt file
                    print(f"{file} is not a .txt file or a .md file. Skipping... \n")
        elif os.path.isfile(dir):
            with open(dir, "r") as text_file:
                if CheckFileExtension(dir):
                    text_file = text_file.read()
                    title = dir.split("\\")[-1].split(".")[-2] if "\\" in dir else dir.split("/")[-1].split(".")[-2]
                    print(title)
                    WriteHTML(text_file, title, output, lang)
                else:
                    # Added an output to indicate if a file was not .md in addition to not being a .txt file
                    print(f"{dir} is not a .txt file or .md file. Skipping... \n")
        else:
            print("Error: Invalid value for 'DIR': Path '" + dir + "' does not exist.")


def CheckFileExtension(file: str):
    if os.path.splitext(file)[1] == ".txt" or os.path.splitext(file)[1] == ".md":
        return True
    else:
        return False

# fmt: off
def WriteHTML(text: str, title: str, output: str = "til", lang: str = "en-CA"):
    # Check for markdown heading syntax before converting to html
    h1_content = title
    h1_start_index = text.find("#")
    h1_end_index = text.find("\n", h1_start_index + 1)
    markdown_heading1 = text[h1_start_index + 1 : h1_end_index].strip()
    new_text_content = text
    if h1_start_index >= 0:
        h1_content = markdown_heading1
        new_text_content = text[h1_end_index:]

    horiz_line = new_text_content.find("---")
    if horiz_line != -1:
        new_text_content = new_text_content.replace("---", "<hr />")
    html = markdown.markdown(new_text_content)

    with open(f"{output}/{title}.html", "w") as html_file:
        html_content = (
            """<!DOCTYPE html>
<html lang=\""""
            + lang
            + """\">
    <style>
    body {
        background-color: rgb(0, 116, 145);
        text-align: center;
        color: white;
        font-family: Arial, Helvetica, sans-serif;
        font-size: xx-large;
    }
    </style>
    <head>
        <meta charset="UTF-8">
        <title>"""
            + title
            + """</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <h1>"""
            + h1_content
            + """</h1>
    <body>
        """
            + html.replace("\n", "\n\t\t")
            + """
    </body>
</html>"""
        )
        if html_content.find("<li>") != -1:
            html_content = html_content.replace("<li>", "\t<li>")
        html_file.write(html_content)
    if h1_start_index >= 0:
        print(f"Converted {title}.md to {title}.html")
    else:
        print(f"Converted {title}.txt to {title}.html")
# fmt: on

if __name__ == "__main__":
    app()
