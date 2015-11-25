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

* The PPCHE (in general)

  * `ppche_make_unicode`

* The YCOE

  * `ycoe_case`

* General utility

  * `ensure_id`

.. note:: TODO

   To support:

   * PPCHE (generally): ppche_word_splits
   * PCEEC: pceec_metadata

"""

from hashlib import md5
import re

import lovett.util as util


#: Category labels which can bear case in IcePaHC.
ICEPAHC_CASE_LABELS = set(("ADJ", "ADJR", "ADJS",
                           "ADV",  # Only one, tagged XXX
                           "ADVR",  # Few
                           "ALSO",
                           "D",
                           "DAN",
                           "ES",  # Only one, tagged XXX
                           "FP",
                           "MAG",  # Only one token
                           "MAN",
                           "N", "NS", "NPR", "NPRS",
                           "ONE", "ONES",
                           "OTHER", "OTHERS",
                           "PRO",
                           "Q", "QR", "QS",
                           "SUCH",
                           "VAG", "VAN", "VBN",
                           "WADJ", "WADV", "WD", "WPRO", "WQ"))

#: Mapping between dash tags and case metadata values in IcePaHC.
ICEPAHC_CASES = {"N": "nominative",
                 "A": "accusative",
                 "D": "dative",
                 "G": "genitive"}


def _icepahc_case_do(tree):
    label = tree.label
    parts = label.split("-")
    # The base label is the label without any dash tags.  Additionally, if it
    # is a compound tag with +, take the rightmost element.  And zap any
    # numeric word split indicators.
    base_label = re.sub("[1-3][1-3]$", "", parts[0].split("+")[-1])
    if len(parts) > 1 and base_label in ICEPAHC_CASE_LABELS and parts[-1] in ICEPAHC_CASES:
        tree.label = "-".join(parts[:-1])
        tree.metadata["CASE"] = ICEPAHC_CASES[parts[-1]]


def icepahc_case(tree):
    """Convert IcePaHC case to metadata.

    In IcePaHC, case is indicated as one of four dash tags attached to
    case-bearing lexical categories.

    """
    _icepahc_case_do(tree)
    if util.is_nonterminal(tree):
        for subtree in tree:
            icepahc_case(subtree)


def icepahc_lemma(tree):
    """Convert IcePaHC lemmata to matadata.

    In IcePaHC, lemmata are stored in the leaf text as ``text-lemma``.

    """
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

def icepahc_word_splits(tree):
    """Convert IcePaHC word splits to proper metadata.

    Words which begin with an ``@`` character have it stripped, and the
    ``IS-CONTINUATION`` metadata set.  Words which end with a ``@`` have it
    stripped, but no metadata is added (it would be redundant with
    ``IS-CONTINUATION``).

    .. note: TODO

        Earlier I had considered a ``HAS-CONTINUATION`` metadata key.  Would
        it be a good idea?

    """
    if util.is_leaf(tree):
        if tree.text.startswith("@"):
            tree.text = tree.text[1:]
            tree.metadata.is_continuation = True
        if tree.text.endswith("@"):
            tree.text = tree.text[:-1]
            # TODO: has_continuation?
    else:
        for child in tree:
            icepahc_word_splits(child)

#: Mapping between PPCHE codes and their unicode translation.  See section
#: B.2.2 at http://clu.uni.no/icame/manuals/HC/INDEX.HTM#con31
PPCHE_UNICODE_TRANSFORMS = [
    ("+a", "æ"),
    ("+A", "Æ"),
    ("+t", "þ"),
    ("+T", "Þ"),
    ("+d", "ð"),
    ("+D", "Ð"),
    ("+g", "ʒ"),
    ("+G", "Ʒ"),
    ("+L", "£"),
    ("+e", "ę"),
    ("+tt", "ꝥ"),
    ("+TT", "Ꝥ"),
    ("+Tt", "Ꝥ")
]

#: Mapping between letters and their Unicode superscripts
PPCHE_UNICODE_SUPERSCRIPT = {
    "a": "ᵃ",
    "b": "ᵇ",
    "c": "ᶜ",
    "d": "ᵈ",
    "e": "ᵉ",
    "f": "ᶠ",
    "g": "ᵍ",
    "h": "ʰ",
    "i": "ⁱ",
    "j": "ʲ",
    "k": "ᵏ",
    "l": "ˡ",
    "m": "ᵐ",
    "n": "ⁿ",
    "o": "ᵒ",
    "p": "ᵖ",
    # No superscript q!
    "r": "ʳ",
    "s": "ˢ",
    "t": "ᵗ",
    "u": "ᵘ",
    "v": "ᵛ",
    "w": "ʷ",
    "x": "ˣ",
    "y": "ʸ",
    "z": "ᶻ"
}


def _ppche_make_unicode_superscript(matchobj):
    g = matchobj.group(1)
    try:
        return "".join(map(lambda x: PPCHE_UNICODE_SUPERSCRIPT[x], list(g)))
    except KeyError:
        raise Exception("Could not convert to superscript: " + g)


def _ppche_make_unicode_leaf(leaf):
    for t in PPCHE_UNICODE_TRANSFORMS:
        leaf.text = leaf.text.replace(t[0], t[1])
    leaf.text = re.sub("=(.*?)=", _ppche_make_unicode_superscript, leaf.text)


def ppche_make_unicode(tree):
    """Convert characters in PPCHE format to unicode.

    Currently handles the ``+X`` notation for aesc, thorn, etc., as well as
    partial support for superscripts delimited by ``=...=``.

    """
    for child in tree:
        if util.is_leaf(tree):
            _ppche_make_unicode_leaf(child)
        else:
            ppche_make_unicode(child)


#: A mapping between caret-tags and case names in the YCOE
YCOE_CASES = {
    "A": "accusative",
    "N": "nominative",
    "D": "dative",
    "G": "genitive",
    "I": "instrumental"
}

#: A mapping between caret-tags and addverb types in the YCOE
YCOE_ADVERB_TYPES = {
    "T": "temporal",
    "L": "locative"
}


def ycoe_case(tree):
    """Convert case in the YCOE into metadata.

    Also handles the adverb-type notations ``^L`` and ``^T`` (locative and
    temporal), which the YCOE codes with a notation like the one for case.

    """
    l = tree.label.split("^")
    if len(l) > 1:
        if len(l) != 2:
            raise Exception("Label with more than 1 '^': %s" % tree.label)
        tree.label = l[0]
        if l[0] == "ADV":
            tree.metadata.adverb_type = YCOE_ADVERB_TYPES[l[1]]
        else:
            tree.metadata.case = YCOE_CASES[l[1]]
    if not util.is_leaf(tree):
        for child in tree:
            ycoe_case(child)


def ensure_id(tree):
    if tree.id is None:
        tree.root.metadata.id = md5.new().update(tree.root.urtext).hexdigest()
