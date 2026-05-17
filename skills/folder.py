"""
Folder Operations Skill - Create, delete, rename, open folders
"""

from skills.base import BaseSkill
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
from pathlib import Path
import os
import shutil

# 🔥 Clean voice input
def clean_folder_name(text: str) -> str:
    text = text.lower().strip()

    replacements = {
        " folder": "",
        " named": "",
        " called": ""
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()


# ================= CREATE FOLDER =================
class CreateFolderSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        name = params.get("name")

        if not name:
            term = query.lower()

            for k in ["create folder", "make folder", "new folder"]:
                term = term.replace(k, "")

            name = clean_folder_name(term)

            if not name:
                return self.error_response("Say: create folder myfolder")

        try:
            path = Path.home() / "Desktop" / name
            path.mkdir(exist_ok=True)

            return self.success_response(f"Folder '{name}' created on Desktop")

        except Exception as e:
            return self.error_response(f"Failed: {e}")


# ================= DELETE FOLDER =================
class DeleteFolderSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        name = params.get("name")

        if not name:
            term = query.lower()
            for k in ["delete folder", "remove folder", "delete", "remove"]:
                term = term.replace(k, "")
            name = clean_folder_name(term)

            if not name:
                return self.error_response("Say: delete folder myfolder")

        try:
            path = Path.home() / "Desktop" / name

            if not path.exists():
                return self.error_response(f"{name} not found")

            # Deletes folder recursively
            shutil.rmtree(path)

            return self.success_response(f"Folder '{name}' deleted successfully")

        except Exception as e:
            return self.error_response(f"Failed: {e}")
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        name = params.get("name")

        if not name:
            term = query.lower()

            for k in ["delete folder", "remove folder", "delete", "remove"]:
                term = term.replace(k, "")

            name = clean_folder_name(term)

            if not name:
                return self.error_response("Say: delete folder myfolder")

        try:
            path = Path.home() / "Desktop" / name

            if not path.exists():
                return self.error_response(f"{name} not found")

            os.rmdir(path)  # ⚠️ only deletes empty folder

            return self.success_response(f"Folder '{name}' deleted")

        except OSError:
            return self.error_response("Folder not empty. Cannot delete.")

        except Exception as e:
            return self.error_response(f"Failed: {e}")


# ================= RENAME FOLDER =================
class RenameFolderSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:

        term = query.lower()

        try:
            # Example: rename folder old to new
            parts = term.replace("rename folder", "").split("to")

            if len(parts) != 2:
                return self.error_response("Say: rename folder old to new")

            old_name = clean_folder_name(parts[0])
            new_name = clean_folder_name(parts[1])

            old_path = Path.home() / "Desktop" / old_name
            new_path = Path.home() / "Desktop" / new_name

            if not old_path.exists():
                return self.error_response(f"{old_name} not found")

            old_path.rename(new_path)

            return self.success_response(f"Renamed '{old_name}' to '{new_name}'")

        except Exception as e:
            return self.error_response(f"Rename failed: {e}")


# ================= OPEN FOLDER =================
class OpenFolderSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        name = params.get("name")

        if not name:
            term = query.lower()

            for k in ["open folder", "open"]:
                term = term.replace(k, "")

            name = clean_folder_name(term)

            if not name:
                return self.error_response("Say: open folder myfolder")

        try:
            path = Path.home() / "Desktop" / name

            if not path.exists():
                return self.error_response(f"{name} not found")

            os.startfile(path)  # Windows

            return self.success_response(f"Opening folder '{name}'")

        except Exception as e:
            return self.error_response(f"Failed: {e}")


# ================= LIST FOLDERS =================
class ListFolderSkill(BaseSkill):
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            path = Path.home() / "Desktop"

            folders = [f for f in path.iterdir() if f.is_dir()]
            folders.sort()

            if not folders:
                return self.success_response("No folders on Desktop")

            response = "Folders on Desktop:\n\n"
            for f in folders[:10]:
                response += f"{f.name}\n"

            return self.success_response(response.strip())

        except Exception as e:
            return self.error_response(f"Failed: {e}")


# ================= COMMAND REGISTRATION =================
@command(["create folder", "make folder", "new folder"], priority=12)
def cmd_create_folder(ctx, query):
    return CreateFolderSkill().execute(ctx, query)

@command(["delete folder", "remove folder"], priority=12)
def cmd_delete_folder(ctx, query):
    return DeleteFolderSkill().execute(ctx, query)

@command(["rename folder"], priority=12)
def cmd_rename_folder(ctx, query):
    return RenameFolderSkill().execute(ctx, query)

@command(["open folder"], priority=12)
def cmd_open_folder(ctx, query):
    return OpenFolderSkill().execute(ctx, query)

@command(["list folders", "show folders"], priority=12)
def cmd_list_folders(ctx, query):
    return ListFolderSkill().execute(ctx, query)