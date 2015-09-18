from functools import reduce
import re

TRACE_TYPES = ["*T*", "*ICH*", "*CL*", "*"]
SILENT_TYPES = ["*con*", "*exp*", "*pro*"]
IDX_GAP = "gap"
IDX_REGULAR = "regular"

# ### Tree validation
# # TODO: this fn is untested
# def validateIndices(tree):
#     indices = []
#     for leaf in tree.leaves():
#         idx = indexOfTree(leaf)
#         if indices[idx]:
#             indices[idx] = indices[idx] + 1
#         else:
#             indices[idx] = 1
#     valid = True
#     for i in indices:
#         if not indices[i] or indices[i] == 1:
#             valid = False
#     return valid

# def validateTagset(tree, tags, dashes):
#     # TODO: Idea: allow passing a list of lists, like:
#     # [ ["NP", "-OB1", "-OB2", ...],
#     #   ...
#     #   ] <-- or maybe use a dict?
#     # Convert this into a grammar (peg style) and validate against it.
#     # Also: separate tagsets for leaves and non-terminals
#     pass

# ### Traces/movement indices
# def _max_or_none(x, y):
#     if x is None and y is None:
#         return None
#     if y is None:
#         return x
#     if x is None:
#         return y
#     return max(x, y)

# def largest_index(tree):
#     return reduce(_max_or_none, map(index, tree.subtrees))


def set_index(tree, index):
    tree.metadata['INDEX'] = index


def index(tree):
    return tree.metadata.get('INDEX', None)


def index_type(tree):
    idx = tree.metadata.get('IDX-TYPE', None)
    if idx and idx not in (IDX_GAP, IDX_REGULAR):
        raise ValueError("Illegal index type %s" % idx)
    return idx

# def index_type_short(tree):
#     it = index_type(tree)
#     if it == IDX_GAP:
#         return "="
#     elif it == IDX_REGULAR:
#         return "-"
#     else:
#         return None


def remove_index(tree):
    try:
        del tree.metadata['INDEX']
    except KeyError:
        pass
    try:
        del tree.metadata['IDX-TYPE']
    except KeyError:
        pass


def label_and_index(s):
    l = s.split("=")
    if len(l) > 2:
        raise ValueError("too many = signs in label: %s" % s)
    if len(l) > 1:
        if l[-1].isdigit():
            return "=".join(l[:-1]), IDX_GAP, int(l[-1])
    l = s.split("-")
    if len(l) > 1:
        if l[-1].isdigit():
            return "-".join(l[:-1]), IDX_REGULAR, int(l[-1])
        else:
            return s, None, None
    else:
        return s, None, None

# def index_from_string(s):
#     return label_and_index(s)[2]

# def index_type_from_string(s):
#     return label_and_index(s)[1]

# TODO: are traces leaves?
def is_leaf(t):
    import lovett.tree
    return isinstance(t, lovett.tree.Leaf)


def is_trace(t):
    return is_leaf(t) and t.text in TRACE_TYPES


def is_trace_string(l):
    return l.split("-")[0] in TRACE_TYPES


def is_silent(t):
    return is_leaf(t) and t.text in SILENT_TYPES


def is_ec(t):
    return is_leaf(t) and (t.text == "0" or is_trace(t) or is_silent(t))


def is_text_leaf(t):
    return is_leaf(t) and not is_ec(t) and not is_silent(t) and \
        t.label.split("-")[0] not in ("CODE", "CODING")


def is_nonterminal(t):
    import lovett.tree
    return isinstance(t, lovett.tree.NonTerminal)

# def iter_flatten(iterable):
#     it = iter(iterable)
#     for e in it:
#         if isinstance(e, (list, tuple)) and not \
#            isinstance(e, lovett.tree.Tree):
#             for f in iter_flatten(e):
#                 yield f
#         else:
#             yield e

# def _parseVersionTree(t):
#     """Parse a version tree.

#     A version tree must have the form:

#     ::

#       ( (VERSION (KEY1 val1)
#                  (KEY2 (SUBKEY1 val1))))

#     :param t: the version tree to parse
#     :type t: `LovettTree`

#     """
#     if not isinstance(t, lovett.tree_new.Root):
#         raise ValueError("pass a Root tree to _parseVersionTree: %r" % t)
#     version = t.tree
#     if version.label != "VERSION":
#         return None
#     return _treeToDict(t[0])

# def _treeToDict(t):
#     """Convert a `LovettTree` to a dictionary.

#     Each key in the dictionary corresponds to a node label from the
#     tree; each value is either a string (leaf node) or another dict
#     (recursive node.)

#     """
#     if isinstance(t, lovett.tree_new.Leaf):
#         return t.text
#     elif isinstance(t, lovett.tree_new.Root):
#         return _treeToDict(t.tree)
#     else:
#         return dict([(n.label, _treeToDict(n)) for n in t])

# UNIFY_VERSION_IGNORE_KEYS = ["HASH"]

# def _unifyVersionTrees(old, new):
#     for k in new.keys():
#         if k in UNIFY_VERSION_IGNORE_KEYS:
#             continue
#         if k in old:
#             if old[k] == new[k]:
#                 pass
#             else:
#                 raise Exception("Mismatched version info")
#         else:
#             old[k] = new[k]
#     return old

# def metadata_str(dic, name="METADATA", indent=0):
#     r = "(" + name + " "
#     l = len(r)

#     def helper(d, k):
#         if not isinstance(d[k], dict):
#             return "(" + k + " " + str(d[k]) + ")"
#         else:
#             return metadata_str(d[k], k, indent + l)
#     r += ("\n" + " " * (indent + l)).join(
#         helper(dic, key) for key in sorted(dic.keys())
#     )
#     r += ")"
#     return r

# def is_word(tree):
#     return (is_leaf(tree)) and (not is_ec(tree)) and \
#         tree.label not in ["CODE", ".", ",", "FW"]

# def is_code_node(tree):
#     return tree.label == "CODE"
