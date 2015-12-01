# This came from transform.py, but it's already handled in the parsing code in
# tree.py.  Keeping it around in case we ever decide to make tree.py dumber.
def movement_index(tree):
    """Convert movement indices expressed on node labels into metadata.

    Labels of the form XP-#, where # represents a string of digits 0-9, is
    transformed into two metadata values on the node.  The digit is the value
    of the ``INDEX`` key, and ``regular`` is assigned to ``IDXTYPE``.  For
    indexes of the form XP=#, ``IDXTYPE`` is instead ``gap``.  Traces -- that
    is, nodes with the text ``*T*``, ``*ICH*``, ``*``, and ``*CL*`` have their
    index taken from the node text.  All other nodes derive their index from
    the label.

    """
    if util.is_leaf(tree):
        t = tree.text
        index_text = True
        if not t.startswith("*T*") or t.startswith("*CL*") or t.startswith("*ICH*") or \
           t.startswith("*-") or t.startswith("*="):
            t = tree.label
            index_text = False
    else:
        t = tree.label
        index_text = False

    parts = t.split("=")
    if len(parts) > 1:
        idxtype = "gap"
        idx = parts[-1]
        txt = "=".join(parts[:-1])
    else:
        parts = t.split("-")
        if len(parts) > 1:
            idx = parts[-1]
            idxtype = "regular"
            txt = "-".join(parts[:-1])
        else:
            # Bogus value which will fail the test for numeric indices
            idx = "X"
    if all(map(lambda char: char in set(("0", "1", "2", "3", "4",
                                         "5", "6", "7", "8", "9")), list(idx))):
        tree.metadata.index = idx
        tree.metadata.idxtype = idxtype
        if index_text:
            tree.text = txt
        else:
            tree.label = txt

    if not util.is_leaf(tree):
        for child in tree:
            movement_index(child)
