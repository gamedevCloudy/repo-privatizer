#!/usr/bin/env python3
"""
GitHub Repository Privacy Manager
A CLI tool to easily make your GitHub repositories private.
"""

import requests
import json
import sys
import os
from typing import List, Dict, Optional
import argparse
from getpass import getpass
from dotenv import load_dotenv

class GitHubPrivacyManager:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Privacy-Manager'
        }
        self.base_url = 'https://api.github.com'

    def test_authentication(self) -> bool:
        """Test if the GitHub token is valid."""
        try:
            response = requests.get(f'{self.base_url}/user', headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Successfully authenticated as: {user_data['login']}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

    def get_public_repos(self) -> List[Dict]:
        """Fetch all public repositories owned by the user."""
        repos = []
        page = 1
        per_page = 100

        print("🔍 Fetching your public repositories...")

        while True:
            try:
                url = f'{self.base_url}/user/repos'
                params = {
                    'visibility': 'public',
                    'affiliation': 'owner',  # 💡 Only include repos owned by the user
                    'page': page,
                    'per_page': per_page,
                    'sort': 'updated',
                    'direction': 'desc'
                }

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                page_repos = response.json()
                if not page_repos:
                    break

                # ✅ Filter to ensure only repos owned by the authenticated user
                owned_repos = [repo for repo in page_repos if repo.get('owner', {}).get('login') == self.username]
                repos.extend(owned_repos)

                page += 1

            except requests.RequestException as e:
                print(f"❌ Error fetching repositories: {e}")
                break

        return repos


    def make_repo_private(self, repo_name: str) -> bool:
        """Make a specific repository private."""
        try:
            url = f'{self.base_url}/repos/{self.username}/{repo_name}'
            data = {'private': True}
            
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to make {repo_name} private: {e}")
            return False

    def display_repos(self, repos: List[Dict]) -> None:
        """Display repositories in a formatted list."""
        if not repos:
            print("🎉 No public repositories found!")
            return

        print(f"\n📋 Found {len(repos)} public repositories:")
        print("-" * 80)
        
        for i, repo in enumerate(repos, 1):
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            updated = repo.get('updated_at', '')[:10]  # Just the date part
            
            print(f"{i:2d}. {repo['name']:<30} ⭐{stars:3d} 🍴{forks:3d} 📅{updated}")
        
        print("-" * 80)

    def interactive_selection(self, repos: List[Dict]) -> List[str]:
        """Interactive repository selection."""
        if not repos:
            return []

        print("\nSelection options:")
        print("• Enter repo numbers (e.g., 1,3,5 or 1-5)")
        print("• Type 'all' to select all repositories")
        print("• Type 'quit' to exit")
        
        while True:
            try:
                selection = input("\nYour selection: ").strip().lower()
                
                if selection == 'quit':
                    return []
                
                if selection == 'all':
                    return [repo['name'] for repo in repos]
                
                # Parse number selections
                selected_repos = []
                parts = selection.split(',')
                
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # Range selection (e.g., 1-5)
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(repos):
                                selected_repos.append(repos[i-1]['name'])
                    else:
                        # Single number
                        i = int(part)
                        if 1 <= i <= len(repos):
                            selected_repos.append(repos[i-1]['name'])
                
                return list(set(selected_repos))  # Remove duplicates
                
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")

    def confirm_action(self, repo_names: List[str]) -> bool:
        """Confirm the action with the user."""
        if not repo_names:
            return False
            
        print(f"\n⚠️  You're about to make {len(repo_names)} repositories private:")
        for name in repo_names:
            print(f"   • {name}")
        
        confirm = input("\nAre you sure? This action cannot be undone easily. (yes/no): ").strip().lower()
        return confirm in ['yes', 'y']

    def process_repos(self, repo_names: List[str]) -> None:
        """Process the selected repositories."""
        if not repo_names:
            print("No repositories selected.")
            return

        print(f"\n🔄 Making {len(repo_names)} repositories private...")
        
        success_count = 0
        for repo_name in repo_names:
            print(f"Processing {repo_name}...", end=' ')
            if self.make_repo_private(repo_name):
                print("✅ Done")
                success_count += 1
            else:
                print("❌ Failed")
        
        print(f"\n🎉 Successfully made {success_count}/{len(repo_names)} repositories private!")

def load_config() -> Dict:
    """Load configuration from file if it exists."""
    config_file = os.path.expanduser('~/.github_privacy_config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_config(config: Dict) -> None:
    """Save configuration to file."""
    config_file = os.path.expanduser('~/.github_privacy_config.json')
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration saved to {config_file}")
    except IOError:
        print("⚠️  Could not save configuration file")

def get_credentials() -> tuple:
    """Get GitHub credentials from user input or environment."""
    config = load_config()
    
    # Try environment variables first
    token = os.getenv('GITHUB_TOKEN') or config.get('token')
    username = os.getenv('GITHUB_USERNAME') or config.get('username')
    
    if not token:
        print("🔑 GitHub Personal Access Token required")
        print("Create one at: https://github.com/settings/tokens")
        print("Required scopes: repo (Full control of private repositories)")
        token = getpass("Enter your GitHub token: ").strip()
    
    if not username:
        username = input("Enter your GitHub username: ").strip()
    
    # Ask if user wants to save credentials
    if not config.get('token') or not config.get('username'):
        save_creds = input("Save credentials for future use? (y/n): ").strip().lower()
        if save_creds in ['y', 'yes']:
            save_config({'token': token, 'username': username})
    
    return token, username

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="GitHub Repository Privacy Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_privacy.py                    # Interactive mode
  python github_privacy.py --batch repo1,repo2  # Batch mode
  python github_privacy.py --list             # List public repos only
        """
    )
    
    parser.add_argument('--list', action='store_true', 
                       help='List public repositories without making changes')
    parser.add_argument('--batch', type=str,
                       help='Comma-separated list of repository names to make private')
    parser.add_argument('--all', action='store_true',
                       help='Make all public repositories private (use with caution)')
    
    args = parser.parse_args()
    
    print("🚀 GitHub Repository Privacy Manager")
    print("=" * 40)
    
    try:
        token, username = get_credentials()
        
        if not token or not username:
            print("❌ GitHub token and username are required")
            sys.exit(1)
        
        manager = GitHubPrivacyManager(token, username)
        
        if not manager.test_authentication():
            sys.exit(1)
        
        repos = manager.get_public_repos()
        manager.display_repos(repos)
        
        if args.list:
            print("📋 Listing complete. Use without --list to make changes.")
            return
        
        selected_repos = []
        
        if args.all:
            selected_repos = [repo['name'] for repo in repos]
        elif args.batch:
            repo_names = [name.strip() for name in args.batch.split(',')]
            available_names = {repo['name'] for repo in repos}
            selected_repos = [name for name in repo_names if name in available_names]
            
            missing = set(repo_names) - set(selected_repos)
            if missing:
                print(f"⚠️  Repositories not found or not public: {', '.join(missing)}")
        else:
            selected_repos = manager.interactive_selection(repos)
        
        if selected_repos and manager.confirm_action(selected_repos):
            manager.process_repos(selected_repos)
        else:
            print("Operation cancelled.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()