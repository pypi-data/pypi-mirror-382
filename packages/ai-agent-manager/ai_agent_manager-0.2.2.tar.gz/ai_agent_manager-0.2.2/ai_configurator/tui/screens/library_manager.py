"""Library management screen."""
import logging
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, DataTable
from textual.binding import Binding

from ai_configurator.tui.screens.base import BaseScreen
from ai_configurator.services.library_service import LibraryService
from ai_configurator.services.sync_service import SyncService

logger = logging.getLogger(__name__)


class LibraryManagerScreen(BaseScreen):
    """Library synchronization interface."""
    
    BINDINGS = [
        Binding("n", "new_file", "New"),
        Binding("e", "edit_file", "Edit"),
        Binding("c", "clone_file", "Clone"),
        Binding("s", "sync", "Sync"),
        Binding("d", "diff", "Diff"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        from ai_configurator.tui.config import get_library_paths
        base_path, personal_path = get_library_paths()
        self.library_service = LibraryService(base_path, personal_path)
        self.sync_service = SyncService()
        self.selected_file = None
        self.personal_path = personal_path
    
    def compose(self) -> ComposeResult:
        """Build screen layout."""
        yield Header()
        yield Container(
            Static("[bold cyan]Library Management[/bold cyan]\n[dim]n=New e=Edit c=Clone s=Sync d=Diff r=Refresh[/dim]", id="title"),
            Static(self.get_status_text(), id="status"),
            DataTable(id="file_table", classes="file-list"),
            id="library-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize table and load data."""
        table = self.query_one(DataTable)
        table.add_columns("File", "Source", "Size")
        table.cursor_type = "row"
        table.focus()
        self.refresh_data()
    
    def get_status_text(self) -> str:
        """Get library status."""
        try:
            library = self.library_service.create_library()
            base_count = sum(1 for f in library.files.values() if f.source.value == 'base')
            personal_count = sum(1 for f in library.files.values() if f.source.value == 'personal')
            
            return f"""[bold]Library Status:[/bold]
  Base Files: {base_count}  Personal Files: {personal_count}  Total: {len(library.files)}"""
        except Exception as e:
            logger.error(f"Error getting status: {e}", exc_info=True)
            return f"[yellow]Status unavailable: {e}[/yellow]"
    
    def refresh_data(self) -> None:
        """Refresh status and file list."""
        # Update status
        status_widget = self.query_one("#status", Static)
        status_widget.update(self.get_status_text())
        
        # Update file table
        table = self.query_one(DataTable)
        table.clear()
        
        try:
            library = self.library_service.create_library()
            
            # Separate base and personal files
            base_files = [(k, f) for k, f in library.files.items() if f.source.value == 'base']
            personal_files = [(k, f) for k, f in library.files.items() if f.source.value == 'personal']
            
            # Add base files
            for file_key, file_info in sorted(base_files, key=lambda x: x[1].path):
                filename = file_info.path
                source = file_info.source.value
                size = f"{file_info.size} bytes" if file_info.size > 0 else "-"
                table.add_row(filename, source, size)
            
            # Add separator if both exist
            if base_files and personal_files:
                table.add_row("─" * 40, "─" * 10, "─" * 10)
            
            # Add personal files
            for file_key, file_info in sorted(personal_files, key=lambda x: x[1].path):
                filename = file_info.path
                source = file_info.source.value
                size = f"{file_info.size} bytes" if file_info.size > 0 else "-"
                table.add_row(filename, source, size)
                
        except Exception as e:
            logger.error(f"Error loading files: {e}", exc_info=True)
            self.show_notification(f"Error loading files: {e}", "error")
    
    def action_sync(self) -> None:
        """Start library synchronization."""
        try:
            from ai_configurator.models.sync_models import LibrarySync
            from ai_configurator.tui.config import get_config_dir
            
            self.show_notification("Syncing library...", "information")
            
            # Create LibrarySync object
            library = self.library_service.create_library()
            backup_path = get_config_dir() / "backups"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            library_sync = LibrarySync(
                base_path=library.base_path,
                personal_path=library.personal_path,
                backup_path=backup_path
            )
            
            result = self.sync_service.sync_library(library_sync, interactive=False)
            
            if result.conflicts_detected > 0:
                self.show_notification(f"Found {result.conflicts_detected} conflicts", "warning")
            else:
                self.show_notification("Sync completed successfully", "information")
            
            self.refresh_data()
        except Exception as e:
            self.show_notification(f"Sync error: {e}", "error")
    
    def action_diff(self) -> None:
        """Show differences."""
        try:
            from ai_configurator.models.sync_models import LibrarySync
            from ai_configurator.tui.config import get_config_dir
            
            library = self.library_service.create_library()
            backup_path = get_config_dir() / "backups"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            library_sync = LibrarySync(
                base_path=library.base_path,
                personal_path=library.personal_path,
                backup_path=backup_path
            )
            
            conflicts = self.sync_service.detect_conflicts(library_sync)
            if conflicts:
                msg = f"Found {len(conflicts)} differences:\n"
                for conflict in conflicts[:5]:  # Show first 5
                    msg += f"  - {conflict.file_path} ({conflict.conflict_type.value})\n"
                if len(conflicts) > 5:
                    msg += f"  ... and {len(conflicts) - 5} more"
                self.show_notification(msg, "information")
            else:
                self.show_notification("No differences found", "information")
        except Exception as e:
            logger.error(f"Error detecting differences: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track selected file."""
        try:
            table = self.query_one(DataTable)
            if event.cursor_row < table.row_count:
                row = table.get_row_at(event.cursor_row)
                filename = str(row[0])
                # Skip separator row
                if not filename.startswith("─"):
                    self.selected_file = filename
        except Exception as e:
            logger.error(f"Error highlighting row: {e}", exc_info=True)
    
    def action_new_file(self) -> None:
        """Create new file in personal library."""
        import subprocess
        import os
        import shutil
        from pathlib import Path
        
        try:
            # Prompt for filename
            from prompt_toolkit import prompt
            filename = prompt("Filename (e.g., my-rules.md): ")
            
            if not filename:
                return
            
            # Ensure .md extension
            if not filename.endswith('.md'):
                filename += '.md'
            
            # Create in personal library
            file_path = self.personal_path / filename
            
            if file_path.exists():
                self.show_notification(f"File already exists: {filename}", "warning")
                return
            
            # Create with template
            file_path.write_text(f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n")
            
            # Open in editor
            editor = os.environ.get('EDITOR')
            if not editor:
                # Try common editors
                for e in ['kate', 'vim', 'vi', 'nano']:
                    if shutil.which(e):
                        editor = e
                        break
            
            if not editor:
                self.show_notification("No editor found. Set $EDITOR environment variable.", "error")
                return
            
            subprocess.run([editor, str(file_path)])
            
            self.show_notification(f"Created: {filename}", "information")
            self.refresh_data()
            
        except Exception as e:
            logger.error(f"Error creating file: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_edit_file(self) -> None:
        """Edit selected file."""
        import subprocess
        import os
        import shutil
        
        if not self.selected_file:
            self.show_notification("No file selected", "warning")
            return
        
        # Skip separator row
        if self.selected_file.startswith("─"):
            return
        
        try:
            # Find the file - prefer personal over base
            library = self.library_service.create_library()
            file_info = None
            
            logger.info(f"Editing file: {self.selected_file}")
            
            # First look for personal version
            for f in library.files.values():
                if f.path == self.selected_file and f.source.value == 'personal':
                    file_info = f
                    break
            
            # If not found, look for base version
            if not file_info:
                for f in library.files.values():
                    if f.path == self.selected_file and f.source.value == 'base':
                        file_info = f
                        break
            
            if not file_info:
                self.show_notification(f"File not found: {self.selected_file}", "error")
                logger.error(f"File not found in library: {self.selected_file}")
                return
            
            logger.info(f"Found file: {file_info.path}, source: {file_info.source.value}")
            
            # Determine full path
            if file_info.source.value == 'personal':
                file_path = self.personal_path / file_info.path
                logger.info(f"Opening personal file: {file_path}")
            else:
                # Base file - suggest cloning
                self.show_notification("Base file - press 'c' to clone to personal first", "warning")
                return
            
            if not file_path.exists():
                self.show_notification(f"File does not exist: {file_path}", "error")
                logger.error(f"File does not exist: {file_path}")
                return
            
            # Open in editor
            editor = os.environ.get('EDITOR')
            if not editor:
                # Try common editors
                for e in ['kate', 'vim', 'vi', 'nano']:
                    if shutil.which(e):
                        editor = e
                        break
            
            if not editor:
                self.show_notification("No editor found. Set $EDITOR environment variable.", "error")
                return
            
            logger.info(f"Opening editor: {editor} {file_path}")
            subprocess.run([editor, str(file_path)])
            
            self.show_notification(f"Edited: {self.selected_file}", "information")
            self.refresh_data()
            
        except Exception as e:
            logger.error(f"Error editing file: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_clone_file(self) -> None:
        """Clone selected file to personal library."""
        import shutil
        
        if not self.selected_file:
            self.show_notification("No file selected", "warning")
            return
        
        # Skip separator row
        if self.selected_file.startswith("─"):
            return
        
        try:
            # Find the file
            library = self.library_service.create_library()
            file_info = None
            source_path = None
            
            for key, f in library.files.items():
                if f.path == self.selected_file:
                    file_info = f
                    # Use the key to construct full path
                    if f.source.value == 'base':
                        source_path = library.base_path / key.replace('base/', '', 1)
                    else:
                        source_path = self.personal_path / key.replace('personal/', '', 1)
                    break
            
            if not file_info or not source_path:
                self.show_notification(f"File not found: {self.selected_file}", "error")
                return
            
            # Target path in personal library
            target_path = self.personal_path / file_info.path
            
            if target_path.exists():
                self.show_notification(f"Already exists in personal: {self.selected_file}", "warning")
                return
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            self.show_notification(f"Cloned to personal: {self.selected_file}", "information")
            self.refresh_data()
            
        except Exception as e:
            logger.error(f"Error cloning file: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
