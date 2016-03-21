from gitutils import mkrepo, packrepo, unpackrepo
import tempfile

# Create a new repo and package it up
path = tempfile.mkdtemp()
mkrepo(path)
proc = packrepo(path)

print('Packed up a new repo from {}'.format(path))

# Cache the repository in memory
repodata = proc.stdout

# Unpack the repo into a new folder
path = tempfile.mkdtemp()
unpackrepo(path, repodata)

print ('Unpacked a repo into {}'.format(path))
