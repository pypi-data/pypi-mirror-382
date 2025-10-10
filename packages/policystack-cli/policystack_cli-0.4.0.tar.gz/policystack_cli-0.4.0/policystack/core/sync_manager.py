"""Marketplace repository synchronization manager."""

import logging
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import git
from git import Repo


logger = logging.getLogger(__name__)


class SyncManager:
    """Manages synchronization of marketplace repositories."""

    # Files/directories to include in archives
    INCLUDE_PATTERNS = [
        "templates/",
        "registry.json",
        "registry.yaml",
        "registry.yml",
        "README.md",
        "LICENSE",
        "LICENSE.md",
        ".gitignore",
    ]

    # Files/directories to exclude
    EXCLUDE_PATTERNS = [
        ".git/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        ".venv/",
        "venv/",
        "node_modules/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".tox/",
        "dist/",
        "build/",
        "*.egg-info/",
    ]

    def __init__(self, cache_dir: Path, marketplace=None):
        """Initialize sync manager."""
        self.cache_dir = cache_dir / "sync"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.marketplace = marketplace

    def pull_repository(
        self,
        source_url: str,
        branch: Optional[str] = None,
        auth_token: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Tuple[bool, Path, str]:
        """
        Pull repository and create archive.

        Args:
            source_url: Source repository URL
            branch: Git branch to pull
            auth_token: Authentication token (from repository config)
            output_path: Path for archive file (optional)

        Returns:
            Tuple of (success, archive_path, message)
        """
        temp_clone = None

        try:
            # Create temporary directory for clone
            temp_clone = Path(tempfile.mkdtemp(prefix="policystack_pull_", dir=self.cache_dir))

            # Prepare authenticated URL if token provided
            clone_url = self._add_auth_to_url(source_url, auth_token) if auth_token else source_url

            # Clone repository
            logger.info(f"Cloning repository from {source_url}")

            clone_kwargs = {
                "depth": 1,
                "single_branch": True,
            }

            if branch:
                clone_kwargs["branch"] = branch

            Repo.clone_from(clone_url, temp_clone, **clone_kwargs)

            # Determine archive path
            if output_path is None:
                repo_name = source_url.rstrip("/").split("/")[-1].replace(".git", "")
                archive_name = f"{repo_name}-marketplace.tar.gz"
                output_path = Path.cwd() / archive_name

            # Create archive
            logger.info(f"Creating archive at {output_path}")
            success, message = self._create_archive(temp_clone, output_path)

            if not success:
                return False, output_path, message

            return True, output_path, f"Archive created successfully: {output_path}"

        except git.GitCommandError as e:
            error_msg = f"Git error: {str(e)}"
            logger.error(error_msg)
            return False, Path(), error_msg

        except Exception as e:
            error_msg = f"Failed to pull repository: {str(e)}"
            logger.error(error_msg)
            return False, Path(), error_msg

        finally:
            # Cleanup temporary clone
            if temp_clone and temp_clone.exists():
                shutil.rmtree(temp_clone, ignore_errors=True)

    def push_archive(
        self,
        archive_path: Path,
        target_url: str,
        branch: Optional[str] = None,
        auth_token: Optional[str] = None,
        commit_message: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Push archive contents to target repository.

        Args:
            archive_path: Path to archive file
            target_url: Target repository URL
            branch: Git branch to push to
            auth_token: Authentication token (from repository config)
            commit_message: Custom commit message

        Returns:
            Tuple of (success, message)
        """
        temp_extract = None
        temp_repo = None

        try:
            if not archive_path.exists():
                return False, f"Archive not found: {archive_path}"

            # Extract archive to temporary directory
            temp_extract = Path(tempfile.mkdtemp(prefix="policystack_extract_", dir=self.cache_dir))

            logger.info(f"Extracting archive {archive_path}")
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(temp_extract)

            # Create/clone target repository
            temp_repo = Path(tempfile.mkdtemp(prefix="policystack_push_", dir=self.cache_dir))

            push_url = self._add_auth_to_url(target_url, auth_token) if auth_token else target_url

            # Try to clone existing repo, or init new one
            try:
                logger.info(f"Cloning target repository {target_url}")
                repo = Repo.clone_from(
                    push_url,
                    temp_repo,
                    branch=branch or "main",
                    depth=1,
                )
            except git.GitCommandError:
                # Repository doesn't exist or is empty, initialize new one
                logger.info("Initializing new repository")
                repo = Repo.init(temp_repo)

                # Set up remote
                origin = repo.create_remote("origin", push_url)

                # Create initial branch
                target_branch = branch or "main"
                repo.git.checkout("-b", target_branch)

            # Copy extracted files to repo
            logger.info("Copying files to repository")
            self._sync_files(temp_extract, temp_repo)

            # Stage all changes
            repo.git.add(A=True)

            # Check if there are changes to commit
            if repo.is_dirty() or repo.untracked_files:
                # Commit changes
                message = commit_message or "Sync marketplace from upstream"
                repo.index.commit(message)

                # Push to remote
                logger.info(f"Pushing to {target_url}")
                origin = repo.remote("origin")

                push_info = origin.push(refspec=f"HEAD:{branch or 'main'}")

                # Check push result
                if push_info and push_info[0].flags & git.PushInfo.ERROR:
                    return False, f"Push failed: {push_info[0].summary}"

                return True, f"Successfully pushed to {target_url}"
            else:
                return True, "No changes to push (repository already up to date)"

        except git.GitCommandError as e:
            error_msg = f"Git error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to push archive: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        finally:
            # Cleanup temporary directories
            if temp_extract and temp_extract.exists():
                shutil.rmtree(temp_extract, ignore_errors=True)
            if temp_repo and temp_repo.exists():
                shutil.rmtree(temp_repo, ignore_errors=True)

    def sync_repositories(
        self,
        source_url: str,
        target_url: str,
        source_branch: Optional[str] = None,
        target_branch: Optional[str] = None,
        source_auth: Optional[str] = None,
        target_auth: Optional[str] = None,
        commit_message: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Sync directly from source to target without intermediate file.

        Args:
            source_url: Source repository URL
            target_url: Target repository URL
            source_branch: Source branch
            target_branch: Target branch (defaults to source_branch or main)
            source_auth: Source authentication token (from repository config)
            target_auth: Target authentication token (from repository config)
            commit_message: Custom commit message

        Returns:
            Tuple of (success, message)
        """
        temp_clone = None
        temp_repo = None

        try:
            # Clone source repository
            temp_clone = Path(tempfile.mkdtemp(prefix="policystack_sync_src_", dir=self.cache_dir))

            source_clone_url = (
                self._add_auth_to_url(source_url, source_auth) if source_auth else source_url
            )

            logger.info(f"Cloning source repository from {source_url}")

            clone_kwargs = {
                "depth": 1,
                "single_branch": True,
            }

            if source_branch:
                clone_kwargs["branch"] = source_branch

            Repo.clone_from(source_clone_url, temp_clone, **clone_kwargs)

            # Remove .git directory from source
            source_git = temp_clone / ".git"
            if source_git.exists():
                shutil.rmtree(source_git)

            # Setup target repository
            temp_repo = Path(tempfile.mkdtemp(prefix="policystack_sync_tgt_", dir=self.cache_dir))

            target_push_url = (
                self._add_auth_to_url(target_url, target_auth) if target_auth else target_url
            )

            # Try to clone target, or init new
            try:
                logger.info(f"Cloning target repository {target_url}")
                repo = Repo.clone_from(
                    target_push_url,
                    temp_repo,
                    branch=target_branch or source_branch or "main",
                    depth=1,
                )
            except git.GitCommandError:
                logger.info("Initializing new target repository")
                repo = Repo.init(temp_repo)
                origin = repo.create_remote("origin", target_push_url)

                branch_name = target_branch or source_branch or "main"
                repo.git.checkout("-b", branch_name)

            # Sync files from source to target
            logger.info("Syncing files")
            self._sync_files(temp_clone, temp_repo)

            # Stage and commit
            repo.git.add(A=True)

            if repo.is_dirty() or repo.untracked_files:
                message = commit_message or f"Sync marketplace from {source_url}"
                repo.index.commit(message)

                # Push
                logger.info(f"Pushing to {target_url}")
                origin = repo.remote("origin")

                push_branch = target_branch or source_branch or "main"
                push_info = origin.push(refspec=f"HEAD:{push_branch}")

                if push_info and push_info[0].flags & git.PushInfo.ERROR:
                    return False, f"Push failed: {push_info[0].summary}"

                return True, f"Successfully synced {source_url} to {target_url}"
            else:
                return True, "No changes to sync (repositories already in sync)"

        except git.GitCommandError as e:
            error_msg = f"Git error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to sync repositories: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        finally:
            # Cleanup
            if temp_clone and temp_clone.exists():
                shutil.rmtree(temp_clone, ignore_errors=True)
            if temp_repo and temp_repo.exists():
                shutil.rmtree(temp_repo, ignore_errors=True)

    def _create_archive(self, source_dir: Path, archive_path: Path) -> Tuple[bool, str]:
        """Create compressed archive from directory."""
        try:
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            with tarfile.open(archive_path, "w:gz") as tar:
                for item in source_dir.rglob("*"):
                    if self._should_include(item, source_dir):
                        arcname = item.relative_to(source_dir)
                        tar.add(item, arcname=arcname)

            return True, "Archive created successfully"

        except Exception as e:
            return False, f"Failed to create archive: {str(e)}"

    def _should_include(self, path: Path, base_dir: Path) -> bool:
        """Check if path should be included in archive."""
        if not path.is_file() and not path.is_dir():
            return False

        rel_path = str(path.relative_to(base_dir))

        # Check exclude patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.endswith("/"):
                if rel_path.startswith(pattern.rstrip("/")):
                    return False
            elif "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(rel_path, pattern):
                    return False
            elif pattern in rel_path:
                return False

        # Check include patterns
        if path.is_file():
            # Include specific files
            if path.name in ["README.md", "LICENSE", "LICENSE.md", ".gitignore"]:
                return True
            if path.name in ["registry.json", "registry.yaml", "registry.yml"]:
                return True

        # Include templates directory
        if "templates" in path.parts:
            return True

        # Include if it's a parent directory of included content
        if path.is_dir():
            # Check if any child would be included
            for child in path.rglob("*"):
                if self._should_include(child, base_dir):
                    return True

        return False

    def _sync_files(self, source_dir: Path, target_dir: Path) -> None:
        """
        Sync files from source to target, preserving relevant content.

        This removes .git and other excluded files.
        """
        # Remove all existing files in target (except .git)
        for item in target_dir.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        # Copy files from source
        for item in source_dir.rglob("*"):
            if self._should_include(item, source_dir):
                rel_path = item.relative_to(source_dir)
                target_path = target_dir / rel_path

                if item.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)

    def _add_auth_to_url(self, url: str, auth_token: str) -> str:
        """Add authentication token to HTTPS URL."""
        if not url.startswith("https://"):
            return url

        # Add token based on git provider
        if "github.com" in url:
            return url.replace("https://", f"https://{auth_token}@")
        elif "gitlab.com" in url:
            return url.replace("https://", f"https://oauth2:{auth_token}@")
        elif "bitbucket.org" in url:
            return url.replace("https://", f"https://x-token-auth:{auth_token}@")
        else:
            # Generic format
            return url.replace("https://", f"https://{auth_token}@")

    def get_repository_info(
        self, url: str, auth_token: Optional[str] = None
    ) -> Tuple[bool, dict, str]:
        """
        Get basic information about a repository without cloning.

        Args:
            url: Repository URL
            auth_token: Authentication token (from repository config)

        Returns:
            Tuple of (success, info_dict, message)
        """
        try:
            auth_url = self._add_auth_to_url(url, auth_token) if auth_token else url

            # Use ls-remote to get basic info
            output = git.cmd.Git().ls_remote(auth_url)

            refs = {}
            for line in output.split("\n"):
                if line:
                    sha, ref = line.split("\t")
                    refs[ref] = sha

            info = {
                "url": url,
                "refs": refs,
                "default_branch": self._detect_default_branch(refs),
                "accessible": True,
            }

            return True, info, "Repository accessible"

        except git.GitCommandError as e:
            error_str = str(e).lower()
            if "not found" in error_str:
                return False, {}, "Repository not found"
            elif "authentication" in error_str or "permission" in error_str:
                return False, {}, "Authentication failed - check repository configuration"
            else:
                return False, {}, f"Error: {str(e)}"
        except Exception as e:
            return False, {}, f"Failed to get repository info: {str(e)}"

    def _detect_default_branch(self, refs: dict) -> str:
        """Detect default branch from refs."""
        # Check HEAD reference
        if "HEAD" in refs:
            for ref, sha in refs.items():
                if sha == refs["HEAD"] and ref.startswith("refs/heads/"):
                    return ref.replace("refs/heads/", "")

        # Fallback to common names
        for branch in ["main", "master"]:
            if f"refs/heads/{branch}" in refs:
                return branch

        # Return first branch found
        for ref in refs:
            if ref.startswith("refs/heads/"):
                return ref.replace("refs/heads/", "")

        return "main"
