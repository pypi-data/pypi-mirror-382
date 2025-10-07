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
from datetime import datetime, timedelta
from typing import Any, List, Callable

from lean.components.api.api_client import APIClient
from lean.components.config.lean_config_manager import LeanConfigManager
from lean.components.util.logger import Logger
from lean.models.errors import MoreInfoError, RequestFailedError


def _store_local_file(file_content: bytes, file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("wb+") as f:
        f.write(file_content)


def parse_timedelta(database_update_frequency: str):
    if '.' not in database_update_frequency and ':' not in database_update_frequency:
        return None
    if database_update_frequency.count(".") == 1:  # Ideally, the format is DD.HH:MM:SS
        days_component, time_component = map(str, database_update_frequency.split("."))
        days = int(days_component)
        hours, minutes, seconds = map(int, time_component.split(":"))
    else:  # However, the format can also be HH:MM:SS
        days = 0
        hours, minutes, seconds = map(int, database_update_frequency.split(":"))
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


class DataDownloader:
    """The DataDownloader is responsible for downloading data from QuantConnect Datasets."""

    def __init__(self,
                 logger: Logger,
                 api_client: APIClient,
                 lean_config_manager: LeanConfigManager,
                 database_update_frequency: str):
        """Creates a new CloudBacktestRunner instance.

        :param logger: the logger to use to log messages with
        :param api_client: the APIClient instance to use when communicating with the QuantConnect API
        :param lean_config_manager: the LeanConfigManager instance to retrieve the data directory from
        :param database_update_frequency: the value of the config option database-update-frequency
        """
        self._logger = logger
        self._api_client = api_client
        self._lean_config_manager = lean_config_manager
        self.database_update_frequency = database_update_frequency

    def update_database_files(self):
        """Will update lean data folder database files if required

        """
        try:
            now = datetime.now()
            config = self._lean_config_manager.get_lean_config()
            last_update = config["file-database-last-update"] if "file-database-last-update" in config else ''

            # The last update date can be in '%m/%d/%Y'(old format) or '%m/%d/%Y %H:%M:%S'(new format)
            last_update = self.parse_last_update_date(last_update)
            if self.database_update_frequency is None:  # The user has not set this parameter yet
                self.database_update_frequency = "1.00:00:00"

            frequency = parse_timedelta(self.database_update_frequency)
            if not frequency:
                self._logger.debug(f"Skipping database-update-frequency, frequency is:"
                                   f" {str(self.database_update_frequency)}")
                return
            self._logger.debug(f"database-update-frequency is: {str(frequency)}")
            if not last_update or now - last_update > frequency:
                data_dir = self._lean_config_manager.get_data_directory()
                self._lean_config_manager.set_properties({"file-database-last-update": now.strftime('%m/%d/%Y %H:%M:%S')})

                _store_local_file(self._api_client.data.download_public_file(
                    "https://raw.githubusercontent.com/QuantConnect/Lean/master/Data/symbol-properties/symbol-properties-database.csv"),
                    data_dir / "symbol-properties" / "symbol-properties-database.csv")
                _store_local_file(self._api_client.data.download_public_file(
                    "https://raw.githubusercontent.com/QuantConnect/Lean/master/Data/market-hours/market-hours-database.json"),
                    data_dir / "market-hours" / "market-hours-database.json")
        except MoreInfoError as e:
            if "not found" in str(e):
                pass
            else:
                self._logger.error(str(e))
        except ValueError as e:
            self._logger.debug(f"Value of config option database-update-frequency is invalid: {str(e)}. "
                               f"Database update will be skipped")
        except Exception as e:
            self._logger.error(str(e))

    def download_files(self, data_files: List[Any], overwrite: bool, organization_id: str) -> None:
        """Downloads files from QuantConnect Datasets to the local data directory.

        :param data_files: the list of data files to download
        :param overwrite: whether existing files may be overwritten
        :param organization_id: the id of the organization that should be billed
        """
        from joblib import delayed, Parallel
        from multiprocessing import cpu_count
        progress = self._logger.progress(suffix="{task.percentage:0.0f}% ({task.completed:,.0f}/{task.total:,.0f})")
        progress_task = progress.add_task("", total=len(data_files))

        try:
            parallel = Parallel(n_jobs=max(1, cpu_count() - 1), backend="threading")

            data_dir = self._lean_config_manager.get_data_directory()
            parallel(delayed(self._download_file)(data_file.file, overwrite, data_dir, organization_id,
                                                  lambda advance: progress.update(progress_task, advance=advance))
                     for data_file in data_files)

            # update our config after we download all files, and not in parallel!
            for datafile in data_files:
                relative_file = datafile.file
                if "/map_files/map_files_" in relative_file and relative_file.endswith(".zip"):
                    self._lean_config_manager.set_properties({
                        "map-file-provider": "QuantConnect.Data.Auxiliary.LocalZipMapFileProvider"
                    })
                if "/factor_files/factor_files_" in relative_file and relative_file.endswith(".zip"):
                    self._lean_config_manager.set_properties({
                        "factor-file-provider": "QuantConnect.Data.Auxiliary.LocalZipFactorFileProvider"
                    })

            progress.stop()
        except KeyboardInterrupt as e:
            progress.stop()
            raise e

    def _process_bulk(self, file: Path, destination: Path):
        from tarfile import open
        tar = open(file)
        tar.errorlevel = 0
        tar.extractall(destination)
        tar.close()
        from os import remove
        remove(file)

    def parse_last_update_date(self, last_update_date: str) -> datetime:
        formats = ['%m/%d/%Y', '%m/%d/%Y %H:%M:%S']

        for fmt in formats:
            try:
                return datetime.strptime(last_update_date, fmt)
            except ValueError:
                continue

    def remove_suffix(self,input_string, suffix):
        if suffix and input_string.endswith(suffix):
            return input_string[:-len(suffix)]
        return input_string

    def _download_file(self,
                       relative_file: str,
                       overwrite: bool,
                       data_directory: Path,
                       organization_id: str,
                       progress_callback: Callable[[float], None]) -> None:
        """Downloads a single file from QuantConnect Datasets to the local data directory.

        If this method downloads a map or factor files zip file,
        it also updates the Lean config file to ensure LEAN uses those files instead of the csv files.

        :param relative_file: the relative path to the file in the data directory
        :param overwrite: whether existing files may be overwritten
        :param data_directory: the path to the local data directory
        :param organization_id: the id of the organization that should be billed
        :param callback: the lambda that is called just before the method returns
        """

        local_path = canary_path = data_directory / relative_file

        is_bulk = "setup/" in relative_file and relative_file.endswith(".tar")
        if is_bulk:
            # for bulk, we will download to a temporary folder and delete it at the end
            import tempfile
            local_path = tempfile.gettempdir() + "/" + relative_file
            canary_path = Path(self.remove_suffix(str(data_directory / relative_file), ".tar") + ".log")

        if canary_path.exists() and not overwrite:
            self._logger.warn("\n".join([
                f"{relative_file} already exists, use --overwrite to overwrite it",
                "You have not been charged for this file"
            ]))
            progress_callback(1)
            return

        try:
            self._api_client.data.download_file(relative_file, organization_id, local_path, progress_callback)
        except RequestFailedError as error:
            self._logger.warn(f"{relative_file}: {error}\nYou have not been charged for this file")
            progress_callback(1)
            return

        # Special case: bulk files need unpacked
        if is_bulk:
            canary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(canary_path, 'a') as log_file:
                log_file.write(f'Downloaded: {relative_file}\n')
            self._process_bulk(local_path, data_directory)
