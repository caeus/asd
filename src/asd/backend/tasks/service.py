from typing import Final, Protocol

import click
from asd.backend.tasks.planner import TaskPlanner
from asd.backend.tasks.repo import TasksRepo
from asd.backend.tasks.runner import TaskRunnerProvider

from asd.kernel import PlanCmd, QueryCmd, RunCmd


class TasksService(Protocol):
    async def run(self, cmd: RunCmd) -> None: ...
    async def query(self, cmd: QueryCmd) -> None: ...
    async def plan(self, cmd: PlanCmd) -> None: ...


class DefaultTasksService:
    __repo: Final[TasksRepo]
    __planner: Final[TaskPlanner]
    __runner_provider: Final[TaskRunnerProvider]

    def __init__(self,
                 repo: TasksRepo,
                 planner: TaskPlanner,
                 runner_provider: TaskRunnerProvider) -> None:
        self.__repo = repo
        self.__planner = planner
        self.__runner_provider = runner_provider

    async def run(self, cmd: RunCmd) -> None:
        tasks = self.__repo.query(cmd.tasks)
        if len(tasks) == 0:
            raise Exception(f"Query {cmd.tasks} didn't match any task")
        plan = self.__planner(tasks)
        runner = self.__runner_provider()
        await runner(plan)

    async def query(self, cmd: QueryCmd) -> None:
        tasks = self.__repo.query(cmd.tasks)
        for ref in tasks:
            print(ref)

    async def plan(self, cmd: PlanCmd) -> None:
        tasks = self.__repo.query(cmd.tasks)
        if len(tasks) == 0:
            raise Exception(f"Query {cmd.tasks} didn't match any task")
        plan = self.__planner(tasks)
        click.echo(
            "\n".join([
                f"{ref}\n"+(
                    "\n".join([f"  * {dep}" for dep in desc.deps])
                ) for (ref, desc) in plan.items()
            ])
        )

    @classmethod
    def create(cls, repo: TasksRepo,
               planner: TaskPlanner,
               runner_provider: TaskRunnerProvider) -> TasksService:
        return cls(repo=repo,
                   planner=planner,
                   runner_provider=runner_provider)
