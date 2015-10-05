"""
Methods to fetch corpora from the web, filesystem, or other sources.

Currently includes:

* A loader for local files (TODO)
* A loader for files from `IcePaHC <http://www.linguist.is/icelandic_treebank/Icelandic_Parsed_Historical_Corpus_(IcePaHC)>`_

"""

import requests
from github.MainClass import Github
import abc
import os.path

import lovett.corpus as corpus
import lovett.tree as tree

# TODO: new classes in the hierarchy: CachingLoader, MutableLoader
# The latter should implement a with: method to iterate through and modify its
# contents, creating a corpus for each one.  (In parallel?)

# Also a parallel filter method -- or would that be better at the corpus
# level?  Argument for putting it here: trees are expensive to create in
# memory(?), so we want to avoid slurping in many of them only to later
# discard.  But when would you ever want to load just a subset of trees into
# memory?


class Loader(object):
    """This is a base class for corpus loaders to inherit from."""
    # TODO: do we also need a class to group together the cache-related methods?
    @abc.abstractmethod
    def file(self, filename):
        """Return the content of one of the files from a corpus.

        This method must use caching if it makes network requests or uses other
        expensive resources (beyond disk access).

        Args
        ----
        filename : str
            The name of the file requested

        Returns
        -------
        str
            The file's content"""
        pass

    @abc.abstractmethod
    def files(self):
        """Return a list of files in the corpus.

        This method must use caching if it makes network requests or uses other
        expensive resources (beyond disk access).

        Returns
        -------
        list of str
            List of filenames"""
        pass

    def corpus(self, files=None):
        """Load files into a ``Corpus``.

        Args
        ----
        files : str or list of str
            The files to include in the corpus.  Default is to include all
            available files.

        Returns
        -------
        Corpus
            The corpus composed of all trees in all files.
        """
        c = corpus.Corpus([])
        if isinstance(files, str):
            files = (files,)
        for file in files or self.files():
            contents = self.file(file)
            for tree_string in contents.split("\n\n"):
                tree_obj = tree.parse(tree_string)
                if tree_obj is not None:
                    tree_obj.metadata.file = file
                    # TODO: file-level metadata
                    c.append(tree_obj)
        return c

    # TODO: a method for converting directly to an indexed corpus, for
    # speed/mem optimization?


# TODO: add a method to allow authentication, for private repos
_GITHUB = Github()


class GithubLoader(Loader):
    """A generic interface for fetching corpus files from a Github repo."""
    def __init__(self, user, repo, ref="master", directory="", extension=".psd"):
        """Initialize a GithubLoader.

        Args
        ----
        user : str
            Github username of the repository to load from
        repo : str
            Name of the repository to load from
        tag : str
            A git ref of the revision to fetch.  Defaults to "master", the
            latest revision.  If the repository uses git tags, you can request
            a specific version of the corpus.  You can also use a sha1 hash to
            request a specific revision.
        directory : str
            Path to the directory containing parsed files.  (TODO: support
            corpora with parsed files in more than one directory.)
        extension : str
            File extension of corpus files.  Defaults to ".psd".  (TODO:
            support multiple extensions.)

        """
        self._user = user
        self._repo = repo
        self._tag = ref
        self._directory = directory
        self._extension = extension
        self._files = {}

    def file(self, filename):
        if self._files[filename]:
            return self._files[filename]
        content = requests.get("https://raw.githubusercontent.com/%s/%s/%s/%s%s" %
                               (self._user, self._repo, self._tag, self._directory, filename))
        self._files[filename] = content
        return content

    def files(self):
        if self._files:
            return self._files
        repo = _GITHUB.get_repo("%s/%s" % (self._user, self._repo))
        contents = repo.get_dir_contents(self._directory, ref=self._tag)
        files = [f.name for f in contents]
        if self._extension is not None:
            files = list(filter(lambda s: s.endswith(self._extension), files))
        self._files = files
        return files

    def fetch_all(self):
        for f in self.files():
            self.file(f)

    def clear_cache(self):
        self._files = {}


# TODO: get sha hashes corresponding to icepahc releases, since there are no
# tags in the repo.
# Meta-TODO: ask icepahc people to add tags to their repo

#: A ``GithubLoader`` which is pre-populated with the details of the IcePaHC
#: corpus.
ICEPAHC = GithubLoader(user="antonkarl",
                       repo="icecorpus",
                       ref="master",
                       directory="finished")


class FileLoader(Loader):
    """A loader for corpus files from the local filesystem."""
    def __init__(self, path, extension=".psd", recursive=False):
        self._path = os.path.abspath(os.path.expanduser(path))
        self._extension = extension
        self._recursive = recursive

    def file(self, filename):
        return open(os.path.join(self._path, filename)).read()

    def files(self):
        files = []
        if self._recursive:
            for dirpath, dirnames, filenames in os.walk(self._path):
                for filename in filenames:
                    if filename.endswith(self._extension):
                        files.append(os.path.join(dirpath, filename))
        else:
            for filename in os.listdir(self._path):
                if filename.endswith(self._extension):
                    files.append(filename)
        return files
