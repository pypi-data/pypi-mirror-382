from dataclasses import fields
from typing import Any, Dict, List, Optional, Union

from dooservice.core.domain.entities.configuration import (
    AutoBackup,
    Backup,
    BackupFormat,
    BaseDomain,
    CloudflareProvider,
    CloudflareTunnel,
    Deployment,
    DeploymentType,
    DockerContainer,
    DockerDeployment,
    Domain,
    DomainsConfig,
    DooServiceConfiguration,
    EnvVars,
    Frequency,
    GitHubConfig,
    GitHubIntegration,
    GitHubOAuth,
    GitHubWatcher,
    GitHubWebhook,
    HealthCheck,
    Instance,
    InstanceAutoBackup,
    InstanceSnapshot,
    Paths,
    Ports,
    Repository,
    RepositoryType,
    RestartPolicy,
    Retention,
    Schedule,
    Snapshot,
    SnapshotRetention,
    SourceType,
    SSLProvider,
    SSLProviderConfig,
)


class ConfigurationMapper:
    def __init__(self):
        self._enum_mappings = {
            "DeploymentType": DeploymentType,
            "SourceType": SourceType,
            "RepositoryType": RepositoryType,
            "SSLProvider": SSLProvider,
            "BackupFormat": BackupFormat,
            "Frequency": Frequency,
            "RestartPolicy": RestartPolicy,
        }

    def map_from_dict(self, data: Dict[str, Any]) -> DooServiceConfiguration:
        return DooServiceConfiguration(
            version=data.get("version", "1.0"),
            domains=self._map_domains_config(data.get("domains", {})),
            backup=self._map_backup(data.get("backup", {})),
            snapshot=self._map_snapshot(data.get("snapshot", {})),
            github=self._map_github_integration(data.get("github", {})),
            repositories=self._map_repositories_dict(data.get("repositories", {})),
            instances=self._map_instances_dict(data.get("instances", {})),
        )

    def _map_domains_config(self, data: Dict[str, Any]) -> DomainsConfig:
        return DomainsConfig(
            default_provider=self._parse_enum(
                data.get("default_provider", "letsencrypt"), SSLProvider
            ),
            default_ssl=data.get("default_ssl", True),
            default_force_ssl=data.get("default_force_ssl", True),
            default_redirect_www=data.get("default_redirect_www", False),
            default_hsts=data.get("default_hsts", True),
            providers=self._map_ssl_providers(data.get("providers", {})),
            base_domains=self._map_base_domains(data.get("base_domains", {})),
            cloudflare=(
                self._map_cloudflare_provider(
                    data.get("providers", {}).get("cloudflare")
                )
                if "providers" in data and "cloudflare" in data["providers"]
                else None
            ),
        )

    def _map_ssl_providers(self, data: Dict[str, Any]) -> Dict[str, SSLProviderConfig]:
        providers = {}
        for name, config in data.items():
            providers[name] = SSLProviderConfig(
                email=config.get("email"),
                api_token=config.get("api_token"),
                zone_id=config.get("zone_id"),
                api_key=config.get("api_key"),
            )
        return providers

    def _map_base_domains(
        self, data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, BaseDomain]:
        domains = {}
        for domain_name, domain_data in data.items():
            domains[domain_name] = BaseDomain(
                name=domain_name,
                instance=domain_data.get("instance", ""),
                ssl_provider=self._parse_enum_optional(
                    domain_data.get("ssl_provider"), SSLProvider
                ),
                ssl=domain_data.get("ssl", True),
                force_ssl=domain_data.get("force_ssl", True),
                redirect_www=domain_data.get("redirect_www", False),
                hsts=domain_data.get("hsts", True),
                cname_target=domain_data.get("cname_target"),
                dns_challenge=domain_data.get("dns_challenge", False),
            )
        return domains

    def _map_cloudflare_provider(self, data: Dict[str, Any]) -> CloudflareProvider:
        tunnels = {}
        for tunnel_name, tunnel_data in data.get("tunnels", {}).items():
            tunnels[tunnel_name] = CloudflareTunnel(
                zone_id=tunnel_data.get("zone_id", ""),
                domain=tunnel_data.get("domain", ""),
                enabled=tunnel_data.get("enabled", True),
            )

        return CloudflareProvider(
            api_token=data.get("api_token", ""),
            account_id=data.get("account_id", ""),
            tunnels=tunnels,
        )

    def _map_backup(self, data: Dict[str, Any]) -> Backup:
        return Backup(
            enabled=data.get("enabled", True),
            output_dir=data.get("output_dir", "/opt/dooservice/backups"),
            format=self._parse_enum(data.get("format", "zip"), BackupFormat),
            retention=self._map_retention(data.get("retention", {})),
            auto_backup=self._map_auto_backup(data.get("auto_backup", {})),
        )

    def _map_retention(self, data: Dict[str, Any]) -> Retention:
        return Retention(
            days=data.get("days", 30), max_backups=data.get("max_backups", 10)
        )

    def _map_auto_backup(self, data: Dict[str, Any]) -> AutoBackup:
        return AutoBackup(
            enabled=data.get("enabled", False),
            format=self._parse_enum(data.get("format", "zip"), BackupFormat),
            schedule=(
                self._map_schedule(data.get("schedule")) if "schedule" in data else None
            ),
        )

    def _map_schedule(self, data: Dict[str, Any]) -> Schedule:
        return Schedule(
            frequency=self._parse_enum(data.get("frequency", "daily"), Frequency),
            time=data.get("time", "02:00"),
        )

    def _map_snapshot(self, data: Dict[str, Any]) -> Snapshot:
        return Snapshot(
            enabled=data.get("enabled", True),
            default_storage_dir=data.get(
                "default_storage_dir", "/opt/dooservice/snapshots"
            ),
            retention=self._map_snapshot_retention(data.get("retention", {})),
        )

    def _map_snapshot_retention(self, data: Dict[str, Any]) -> SnapshotRetention:
        return SnapshotRetention(
            days=data.get("days", 60), max_snapshots=data.get("max_snapshots", 100)
        )

    def _map_github_integration(self, data: Dict[str, Any]) -> GitHubIntegration:
        return GitHubIntegration(
            enabled=data.get("enabled", True),
            oauth=self._map_github_oauth(data.get("oauth", {})),
            webhook=self._map_github_webhook(data.get("webhook", {})),
        )

    def _map_github_oauth(self, data: Dict[str, Any]) -> GitHubOAuth:
        return GitHubOAuth(
            client_id=data.get("client_id", ""),
            client_secret=data.get("client_secret", ""),
            redirect_uri=data.get(
                "redirect_uri", "http://localhost:8080/auth/callback"
            ),
            scopes=data.get("scopes", ["repo", "read:user", "admin:public_key"]),
        )

    def _map_github_webhook(self, data: Dict[str, Any]) -> GitHubWebhook:
        return GitHubWebhook(
            enabled=data.get("enabled", True),
            default_host=data.get("default_host", "localhost"),
            default_port=data.get("default_port", 8080),
            default_secret=data.get("default_secret", ""),
            auto_start=data.get("auto_start", False),
        )

    def _map_repositories_dict(self, data: Dict[str, Any]) -> Dict[str, Repository]:
        repositories = {}
        for name, repo_data in data.items():
            repositories[name] = self._map_repository(repo_data)
        return repositories

    def _map_repository(self, data: Dict[str, Any]) -> Repository:
        return Repository(
            source_type=self._parse_enum(data.get("source_type", "git"), SourceType),
            path=data.get("path", ""),
            type=self._parse_enum(data.get("type", "git"), RepositoryType),
            url=data.get("url", ""),
            branch=data.get("branch", "main"),
            ssh_key_path=data.get("ssh_key_path", ""),
            submodules=data.get("submodules", False),
            github=(
                self._map_github_config(data.get("github"))
                if "github" in data
                else None
            ),
        )

    def _map_github_config(self, data: Dict[str, Any]) -> GitHubConfig:
        return GitHubConfig(
            auto_watch=data.get("auto_watch", True),
            default_action=data.get("default_action", "pull+restart"),
            watchers=self._map_github_watchers(data.get("watchers", [])),
            exclude_instances=data.get("exclude_instances", []),
        )

    def _map_github_watchers(self, data: List[Dict[str, Any]]) -> List[GitHubWatcher]:
        return [
            GitHubWatcher(
                instance=watcher_data.get("instance", ""),
                action=watcher_data.get("action", "pull+restart"),
                enabled=watcher_data.get("enabled", True),
            )
            for watcher_data in data
        ]

    def _map_instances_dict(self, data: Dict[str, Any]) -> Dict[str, Instance]:
        instances = {}
        for name, instance_data in data.items():
            instances[name] = self._map_instance(instance_data)
        return instances

    def _map_instance(self, data: Dict[str, Any]) -> Instance:
        return Instance(
            odoo_version=data.get("odoo_version", "17.0"),
            data_dir=data.get("data_dir", ""),
            paths=self._map_paths(data.get("paths", {})),
            ports=self._map_ports(data.get("ports", {})),
            env_vars=self._map_env_vars(data.get("env_vars", {})),
            domain=self._map_domain(data.get("domain", {})),
            deployment=self._map_deployment(data.get("deployment", {})),
            auto_backup=self._map_instance_auto_backup(data.get("auto_backup", {})),
            repositories=self._map_instance_repositories(data.get("repositories", {})),
            python_dependencies=data.get("python_dependencies", []),
            snapshot=self._map_instance_snapshot(data.get("snapshot", {})),
        )

    def _map_paths(self, data: Dict[str, Any]) -> Paths:
        return Paths(
            config=data.get("config", ""),
            addons=data.get("addons", ""),
            logs=data.get("logs", ""),
            filestore=data.get("filestore", ""),
        )

    def _map_ports(self, data: Dict[str, Any]) -> Ports:
        return Ports(
            http=str(data.get("http", "")), longpolling=str(data.get("longpolling", ""))
        )

    def _map_env_vars(self, data: Dict[str, Any]) -> EnvVars:
        return EnvVars(
            **{
                field.name: data.get(field.name)
                for field in fields(EnvVars)
                if field.name in data
            }
        )

    def _map_domain(self, data: Dict[str, Any]) -> Domain:
        return Domain(
            base=data.get("base", ""),
            subdomain=data.get("subdomain", ""),
            use_root_domain=data.get("use_root_domain", False),
        )

    def _map_deployment(self, data: Dict[str, Any]) -> Deployment:
        return Deployment(
            type=self._parse_enum(data.get("type", "docker"), DeploymentType),
            docker=(
                self._map_docker_deployment(data.get("docker"))
                if "docker" in data
                else None
            ),
        )

    def _map_docker_deployment(self, data: Dict[str, Any]) -> DockerDeployment:
        return DockerDeployment(
            web=self._map_docker_container(data.get("web", {})),
            db=self._map_docker_container(data.get("db")) if "db" in data else None,
        )

    def _map_docker_container(self, data: Dict[str, Any]) -> DockerContainer:
        return DockerContainer(
            image=data.get("image", ""),
            container_name=data.get("container_name", ""),
            restart_policy=self._parse_enum(
                data.get("restart_policy", "no"), RestartPolicy
            ),
            volumes=data.get("volumes", []),
            networks=data.get("networks", []),
            environment=data.get("environment", {}),
            ports=data.get("ports", []),
            depends_on=data.get("depends_on", []),
            healthcheck=(
                self._map_healthcheck(data.get("healthcheck"))
                if "healthcheck" in data
                else None
            ),
        )

    def _map_healthcheck(self, data: Dict[str, Any]) -> HealthCheck:
        return HealthCheck(
            test=data.get("test", []),
            interval=data.get("interval", "30s"),
            timeout=data.get("timeout", "30s"),
            retries=data.get("retries", 3),
            start_period=data.get("start_period", "0s"),
        )

    def _map_instance_auto_backup(self, data: Dict[str, Any]) -> InstanceAutoBackup:
        return InstanceAutoBackup(
            enabled=data.get("enabled", True), db_name=data.get("db_name", "")
        )

    def _map_instance_snapshot(self, data: Dict[str, Any]) -> InstanceSnapshot:
        return InstanceSnapshot(
            enabled=data.get("enabled", True),
            storage_dir=data.get("storage_dir", ""),
            include_backup_by_default=data.get("include_backup_by_default", True),
            retention=self._map_snapshot_retention(data.get("retention", {})),
        )

    def _map_instance_repositories(
        self, data: Union[Dict[str, Any], List[str]]
    ) -> Dict[str, Repository]:
        if isinstance(data, list):
            # Handle list of repository names (references to global repositories)
            repositories = {}
            for repo_name in data:
                # Create a minimal repository reference
                repositories[repo_name] = Repository(
                    source_type=SourceType.GIT,
                    path=f"${{data_dir}}/repos/{repo_name}",
                    type=RepositoryType.GITHUB,
                    url="",  # Will be resolved from global repositories
                    branch="main",
                )
            return repositories
        if isinstance(data, dict):
            # Handle dictionary of repository definitions
            return self._map_repositories_dict(data)
        return {}

    def _parse_enum(self, value: str, enum_class) -> Any:
        try:
            return enum_class(value)
        except ValueError:
            return list(enum_class)[0]  # Return first enum value as default

    def _parse_enum_optional(self, value: Optional[str], enum_class) -> Optional[Any]:
        if value is None:
            return None
        try:
            return enum_class(value)
        except ValueError:
            return None
