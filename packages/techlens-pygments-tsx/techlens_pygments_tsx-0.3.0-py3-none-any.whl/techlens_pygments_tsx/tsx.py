from jsx import JsxLexer
from jsx.lexer import TOKENS
from pygments.lexers.javascript import TypeScriptLexer
from pygments.lexers._mapping import LEXERS
from pygments.lexers import _lexer_cache


class TypeScriptXLexer(TypeScriptLexer):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.tokens = TOKENS | super().tokens

    name = "TypeScriptX"
    aliases = ["tsx", "typescriptx"]
    filenames = ["*.tsx"]
    tokens = TOKENS


class ToolScriptLexer(TypeScriptLexer):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.tokens = TOKENS | super().tokens

    name = "ToolScript"
    aliases = ["rsx", "toolscript"]
    filenames = ["*.rsx"]
    tokens = TOKENS


def patch_pygments():
    # Hack to register an internal lexer.
    _lexer_cache["TypeScriptXLexer"] = TypeScriptXLexer
    _lexer_cache["ToolScriptLexer"] = ToolScriptLexer
    _lexer_cache["JsxLexer"] = JsxLexer

    LEXERS["TypeScriptXLexer"] = (
        "",
        "TypeScriptXLexer",
        ("typescriptx", "pygments_tsx"),
        ("*.tsx",),
        ("application/x-typescript", "text/x-typescript"),
    )

    LEXERS["ToolScriptLexer"] = (
        "",
        "ToolScriptLexer",
        ("toolscript", "rsx"),
        ("*.rsx",),
        ("application/x-toolscript", "text/x-toolscript"),
    )

    LEXERS["JsxLexers"] = (
        "",
        "JsxLexer",
        ("react", "jsx"),
        ("*.jsx", "*.react"),
        ("text/jsx"),
    )
