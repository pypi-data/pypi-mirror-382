#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
temp_utils

Temporary files utilities

"""

import tempfile
import uuid
import warnings
import weakref
from tempfile import TemporaryDirectory
from typing import Any, Optional

from eopf import EOConfiguration, EOLogging
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Singleton

EOConfiguration().register_requested_parameter(
    "temporary__folder",
    param_is_optional=True,
    default_value=tempfile.gettempdir(),
    description="Folder create the temporary folder in",
)

EOConfiguration().register_requested_parameter(
    "temporary__folder_local",
    param_is_optional=True,
    default_value=tempfile.gettempdir(),
    description="Local folder to create the local temporary folder",
)

EOConfiguration().register_requested_parameter(
    "temporary__folder_s3_secret",
    param_is_optional=True,
    description="S3 secret to use to create temp folder",
)

EOConfiguration().register_requested_parameter(
    "temporary__folder_create_folder",
    param_is_optional=True,
    default_value=True,
    description="Create the folder if no exist if True, else raise exception",
)


class S3TemporaryDirectory:
    """Mimics tempfile.TemporaryDirectory but for S3 using fsspec, with automatic cleanup."""

    def __init__(self, directory: AnyPath, prefix: Optional[str] = None) -> None:
        """
        constructor
        Parameters
        ----------
        directory : base directory to build temp path from
        prefix : prefix for the temp folder
        """
        self._base_dir = directory
        if not self._base_dir.isdir():
            raise ValueError(f"S3 Temporary base folder {self._base_dir} doesn't point to a folder")
        self._temp_dir = self._base_dir / f"{prefix}{uuid.uuid4()}"
        # Create a marker file to ensure the "folder" exists
        self._keep_file = self._temp_dir / ".keep"
        self._keep_file.touch()
        # Register finalizer to ensure cleanup
        # Use of a weak ref allows to garbage collect
        self._finalizer = weakref.finalize(
            self,
            self._cleanup,
            self._temp_dir,
            warn_message=f"Implicitly cleaning up {self._temp_dir}",
        )
        # provide it to user
        self.name = self._temp_dir

    @classmethod
    def _cleanup(
        cls,
        temp_dir: AnyPath,
        warn_message: str,
    ) -> None:
        """
        Cleanup function to automatically cleanup at garbage collect

        Parameters
        ----------
        temp_dir
        warn_message

        Returns
        -------

        """
        temp_dir.rm(recursive=True)
        warnings.warn(warn_message, ResourceWarning)

    def __enter__(self) -> AnyPath:
        """
        Context manager enter

        Returns
        -------
        self.name
        """
        return self.name  # Return S3 path of the temp directory

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """
        Context manager exit
        Parameters
        ----------
        exc_type
        exc_value
        traceback

        Returns
        -------

        """
        self.cleanup()

    def cleanup(self) -> None:
        """
        Manually trigger cleanup and unregister the finalizer.
        Returns
        -------

        """
        if self._finalizer.detach() or self._temp_dir.exists():
            self._temp_dir.rm(recursive=True)


class EOTemporaryFolder(metaclass=Singleton):
    """
    This singleton will retain a temporary folder during all the execution if not cleared

    """

    def __init__(self, prefix: str = "eoptmp-") -> None:
        self._logger = EOLogging().get_logger("eopf.temporary_folder")
        self._s3_secret = (
            EOConfiguration().temporary__folder_s3_secret
            if EOConfiguration().has_value("temporary__folder_s3_secret")
            else None
        )
        self._s3_storage = EOConfiguration().secrets(self._s3_secret) if self._s3_secret is not None else {}
        self._base_anypath = AnyPath.cast(EOConfiguration().temporary__folder, **self._s3_storage)
        if not self._base_anypath.isdir():
            if not bool(EOConfiguration().temporary__folder_create_folder):
                raise ValueError(
                    "Temporary base folder EOConfiguration().temporary__folder : {EOConfiguration().temporary__folder}"
                    " doesn't point to an existing folder, use EOConfiguration().temporary__folder_create_folder"
                    " if you want to create it automatically ",
                )
            self._base_anypath.mkdir()
        if self._base_anypath.islocal():
            self._logger.debug(f"Creating local temporary folder in {self._base_anypath}")
            self._tmp_dir: TemporaryDirectory[str] | S3TemporaryDirectory = TemporaryDirectory(
                dir=self._base_anypath.path,
                prefix=prefix,
            )
            self._user_anypath = AnyPath.cast(self._tmp_dir.name)
        else:
            self._logger.debug(f"Creating S3 temporary folder in {self._base_anypath}")
            self._tmp_dir = S3TemporaryDirectory(directory=self._base_anypath, prefix="eotmp-")
            self._user_anypath = AnyPath.cast(self._tmp_dir.name)
        self._logger.debug(f"Temporary folder is {self._user_anypath}")
        self._finalizer = weakref.finalize(
            self,
            self._cleanup,
            self._tmp_dir,
            warn_message=f"Implicitly cleaning up {self}",
        )

    def get(self) -> AnyPath:
        return self._user_anypath

    def get_uuid_subfolder(self) -> AnyPath:
        return (self._user_anypath / str(uuid.uuid4())).mkdir()

    @classmethod
    def _cleanup(cls, tmp_dir: TemporaryDirectory[str] | S3TemporaryDirectory, warn_message: str) -> None:
        tmp_dir.cleanup()
        warnings.warn(warn_message, ResourceWarning)

    def cleanup(self) -> None:
        if self._finalizer.detach() or self._user_anypath.exists():
            self._tmp_dir.cleanup()


class EOLocalTemporaryFolder(metaclass=Singleton):
    """
    This singleton will retain a local temporary folder during all the execution if not cleared

    """

    def __init__(self, prefix: str = "eoptmp-") -> None:
        self._logger = EOLogging().get_logger("eopf.temporary__folder_local")
        self._base_anypath = AnyPath.cast(EOConfiguration().temporary__folder_local)
        if not self._base_anypath.isdir():
            if not bool(EOConfiguration().temporary__folder_create_folder):
                raise ValueError(
                    "Temporary base folder EOConfiguration().temporary__folder : {EOConfiguration().temporary__folder}"
                    " doesn't point to an existing folder, use EOConfiguration().temporary__folder_create_folder"
                    " if you want to create it automatically ",
                )
            self._base_anypath.mkdir()
        if self._base_anypath.islocal():
            self._logger.debug(f"Creating local temporary folder in {self._base_anypath}")
            self._tmp_dir: TemporaryDirectory[str] | S3TemporaryDirectory = TemporaryDirectory(
                dir=self._base_anypath.path,
                prefix=prefix,
            )
            self._user_anypath = AnyPath.cast(self._tmp_dir.name)
        else:
            raise ValueError("Only local folder accepted")
        self._logger.debug(f"Temporary local folder is {self._user_anypath}")
        self._finalizer = weakref.finalize(
            self,
            self._cleanup,
            self._tmp_dir,
            warn_message=f"Implicitly cleaning up {self}",
        )

    def get(self) -> AnyPath:
        return self._user_anypath

    def get_uuid_subfolder(self) -> AnyPath:
        return (self._user_anypath / str(uuid.uuid4())).mkdir()

    @classmethod
    def _cleanup(cls, tmp_dir: TemporaryDirectory[str] | S3TemporaryDirectory, warn_message: str) -> None:
        tmp_dir.cleanup()
        warnings.warn(warn_message, ResourceWarning)

    def cleanup(self) -> None:
        if self._finalizer.detach() or self._user_anypath.exists():
            self._tmp_dir.cleanup()
