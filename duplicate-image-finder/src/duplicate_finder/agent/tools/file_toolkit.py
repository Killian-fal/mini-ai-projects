from pathlib import Path
from typing import List, Optional
from agno.tools.file import FileTools
from agno.tools._local_file_utils import DEFAULT_EXCLUDE_PATTERNS


class CustomFileTools(FileTools):
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        expose_base_directory: bool = False,
        max_file_length: int = 10000000,
        max_file_lines: int = 100000,
        line_separator: str = "\n",
        exclude_patterns: Optional[List[str]] = None,
        **kwargs,
    ):
        self.base_dir: Path = (base_dir or Path.cwd()).resolve()

        tools = []
        self.max_file_length = max_file_length
        self.max_file_lines = max_file_lines
        self.line_separator = line_separator
        self.expose_base_directory = expose_base_directory
        self.exclude_patterns: List[str] = (
            exclude_patterns
            if exclude_patterns is not None
            else list(DEFAULT_EXCLUDE_PATTERNS)
        )

        tools.append(self.list_workspace_files)
        tools.append(self.search_workspace_files)
        tools.append(self.delete_workspace_file)

        super(FileTools, self).__init__(name="file_tools", tools=tools, **kwargs)

    def search_workspace_files(self, pattern: str) -> str:
        """Searches for files in the workspace directory that match the pattern

        :param pattern: The pattern to search for, e.g. "*.txt", "file*.csv", "**/*.py".
        :return: JSON formatted list of matching file paths, or error message.
        """
        return self.search_files(pattern=pattern)

    def list_workspace_files(self, directory: str | None = ".") -> str:
        """Returns a list of files in the workspace directory
        :param directory: (Optional) name of directory to list.

        :return: The contents of the file if successful, otherwise returns an error message.
        """
        return self.list_files(directory=directory)

    def delete_workspace_file(self, file_name: str) -> str:
        """Deletes a file in the workspace directory
        :param file_name: Name of the file to delete

        :return: Empty string, if operation succeeded, otherwise returns an error message
        """
        return self.delete_file(file_name=file_name)
