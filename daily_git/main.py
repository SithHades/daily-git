import os
import json
import sqlite3
import datetime
import git
from rich.console import Console
from rich.table import Table

def create_tables(db):
    db.execute('''CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS commits (
        id INTEGER PRIMARY KEY,
        repository_id INTEGER,
        commit_hash TEXT,
        author_date TEXT,
        lines_added INTEGER,
        lines_deleted INTEGER,
        UNIQUE(repository_id, commit_hash)
    )''')
    db.commit()

def scan_repositories(path):
    repo_paths = []
    for root, dirs, _ in os.walk(path):
        if '.git' in dirs:
            repo_paths.append(root)
            dirs.remove('.git')
    return repo_paths

def get_or_insert_repo(db, repo_path):
    cursor = db.execute("SELECT id FROM repositories WHERE path = ?", (repo_path,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor = db.execute("INSERT INTO repositories (path) VALUES (?)", (repo_path,))
        db.commit()
        return cursor.lastrowid

def update_commits(db, repo_id, repo_path, user_email):
    repo = git.Repo(repo_path)
    try:
        _ = repo.head.commit
    except ValueError:
        print(f"Skipping repository {repo_path} because it has no commits.")
        return
    since_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    commits = repo.iter_commits("HEAD", author=user_email, since=since_date)
    for commit in commits:
        cursor = db.execute("SELECT id FROM commits WHERE repository_id = ? AND commit_hash = ?", (repo_id, commit.hexsha))
        if cursor.fetchone() is None:
            lines_added = commit.stats.total['insertions']
            lines_deleted = commit.stats.total['deletions']
            author_date = datetime.datetime.fromtimestamp(commit.authored_date).date().isoformat()
            db.execute("INSERT INTO commits (repository_id, commit_hash, author_date, lines_added, lines_deleted) VALUES (?, ?, ?, ?, ?)",
                       (repo_id, commit.hexsha, author_date, lines_added, lines_deleted))
    db.commit()

def main(db=None, config=None):
    # Load configuration if not provided  
    if not config:
        config_path = os.path.expanduser('~/.daily_git')
        if not os.path.exists(config_path):
            print("Configuration file not found. Please create ~/.daily_git")
            return
        with open(config_path) as f:
            config = json.load(f)
    
    # Connect to DB if not provided  
    if not db:
        db_path = os.path.expanduser('~/.repo_scanner.db')
        db = sqlite3.connect(db_path)
        create_tables(db)
    
    repositories_path = config['repositories_path']
    user_email = config['user_email']
    
    # Scan repositories
    repo_paths = scan_repositories(repositories_path)
    for repo_path in repo_paths:
        repo_id = get_or_insert_repo(db, repo_path)
        update_commits(db, repo_id, repo_path, user_email)
    
    # Query stats
    today = datetime.date.today().isoformat()
    last_7_days_start = (datetime.date.today() - datetime.timedelta(days=6)).isoformat()
    last_30_days_start = (datetime.date.today() - datetime.timedelta(days=29)).isoformat()
    
    today_stats = db.execute("SELECT COUNT(*), SUM(lines_added), SUM(lines_deleted) FROM commits WHERE author_date = ?", (today,)).fetchone()
    commits_today = today_stats[0] or 0
    lines_added_today = today_stats[1] or 0
    lines_deleted_today = today_stats[2] or 0
    
    last_7_days_stats = db.execute("SELECT COUNT(*), SUM(lines_added), SUM(lines_deleted) FROM commits WHERE author_date >= ?", (last_7_days_start,)).fetchone()
    commits_last_7 = last_7_days_stats[0] or 0
    lines_added_last_7 = last_7_days_stats[1] or 0
    lines_deleted_last_7 = last_7_days_stats[2] or 0
    
    last_30_days_stats = db.execute("SELECT COUNT(*), SUM(lines_added) FROM commits WHERE author_date >= ?", (last_30_days_start,)).fetchone()
    total_commits_30 = last_30_days_stats[0] or 0
    total_lines_added_30 = last_30_days_stats[1] or 0
    
    average_commits = total_commits_30 / 30.0
    average_lines_added = total_lines_added_30 / 30.0
    
    more_commits_needed = max(0, average_commits - commits_today)
    more_lines_needed = max(0, average_lines_added - lines_added_today)
    
    # Display stats
    console = Console()
    table = Table(title="Your Coding Stats")
    table.add_column("Metric", justify="left", style="cyan")
    table.add_column("Today", justify="right", style="green")
    table.add_column("Last 7 Days", justify="right", style="blue")
    table.add_row("Commits", str(commits_today), str(commits_last_7))
    table.add_row("Lines Added", str(lines_added_today), str(lines_added_last_7))
    table.add_row("Lines Deleted", str(lines_deleted_today), str(lines_deleted_last_7))
    console.print(table)
    
    console.print(f"\nDaily Goal (based on last 30 days average): {average_commits:.2f} commits, {average_lines_added:.2f} lines added", style="bold")
    if more_commits_needed == 0 and more_lines_needed == 0:
        console.print("Great job! You've reached your daily goal!", style="green bold")
    else:
        console.print(f"Keep going! You need {more_commits_needed:.2f} more commits and {more_lines_needed:.2f} more lines to reach your daily goal.", style="yellow bold")

if __name__ == "__main__":
    main()