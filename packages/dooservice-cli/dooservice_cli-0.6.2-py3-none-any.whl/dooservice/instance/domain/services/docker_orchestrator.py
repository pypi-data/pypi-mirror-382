from typing import Dict, List

from dooservice.core.domain.entities.configuration import DockerContainer, Instance
from dooservice.instance.domain.entities.instance_configuration import (
    InstanceEnvironment,
)


class DockerOrchestrator:
    """Service for orchestrating Docker container operations."""

    def build_docker_compose_config(
        self, instance_env: InstanceEnvironment, instance_config: Instance
    ) -> Dict:
        """Build Docker Compose configuration for an instance."""
        services = {}
        networks = {f"net_{instance_env.name}": {"driver": "bridge"}}

        if instance_config.deployment.docker and instance_config.deployment.docker.web:
            services[f"web_{instance_env.name}"] = self._build_web_service(
                instance_env, instance_config.deployment.docker.web
            )

        if instance_config.deployment.docker and instance_config.deployment.docker.db:
            services[f"db_{instance_env.name}"] = self._build_db_service(
                instance_env, instance_config.deployment.docker.db
            )

        return {"version": "3.8", "services": services, "networks": networks}

    def _build_web_service(
        self, instance_env: InstanceEnvironment, web_config: DockerContainer
    ) -> Dict:
        """Build web service configuration."""
        service = {
            "image": web_config.image,
            "container_name": web_config.container_name,
            "restart": web_config.restart_policy.value,
            "environment": {**web_config.environment, **instance_env.env_vars},
            "volumes": web_config.volumes,
            "ports": web_config.ports,
            "networks": web_config.networks,
            "depends_on": web_config.depends_on,
        }

        if web_config.healthcheck:
            service["healthcheck"] = {
                "test": web_config.healthcheck.test,
                "interval": web_config.healthcheck.interval,
                "timeout": web_config.healthcheck.timeout,
                "retries": web_config.healthcheck.retries,
                "start_period": web_config.healthcheck.start_period,
            }

        return service

    def _build_db_service(
        self, instance_env: InstanceEnvironment, db_config: DockerContainer
    ) -> Dict:
        """Build database service configuration."""
        service = {
            "image": db_config.image,
            "container_name": db_config.container_name,
            "restart": db_config.restart_policy.value,
            "environment": {**db_config.environment, **instance_env.env_vars},
            "volumes": db_config.volumes,
            "ports": db_config.ports,
            "networks": db_config.networks,
        }

        if db_config.healthcheck:
            service["healthcheck"] = {
                "test": db_config.healthcheck.test,
                "interval": db_config.healthcheck.interval,
                "timeout": db_config.healthcheck.timeout,
                "retries": db_config.healthcheck.retries,
                "start_period": db_config.healthcheck.start_period,
            }

        return service

    def get_container_names(self, _: str, instance_config: Instance) -> List[str]:
        """Get list of container names for an instance."""
        container_names = []

        if instance_config.deployment.docker and instance_config.deployment.docker.web:
            container_names.append(instance_config.deployment.docker.web.container_name)

        if instance_config.deployment.docker and instance_config.deployment.docker.db:
            container_names.append(instance_config.deployment.docker.db.container_name)

        return container_names
