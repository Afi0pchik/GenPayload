import os
import shutil
from pathlib import Path
from git import Repo, GitCommandError, RemoteProgress
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

console = Console()
LOCAL_REPO_DIR = Path.cwd() / "SecLists"
MERGED_FILE = LOCAL_REPO_DIR / "merged_list.txt"
GIT_REPO_URL = "https://github.com/danielmiessler/SecLists.git"

class RichGitProgress(RemoteProgress):
    def __init__(self, progress, task_id):
        super().__init__()
        self.progress = progress
        self.task_id = task_id

    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count:
            self.progress.update(self.task_id, total=max_count, completed=cur_count, description=message or "Cloning...")
        else:
            self.progress.update(self.task_id, description=message or "Cloning...")

def clone_or_update_repo():
    if LOCAL_REPO_DIR.exists():
        console.print("[yellow]SecLists repo already cloned. Pulling latest changes...[/yellow]")
        try:
            repo = Repo(LOCAL_REPO_DIR)
            origin = repo.remotes.origin
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("Pulling latest changes...", start=False)
                progress.start_task(task)
                origin.pull(progress=RichGitProgress(progress, task))
            console.print("[green]Repo updated successfully[/green]")
        except GitCommandError as e:
            console.print(f"[red]Git pull failed: {e}[/red]")
    else:
        console.print("[green]Cloning SecLists repo...[/green]")
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("Cloning repo...", start=False)
                progress.start_task(task)
                Repo.clone_from(GIT_REPO_URL, LOCAL_REPO_DIR, progress=RichGitProgress(progress, task))
            console.print("[green]Repo cloned successfully[/green]")
        except GitCommandError as e:
            console.print(f"[red]Git clone failed: {e}[/red]")

def list_dir(path: Path):
    entries = []
    try:
        for entry in sorted(path.iterdir()):
            if entry.is_dir():
                entries.append({"name": entry.name, "type": "dir", "path": entry})
            elif entry.is_file():
                entries.append({"name": entry.name, "type": "file", "path": entry})
    except Exception as e:
        console.print(f"[red]Failed to list directory: {e}[/red]")
    return entries

def print_table(items, title):
    table = Table(title=title, box=box.HEAVY_EDGE, show_lines=True)
    table.add_column("Index", justify="center", style="cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Type", justify="center", style="magenta")
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item["name"], item["type"])
    console.print(table)

def select_items(items):
    selection = Prompt.ask("Enter numbers separated by commas (0 = Cancel)", default="0")
    if selection.strip() == "0":
        return []
    try:
        indexes = [int(x.strip()) for x in selection.split(",")]
        return [items[i - 1] for i in indexes if 0 < i <= len(items)]
    except Exception:
        console.print("[red]Invalid input[/red]")
        return []

def upload_custom_wordlist():
    console.print("[bold]Enter the full path to your local wordlist file:[/bold]")
    path = prompt("> ", completer=PathCompleter())
    p = Path(path)
    if not p.is_file():
        console.print("[red]File not found.[/red]")
        return
    try:
        shutil.copy(p, MERGED_FILE)
        console.print(f"[green]Copied your file to:[/green] {MERGED_FILE}")
    except Exception as e:
        console.print(f"[red]Failed to copy file: {e}[/red]")

def browse_and_select_files(base_path):
    current_path = base_path
    while True:
        entries = list_dir(current_path)
        if not entries:
            console.print("[yellow]No files or directories here.[/yellow]")
            return []
        print_table(entries, f"Browsing: {current_path.relative_to(base_path)}")
        selected = select_items(entries)
        if not selected:
            if current_path == base_path:
                return []
            current_path = current_path.parent
            continue
        selected_files = []
        for entry in selected:
            if entry["type"] == "dir":
                current_path = entry["path"]
                break
            elif entry["type"] == "file":
                selected_files.append(entry["path"])
        else:
            return selected_files

def merge_files_interactive(base_path):
    console.print("[bold]Select the first wordlist file to merge:[/bold]")
    first_files = browse_and_select_files(base_path)
    if not first_files or len(first_files) != 1:
        console.print("[red]You must select exactly one file.[/red]")
        return
    console.print("[bold]Select the second wordlist file to merge:[/bold]")
    second_files = browse_and_select_files(base_path)
    if not second_files or len(second_files) != 1:
        console.print("[red]You must select exactly one file.[/red]")
        return
    p1 = first_files[0]
    p2 = second_files[0]
    try:
        with p1.open("r", encoding="utf-8", errors="ignore") as file1, \
             p2.open("r", encoding="utf-8", errors="ignore") as file2:
            lines = set(file1.read().splitlines() + file2.read().splitlines())
        with MERGED_FILE.open("w", encoding="utf-8") as out_file:
            out_file.write("\n".join(sorted(lines)))
        console.print(f"[green]Merged files saved as:[/green] {MERGED_FILE}")
    except Exception as e:
        console.print(f"[red]Failed to merge files: {e}[/red]")

def main():
    clone_or_update_repo()
    while True:
        console.print(Panel("[bold green]SecLists Local Tool[/bold green]\nChoose an option:", box=box.ROUNDED))
        console.print("1. Browse SecLists repo and select files")
        console.print("2. Upload your own wordlist file (copy to merged_list.txt)")
        console.print("3. Merge two local wordlists into merged_list.txt")
        console.print("0. Exit")
        choice = Prompt.ask("Your choice", choices=["0","1","2","3"], default="1")
        if choice == "0":
            console.print("Goodbye!")
            break
        elif choice == "1":
            files = browse_and_select_files(LOCAL_REPO_DIR)
            if not files:
                console.print("[yellow]No files selected.[/yellow]")
                continue
            try:
                merged_lines = set()
                for f in files:
                    with open(f, "r", encoding="utf-8", errors="ignore") as file:
                        merged_lines.update(line.strip() for line in file if line.strip())
                with MERGED_FILE.open("w", encoding="utf-8") as out_file:
                    out_file.write("\n".join(sorted(merged_lines)))
                console.print(f"[green]Selected files merged and saved as:[/green] {MERGED_FILE}")
            except Exception as e:
                console.print(f"[red]Failed to merge selected files: {e}[/red]")
        elif choice == "2":
            upload_custom_wordlist()
        elif choice == "3":
            merge_files_interactive(LOCAL_REPO_DIR)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/red]")
