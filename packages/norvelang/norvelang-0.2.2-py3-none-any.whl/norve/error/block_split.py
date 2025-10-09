"""Block splitting utilities for Norvelang pipelines."""


def split_blocks(pipeline: str):
    """
    Split a pipeline string into top-level blocks, handling multi-line `let` statements.
    Blocks start when a line (after stripping) begins with:
      - "let "
      - "$" (a variable)
      - a filename/token that ends with a known extension (csv,json,xlsx,xls,sqlite,db,xml)

    Multi-line let: after a `let ...` line that doesn't terminate, subsequent lines are
    collected until a terminating condition is seen:
      - a line that ends with a known extension
      - a line that starts with '|' (pipeline continuation) or '$' (new block)
      - a line that itself is a block starter

    Comments (lines beginning with '#') and empty lines are ignored.
    """
    extensions = (".csv", ".json", ".xlsx", ".xls", ".sqlite", ".sqlite3", ".db", ".xml")

    def is_comment_or_empty(s: str) -> bool:
        return not s or s.startswith("#")

    def looks_like_filename_token(tok: str) -> bool:
        tok = tok.rstrip(",")  # allow tokens followed by commas
        for ext in extensions:
            if tok.lower().endswith(ext):
                return True
        return False

    def line_is_block_starter(stripped: str) -> bool:
        if stripped.startswith("let "):
            return True
        if stripped.startswith("$"):
            return True
        # check first token for filename-like ending
        first_tok = stripped.split()[0] if stripped.split() else ""
        return looks_like_filename_token(first_tok)

    def line_is_let_start(stripped: str) -> bool:
        return stripped.startswith("let ")

    def line_terminates_let(stripped: str) -> bool:
        # A let is considered complete if:
        # - the line ends with a known extension
        # - OR the line starts a pipeline ('|') or a new variable ('$')
        if not stripped:
            return False
        if stripped.startswith(("|", "$")):
            return True
        for ext in extensions:
            if stripped.lower().endswith(ext):
                return True
        # also if the line itself starts a new block (e.g., new 'let' or filename)
        return line_is_block_starter(stripped)

    blocks = []
    current_block = []
    in_multiline_let = False

    for raw_line in pipeline.splitlines():
        stripped = raw_line.strip()

        # skip comments and blank lines
        if is_comment_or_empty(stripped):
            continue

        # If we are inside a multi-line let, keep appending until termination
        if in_multiline_let:
            current_block.append(raw_line)
            if line_terminates_let(stripped):
                in_multiline_let = False
            continue

        # normal handling: decide if this line starts a new block
        starter = line_is_block_starter(stripped)

        if starter and current_block:
            # commit previous block
            blocks.append("\n".join(current_block))
            current_block = [raw_line]
        else:
            current_block.append(raw_line)

        # if this line starts a let but does NOT terminate it, open multiline mode
        if line_is_let_start(stripped) and not line_terminates_let(stripped):
            in_multiline_let = True

    if current_block:
        blocks.append("\n".join(current_block))

    return blocks
