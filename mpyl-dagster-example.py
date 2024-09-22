from pathlib import Path

from dagster import (
    config_from_files,
    op,
    DynamicOut,
    DynamicOutput,
    get_dagster_logger,
    Output,
    Failure,
    job,
)

from mpyl.project import load_project
from mpyl.project_execution import ProjectExecution
from mpyl.stages.discovery import find_projects_to_execute
from mpyl.steps import build, test, deploy, IPluginRegistry
from mpyl.steps.collection import StepsCollection
from mpyl.steps.run_properties import construct_run_properties
from mpyl.steps.steps import Steps, StepResult
from mpyl.utilities.pyaml_env import parse_config
from mpyl.utilities.repo import Repository, RepoConfig
from cicd.steps.docker import AssembleDocker
from cicd.steps.gradle import BuildGradle, TestGradle

ROOT_PATH = "./"

IPluginRegistry.plugins.append(BuildGradle)
IPluginRegistry.plugins.append(AssembleDocker)
IPluginRegistry.plugins.append(TestGradle)


def execute_step(proj: ProjectExecution, stage: str, dry_run: bool = True) -> StepResult:
    config = parse_config(Path(f"{ROOT_PATH}mpyl_config.yml"))
    properties = parse_config(Path(f"{ROOT_PATH}run_properties.yml"))
    run_properties = construct_run_properties(
        config=config, properties=properties, run_plan=None, explain_run_plan=True
    )
    dagster_logger = get_dagster_logger()
    executor = Steps(dagster_logger, run_properties)
    step_result = executor.execute(stage, proj, dry_run)
    if not step_result.output.success:
        raise Failure(description=step_result.output.message)
    return step_result


@op(description="Build stage. Build steps produce a docker image")
def build_project(context, project: ProjectExecution) -> Output:
    return Output(execute_step(project, build.STAGE_NAME))


@op(description="Test stage. Test steps produce junit compatible test results")
def test_project(context, project) -> Output:
    return Output(execute_step(project, test.STAGE_NAME))


@op(
    description="Deploy a project to the target specified in the step",
    config_schema={"dry_run": bool},
)
def deploy_project(context, project: ProjectExecution) -> Output:
    dry_run: bool = context.op_config["dry_run"]
    return Output(execute_step(project, deploy.STAGE_NAME, dry_run))


@op(
    description="Deploy all artifacts produced over all runs of the pipeline",
    config_schema={"simulate_deploy": bool},
)
def deploy_projects(
        context, projects: list[ProjectExecution], outputs: list[StepResult]
) -> Output[list[StepResult]]:
    simulate_deploy: bool = context.op_config["simulate_deploy"]
    res = []
    if simulate_deploy:
        for proj in projects:
            res.append(execute_step(proj, deploy.STAGE_NAME))
    else:
        get_dagster_logger().info(f"Not deploying {projects}")
    return Output(res)


def find_projects(stage: str) -> list[DynamicOutput[ProjectExecution]]:
    yaml_values = parse_config(Path(f"{ROOT_PATH}mpyl_config.yml"))
    with Repository(RepoConfig.from_config(yaml_values)) as repo:
        changes_in_branch = repo.changes_in_branch_including_local()
        project_paths = repo.find_projects()
    all_projects = set(
        map(lambda p: load_project(Path("."), Path(p), strict=False), project_paths)
    )
    dagster_logger = get_dagster_logger()
    dagster_logger.info(f"{project_paths} -> {all_projects}")
    steps = StepsCollection(logger=dagster_logger)
    project_executions = find_projects_to_execute(
        logger=dagster_logger,
        all_projects=all_projects,
        stage=stage,
        changeset=changes_in_branch,
        steps=steps,
    )
    return [DynamicOutput(ex, mapping_key=ex.name.replace("-", "_")) for ex in project_executions if not ex.cached]


@op(out=DynamicOut(), description="Find artifacts that need to be built")
def find_build_projects() -> list[DynamicOutput[ProjectExecution]]:
    return find_projects(build.STAGE_NAME)


@op(out=DynamicOut(), description="Find artifacts that need to be tested")
def find_test_projects(_projects) -> list[DynamicOutput[ProjectExecution]]:
    return find_projects(test.STAGE_NAME)


@op(out=DynamicOut(), description="Find artifacts that need to be deployed")
def find_deploy_projects(_projects) -> list[DynamicOutput[ProjectExecution]]:
    return find_projects(deploy.STAGE_NAME)


@job(config=config_from_files(["mpyl-dagster-example.yml"]))
def run_build():
    build_projects = find_build_projects()
    build_results = build_projects.map(build_project)

    test_projects = find_test_projects(build_results.collect())
    test_results = test_projects.map(test_project)

    projects_to_deploy = find_deploy_projects(test_projects.collect())

    deploy_projects(
        projects=projects_to_deploy.collect(), outputs=test_results.collect()
    )
