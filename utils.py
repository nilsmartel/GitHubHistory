import requests
from subprocess import check_output

def exec(args):
    return check_output(args).decode("utf-8")

"""
get date of a specific commit.
current working directory must be inside the git repository
"""
def commit_date(commit):
    return exec(["git", "show", "-s", "--format=%ci", commit])

"""
get all commits from the git repo (and branch)
in the current directory.
"""
def all_commits():
    for line in exec(["git", "log"]).splitlines():
        if line.startswith("commit"):
            # cut "commit "
            yield line[7:]

def page_info(resp):
    relations = dict()
    for part in resp.headers['link'].split(","):
        part = part.strip()
        assert part.startswith("<")
        part = part[1:]

        [link, rel] = part.split(">; rel=")
        assert rel.startswith('"')
        rel = rel[1:]
        assert rel.endswith('"')
        rel = rel[:-1]

        relations[rel] = link

    return relations

def repo_info(user):
    url = f"https://api.github.com/users/{user}/repos"
    while True:
        resp = requests.get(url)
        relations = page_info(resp)
        json = resp.json()
        # expect an array here
        for field in json:
            yield field
        if 'next' in relations:
            url = relations['next']
        else:
            break

def all_repo_names(user):
    for repo in repo_info(user):
        yield repo['full_name']

