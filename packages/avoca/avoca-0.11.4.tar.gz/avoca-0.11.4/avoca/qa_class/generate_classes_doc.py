"""Generate the classes documentation for the QA classes.

The principle for building the doc is too look at all the registered QA classes.
Then we generate a file for sphinx that will read all the classes with autodoc.
In the conf.py file, this code will be runned every time to generate the documentation.

"""

import logging
from pathlib import Path

import avoca
from avoca.manager import AssignerManager


def main(directory: Path | None = None):
    logging.basicConfig(level=logging.INFO)
    if directory is None:
        # Add the path to the avoca package
        avoca_path = Path(*avoca.__path__).parent
        directory = avoca_path / "docs" / "source"
    else:
        directory = Path(directory)
    qa_class_file = directory / "qa_classes.md"
    logging.getLogger(__name__).info(f"Writing the QA classes to {qa_class_file}")

    # Get all the classes in the qa_class module
    assigners = AssignerManager._assigners_importpath

    # Write the rst file
    with open(qa_class_file, "w") as file:
        # Write a link to this
        file.write("(Models)=\n")
        file.write("# QA Classes\n\n")

        for assigner, assigner_importpath in assigners.items():
            # Get the docsting of the class
            # assigner_module = __import__(assigner_importpath, fromlist=[""])
            # assigner_class = getattr(assigner_module, assigner)
            # doc = assigner_class.__doc__

            # Write the docstring to the file
            # Go from Camel case to normal case
            file.write(f"## {assigner}\n")
            # file.write(f"{doc}\n")
            file.write("```{eval-rst} \n")
            file.write(f".. autoclass:: {assigner_importpath}.{assigner}\n")
            # file.write("    :members:\n")
            file.write("```\n")
            file.write("\n")


if __name__ == "__main__":

    main()
