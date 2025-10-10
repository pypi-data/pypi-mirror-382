"""JS DAPI validator module"""

from __future__ import annotations

from typing import List

from opendapi.config import construct_project_full_path, get_project_path_from_full_path
from opendapi.models import OverrideConfig
from opendapi.utils import find_files_with_suffix
from opendapi.validators.dapi.base.main import BaseDapiValidator
from opendapi.validators.dapi.models import PackageScopedProjectInfo


class JsProjectsDapiValidatorBase(BaseDapiValidator):
    """Base class for DAPI validators that are scoped to packages."""

    PACKAGE_JSON: str = "package.json"
    LOOKUP_FILE_SUFFIXES: List[str] = NotImplementedError

    def get_all_projects(self) -> List[PackageScopedProjectInfo]:
        """Get all package.json files in the project."""
        package_file = f"/{self.settings.artifact_path or self.PACKAGE_JSON}"
        files = find_files_with_suffix(self.root_dir, [package_file])
        packages = [filename.replace(package_file, "") for filename in files]

        if self.settings.include_all:
            projects = [
                PackageScopedProjectInfo(
                    org_name_snakecase=self.config.org_name_snakecase,
                    override=OverrideConfig(
                        project_path=get_project_path_from_full_path(
                            self.root_dir, package
                        )
                    ),
                    root_path=self.root_dir,
                    full_path=package,
                )
                for package in packages
            ]
        else:
            projects = []

        for override in self.settings.overrides:
            full_path = construct_project_full_path(
                self.root_dir, override.project_path
            )
            if full_path not in packages:
                continue

            project = PackageScopedProjectInfo(
                org_name_snakecase=self.config.org_name_snakecase,
                override=override,
                root_path=self.root_dir,
                full_path=construct_project_full_path(
                    self.root_dir, override.project_path
                ),
            )
            projects.append(project)

        # Update the file contents in the projects
        for project in projects:
            pkg_files = find_files_with_suffix(
                project.full_path, self.LOOKUP_FILE_SUFFIXES
            )
            for filename in pkg_files:
                with open(filename, encoding="utf-8") as f:
                    project.file_contents[filename] = f.read()

        return projects
