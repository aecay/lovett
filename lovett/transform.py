"""Tree transformations to accommodate various corpus formats.

The functions in this module operate on `Tree` objects which have been read
from a corpus file in a known format.  Certain data is represented
conventionally (and idiosyncratically) in these corpora; these functions
convert this data into more useful metadata entries.

The following corpora are supported by the following functions:

* IcePaHC

  * `icepahc_case`
  * `icepahc_lemma`
  * `icepahc_year`

* General utility

  * `ensure_id`

.. note:: TODO

   To support:

   * IcePaHC: icepahc_word_splits
   * PPCHE (generally): ppche_make_unicode, ppche_word_splits
   * YCOE: ycoe_case
   * PCEEC: pceec_metadata

"""

from hashlib import md5

import lovett.util as util


# TODO: make sure ICEPAHC_CASE_LABELS is complete

#: Category labels which can bear case in IcePaHC.
ICEPAHC_CASE_LABELS = set(("N", "NS", "NPR", "NPRS", "Q", "D"))

#: Mapping between dash tags and case metadata values in IcePaHC.
ICEPAHC_CASES = {"N": "nominative",
                 "A": "accusative",
                 "D": "dative",
                 "G": "genitive"}


def _icepahc_case_do(tree):
    label = tree.label
    parts = label.split("-")
    # TODO: will we ever get something like N-G-1 with movt index???
    if len(parts) > 1 and parts[0] in ICEPAHC_CASE_LABELS and \
       parts[-1] in ICEPAHC_CASES:
        tree.label = "-".join(parts[:-1])
        tree.metadata["CASE"] = ICEPAHC_CASES[parts[-1]]


def icepahc_case(tree):
    _icepahc_case_do(tree)
    if util.is_nonterminal(tree):
        for subtree in tree:
            icepahc_case(subtree)


def icepahc_lemma(tree):
    if util.is_nonterminal(tree):
        for subtree in tree:
            icepahc_lemma(subtree)
    else:
        parts = tree.text.split("-")
        if len(parts) > 1:
            tree.text = "-".join(parts[:-1])
            tree.metadata["LEMMA"] = parts[-1]


def icepahc_year(tree):
    """Add year metadata to a tree from IcePaHC.

    This function assumes that the tree's file is already present in its
    metadata, and that the file name begins with a four-digit year.

    """
    tree.metadata.year = int(tree.metadata.file[0:4])


def ensure_id(tree):
    if tree.id is None:
        tree.root.metadata.id = md5.new().update(tree.root.urtext).hexdigest()

# TODO: ycoe_case
