"""
File Operations Skill - Create, search, and manage files
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any, List
from pathlib import Path
import os


class CreateFileSkill(BaseSkill):
    """Create a new file on desktop"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = params.get('filename')
        content = params.get('content', '')
        
        if not filename:
            return self.error_response(
                "Filename required. Example: 'create file test.txt'"
            )
        
        try:
            # Get desktop path
            desktop_path = Path.home() / "Desktop"
            filepath = desktop_path / filename
            
            # Create file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return SkillResult()\
                .with_message(f"File '{filename}' created on your desktop")\
                .with_data({
                    'filepath': str(filepath),
                    'filename': filename
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to create file: {e}")


class SearchFileSkill(BaseSkill):
    """Search for files in user directory"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filename = params.get('filename')
        
        if not filename:
            # Try to extract from query
            # "search for test.txt" -> "test.txt"
            match = query.lower().replace('search file', '').replace('find file', '')
            match = match.replace('search for', '').replace('find', '').strip()
            
            if match:
                filename = match
            else:
                return self.error_response(
                    "Filename required. Example: 'search file test.txt'"
                )
        
        try:
            # Search in home directory
            search_path = Path.home()
            found_files: List[Path] = []
            
            # Limit search depth and results
            max_results = 5
            max_depth = 3
            
            def search_directory(directory: Path, depth: int = 0):
                if depth > max_depth or len(found_files) >= max_results:
                    return
                
                try:
                    for item in directory.iterdir():
                        if len(found_files) >= max_results:
                            break
                        
                        if item.is_file() and filename.lower() in item.name.lower():
                            found_files.append(item)
                        elif item.is_dir() and not item.name.startswith('.'):
                            search_directory(item, depth + 1)
                except (PermissionError, OSError):
                    pass
            
            # Perform search
            search_directory(search_path)
            
            if not found_files:
                return self.success_response(
                    f"No files found matching '{filename}'"
                )
            
            # Build response
            response = f"Found {len(found_files)} file(s):\n\n"
            for path in found_files:
                response += f"📄 {path}\n"
            
            return SkillResult()\
                .with_message(response.strip())\
                .with_data({
                    'found_files': [str(p) for p in found_files],
                    'count': len(found_files)
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"File search failed: {e}")


class OpenFileSkill(BaseSkill):
    """Open a file with default application"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        filepath = params.get('filepath')
        
        if not filepath:
            return self.error_response("Filepath required")
        
        try:
            path = Path(filepath)
            
            if not path.exists():
                return self.error_response(f"File not found: {filepath}")
            
            # Open with default application
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.name == 'posix':  # Linux/Mac
                import subprocess
                subprocess.run(['xdg-open', filepath])
            
            return self.success_response(f"Opening {path.name}")
        
        except Exception as e:
            return self.error_response(f"Failed to open file: {e}")


class ListFilesSkill(BaseSkill):
    """List files in a directory"""
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        directory = params.get('directory', str(Path.home() / "Desktop"))
        
        try:
            path = Path(directory)
            
            if not path.exists() or not path.is_dir():
                return self.error_response(f"Directory not found: {directory}")
            
            # List files
            files = [f for f in path.iterdir() if f.is_file()]
            files.sort(key=lambda x: x.name.lower())
            
            if not files:
                return self.success_response(f"No files in {path.name}")
            
            # Build response (limit to 10 files)
            response = f"Files in {path.name}:\n\n"
            for f in files[:10]:
                size = f.stat().st_size
                size_str = self._format_size(size)
                response += f"📄 {f.name} ({size_str})\n"
            
            if len(files) > 10:
                response += f"\n...and {len(files) - 10} more files"
            
            return SkillResult()\
                .with_message(response.strip())\
                .with_data({
                    'files': [f.name for f in files],
                    'count': len(files)
                })\
                .build()
        
        except Exception as e:
            return self.error_response(f"Failed to list files: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# Register commands
@command(["create file", "new file", "make file"], priority=10)
def cmd_create_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return CreateFileSkill().execute(ctx, query)


@command(["search file", "find file", "search for"], priority=10)
def cmd_search_file(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return SearchFileSkill().execute(ctx, query)


@command(["list files", "show files"], priority=10)
def cmd_list_files(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return ListFilesSkill().execute(ctx, query)