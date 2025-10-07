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
from lean.components.util.logger import Logger

class TempManager:
    """The TempManager class provides access to temporary directories."""

    def __init__(self, logger: Logger) -> None:
        """Creates a new TempManager instance."""
        self._temporary_directories = []
        self.delete_temporary_directories_when_done = True
        self._logger = logger

    def create_temporary_directory(self) -> Path:
        """Returns the path to an empty temporary directory.

        :return: a path to an empty temporary directory
        """
        from tempfile import mkdtemp
        path = Path(mkdtemp(prefix="lean-cli-"))
        self._temporary_directories.append(path)
        self._logger.debug(f"Created temporary directory: {path}")
        return path

    def delete_temporary_directories(self) -> None:
        """Deletes temporary directories that were created while the CLI ran.

        Only the files that the user can delete are deleted, any permission errors are ignored.
        """
        from shutil import rmtree
        for path in self._temporary_directories:
            rmtree(path, ignore_errors=True)
