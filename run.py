
from mpyl import main_group, add_commands
from mpyl.steps import IPluginRegistry

from steps.gradle import BuildGradle, TestGradle

IPluginRegistry.plugins.append(BuildGradle)
IPluginRegistry.plugins.append(TestGradle)

add_commands()
main_group(["build", "-c", "mpyl_config.yml", "run", "--ci"], standalone_mode=False)
