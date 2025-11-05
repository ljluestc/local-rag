import os
import json
import requests
import subprocess

import streamlit as st

from exiftool import ExifToolHelper

import utils.logs as logs

###################################
#
# Save File Upload to Disk
#
###################################


def save_uploaded_file(uploaded_file: bytes, save_dir: str):
    """
    Saves the uploaded file to the specified directory.

    Args:
        uploaded_file (BytesIO): The uploaded file content.
        save_dir (str): The directory where the file will be saved.

    Returns:
        None

    Raises:
        Exception: If there is an error saving the file to disk.
    """
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logs.log.info(f"Directory {save_dir} did not exist so creating it")
        with open(os.path.join(save_dir, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
            logs.log.info(f"Upload {uploaded_file.name} saved to disk")
    except Exception as e:
        logs.log.error(f"Error saving upload to disk: {e}")


###################################
#
# Confirm a GitHub Repo Exists
#
###################################


def validate_github_repo(repo: str):
    """
    Validates whether a GitHub repository exists.

    Args:
        repo (str): The name of the GitHub repository.

    Returns:
        True if the repository exists, False otherwise.

    Raises:
        Exception: If there is an error validating the repository.
    """
    try:
        if repo is None or not isinstance(repo, str) or repo.strip() == "":
            logs.log.error("GitHub repo is empty. Expected format: owner/repo")
            return False

        # Prefer GitHub API for reliable existence check (unauthenticated)
        api_url = f"https://api.github.com/repos/{repo.strip()}"
        resp = requests.get(api_url, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logs.log.error(f"Error validating GitHub repo '{repo}': {e}")
        return False


###################################
#
# Clone a GitHub Repo
#
###################################


def clone_github_repo(repo: str):
    """
    Clones a GitHub repository.

    Args:
        repo (str): The name of the GitHub repository.

    Returns:
        True if the repository is cloned successfully, False otherwise.

    Raises:
        Exception: If there is an error cloning the repository.
    """
    # Default state flags for UI to consume
    st.session_state["github_clone_success"] = False
    st.session_state["github_clone_error"] = None

    # Validate input
    if repo is None or not isinstance(repo, str) or repo.strip() == "":
        msg = "Please enter a repository in the format owner/repo."
        logs.log.error(msg)
        st.session_state["github_clone_error"] = msg
        return False

    repo = repo.strip()

    # Verify the repo exists before cloning
    if not validate_github_repo(repo):
        msg = f"Repository '{repo}' not found or inaccessible. Check the name and your internet connection."
        logs.log.error(msg)
        st.session_state["github_clone_error"] = msg
        return False

    repo_endpoint = f"https://github.com/{repo}.git"

    # Ensure destination directory exists
    save_dir = os.path.join(os.getcwd(), "data")
    try:
        os.makedirs(save_dir, exist_ok=True)
    except Exception as e:
        msg = f"Unable to create data directory: {e}"
        logs.log.error(msg)
        st.session_state["github_clone_error"] = msg
        return False

    dest_dir = os.path.join(save_dir, repo)

    # If already cloned, skip to avoid failures and re-use existing data
    if os.path.isdir(dest_dir):
        logs.log.info(f"Repository already present at {dest_dir}; skipping clone")
        st.session_state["github_clone_success"] = True
        return True

    # Perform clone
    try:
        result = subprocess.run(
            ["git", "clone", "-q", repo_endpoint, dest_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        logs.log.info(f"Cloned {repo} repo")
        st.session_state["github_clone_success"] = True
        return True
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or str(e)
        friendly = f"Failed to clone '{repo}': {msg}"
        logs.log.error(friendly)
        st.session_state["github_clone_error"] = friendly
        return False
    except Exception as e:
        friendly = f"Unexpected error cloning '{repo}': {e}"
        logs.log.error(friendly)
        st.session_state["github_clone_error"] = friendly
        return False


###################################
#
# Extract File Metadata
#
###################################


def get_file_metadata(file_path):
    """
    Extracts various metadata for the specified file.

    Args:
        file_path (str): The path to the file.

    Returns:
        A dictionary containing the extracted metadata.

    Raises:
        Exception: If there is an error extracting the metadata.
    """
    try:
        with ExifToolHelper() as et:
            for d in et.get_metadata(file_path):
                return json.dumps(d, indent=2)
    except Exception:
        pass
