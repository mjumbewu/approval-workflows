import subprocess
import tempfile
import io
import shutil
from itertools import chain
from os.path import join as pathjoin

from logging import getLogger
logger = getLogger(__name__)


def run(cmd, **run_kwargs):
    logger.debug(' -- Command: ' + cmd)

    run_kwargs.setdefault('shell', True)
    run_kwargs.setdefault('stdout', subprocess.PIPE)
    run_kwargs.setdefault('check', True)

    proc = subprocess.run(cmd, **run_kwargs)

    logger.debug(' -- Output: ' + proc.stdout.decode())
    return proc

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

    def __exit__(self, type, value, tb):
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
            return '"' + val.replace('"', '\\"') + '"'

        cmdargs.extend(args)
        cmdargs.extend(chain.from_iterable(
            [flagify(key)] if val is True else [flagify(key), quote(val)]
            for key, val in kwargs.items() if val is not False
        ))

        p = run("""
                cd {path}
                git {cmdstr}
                """.format(path=self.path,
                           cmdstr=' '.join(cmdargs)))
        return p

    def __ensure(self, valname, val):
        """
        Make sure that value is a string and is not empty.
        """
        val = str(val)
        if len(val) < 1:
            raise ValueError(valname + ' must not be empty.')
        return val

    @classmethod
    def init(cls, path=None, bare=False):
        repo = cls(path=path)
        repo.runcmd('init', '.', bare=bare)
        return repo

    @classmethod
    def clone(cls, upstream, path=None):
        repo = cls(path=path, remotes={'origin': upstream})
        repo.runcmd('clone', upstream, '.')
        logger.debug('Cloned to {}'.format(repo.path))
        return repo

    def add(self, path):
        path = self.__ensure('Path', path)
        self.runcmd('add', path)

    def add_remote(self, remote, url):
        remote = self.__ensure('Remote name', remote)
        url = self.__ensure('Remote URL', url)
        self.runcmd('remote', 'add', remote, url)

    def commit(self, message):
        message = self.__ensure('Commit message', message)
        self.runcmd('commit', m=message)

    def tag(self, tagname, message, sign=False, key=False):
        message = self.__ensure('Tag message', message)
        self.runcmd('tag', tagname, m=message, s=sign, u=key)

    def push(self, remote='origin', branch='master', tags=False):
        remote = self.__ensure('Remote name', remote)
        branch = self.__ensure('Branch name', branch)
        self.runcmd('push', remote, branch, tags=tags)

    def create(self):
        run("mkdir -p {path}".format(path=self.path))

    def destroy(self):
        run("rm -rf {path}".format(path=self.path))
