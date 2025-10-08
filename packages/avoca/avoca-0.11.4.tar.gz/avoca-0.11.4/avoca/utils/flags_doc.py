import logging
import re
from enum import Enum
from pathlib import Path

import avoca


def parse_enum_comments(filepath: Path, enum_class_name: str) -> dict[Enum, str]:
    """

    Parses comments above enum members in a Python file and returns a dictionary
    mapping each enum member to its associated comment.

    Supports multiline comments and preserves line breaks.

    Args:
        filepath (str): Path to the Python file containing the enum definition.
        enum_class_name (str): Name of the Enum class to parse.

    Returns:
        dict: A dictionary where keys are enum members (e.g., Qa_Flag.MISSING)
              and values are the corresponding comments as strings.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    comment_dict = {}
    current_comments = []
    enum_name_pattern = re.compile(rf"\s*{enum_class_name}\.(\w+)\s*=")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            # Collect multiline comments
            current_comments.append(stripped.lstrip("#").strip())
        elif enum_name_pattern.search(line) or "=" in stripped:
            # Extract enum constant name
            match = re.search(r"^(\s*)(\w+)\s*=", line)
            if match:
                constant_name = match.group(2)
                if current_comments:
                    comment_text = "\n".join(current_comments)
                    comment_dict[constant_name] = comment_text
                    current_comments = []
                else:
                    comment_dict[constant_name] = ""
        else:
            current_comments = []

    # Build full enum keys like Qa_Flag.MISSING
    enum_obj = {}
    module = {}
    with open(filepath, "r") as f:
        code = f.read()
        exec(code, module)
        enum_cls = module[enum_class_name]
        for name, comment in comment_dict.items():
            enum_member = getattr(enum_cls, name)
            enum_obj[enum_member] = comment

    return enum_obj


def main(directory: Path | None = None):
    """Generate the documentation for the flags."""

    logging.basicConfig(level=logging.INFO)
    avoca_path = Path(*avoca.__path__).parent
    if directory is None:
        # Add the path to the avoca package
        directory = avoca_path / "docs" / "source"
    else:
        directory = Path(directory)

    flags_file = directory / "flags.md"
    logging.getLogger(__name__).info(f"Writing the Flag doc to {flags_file}")

    enum_comments = parse_enum_comments(avoca_path / "avoca/flags.py", "QA_Flag")

    with open(flags_file, "w") as file:
        # Write a link to this
        doc = "(Flags)=\n"
        doc += "# QA Flags\n\n"

        doc += "\n\n"
        doc += "## How do flags work\n\n"
        doc += "@voc@ uses the boolean logic to combine flags. \n"
        doc += "This means that each value is assigned one flag value.\n"
        doc += "The flag value can contain one or more flags.\n"
        doc += "\n"
        doc += "If the value is 0, no flag is assigned.\n"
        doc += "If the value is 1, the flag with value 1 is assigned.\n"
        doc += "If the value is 2, the flag with value 2 is assigned.\n"
        doc += "If the value is 3, the flag with value 1 and 2 is assigned.\n"
        doc += "\n"
        doc += "This allow to combine flags without having to create more variables.\n"
        doc += "\n"
        doc += "[Learn more ](https://docs.python.org/3/library/enum.html#flag) \n"
        doc += "\n\n"

        doc += "## Descriptions\n\n"
        doc += "Various flags are available in @voc@. \n\n"
        for flag, flag_doc in enum_comments.items():
            # Write the docstring to the file
            # Go from Camel case to normal case
            doc += f"### {flag.name.lower().replace("_", " ").capitalize()}\n"
            doc += f"{flag}: {flag.value}\n\n"
            doc += f"{flag_doc}\n\n"

        file.write(doc)


if __name__ == "__main__":
    print(parse_enum_comments("avoca/flags.py", "QA_Flag"))
