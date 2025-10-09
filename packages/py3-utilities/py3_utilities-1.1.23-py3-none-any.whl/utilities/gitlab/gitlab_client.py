import gitlab
import os
import functools
import time
import zipfile

from dataclasses import dataclass
from typing import Callable, TypeVar, Any, Optional, Union, cast, List
from gitlab.v4.objects import Project
from git import Repo
from datetime import datetime, date

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper

T = TypeVar("T")

# Classes for storing Merge request and commit metadata
@dataclass
class MergeRequestActivity:
    id: int
    body: str
    type: Optional[str]
    author: str
    created_at: str


@dataclass
class MergeRequestMetadata:
    parent_branch_name: str
    source_branch_name: str
    merge_request_id: int
    merge_request_title: str
    merge_request_description: str
    merge_request_state: str
    merge_request_url: str
    branch_changed_files: Optional[List[str]] = None
    merge_request_activity: Optional[List[MergeRequestActivity]] = None


@dataclass
class CommitMetadata:
    commit_short_id: str
    commit_title: str
    commit_author_name: str
    commit_id: str
    commit_date: str


def handle_gitlab_errors(
    default_return: Optional[T] = None,
    max_retries_attr: str = 'retries',
    backoff_factor: float = 0.5,
    raise_on_fail: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for error handling, retry logic, and optional default return for GitLab API methods.

    Args:
        default_return: Value to return if all retries fail (and raise_on_fail is False).
        max_retries_attr: Name of attribute on self for retry count.
        backoff_factor: Initial backoff delay, doubles per retry.
        raise_on_fail: If True, raises last exception after retries.

    Returns:
        The decorated function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
            retries = getattr(self, max_retries_attr, 3)
            delay = backoff_factor
            last_exception: Optional[Exception] = None

            for attempt in range(retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if hasattr(self, 'logger'):
                        self.logger.critical(f"Exception in {func.__name__} (attempt {attempt + 1}/{retries}): {e}")

                    if attempt < retries - 1:
                        time.sleep(delay)
                        delay *= 1.5

            if raise_on_fail and last_exception is not None:
                raise last_exception
            
            return default_return
        return cast(Callable[..., T], wrapper)
    return decorator


class GitlabClient(UtilityBase):
    """
    GitLab client for interacting with projects, branches, tags, MRs, and repository data.

    Args:
        url: GitLab instance URL.
        private_token: Personal/private access token.
        verbose: Enable verbose logging.
        ssl_verify: Verify SSL certificates.
        logger: Optional logger instance.
        log_level: Logging level.
        timeout: API call timeout (seconds).
        retries: Number of retries for API calls.
        large_repo_threshold: Warn threshold for large projects (branches/tags/commits).
    """
    def __init__(
        self,
        url: str,
        private_token: str,
        verbose: bool = False,
        ssl_verify: bool = True,
        logger: Optional[Union[Logger, LogWrapper]] = None,
        log_level: Optional[int] = None,
        timeout: float = 50,
        retries: int = 3,
        large_repo_threshold: int = 500
    ):
        super().__init__(verbose, logger, log_level)

        self.url = url
        self.retries = retries
        self.large_repo_threshold = large_repo_threshold

        self.gl = gitlab.Gitlab(url, private_token=private_token, timeout=timeout, retry_transient_errors=True, ssl_verify=ssl_verify)
        self.gl.auth()

    def _warn_large(self, resource: Any, project_path: str, label: str) -> None:
        """Warn if resource count exceeds the large repo threshold."""
        count = len(resource.list(per_page=100))
        
        if count > self.large_repo_threshold:
            self._log_warning(f"Project '{project_path}' has {count}+ {label}. all=True may be slow.")

    def _to_iso8601(self, dt: Union[str, datetime, date]) -> str:
        """Accept str (assumed already ISO-8601), date, or datetime. Naive treated as UTC."""
        if isinstance(dt, str):
            return dt
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        if dt.tzinfo is None:
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return dt.astimezone().strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _parse_committed_date(commit_info: dict) -> datetime:
        """Parse the committed date from a commit info dict."""
        date_str = commit_info.get("committed_date")

        if date_str:
            try:
                return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            except Exception:
                pass
        
        return datetime.min

    @handle_gitlab_errors(default_return=None)
    def get_project(self, project_path: str) -> Optional[Project]:
        """
        Get a GitLab project by path or ID.

        Args:
            project_path (str): Project path or ID.

        Returns:
            Project object or None if not found.
        """
        return self.gl.projects.get(project_path)

    @handle_gitlab_errors(default_return=[])
    def list_branches(self, project_path: str, max_branches: Optional[int] = None) -> list[str]:
        """
        List branch names in a project.

        Args:
            project_path (str): Project path or ID.
            max_branches (Optional, int): Max branches to return. If None, return all.

        Returns:
            List of branch names.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        if max_branches is not None:
            branches = project.branches.list(per_page=max_branches)
        else:
            self._warn_large(project.branches, project_path, "branches")
            branches = project.branches.list(all=True)

        return [branch.name for branch in branches]

    @handle_gitlab_errors(default_return=[])
    def list_recent_branches(self, project_path: str, num_branches: int = 10) -> list[str]:
        """
        Return N most recently updated branch names in the project.

        Args:
            project_path (str): Project path or ID.
            num_branches (int, default = 10): Number of recent branches to return.

        Returns:
            List of branch names.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        branches = project.branches.list(all=True)
        branches_with_dates = [
            (branch.name, self._parse_committed_date(getattr(project.branches.get(branch.name), "commit", {}) or {}))
            for branch in branches
        ]
        branches_with_dates.sort(key=lambda x: x[1], reverse=True)

        return [name for name, _ in branches_with_dates[:num_branches]]

    @handle_gitlab_errors(default_return=None)
    def get_branch_mr(
        self,
        project_path: str,
        branch_name: str,
        state: str = "all",
        get_changed_files: bool = False,
        get_activity: bool = False,  # NEW ARGUMENT
    ) -> Optional[List[MergeRequestMetadata]]:
        """
        Get all the merge requests for a branch.

        Args:
            project_path (str): Project path or ID.
            branch_name (str): Branch to check.
            state (str, default = all): MR state ('opened', 'closed', 'merged', 'all').
            get_changed_files (bool, default = False): If True, retrieve the list of changed files per MR.
            get_activity (bool, default = False): If True, retrieve activity (notes) for the MR.

        Returns:
            List of MergeRequestMetadata object(s) or None.
        """
        if not (project := self.get_project(project_path)):
            return None

        mrs = project.mergerequests.list(
            source_branch=branch_name,
            state=state,
            order_by='updated_at',
            sort='desc'
        )

        if mrs:
            result = []
            for mr in mrs:
                branch_changed_files = []
                if get_changed_files:
                    try:
                        # Get the full MR object to access changes
                        mr_full = project.mergerequests.get(mr.iid, lazy=False)
                        changes = mr_full.changes()
                        branch_changed_files = [change['new_path'] for change in changes['changes']]
                    except Exception:
                        branch_changed_files = []
                else:
                    mr_full = project.mergerequests.get(mr.iid, lazy=False)

                merge_request_activity = None
                if get_activity:
                    try:
                        notes = mr_full.notes.list(all=True)
                        merge_request_activity = [
                            MergeRequestActivity(
                                id=note.id,
                                body=note.body,
                                type=getattr(note, 'type', None),
                                author=note.author['name'],
                                created_at=note.created_at,
                            )
                            for note in notes
                        ]
                    except Exception:
                        merge_request_activity = []

                result.append(
                    MergeRequestMetadata(
                        parent_branch_name=mr.target_branch,
                        source_branch_name=branch_name,
                        merge_request_id=mr.iid,
                        merge_request_title=mr.title,
                        merge_request_description=mr.description,
                        merge_request_state=mr.state,
                        merge_request_url=mr.web_url,
                        branch_changed_files=branch_changed_files,
                        merge_request_activity=merge_request_activity,
                    )
                )
            return result

        return None

    @handle_gitlab_errors(default_return=[])
    def list_tags(self, project_path: str, max_tags: Optional[int] = None) -> list[str]:
        """
        List tag names in a project.

        Args:
            project_path (str): Project path or ID.
            max_tags (Optional, int): Max tags to return. If None, return all.

        Returns:
            List of tag names.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        if max_tags is not None:
            tags = project.tags.list(per_page=max_tags)
        else:
            self._warn_large(project.tags, project_path, "tags")
            tags = project.tags.list(all=True)

        return [tag.name for tag in tags]
    
    @handle_gitlab_errors(default_return=[])
    def list_changed_files_between_tags(
        self, project_path: str, from_tag: str, to_tag: str
    ) -> list[str]:
        """
        List all files changed between two tags.

        Args:
            project_path (str): Project path or ID.
            from_tag (str): The base tag.
            to_tag (str): The target tag.

        Returns:
            List of changed file paths.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        comparison = project.repository_compare(from_=from_tag, to=to_tag)
        diffs = comparison.get('diffs', [])
        changed_files = {diff['new_path'] for diff in diffs}
        return list(changed_files)

    @handle_gitlab_errors(default_return=None)
    def get_commit_metadata(
        self, 
        project_path: str, 
        commit_hash: str
    ) -> Optional[CommitMetadata]:
        """
        Get metadata for a single commit by hash.

        Args:
            project_path (str): Project path or ID.
            commit_hash (str): Commit hash or short hash.

        Returns:
            CommitMetadata or None.
        """
        if not (project := self.get_project(project_path)):
            return None

        try:
            commit = project.commits.get(commit_hash)
        except Exception:
            self._log_exception(f"Error occurred while requesting commit metadata for `{commit_hash}`")
            return None
        
        return CommitMetadata(
            commit_short_id=commit.short_id,
            commit_title=commit.title,
            commit_author_name=commit.author_name,
            commit_id=commit.id,
            commit_date=commit.committed_date
        )

    @handle_gitlab_errors(default_return=[])
    def list_commits(
        self,
        project_path: str,
        branch: str,
        max_commits: Optional[int] = None,
        since: Optional[Union[str, datetime, date]] = None,
        until: Optional[Union[str, datetime, date]] = None,
    ) -> list[CommitMetadata]:
        """
        List commits on a branch (optionally filtered by date range).

        Args:
            project_path: Project path or ID.
            branch: Branch to list commits from.
            max_commits: If provided, limit mapped results (per_page size); omit for full range.
            since: Include commits at/after this timestamp/date (ISO-8601, datetime, or date).
            until: Include commits up to this timestamp/date (inclusive per GitLab semantics).
        """
        if not (project := self.get_project(project_path)):
            return []

        params: dict[str, Any] = {"ref_name": branch}
        if since:
            params["since"] = self._to_iso8601(since)
        if until:
            params["until"] = self._to_iso8601(until)

        if max_commits is not None:
            commits = project.commits.list(per_page=max_commits, **params)
        else:
            self._warn_large(project.commits, project_path, "commits")
            commits = project.commits.list(all=True, **params)

        result = [
            CommitMetadata(
                commit_short_id=c.short_id,
                commit_title=c.title,
                commit_author_name=c.author_name,
                commit_id=c.id,
                commit_date=c.committed_date
            )
            for c in commits
        ]

        if max_commits is not None:
            result = result[:max_commits]

        return result

    @handle_gitlab_errors(default_return=[])
    def list_unique_commits_on_branch(
        self, project_path: str, base_branch: str, compare_branch: str
    ) -> list[CommitMetadata]:
        """
        List commits unique to compare_branch relative to base_branch.

        Args:
            project_path (str): Project path or ID.
            base_branch (str): Base branch.
            compare_branch (str): Branch to find unique commits in.

        Returns:
            List of CommitMetadata.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        comparison = project.repository_compare(from_=base_branch, to=compare_branch)
        commits = comparison['commits']

        return [
            CommitMetadata(
                commit_short_id=commit['short_id'],
                commit_title=commit['title'],
                commit_author_name=commit['author_name'],
                commit_id=commit['id']
            )
            for commit in commits
        ]

    @handle_gitlab_errors(default_return=[])
    def get_commit_changed_files(self, project_path: str, commit_id: str) -> list[str]:
        """
        Get list of files changed in a commit.

        Args:
            project_path (str): Project path or ID.
            commit_id (str): Commit SHA or ID.

        Returns:
            List of changed file paths.
        """
        if not (project := self.get_project(project_path)):
            return []
        
        changes = project.commits.get(commit_id).diff()
        return [file['new_path'] for file in changes]

    @handle_gitlab_errors(default_return=None)
    def clone_repository(
        self, project_url: str, local_path: str, branch: Optional[str] = None
    ) -> Optional[Repo]:
        """
        Clone a remote repository to local path (or open if already exists).

        Args:
            project_url (str): Remote repository path (after the GitLab base URL).
            local_path (str): Local directory for the clone.
            branch (Optional, str): Optional branch to check out.

        Returns:
            GitPython Repo object or None if failure.
        """
        if not os.path.exists(local_path):
            repo = Repo.clone_from(f"{self.url}/{project_url}.git", local_path)
        elif os.path.isdir(os.path.join(local_path, '.git')):
            repo = Repo(local_path)
        else:
            raise RuntimeError(f"Directory '{local_path}' exists but is not a git repository.")
        
        if branch:
            repo.git.checkout(branch)

        return repo

    @handle_gitlab_errors(default_return=None)
    def checkout_branch(self, local_path: str, branch: str) -> None:
        """
        Check out a branch in a local repository.

        Args:
            local_path (str): Local repository path.
            branch (str): Branch name to check out.
        """
        repo = Repo(local_path)

        repo.git.fetch()
        try:
            repo.git.checkout(branch)
        except Exception:
            repo.git.checkout('-b', branch, f'origin/{branch}')

    @handle_gitlab_errors(default_return=None)
    def checkout_tag(self, local_path: str, tag: str, new_branch: str = None) -> None:
        """
        Check out a tag in a local repository. Optionally create and switch to a new branch at the tag.

        Args:
            local_path (str): Local repository path.
            tag (str): Tag name to check out.
            new_branch (Optional, str): If provided, create this branch from the tag and check it out.
        """
        repo = Repo(local_path)

        repo.git.fetch('--tags')
        if new_branch:
            repo.git.checkout('-b', new_branch, tag)
        else:
            repo.git.checkout(tag)

    @handle_gitlab_errors(default_return=None)
    def download_pipeline_artifacts(
        self,
        project_path: str,
        pipeline_id: int,
        jobs_of_interest: list[str],
        output_folder: str
    ) -> None:
        """
        Download and extract artifacts from specified jobs in a pipeline.

        Args:
            project_path (str): Project path or ID.
            pipeline_id (int): Pipeline ID.
            jobs_of_interest (list[str]): List of job names whose artifacts to download.
            output_folder (str): Directory to save artifacts.
        """
        import shutil

        project = self.get_project(project_path)
        if not project:
            self._log_error(f"Project '{project_path}' not found.")
            return

        # Remove output folder if it exists
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder, ignore_errors=True)
        os.makedirs(output_folder, exist_ok=True)

        jobs = project.pipelines.get(pipeline_id).jobs.list(all=True)
        found_any = False

        for job in jobs:
            if job.name in jobs_of_interest:
                found_any = True
                job_dir = os.path.join(output_folder, job.name)
                os.makedirs(job_dir, exist_ok=True)
                zip_path = os.path.join(job_dir, "artifacts.zip")
                try:

                    # Get the full job object
                    full_job = project.jobs.get(job.id)

                    # Download artifact
                    with open(zip_path, "wb") as f:
                        f.write(full_job.artifacts())

                    # Unpack artifact
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        z.extractall(path=job_dir)
                    os.remove(zip_path)

                    self._log_info(f"Downloaded and extracted artifacts for job: {job.name}")
                except Exception as e:
                    self._log_error(f"Failed to process artifacts for job {job.name}: {e}")
            else:
                self._log_info(f"Skipped job: {job.name}")

        if not found_any:
            self._log_warning("No matching jobs with artifacts found in the pipeline.")
