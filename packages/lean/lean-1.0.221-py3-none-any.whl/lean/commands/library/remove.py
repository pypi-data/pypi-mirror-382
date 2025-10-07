# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from click import command, argument, option

from lean.click import LeanCommand, PathParameter
from lean.container import container
from lean.models.errors import MoreInfoError


def _remove_package_from_csharp_project(project_dir: Path, name: str, no_local: bool) -> None:
    """Removes a custom C# library from a C# project.

    Removes the library from the project's .csproj file,
    and restores the project if dotnet is on the user's PATH and no_local is False.

    :param project_dir: the path to the project directory
    :param name: the name of the library to remove
    :param no_local:
    """
    from shutil import which
    from subprocess import run
    logger = container.logger
    path_manager = container.path_manager

    csproj_file = next(p for p in project_dir.iterdir() if p.name.endswith(".csproj"))
    logger.info(f"Removing {name} from '{path_manager.get_relative_path(csproj_file)}'")

    xml_manager = container.xml_manager
    csproj_tree = xml_manager.parse(csproj_file.read_text(encoding="utf-8"))

    for package_reference in csproj_tree.findall(".//PackageReference"):
        if package_reference.get("Include", "").lower() == name.lower():
            package_reference.getparent().remove(package_reference)

    csproj_file.write_text(xml_manager.to_string(csproj_tree), encoding="utf-8")

    if not no_local and which("dotnet") is not None:
        logger.info(f"Restoring packages in '{path_manager.get_relative_path(project_dir)}'")

        process = run(["dotnet", "restore", str(csproj_file)], cwd=project_dir)

        if process.returncode != 0:
            raise RuntimeError("Something went wrong while restoring packages, see the logs above for more information")


def _remove_pypi_package_from_python_project(project_dir: Path, name: str) -> None:
    """Removes a custom Python library from a Python project.

    Removes the library from the project's requirements.txt file.

    :param project_dir: the path to the project directory
    :param name: the name of the library to remove
    """
    from pkg_resources import Requirement

    logger = container.logger
    path_manager = container.path_manager

    requirements_file = project_dir / "requirements.txt"
    logger.info(f"Removing {name} from '{path_manager.get_relative_path(requirements_file)}'")

    if not requirements_file.is_file():
        return

    requirements_content = requirements_file.read_text(encoding="utf-8")
    new_lines = []

    for line in requirements_content.splitlines():
        try:
            requirement = Requirement.parse(line)
            if requirement.name.lower() != name.lower():
                new_lines.append(line)
        except ValueError:
            new_lines.append(line)

    new_content = "\n".join(new_lines).strip()
    new_content = new_content + "\n" if len(new_content) > 0 else new_content
    requirements_file.write_text(new_content, encoding="utf-8")


@command(cls=LeanCommand, requires_docker=True)
@argument("project", type=PathParameter(exists=True, file_okay=False, dir_okay=True))
@argument("name", type=str)
@option("--no-local", is_flag=True, default=False, help="Skip making changes to your local environment")
def remove(project: Path, name: str, no_local: bool) -> None:
    """Remove a custom library from a project.

    PROJECT must be the path to the project directory.

    NAME must be either the name of the NuGet package (for C# projects), the PyPI package (for Python projects),
    or the path to the Lean CLI library to remove.

    Custom C# libraries are removed from the project's .csproj file,
    which is then restored if dotnet is on your PATH and the --no-local flag has not been given.

    Custom Python libraries are removed from the project's requirements.txt file.

    \b
    C# example usage:
    $ lean library remove "My CSharp Project" Microsoft.ML

    \b
    Python example usage:
    $ lean library remove "My Python Project" tensorflow
    """
    project_config = container.project_config_manager.get_project_config(project)
    project_language = project_config.get("algorithm-language", None)

    if project_language is None:
        raise MoreInfoError(f"{project} is not a Lean CLI project",
                            "https://www.lean.io/docs/v2/lean-cli/projects/project-management#02-Create-Projects")

    library_manager = container.library_manager
    library_dir = Path(name).expanduser().resolve()
    if library_manager.is_lean_library(library_dir):
        if project_language == "CSharp":
            library_manager.remove_lean_library_from_csharp_project(project, library_dir, no_local)
        else:
            library_manager.remove_lean_library_from_python_project(project, library_dir)
    else:
        if project_language == "CSharp":
            _remove_package_from_csharp_project(project, name, no_local)
        else:
            _remove_pypi_package_from_python_project(project, name)
