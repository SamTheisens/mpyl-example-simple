
from mpyl import main_group, add_commands
from mpyl.steps import IPluginRegistry

from cicd.steps.docker import AssembleDocker
from cicd.steps.gradle import BuildGradle, TestGradle


def build() -> None:
    """CLI entry point."""
    IPluginRegistry.plugins.append(BuildGradle)
    IPluginRegistry.plugins.append(AssembleDocker)
    IPluginRegistry.plugins.append(TestGradle)

    add_commands()
    main_group(["build", "-c", "mpyl_config.yml", "run", "--ci"], standalone_mode=False)
