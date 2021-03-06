"""
    The preprocessing tokens in C are particularly hard, and
    this character stream makes it slightly easier.
"""

class CharacterStream(object):
    def __init__(self, generator, line=1, filename=""):
        self.comments = True
        self.generator = discard_comments(self, logical_characters(self, generator))
        self.line = line
        self.filename = filename
        self.character = '\n' # Marks beginning of new line
                              # Doesn't go through line incrementing, so
                              # it is sufficient for denoting beginning of the first line.

    def get_next(self):
        assert self.character, "error in tokenizing"
        character = self.character
        self.character = pull(self.generator)
        return character

    def is_space(self):
        return self.character in spaces

    def skip_spaces(self):
        while self.character in spaces:
            self.get_next()

    def skip_spaces_and_newlines(self):
        while self.character in spaces_and_newlines:
            self.get_next()

    @property
    def position(self):
        return self.line, self.filename

def logical_characters(stream, sequence):
    backslash = False
    for ch in sequence:
        if backslash:
            backslash = False
            if ch == "\n":
                stream.line += 1
                continue
            yield "\\"
            if ch != "\\":
                yield ch
            continue
        elif ch != "\\":
            if ch == "\n":
                stream.line += 1
            yield ch
        else:
            backslash = True
    if backslash:
        yield "\\"

def discard_comments(stream, sequence):
    "C tokenizer is fat!"
    state = 0
    for ch in sequence:
        if state == 0:
            if ch != '/':
                yield ch
            elif stream.comments:
                state = 1
            else:
                yield ch
        elif state == 1:
            if ch == '/':
                state = 2
            elif ch == '*':
                state = 3
            else:
                yield '/'
                yield ch
                state = 0
        elif state == 2 and ch == '\n':
            yield ch
            state = 0
        elif state == 3 and ch == '*':
            state = 4
        elif state == 4:
            if ch == '/':
                yield ' '
                state = 0
            elif ch != '*':
                state = 3

def pull(generator):
    try:
        return generator.next()
    except StopIteration as stop:
        return ""


spaces = set(['\x00', ' ', '\t', '\r'])
spaces_and_newlines = set(['\x00', ' ', '\t', '\r', '\n'])
