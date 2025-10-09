from re import L
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.runtime import get_runtime, Runtime
from langchain.tools.tool_node import InjectedState
from typing import Annotated, Any
from deepagents.state import Todo, FilesystemState
from deepagents.prompts import (
    WRITE_TODOS_TOOL_DESCRIPTION,
    LIST_FILES_TOOL_DESCRIPTION,
    READ_FILE_TOOL_DESCRIPTION,
    WRITE_FILE_TOOL_DESCRIPTION,
    EDIT_FILE_TOOL_DESCRIPTION,
    LIST_FILES_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT,
    READ_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT,
    WRITE_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT,
    EDIT_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT,
)

def has_memories_prefix(file_path: str) -> bool:
    return file_path.startswith("memories/")

def append_memories_prefix(file_path: str) -> str:
    return f"memories/{file_path}"

def strip_memories_prefix(file_path: str) -> str:
    return file_path.replace("memories/", "")

def get_namespace(runtime: Runtime[Any]) -> tuple[str, str]:
    namespace = ("filesystem")
    if runtime.context is None:
        return namespace
    assistant_id = runtime.context.get("assistant_id")
    if assistant_id is None:
        return namespace
    return (assistant_id, "filesystem")

@tool(description=WRITE_TODOS_TOOL_DESCRIPTION)
def write_todos(
    todos: list[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(f"Updated todo list to {todos}", tool_call_id=tool_call_id)
            ],
        }
    )

def ls_tool_generator(has_longterm_memory: bool, custom_description: str = None) -> tool:
    tool_description = LIST_FILES_TOOL_DESCRIPTION
    if custom_description:
        tool_description = custom_description
    elif has_longterm_memory:
        tool_description += LIST_FILES_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT

    if has_longterm_memory:
        # Tool with Long-term memory
        @tool(description=tool_description)
        def ls(state: Annotated[FilesystemState, InjectedState]) -> list[str]:
            files = []
            files.extend(list(state.get("files", {}).keys()))

            runtime = get_runtime()
            store = runtime.store
            if store is None: 
                raise ValueError("Longterm memory is enabled, but no store is available")
            namespace = get_namespace(runtime)
            file_data_list = store.search(namespace)
            memories_files = [append_memories_prefix(f.key) for f in file_data_list]
            files.extend(memories_files)
            return files
    else:
        # Tool without long-term memory
        @tool(description=tool_description)
        def ls(state: Annotated[FilesystemState, InjectedState]) -> list[str]:
            files = list(state.get("files", {}).keys())
            return files
    return ls
    

def read_file_tool_generator(has_longterm_memory: bool, custom_description: str = None) -> tool:
    tool_description = READ_FILE_TOOL_DESCRIPTION
    if custom_description:
        tool_description = custom_description
    elif has_longterm_memory:
        tool_description += READ_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT

    if has_longterm_memory:
        # Tool with Long-term memory
        @tool(description=tool_description)
        def read_file(
            file_path: str,
            state: Annotated[FilesystemState, InjectedState],
            offset: int = 0,
            limit: int = 2000,
        ) -> str:
            if has_memories_prefix(file_path):
                stripped_file_path = strip_memories_prefix(file_path)
                runtime = get_runtime()
                store = runtime.store
                if store is None:
                    raise ValueError("Longterm memory is enabled, but no store is available")
                namespace = get_namespace(runtime)
                item = store.get(namespace, stripped_file_path)
                if item is None:
                    return f"Error: File '{file_path}' not found"
                content = item.value
            else: 
                mock_filesystem = state.get("files", {})
                if file_path not in mock_filesystem:
                    return f"Error: File '{file_path}' not found"
                content = mock_filesystem[file_path]
            if not content or content.strip() == "":
                return "System reminder: File exists but has empty contents"
            lines = content.splitlines()
            start_idx = offset
            end_idx = min(start_idx + limit, len(lines))
            if start_idx >= len(lines):
                return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"
            result_lines = []
            for i in range(start_idx, end_idx):
                line_content = lines[i]
                if len(line_content) > 2000:
                    line_content = line_content[:2000]
                line_number = i + 1
                result_lines.append(f"{line_number:6d}\t{line_content}")

            return "\n".join(result_lines)
    else:
        # Tool without long-term memory
        @tool(description=tool_description)
        def read_file(
            file_path: str,
            state: Annotated[FilesystemState, InjectedState],
            offset: int = 0,
            limit: int = 2000,
        ) -> str:
            mock_filesystem = state.get("files", {})
            if file_path not in mock_filesystem:
                return f"Error: File '{file_path}' not found"
            content = mock_filesystem[file_path]
            if not content or content.strip() == "":
                return "System reminder: File exists but has empty contents"
            lines = content.splitlines()
            start_idx = offset
            end_idx = min(start_idx + limit, len(lines))
            if start_idx >= len(lines):
                return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"
            result_lines = []
            for i in range(start_idx, end_idx):
                line_content = lines[i]
                if len(line_content) > 2000:
                    line_content = line_content[:2000]
                line_number = i + 1
                result_lines.append(f"{line_number:6d}\t{line_content}")

            return "\n".join(result_lines)
    return read_file


def write_file_tool_generator(has_longterm_memory: bool, custom_description: str = None) -> tool:
    tool_description = WRITE_FILE_TOOL_DESCRIPTION
    if custom_description:
        tool_description = custom_description
    elif has_longterm_memory:
        tool_description += WRITE_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT

    if has_longterm_memory:
        # Tool with Long-term memory
        @tool(description=tool_description)
        def write_file(file_path: str, content: str, state: Annotated[FilesystemState, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
            if has_memories_prefix(file_path):
                stripped_file_path = strip_memories_prefix(file_path)
                runtime = get_runtime()
                store = runtime.store
                if store is None:
                    raise ValueError("Longterm memory is enabled, but no store is available")
                namespace = get_namespace(runtime)
                store.put(namespace, stripped_file_path, content)
                return Command(
                    update={
                        "messages": [ToolMessage(f"Updated longterm memories file {file_path}", tool_call_id=tool_call_id)]
                    }
                )
            else:
                mock_filesystem = state.get("files", {})
                mock_filesystem[file_path] = content
                return Command(
                    update={
                        "files": mock_filesystem,
                        "messages": [ToolMessage(f"Updated file {file_path}", tool_call_id=tool_call_id)]
                    }
                )
    else:
        # Tool without long-term memory
        @tool(description=tool_description)
        def write_file(file_path: str, content: str, state: Annotated[FilesystemState, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
            mock_filesystem = state.get("files", {})
            mock_filesystem[file_path] = content
            return Command(
                update={
                    "files": mock_filesystem,
                    "messages": [ToolMessage(f"Updated file {file_path}", tool_call_id=tool_call_id)]
                }
            )
    return write_file


def edit_file_tool_generator(has_longterm_memory: bool, custom_description: str = None) -> tool:
    tool_description = EDIT_FILE_TOOL_DESCRIPTION
    if custom_description:
        tool_description = custom_description
    elif has_longterm_memory:
        tool_description += EDIT_FILE_TOOL_DESCRIPTION_LONGTERM_SUPPLEMENT

    if has_longterm_memory:
        # Tool with Long-term memory
        @tool(description=tool_description)
        def edit_file(file_path: str, old_string: str, new_string: str, state: Annotated[FilesystemState, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId], replace_all: bool = False) -> Command:
            if has_memories_prefix(file_path):
                stripped_file_path = strip_memories_prefix(file_path)
                runtime = get_runtime()
                store = runtime.store
                if store is None:
                    raise ValueError("Longterm memory is enabled, but no store is available")
                namespace = get_namespace(runtime)
                item = store.get(namespace, stripped_file_path)
                if item is None:
                    return f"Error: File '{file_path}' not found"
                content = item.value
                if old_string not in content:
                    return f"Error: String not found in file: '{old_string}'"
                if not replace_all:
                    occurrences = content.count(old_string)
                    if occurrences > 1:
                        return f"Error: String '{old_string}' appears {occurrences} times in file. Use replace_all=True to replace all instances, or provide a more specific string with surrounding context."
                    elif occurrences == 0:
                        return f"Error: String not found in file: '{old_string}'"
                new_content = content.replace(old_string, new_string)
                replacement_count = content.count(old_string)
                store.put(namespace, stripped_file_path, new_content)
                return Command(
                    update={
                        "messages": [ToolMessage(f"Successfully replaced {replacement_count} instance(s) of the string in '{file_path}'", tool_call_id=tool_call_id)]
                    }
                )
            else:
                mock_filesystem = state.get("files", {})
                if file_path not in mock_filesystem:
                    return f"Error: File '{file_path}' not found"
                content = mock_filesystem[file_path]
                if old_string not in content:
                    return f"Error: String not found in file: '{old_string}'"
                if not replace_all:
                    occurrences = content.count(old_string)
                    if occurrences > 1:
                        return f"Error: String '{old_string}' appears {occurrences} times in file. Use replace_all=True to replace all instances, or provide a more specific string with surrounding context."
                    elif occurrences == 0:
                        return f"Error: String not found in file: '{old_string}'"
                new_content = content.replace(old_string, new_string)
                replacement_count = content.count(old_string)
                result_msg = f"Successfully replaced {replacement_count} instance(s) of the string in '{file_path}'"
                mock_filesystem[file_path] = new_content
                return Command(
                    update={
                        "files": mock_filesystem,
                        "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
                    }
                )
    else:
        # Tool without long-term memory
        @tool(description=tool_description)
        def edit_file(file_path: str, old_string: str, new_string: str, state: Annotated[FilesystemState, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId], replace_all: bool = False) -> Command:
            mock_filesystem = state.get("files", {})
            if file_path not in mock_filesystem:
                return f"Error: File '{file_path}' not found"
            content = mock_filesystem[file_path]
            if old_string not in content:
                return f"Error: String not found in file: '{old_string}'"
            if not replace_all:
                occurrences = content.count(old_string)
                if occurrences > 1:
                    return f"Error: String '{old_string}' appears {occurrences} times in file. Use replace_all=True to replace all instances, or provide a more specific string with surrounding context."
                elif occurrences == 0:
                    return f"Error: String not found in file: '{old_string}'"
            new_content = content.replace(old_string, new_string)
            replacement_count = content.count(old_string)
            result_msg = f"Successfully replaced {replacement_count} instance(s) of the string in '{file_path}'"
            mock_filesystem[file_path] = new_content
            return Command(
                update={
                    "files": mock_filesystem,
                    "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
                }
            )
    return edit_file

TOOL_GENERATORS = {
    "ls": ls_tool_generator,
    "read_file": read_file_tool_generator,
    "write_file": write_file_tool_generator,
    "edit_file": edit_file_tool_generator,
}

def get_filesystem_tools(has_longterm_memory: bool, custom_tool_descriptions: dict[str, str] = {}) -> list[tool]:
    tools = []
    for tool_name, tool_generator in TOOL_GENERATORS.items():
        tool = tool_generator(has_longterm_memory, custom_tool_descriptions.get(tool_name, None))
        tools.append(tool)
    return tools