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

    def __init__(self, upstream, path=None):
        self.upstream = upstream
        self.path = path
        self.temp_path = (path == None)

        # Make sure the path starts with some valid root
        if path and not any(path.startswith(root) for root in self.VALID_ROOTS):
            raise ValueError(
                'Path must be in one of the valid folders: {}'
                .format(', '.join(self.VALID_ROOTS)))

    def __enter__(self):
        if self.path is None:
            self.path = tempfile.mkdtemp()

    def __exit__(self):
        shutil.rmtree(self.path)

    @classmethod
    def clone(cls, upstream, path=None):
        repo = cls(upstream, path=path)
        run("""
            cd {path}
            git clone {upstream}
            """.format(path=path,
                       upstream=upstream))
        return repo

    def runcmd(self, cmd, *args, **kwargs):
        cmdargs = [cmd]

        def flagify(key):
            return ('-' + key) if len(key) == 1 else ('--' + key)

        def quote(val):
            return '"' + value.replace('"', '\\"') + '"'

        cmdargs.extend(chain.from_iterables(
            [flagify(key), quote(val)]
            for key, val in kwargs.items()
        ))
        cmdargs.extend(args)

        p = run("""
                cd {path}
                git {cmdstr}
                """.format(path=self.path,
                           cmdstr=' '.join(cmdargs)))
        return p.stdout

    def add(self, name):
        return self.runcmd('add', name)

    def commit(self, message=''):
        return self.runcmd('commit', m=message)

    def push(self, remote='origin', branch='master'):
        return self.runcmd('push', remote, branch)
