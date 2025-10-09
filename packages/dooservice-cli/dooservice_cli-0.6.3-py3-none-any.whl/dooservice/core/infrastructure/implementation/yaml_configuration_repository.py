from pathlib import Path

from dooservice.core.domain.entities.configuration import DooServiceConfiguration
from dooservice.core.domain.exceptions.configuration_exceptions import (
    ConfigurationFileNotFoundException,
    ConfigurationParsingException,
)
from dooservice.core.domain.repositories.configuration_repository import (
    ConfigurationRepository,
)
from dooservice.core.domain.services.parameter_resolution_service import (
    ParameterResolutionService,
)
from dooservice.core.infrastructure.driven_adapter.configuration_mapper import (
    ConfigurationMapper,
)
from dooservice.core.infrastructure.driven_adapter.yaml_parser import YamlParser


class YamlConfigurationRepository(ConfigurationRepository):
    def __init__(self):
        self._parser = YamlParser()
        self._mapper = ConfigurationMapper()
        self._parameter_resolver = ParameterResolutionService()

    def load_from_file(self, file_path: Path) -> DooServiceConfiguration:
        if not file_path.exists():
            raise ConfigurationFileNotFoundException(str(file_path))

        try:
            yaml_data = self._parser.load_from_file(file_path)

            # Resolve parameters for each instance
            resolved_yaml_data = self._resolve_configuration_parameters(yaml_data)

            return self._mapper.map_from_dict(resolved_yaml_data)

        except Exception as e:
            if isinstance(e, ConfigurationFileNotFoundException):
                raise
            raise ConfigurationParsingException(str(e), str(file_path)) from e

    def save_to_file(
        self, configuration: DooServiceConfiguration, file_path: Path
    ) -> None:
        try:
            yaml_content = self.serialize_to_yaml(configuration)

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(yaml_content)

        except OSError as e:
            raise ConfigurationParsingException(
                f"Error saving configuration: {str(e)}", str(file_path)
            ) from e

    def validate_configuration(self, configuration: DooServiceConfiguration) -> bool:
        return True

    def parse_yaml_content(self, yaml_content: str) -> DooServiceConfiguration:
        try:
            yaml_data = self._parser.parse_yaml_content(yaml_content)

            # Resolve parameters for each instance
            resolved_yaml_data = self._resolve_configuration_parameters(yaml_data)

            return self._mapper.map_from_dict(resolved_yaml_data)

        except (ValueError, TypeError) as e:
            raise ConfigurationParsingException(
                f"Error parsing YAML content: {str(e)}"
            ) from e

    def serialize_to_yaml(self, configuration: DooServiceConfiguration) -> str:
        try:
            return self._parser.serialize_to_yaml(configuration)

        except (ValueError, TypeError) as e:
            raise ConfigurationParsingException(
                f"Error serializing configuration to YAML: {str(e)}"
            ) from e

    def _resolve_configuration_parameters(self, yaml_data: dict) -> dict:
        """
        Resolve all parameter references in the configuration data.

        Args:
            yaml_data: The raw YAML data dictionary

        Returns:
            Configuration data with all parameters resolved
        """
        # Make a deep copy to avoid modifying the original data
        import copy

        resolved_data = copy.deepcopy(yaml_data)

        # Resolve parameters for each instance
        instances = resolved_data.get("instances", {})
        for instance_name, instance_data in instances.items():
            # Resolve parameters for this instance
            resolved_instance_data = (
                self._parameter_resolver.resolve_instance_parameters(
                    instance_name=instance_name,
                    instance_data=instance_data,
                    global_config=resolved_data,
                )
            )

            # Update the instance data with resolved values
            instances[instance_name] = resolved_instance_data

        return resolved_data
