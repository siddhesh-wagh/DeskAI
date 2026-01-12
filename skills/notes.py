"""
Notes Management Skill - Save, read, and delete notes
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path


class NotesManager(BaseSkill):
    """Base class for note operations"""
    
    def _get_notes_file(self, context: AssistantContext) -> Path:
        """Get notes file path"""
        return context.config_dir / "notes.json"
    
    def _load_notes(self, context: AssistantContext) -> Dict:
        """Load notes from file"""
        notes_file = self._get_notes_file(context)
        
        if not notes_file.exists():
            return {}
        
        try:
            with open(notes_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._logger.error(f"Failed to load notes: {e}")
            return {}
    
    def _save_notes(self, context: AssistantContext, notes: Dict):
        """Save notes to file"""
        notes_file = self._get_notes_file(context)
        
        try:
            with open(notes_file, 'w') as f:
                json.dump(notes, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save notes: {e}")


class TakeNoteSkill(NotesManager):
    """Create a new note with title and content"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Note: In a real implementation, you'd use dialog boxes or voice prompts
        # For now, we'll return a message to use a dialog
        
        return SkillResult()\
            .with_message(
                "Note feature requires dialog input. "
                "This will be implemented with GUI dialogs."
            )\
            .with_data({"action": "show_note_dialog"})\
            .build()


class ReadNotesSkill(NotesManager):
    """Read all saved notes"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        try:
            notes = self._load_notes(context)
            
            if not notes:
                return self.success_response("You have no saved notes.")
            
            # Build response
            count = len(notes)
            response = f"You have {count} note(s):\n\n"
            
            for title, data in notes.items():
                timestamp = data.get('timestamp', 'Unknown date')
                content = data.get('content', '')
                response += f"📝 {title} ({timestamp})\n"
                response += f"   {content}\n\n"
            
            return SkillResult()\
                .with_message(response.strip())\
                .with_data({"notes": notes, "count": count})\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to read notes: {e}")


class DeleteNoteSkill(NotesManager):
    """Delete a note by title"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        return SkillResult()\
            .with_message(
                "Delete note feature requires dialog input. "
                "This will be implemented with GUI dialogs."
            )\
            .with_data({"action": "show_delete_note_dialog"})\
            .build()


class SaveNoteSkill(NotesManager):
    """
    Save a note programmatically (for use by other skills or GUI)
    """
    
    def save_note(
        self, 
        context: AssistantContext, 
        title: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Save a note with given title and content.
        
        Args:
            context: Assistant context
            title: Note title
            content: Note content
        
        Returns:
            Result dictionary
        """
        if not title or not content:
            return self.error_response("Title and content are required")
        
        try:
            notes = self._load_notes(context)
            
            notes[title] = {
                'content': content,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'tags': []
            }
            
            self._save_notes(context, notes)
            
            return SkillResult()\
                .with_message(f"Note '{title}' saved successfully")\
                .with_data({
                    'title': title,
                    'total_notes': len(notes)
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to save note: {e}")
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Extract title and content from params if provided
        title = params.get('title')
        content = params.get('content')
        
        if title and content:
            return self.save_note(context, title, content)
        
        return SkillResult()\
            .with_message("Use 'take note' command for interactive note creation")\
            .build()


class DeleteNoteByTitleSkill(NotesManager):
    """
    Delete a note by title (for use by other skills or GUI)
    """
    
    def delete_note(
        self, 
        context: AssistantContext, 
        title: str
    ) -> Dict[str, Any]:
        """
        Delete a note with given title.
        
        Args:
            context: Assistant context
            title: Note title to delete
        
        Returns:
            Result dictionary
        """
        try:
            notes = self._load_notes(context)
            
            if title not in notes:
                return self.error_response(f"Note '{title}' not found")
            
            del notes[title]
            self._save_notes(context, notes)
            
            return SkillResult()\
                .with_message(f"Note '{title}' deleted successfully")\
                .with_data({'remaining_notes': len(notes)})\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to delete note: {e}")
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        title = params.get('title')
        
        if title:
            return self.delete_note(context, title)
        
        return self.error_response("Note title required")


# Register commands
@command(["take note", "create note", "make note", "new note"], priority=10)
def cmd_take_note(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return TakeNoteSkill().execute(ctx, query)


@command(["read notes", "show notes", "my notes", "list notes"], priority=10)
def cmd_read_notes(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ReadNotesSkill().execute(ctx, query)


@command(["delete note", "remove note"], priority=10)
def cmd_delete_note(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return DeleteNoteSkill().execute(ctx, query)