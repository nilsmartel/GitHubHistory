from multiprocessing import Pool
import utils
from sys import argv
import os

def print_help(msg = None, code = 0):
    if not msg is None:
        print(msg)
    print("""usage:
          --dir <directory where to clone all repos> REQUIRED
          --user <user to check out> REQUIRED
          --repo <additional repo to check out> optional

          repo can be applied multiple times""")

    exit(code)

def parse_args() -> tuple[str, str, list[str]]:
    dir = None
    user = None
    repos = []

    a = argv
    while len(a) != 0:
        first = a[0]
        if "=" in first:
            l = first.split("=")
            a = l + a[1:]
            continue

        if first in ["--help", "-h"]:
            print_help(0)

        elif first in ["--dir", "-d"]:
            dir = a[1]

        elif first in ["--user", "-u"]:
            user = a[1]

        elif first in ["--repo", "-r"]:
            repo = a[1]
            repos.append(repo)
        else:
            print_help(f"unknown command '{first}'", code=1)

        a = a[2:]

    if None in [dir, user]:
        print_help("required arguments missing", code=1)

    return str(user), str(dir), repos

user, dir, repos = parse_args()

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
    ("glsl", "glsl"),
    ("wgsl", "wgsl"),
    ("jl", "julia"),
    ("zig", "zig"),
        ]

ftdict = dict()

csvheader = "repo;commit;date"
for ext,name in filetypes:
    csvheader += ";" + name
    ftdict[ext] = name

def suffix(name):
    return name.rsplit(".", maxsplit=1)[-1]

def linecount(path):
    # read file
    f = open(path, "r")
    c = f.read()
    f.close()

    # count lines
    n = 0
    for _ in c.splitlines():
        n+=1
    return n


def crunch_repo(repo: str):
    print("crunching " + repo)

    os.chdir(dir)
    reponame = repo.rsplit("/", maxsplit=1)[-1]
    url = "https://github.com/" + repo
    utils.exec(["git", "clone", url, reponame])
    os.chdir(reponame)
    csvfilename = f"../{reponame}.csv"
    csvcontent = csvheader
    lines = []

    commits = list(utils.all_commits())
    for commit in commits:
        date = utils.commit_date(commit)
        line = [reponame, commit, date]
        info = dict()
        for ext, _ in filetypes:
            info[ext] = 0

        # check out commit
        utils.exec(["git", "checkout", commit])
        for (root,_,files) in os.walk('.'):
            for file in files:
                s = suffix(file)
                file = root + "/" + file
                if not s in ftdict:
                    continue

                info[s] += linecount(file)

        for ext, _ in filetypes:
            line.append(info[ext])

        lines.append(line)

    csvcontent += "\n".join(lines)

    f = open(csvfilename, "w")
    f.write(csvcontent)
    f.close()

    print("completed " + repo)
    return

os.mkdir(dir)

# create thread pool for
# downloading and organizing repositories.
pool = Pool(32)

allrepos = list(utils.all_repo_names(user)) + repos

print(f"found {len(allrepos)} repositories")

pool.map(crunch_repo, allrepos)
