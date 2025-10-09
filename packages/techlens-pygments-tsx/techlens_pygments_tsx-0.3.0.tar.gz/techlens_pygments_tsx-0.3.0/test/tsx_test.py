import os

import pygments
from pygments import lexers
from pygments.token import _TokenType
from techlens_pygments_tsx.tsx import TypeScriptXLexer
from techlens_pygments_tsx.tsx import ToolScriptLexer
from techlens_pygments_tsx.tsx import patch_pygments

parent = os.path.dirname(__file__)
tsx_file_path = os.path.join(parent, "Blank.tsx")
rsx_file_path = os.path.join(parent, "Sample.rsx")


def test_lexer_on_Blank():
    tsx_lexer = TypeScriptXLexer()
    with open(tsx_file_path) as f:
        txt = f.read()
        tokens = pygments.lex(txt, lexer=tsx_lexer)
        tokens = list(tokens)
        for idx, token in enumerate(tokens):
            print(idx)
            print(token)
        assert tokens[27][1] == "div"
        assert isinstance(tokens[27][0], _TokenType)


def test_patch_pygments():
    patch_pygments()
    lexers.get_lexer_for_filename(tsx_file_path)
    assert True


def test_pygmemts():
    assert True


def test_lexer_on_rsx():
    rsx_lexer = ToolScriptLexer()
    with open(rsx_file_path) as f:
        txt = f.read()
        tokens = list(pygments.lex(txt, lexer=rsx_lexer))
        # Test for some RSX-specific tokens
        filtered_tokens = (t for t in tokens if t[1] == "Container")
        container_token = next(filtered_tokens, None)
        assert container_token is not None
        text_token = next((t for t in tokens if t[1] == "Text"), None)
        assert text_token is not None

        # Verify lexer name
        assert rsx_lexer.name == "ToolScript"
        # Verify file extension support
        assert "*.rsx" in rsx_lexer.filenames
