from agno.agent import Agent
from agno.models.lmstudio import LMStudio


from duplicate_finder.agent.tools.file_toolkit import CustomFileTools
from duplicate_finder.agent.tools.group_toolkit import GroupToolkit
from duplicate_finder.agent.tools.image_toolkit import ImageToolkit
from duplicate_finder.config import Config


AGENT_INSTRUCTIONS = """\
You help the user manage detected duplicate photo groups in their library.
Reply to the user in the same language they wrote in (typically French).

Available tools (in three toolkits):
- group_toolkit: list_groups, get_group, copy_group
- image_toolkit: list_orphan_images, copy_image
- file_toolkit: list_files, search_files, delete_file => Use them to inspect and manage files in the agent workspace. For example, you can list_files in the workspace to see copied groups and orphans, and delete_file if you want to remove an orphan from the workspace after inspecting it.

Strict rules:
1. Never invent a group_id. If you don't know one, call list_groups first.
2. All `dest` arguments are RELATIVE to the agent workspace. No absolute paths,
   no `..` segments — both will be rejected.
3. For list_orphan_images, paginate (offset += limit) when the user asks for
   "all" orphans and the returned page is incomplete.
4. If a tool returns an error string (e.g. starts with "Unknown", "Refused",
   "Source not found"), report it to the user and STOP. Do not retry with a guess.
5. Be concise: return the tool result and stop. No filler.
"""


def build_agent(
    config: Config, group_toolkit: GroupToolkit, image_toolkit: ImageToolkit
) -> Agent:
    file_toolkit = CustomFileTools(base_dir=config.agent_workspace)

    return Agent(
        name="duplicate-finder-agent",
        id="duplicate_finder_agent",
        model=LMStudio(
            id=config.agent_model_id, base_url=config.agent_url, api_key="lm-studio"
        ),
        tools=[group_toolkit, image_toolkit, file_toolkit],
        instructions=AGENT_INSTRUCTIONS,
        markdown=True,
    )
