"""Methods to fetch corpora from the web, filesystem, or other sources.

Currently includes:

* A loader for local files
* A loader for files from `IcePaHC <http://www.linguist.is/icelandic_treebank/Icelandic_Parsed_Historical_Corpus_(IcePaHC)>`_

.. note:: TODO

   It should be possible to associate a pipeline of functions from
   ``transform.py`` with a corpus loader, and to specify e.g. the IcePaHC
   loader as having the appropriate transforms built in.

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
# memory? LATER NOTE: that makes no sense, since the tree must be created
# anyway in order to know whether we want to filter it.


class Loader(object):
    """This is a base class for corpus loaders to inherit from.

    .. note:: TODO

       * For speed/memory reasons , should this class have a method that
         converts directly to a `CorpusDb` object, without passing through a
         `Corpus` first?
       * Is there a way to use the superclass to implement the caching?  Perhaps
         it's too much hassle.

    """
    @abc.abstractmethod
    def file(self, filename):
        """Return the content of one of the files from a corpus.

        This method must use caching if it makes network requests or uses
        other expensive resources (beyond disk access).  Subclasses should
        call the method defined on this class (via ``super()``) in order to
        partake of common error checking code.

        Args:
            filename (str): The name of the file requested.

        Returns:
            str: The file's content.

        """
        if filename not in self.files():
            raise Exception("Invalid filename")

    @abc.abstractmethod
    def files(self):
        """Return a list of files in the corpus.

        This method must use caching if it makes network requests or uses other
        expensive resources (beyond disk access).

        Returns:
            list of str: List of filenames.
        """
        pass

    def corpus(self, files=None):
        """Load files into a `Corpus`.

        .. note:: TODO

           Handle file-level metadata in this method (need a specification of
           how this appears in the files as well).

        Args:
            files (str or list of str): The files to include in the corpus.
                Default is to include all available files.
        Returns:
            Corpus: The corpus composed of all trees in all files.

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
                    c.append(tree_obj)
        return c


# TODO: add a method to allow authentication, for private repos
_GITHUB = Github()


class GithubLoader(Loader):
    """A generic interface for fetching corpus files from a Github repo."""
    def __init__(self, user, repo, ref="master", directory="", extension=".psd"):
        """Initialize a GithubLoader.

        .. note:: TODO

           * support corpora with parsed files in more than one directory
           * support corpora with more than one kind of file extension

        Args:
            user (str): Github username of the repository to load from
            repo (str): Name of the repository to load from.
            tag (str): A git ref of the revision to fetch.
                Defaults to "master", the latest revision.  If the repository
                uses git tags, you can request a specific version of the
                corpus.  You can also use a sha1 hash to request a specific
                revision.
            directory (str): Path to the directory containing parsed files.
            extension (str): File extension of corpus files. Defaults to ".psd".

        """
        self._user = user
        self._repo = repo
        self._tag = ref
        self._directory = directory
        self._extension = extension
        self._files = None
        self._file_content = {}

    def file(self, filename):
        super().file(filename)
        if filename in self._file_content:
            return self._file_content[filename]
        print("https://raw.githubusercontent.com/%s/%s/%s/%s%s" %
                               (self._user, self._repo,
                                self._tag, self._directory, filename))
        content = requests.get("https://raw.githubusercontent.com/%s/%s/%s/%s%s" %
                               (self._user, self._repo,
                                self._tag, self._directory, filename)).text
        self._file_content[filename] = content
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
    """A loader for corpus files from the local filesystem.

    Args:
        path (str): path to the directory where the corpus files can be found.
        extension (str): the file extension used by the corpus.  Defaults
            to ``.psd``, which is the Penn Historical Corpora standrad.
        recursive (bool): whether to search for files in ``path`` recursively,
            or only consider files immediately contained therein.

    """
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
