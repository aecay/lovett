def strip_corpussearch_comments(s):
    output = []
    comment = False
    for line in s.split("\n"):
        if line.startswith("/*") or line.startswith("/~*"):
            comment = True
        elif line.startswith("<+"):
            # Ignore parser-mode comments
            pass
        elif not comment:
            output.append(line)
        elif line.startswith("*/") or line.startswith("*~/"):
            comment = False
        else:  # pragma: no cover
            # Should never happen!
            pass

    if comment:
        raise Exception("Unterminated comment in input file!")

    return "\n".join(output)
