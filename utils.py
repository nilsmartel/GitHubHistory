from os import system
from subprocess import check_output

"""
get date of a specific commit.
current working directory must be inside the git repository
"""
def commit_date(commit):
    return check_output("git show -s --format=%ci " + commit)

"""
get all commits from the git repo (and branch)
in the current directory.
"""
def all_commits():
    for line in check_output("git log").lines():
        if line.startsWith("commit"):
            # cut "commit "
            yield line[7:]

