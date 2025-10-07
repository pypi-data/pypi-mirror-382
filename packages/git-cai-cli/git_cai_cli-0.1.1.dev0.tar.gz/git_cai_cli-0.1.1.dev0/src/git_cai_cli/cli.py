"""
Main function
"""

import logging
import subprocess
import sys
from pathlib import Path

from git_cai_cli.core.config import get_default_config, load_config, load_token
from git_cai_cli.core.gitutils import find_git_root, git_diff_excluding
from git_cai_cli.core.llm import CommitMessageGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    """
    Check for git repo, load access tokens and run git cai
    """
    # Ensure invoked as 'git cai'
    invoked_as = Path(sys.argv[0]).name
    if not invoked_as.startswith("git-"):
        print("This command must be run as 'git cai'", file=sys.stderr)
        sys.exit(1)

    # Find the git repo root
    repo_root = find_git_root()
    if not repo_root:
        log.error("Not inside a Git repository.")
        sys.exit(1)

    # Load configuration and token
    config = load_config()
    default_model = get_default_config()
    log.debug("Default model from config: %s", default_model)
    token = load_token(default_model)
    if not token:
        log.error("Missing %s token in ~/.config/cai/tokens.yml", default_model)
        sys.exit(1)

    # Get git diff
    diff = git_diff_excluding(repo_root)
    if not diff.strip():
        log.info("No changes to commit. Did you run 'git add'? Files must be staged.")
        sys.exit(0)

    # Generate commit message
    generator = CommitMessageGenerator(token, config, default_model)
    commit_message = generator.generate(diff)

    # Open git commit editor with the generated message
    subprocess.run(["git", "commit", "--edit", "-m", commit_message], check=True)


if __name__ == "__main__":
    main()
