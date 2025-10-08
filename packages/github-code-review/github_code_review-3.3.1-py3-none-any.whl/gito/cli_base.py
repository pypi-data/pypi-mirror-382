import contextlib
import logging
import tempfile

import microcore as mc
import typer
from git import Repo
from gito.constants import REFS_VALUE_ALL

from .utils import parse_refs_pair
from .env import Env


def args_to_target(refs, what, against) -> tuple[str | None, str | None]:
    if refs == REFS_VALUE_ALL:
        return REFS_VALUE_ALL, None
    _what, _against = parse_refs_pair(refs)
    if _what:
        if what:
            raise typer.BadParameter(
                "You cannot specify both 'refs' <WHAT>..<AGAINST> and '--what'. Use one of them."
            )
    else:
        _what = what
    if _against:
        if against:
            raise typer.BadParameter(
                "You cannot specify both 'refs' <WHAT>..<AGAINST> and '--against'. Use one of them."
            )
    else:
        _against = against
    return _what, _against


def arg_refs() -> typer.Argument:
    return typer.Argument(
        default=None,
        help=(
            "Git refs to review, [what]..[against] (e.g., 'HEAD..HEAD~1'). "
            "If omitted, the current index (including added but not committed files) "
            "will be compared to the repository’s main branch."
        ),
    )


def arg_what() -> typer.Option:
    return typer.Option(None, "--what", "-w", help="Git ref to review")


def arg_filters() -> typer.Option:
    return typer.Option(
        "", "--filter", "-f", "--filters",
        help="""
            filter reviewed files by glob / fnmatch pattern(s),
            e.g. 'src/**/*.py', may be comma-separated
            """,
    )


def arg_out() -> typer.Option:
    return typer.Option(
        None,
        "--out", "-o", "--output",
        help="Output folder for the code review report"
    )


def arg_against() -> typer.Option:
    return typer.Option(
        None,
        "--against", "-vs", "--vs",
        help="Git ref to compare against"
    )


app = typer.Typer(pretty_exceptions_show_locals=False)


@contextlib.contextmanager
def get_repo_context(url: str, branch: str):
    if branch == REFS_VALUE_ALL:
        branch = None
    """Context manager for handling both local and remote repositories."""
    if url:
        with tempfile.TemporaryDirectory() as temp_dir:
            logging.info(
                f"get_repo_context: "
                f"Cloning [{mc.ui.green(url)}] to {mc.utils.file_link(temp_dir)} ..."
            )
            repo = Repo.clone_from(url, branch=branch, to_path=temp_dir)
            prev_folder = Env.working_folder
            Env.working_folder = temp_dir
            try:
                yield repo, temp_dir
            finally:
                repo.close()
                Env.working_folder = prev_folder
    else:
        logging.info("get_repo_context: Using local repo...")
        repo = Repo(".")
        try:
            yield repo, "."
        finally:
            repo.close()
