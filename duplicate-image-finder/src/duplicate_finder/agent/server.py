from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

from duplicate_finder.agent.agent import build_agent
from duplicate_finder.agent.tools.group_toolkit import GroupToolkit
from duplicate_finder.agent.tools.image_toolkit import ImageToolkit
from duplicate_finder.agent.workspace import ensure_workspace
from duplicate_finder.config import Config
from duplicate_finder.repository.duplicate_group.repository import (
    DuplicateGroupRepository,
)
from duplicate_finder.repository.image.repository import ImageRepository


def build_agent_os(
    config: Config,
    image_repository: ImageRepository,
    group_repository: DuplicateGroupRepository,
) -> AgentOS:
    ensure_workspace(config.agent_workspace)

    group_toolkit = GroupToolkit(
        image_repository, group_repository, config.agent_workspace
    )
    image_toolkit = ImageToolkit(
        image_repository, group_repository, config.agent_workspace
    )

    agent = build_agent(config, group_toolkit, image_toolkit)

    return AgentOS(
        id="duplicate-finder-os",
        description="Manage detected duplicate groups and orphan images.",
        agents=[agent],
        interfaces=[AGUI(agent=agent)],
    )


def run_agent_os(
    config: Config,
    image_repository: ImageRepository,
    group_repository: DuplicateGroupRepository,
) -> None:
    agent_os = build_agent_os(config, image_repository, group_repository)
    app = agent_os.get_app()
    agent_os.serve(app=app, log_level="info")
