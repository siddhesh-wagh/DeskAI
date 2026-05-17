"""
File Operations Skill - Create, search, list, rename, compress, extract and manage files
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any, List
from pathlib import Path
import os
import shutil
import zipfile


# 🔥 Helper function to clean voice input
def clean_filename(text: str) -> str:
    text = text.lower().strip()

    replacements = {
         " dot txt": ".txt",
        " dot pdf": ".pdf",
        " dot zip": ".zip",   
        " dot docx": ".docx",
        " dot dogs": ".docx",
        " dot doc": ".docx",
        " dot": ".",
        " txt": ".txt",
        " pdf": ".pdf",
        " zip": ".zip",      
        " file": ".zip",      
        " doc": ".docx",
        "text file": ".txt"
    }

    for k, v in replacements.items():
        if k in text:
            text = text.replace(k, v)

    return text.strip()


# ================= CREATE FILE =================
class CreateFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = params.get('filename')

        if not filename:
            term = query.lower()

            for keyword in ["create file", "new file", "make file"]:
                term = term.replace(keyword, "")

            term = clean_filename(term)

            if not term:
                return self.success_response("What should I name the file?")

            filename = term

        # Default extension
        if "." not in filename:
            filename += ".txt"

        try:
            filepath = Path.home() / "Desktop" / filename

            with open(filepath, 'w', encoding='utf-8'):
                pass

            return self.success_response(f"File '{filename}' created on Desktop")

        except Exception as e:
            return self.error_response(f"Failed to create file: {e}")


# ================= DELETE FILE =================
class DeleteFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = params.get('filename')

        if not filename:
            term = query.lower()

            for keyword in ["delete file", "remove file", "delete", "remove"]:
                term = term.replace(keyword, "")

            term = clean_filename(term)

            if not term:
                return self.error_response("Say: delete file test.txt")

            filename = term

        try:
            filepath = Path.home() / "Desktop" / filename

            if not filepath.exists():
                return self.error_response(f"File not found: {filename}")

            # 🔥 Simple delete (no dependency)
            os.remove(filepath)

            return self.success_response(f"File '{filename}' deleted")

        except Exception as e:
            return self.error_response(f"Delete failed: {e}")


# ================= SEARCH FILE =================
class SearchFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = params.get('filename')

        if not filename:
            term = query.lower()

            for keyword in ["search file", "find file", "search for", "find"]:
                term = term.replace(keyword, "")

            term = clean_filename(term)

            if not term:
                return self.error_response("Say: search file test.txt")

            filename = term

        try:
            found_files: List[Path] = []

            def search_directory(directory: Path, depth=0):
                if depth > 3 or len(found_files) >= 5:
                    return

                try:
                    for item in directory.iterdir():
                        if len(found_files) >= 5:
                            break

                        if item.is_file() and filename in item.name.lower():
                            found_files.append(item)
                        elif item.is_dir() and not item.name.startswith('.'):
                            search_directory(item, depth + 1)
                except:
                    pass

            search_directory(Path.home())

            if not found_files:
                return self.success_response(f"No files found: {filename}")

            response = "Found files:\n\n"
            for f in found_files:
                response += f"{f}\n"

            return self.success_response(response.strip())

        except Exception as e:
            return self.error_response(f"Search failed: {e}")


# ================= LIST FILES =================
class ListFilesSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            path = Path.home() / "Desktop"

            files = [f for f in path.iterdir() if f.is_file()]
            files.sort()

            if not files:
                return self.success_response("No files on Desktop")

            response = "Files on Desktop:\n\n"
            for f in files[:10]:
                response += f"{f.name}\n"

            return self.success_response(response.strip())

        except Exception as e:
            return self.error_response(f"Failed: {e}")
        
    
# ================= OPEN FILE =================
class OpenFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = query.lower()

        for keyword in ["open file", "open"]:
            filename = filename.replace(keyword, "")

        filename = clean_filename(filename)

        if not filename:
            return self.error_response("Say: open file test.txt")

        try:
            filepath = Path.home() / "Desktop" / filename

            if not filepath.exists():
                return self.error_response(f"File not found: {filename}")

            os.startfile(filepath)  # Windows only

            return self.success_response(f"Opening {filename}")

        except Exception as e:
            return self.error_response(f"Open failed: {e}")


# ================= RENAME FILE =================
class RenameFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Example: rename file a.txt to b.txt
            text = query.lower().replace("rename file", "").replace("rename", "").strip()

            if "to" not in text:
                return self.error_response("Say: rename file old.txt to new.txt")

            old_name, new_name = text.split("to")

            old_name = clean_filename(old_name.strip())
            new_name = clean_filename(new_name.strip())

            old_path = Path.home() / "Desktop" / old_name
            new_path = Path.home() / "Desktop" / new_name

            if not old_path.exists():
                return self.error_response(f"{old_name} not found")

            old_path.rename(new_path)

            return self.success_response(f"Renamed to {new_name}")

        except Exception as e:
            return self.error_response(f"Rename failed: {e}")


# ================= MOVE FILE =================
class MoveFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Example: move file a.txt to documents
            text = query.lower().replace("move file", "").replace("move", "").strip()

            if "to" not in text:
                return self.error_response("Say: move file test.txt to documents")

            filename, destination = text.split("to")

            filename = clean_filename(filename.strip())
            destination = destination.strip()

            src = Path.home() / "Desktop" / filename
            dest = Path.home() / destination.capitalize()

            if not src.exists():
                return self.error_response(f"{filename} not found")

            if not dest.exists():
                return self.error_response(f"Folder not found: {destination}")

            shutil.move(str(src), str(dest))

            return self.success_response(f"Moved {filename} to {destination}")

        except Exception as e:
            return self.error_response(f"Move failed: {e}")


# ================= COMPRESS FILE =================
class CompressFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Example: compress file test.txt
            filename = query.lower().replace("compress file", "").replace("zip file", "").strip()
            filename = clean_filename(filename)

            filepath = Path.home() / "Desktop" / filename

            if not filepath.exists():
                return self.error_response(f"{filename} not found")

            zip_path = filepath.with_suffix(".zip")

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(filepath, arcname=filepath.name)

            return self.success_response(f"Compressed to {zip_path.name}")

        except Exception as e:
            return self.error_response(f"Compression failed: {e}")


# ================= EXTRACT ZIP =================
class ExtractFileSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            # Example: extract file test.zip
            filename = query.lower().replace("extract file", "").replace("unzip", "").strip()
            filename = clean_filename(filename)

            zip_path = Path.home() / "Desktop" / filename

            if not zip_path.exists():
                return self.error_response(f"{filename} not found")

            extract_path = zip_path.with_suffix("")

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_path)

            return self.success_response(f"Extracted to {extract_path.name}")

        except Exception as e:
            return self.error_response(f"Extraction failed: {e}")


# ================= COMMAND REGISTRATION =================
@command(["open file"], priority=10)
def cmd_open_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return OpenFileSkill().execute(ctx, query)


@command(["rename file", "rename"], priority=10)
def cmd_rename_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return RenameFileSkill().execute(ctx, query)


@command(["move file", "move"], priority=10)
def cmd_move_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return MoveFileSkill().execute(ctx, query)


@command(["compress file", "zip file"], priority=10)
def cmd_compress_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return CompressFileSkill().execute(ctx, query)


@command(["extract file", "unzip"], priority=10)
def cmd_extract_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ExtractFileSkill().execute(ctx, query)



# ================= COMMAND REGISTRATION =================
@command(["create file", "new file", "make file"], priority=10)
def cmd_create_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return CreateFileSkill().execute(ctx, query)


@command(["delete file", "remove file", "remove"], priority=10)
def cmd_delete_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return DeleteFileSkill().execute(ctx, query)


@command(["search file", "find file", "search for"], priority=10)
def cmd_search_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SearchFileSkill().execute(ctx, query)


@command(["list files", "show files", "open files"], priority=10)
def cmd_list_files(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ListFilesSkill().execute(ctx, query)