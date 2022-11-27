import requests
import datetime
import time
from subprocess import check_output

def exec(args):
    return check_output(args).decode("utf-8")

"""
get date of a specific commit.
current working directory must be inside the git repository
"""
def commit_date(commit):
    return exec(["git", "show", "-s", "--format=%ci", commit]).replace("\n", "")

def to_datetime(cdate):
    # sample input: '2022-11-27 13:06:22 +0100'

    day, time = cdate.split(" ")[0:2]
    ints = lambda n: list(map(int, n))
    y,m,d = ints(day.split("-"))
    h,min,sec = ints(time.split(":"))

    return datetime.datetime(y,m,d,h,min,sec)

def to_unixtime(dtime):
    return int(time.mktime(dtime.timetuple()))

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

filetypes = [
    ("md", "Markdown"),
    ("go", "go"),
    ("rs", "rust"),
    ("swift", "swift"),
    ("hs", "haskell"),
    ("elm", "elm"),
    ("js", "javascript"),
    ("css", "css"),
    ("html", "html"),
    ("ts", "typescript"),
    ("tsx", "react (typescript)"),
    ("jsx", "react (javascript)"),
    ("c", "c"),
    ("h", "header"),
    ("cpp", "c++"),
    ("c++", "c++"),
    ("cxx", "c++"),
    ("toml", "toml"),
    ("yaml", "yaml"),
    ("json", "json"),
    ("zsh", "shell"),
    ("sh", "shell"),
    ("fish", "shell"),
    ("cr", "crystal"),
    ("sol", "solar"),
    ("java", "java"),
    ("kt", "kotlin"),
    ("clj", "clojure"),
    ("lisp", "lisp"),
    ("cs", "c#"),
    ("py", "python"),
    ("vim", "vim"),
    ("alloy", "alloy"),
    ("dart", "dart"),
    ("csv", "csv"),
    ("glsl", "glsl"),
    ("wgsl", "wgsl"),
    ("jl", "julia"),
    ("zig", "zig"),
        ]

