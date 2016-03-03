import subprocess
import tempfile
import io
import shutil


def run(cmd, **run_kwargs):
    run_kwargs.setdefault('shell', True)
    run_kwargs.setdefault('stdout', subprocess.PIPE)
    return subprocess.run(cmd, **run_kwargs)

# Make a bare git repo
def mkrepo(repopath):
    p = run("""
            cd {path}
            git init --bare
            git lfs track "*.psd"
            """.format(path=repopath))
    return p

# Pack up a bare git repo
def packrepo(repopath):
    p = run("""
            cd {path}
            tar -cz *
            """.format(path=repopath))
    tardata = p.stdout
    return p

# Extact a bare git repo
def unpackrepo(repopath, repodata):
    p = run("""
            cd {path}
            tar -xzf -
            """.format(data=repodata,
                       path=repopath),
            input=repodata)
    return p

def cleanuprepo(repopath):
    p = run("""
            rm -rf {path}
            """.format(path=repopath))
    return p


#
# Working With Repository Content & Commits
# -----------------------------------------

class GitRepo:
    VALID_ROOTS = ['/tmp']

    def __init__(self, path=None, remotes=None):
        self.remotes = remotes
        self.path = path or tempfile.mkdtemp()
        self.temp_path = (path == None)

        # Make sure the path starts with some valid root
        if path and not any(path.startswith(root) for root in self.VALID_ROOTS):
            raise ValueError(
                'Path must be in one of the valid folders: {}'
                .format(', '.join(self.VALID_ROOTS)))

    def __enter__(self):
        return self

    def __exit__(self):
        if self.temp_path:
            self.destroy()

    def runcmd(self, cmd, *args, **kwargs):
        cmdargs = [cmd]

        def flagify(key):
            """
            Convert a key (such as a keyword argument) into a command line
            flag. For example:
            * "m" becomes "-m"
            * "message" becomes "--message"
            """
            return ('-' + key) if len(key) == 1 else ('--' + key)

        def quote(val):
            """
            Escape internal quotes in a string and return a new quoted string.
            """
            return '"' + value.replace('"', '\\"') + '"'

        cmdargs.extend(args)
        cmdargs.extend(chain.from_iterables(
            [flagify(key), quote(val)]
            for key, val in kwargs.items()
        ))

        p = run("""
                cd {path}
                git {cmdstr}
                """.format(path=self.path,
                           cmdstr=' '.join(cmdargs)))
        return p.stdout

    @classmethod
    def init(cls, path):
        repo = cls(path=path)
        repo.runcmd('init', '.')
        return repo

    @classmethod
    def clone(cls, upstream, path):
        repo = cls(path=path, remotes={'origin': upstream})
        repo.runcmd('clone', upstream, '.')
        return repo

    def add(self, name):
        self.runcmd('add', name)

    def commit(self, message=''):
        self.runcmd('commit', m=message)

    def push(self, remote='origin', branch='master'):
        self.runcmd('push', remote, branch)

    def create(self):
        run("mkdir -p {path}".format(path=self.path))

    def destroy(self):
        run("rm -rf {path}".format(path=self.path))
