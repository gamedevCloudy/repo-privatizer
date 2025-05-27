# repo-privatizer

## GitHub Repository Privacy Manager

A simple CLI tool to help you list and make your GitHub repositories private with ease.

## Features

* Authenticate using a GitHub Personal Access Token
* List all **public repositories** owned by you
* Make selected repositories private via:

  * Interactive selection
  * Batch mode with specific repo names
  * All-at-once mode
* Supports persistent credential storage (optional)
* Works cross-platform (Linux, macOS, Windows)

## Requirements

* Python 3.6+
* GitHub Personal Access Token (with `repo` scope)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/github-privacy-manager.git
   cd github-privacy-manager
   ```

2. Install required dependencies:

   ```bash
   pip install requests python-dotenv
   ```

   > If you're using environment variables from `.env`, make sure you have `python-dotenv` installed.

## Usage

Run the script directly using Python:

```bash
python github_privacy.py
```

### Options

* `--list`
  Only list your public repositories without making any changes.

* `--batch repo1,repo2,...`
  Provide a comma-separated list of repository names to make private.

* `--all`
  Make all your public repositories private. Use with caution.

### Example Commands

* Interactive mode (default):

  ```bash
  python github_privacy.py
  ```

* Batch mode:

  ```bash
  python github_privacy.py --batch my-repo1,my-repo2
  ```

* Make all public repositories private:

  ```bash
  python github_privacy.py --all
  ```

* Just list public repositories:

  ```bash
  python github_privacy.py --list
  ```

## Authentication

The script will prompt you for your GitHub token and username on the first run. You can optionally choose to save them locally in a config file (`~/.github_privacy_config.json`) for future runs.

Alternatively, you can set environment variables:

```bash
export GITHUB_TOKEN=your_token_here
export GITHUB_USERNAME=your_username_here
```

You can also use a `.env` file:

```env
GITHUB_TOKEN=your_token_here
GITHUB_USERNAME=your_username_here
```

## Notes

* Only repositories **you own** will be shown and processed.
* The tool uses GitHub's REST API (v3).
* Ensure your token has the `repo` scope, or the requests to update privacy will fail.

## License

MIT License

---

