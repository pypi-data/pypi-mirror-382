# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import unreal
from typing import Optional, Union
from openjd.model import parse_model
from openjd.model.v2023_09 import (
    Environment,
    EnvironmentScript,
)

from deadline.unreal_submitter import settings
from deadline.unreal_submitter.unreal_open_job.unreal_open_job_entity import UnrealOpenJobEntity
from deadline.unreal_submitter.unreal_open_job.unreal_open_job_parameters_consistency import (
    ParametersConsistencyChecker,
)
from deadline.unreal_logger import get_logger


logger = get_logger()


# Base Environment implementation
class UnrealOpenJobEnvironment(UnrealOpenJobEntity):
    """
    Unreal Open Job Environment entity
    """

    def __init__(
        self,
        file_path: Optional[str] = None,
        name: Optional[str] = None,
        variables: Optional[dict[str, str]] = None,
    ):
        """
        :param file_path: The file path of the environment descriptor
        :type file_path: str

        :param name: The name of the environment
        :type name: str

        :param variables: Environment variables as dictionary
        :type variables: dict[str, str]
        """

        super().__init__(Environment, file_path, name)

        self._variables = variables or {}
        self._create_missing_variables_from_template()

    @property
    def variables(self) -> dict[str, str]:
        return self._variables

    @variables.setter
    def variables(self, value: Union[dict[str, str], unreal.Map]):
        self._variables = dict(value)

    @classmethod
    def from_data_asset(cls, data_asset: unreal.DeadlineCloudEnvironment):
        """
        Create the instance of UnrealOpenJobEnvironment from unreal.DeadlineCloudEnvironment

        :param data_asset: unreal.DeadlineCloudEnvironment instance

        :return: UnrealOpenJobEnvironment instance
        :rtype: UnrealOpenJobEnvironment
        """
        return cls(
            file_path=data_asset.path_to_template.file_path,
            name=data_asset.name,
            variables=dict(data_asset.variables.variables),
        )

    def _create_missing_variables_from_template(self):
        """
        Update variables with YAML template data. Mostly needed for custom job submission process.

        If no template file found, skip updating and log warning.
        This is not an error and should not break the building process.
        """
        try:
            template_variables = self.get_template_object().get("variables", {})
            for key, value in template_variables.items():
                if key not in self._variables:
                    self._variables[key] = value
        except FileNotFoundError:
            logger.warning("No template file found to read parameters from.")

    def _check_parameters_consistency(self):
        """
        Check Environment variables consistency

        :return: Result of parameters consistency check
        :rtype: ParametersConsistencyCheckResult
        """
        result = ParametersConsistencyChecker.check_environment_variables_consistency(
            environment_template_path=self.file_path, environment_variables=self._variables
        )
        result.reason = f'OpenJob Environment "{self.name}": ' + result.reason

        return result

    def _build_template(self) -> Environment:
        """
        Build Environment OpenJD model with updated name and variables dictionary
        """
        environment_template_object = self.get_template_object()

        template_dict = {
            "name": self.name,
        }

        script = environment_template_object.get("script")
        if script:
            template_dict["script"] = parse_model(model=EnvironmentScript, obj=script)

        if self._variables:
            template_dict["variables"] = self._variables

        return parse_model(model=self.template_class, obj=template_dict)


# Launch Unreal Editor Environment
class LaunchEditorUnrealOpenJobEnvironment(UnrealOpenJobEnvironment):
    """Predefined Environment for launching the Unreal Editor"""

    default_template_path = settings.LAUNCH_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


# UGS Environments
class UgsUnrealOpenJobEnvironment(UnrealOpenJobEnvironment):
    """Parent class for predefined UGS Environment"""

    pass


class UgsLaunchEditorUnrealOpenJobEnvironment(UgsUnrealOpenJobEnvironment):
    """Predefined Environment for launching the Unreal Editor in UGS case"""

    default_template_path = settings.UGS_LAUNCH_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


class UgsSyncCmfUnrealOpenJobEnvironment(UgsUnrealOpenJobEnvironment):
    """Predefined Environment for syncing the Unreal project via UGS on CMF farm"""

    default_template_path = settings.UGS_SYNC_CMF_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


class UgsSyncSmfUnrealOpenJobEnvironment(UgsUnrealOpenJobEnvironment):
    """Predefined Environment for syncing the Unreal project via UGS on SMF farm"""

    default_template_path = settings.UGS_SYNC_SMF_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


# Perforce (non UGS) Environments
class P4UnrealOpenJobEnvironment(UnrealOpenJobEnvironment):
    pass


class P4LaunchEditorUnrealOpenJobEnvironment(P4UnrealOpenJobEnvironment):
    default_template_path = settings.P4_LAUNCH_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


class P4SyncCmfUnrealOpenJobEnvironment(P4UnrealOpenJobEnvironment):
    default_template_path = settings.P4_SYNC_CMF_ENVIRONMENT_TEMPLATE_DEFAULT_PATH


class P4SyncSmfUnrealOpenJobEnvironment(P4UnrealOpenJobEnvironment):
    default_template_path = settings.P4_SYNC_SMF_ENVIRONMENT_TEMPLATE_DEFAULT_PATH
