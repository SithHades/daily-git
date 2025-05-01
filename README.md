# daily-git project

## Overview
`daily-git` is a command-line tool designed to help developers track their coding activity across multiple Git repositories. It scans specified directories for Git repositories, records commit statistics, and provides insights into daily coding goals.

## Features
- Scans for Git repositories in a specified directory.
- Records commit statistics such as lines added and deleted.
- Provides daily goals based on the average activity over the last 30 days.
- Displays statistics in a user-friendly format.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/daily-git.git
   cd daily-git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. (Optional) Install the package locally:
   ```
   pip install .
   ```

## Usage

To use the `daily-git` tool, you need to create a configuration file at `~/.daily_git` with the following structure:

```json
{
    "repositories_path": "/path/to/your/repositories",
    "user_email": "your_email@example.com"
}
```

Once the configuration is set up, you can run the tool using the following command:

```
daily-git
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.