import argparse
import os
import json
import sqlite3
from daily_git.main import main

def parse_arguments():
    parser = argparse.ArgumentParser(description="Daily Git: Track your coding stats.")
    parser.add_argument(
        '--config', 
        type=str, 
        default=os.path.expanduser('~/.daily_git'), 
        help='Path to the configuration file (default: ~/.daily_git)'
    )
    return parser.parse_args()

def run_daily_git(config_path):
    if not os.path.exists(config_path):
        print("Configuration file not found. Please create the configuration file at", config_path)
        return
    with open(config_path) as f:
        config = json.load(f)
    
    db_path = os.path.expanduser('~/.repo_scanner.db')
    db = sqlite3.connect(db_path)
    # Ensure the necessary tables exist.
    from daily_git.main import create_tables
    create_tables(db)
    
    main(db, config)

def main_cli():
    args = parse_arguments()
    run_daily_git(args.config)

if __name__ == "__main__":
    main_cli()