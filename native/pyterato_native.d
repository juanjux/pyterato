module pyterato_native;

import checks;

import pyd.pyd;

class NativeCheckException : Exception
{
    this(string msg, string file = __FILE__, size_t line = __LINE__) {
        super(msg, file, line);
    }
}

class Checker
{
    private string currentWord;
    private string[] words;
    private bool[string] disabled;
    private bool[string] enabled;
    private string _SEPARATOR = "------------------------------";
    private uint _CONTEXT_SIZE = 6;
    private string[] function(string, string[])[string] checkers;

    this(uint numwords = 2048)
    {
        import std.array: reserve;

        words.reserve(numwords);

        checkers = [
            "pedanticsayword": &pedanticSayword,
            "misusedsayword": &misusedSayword,
            "overused": &overusedWord,
            "mente": &menteFind,
            "repetition": &repetitionFind,
            "cliche": &clicheFind,
            "misusedverb": &misusedVerbFind,
            "contained": &containedFind,
            "misusedexpression": &misusedExpressionFind,
            "calco": &calcoFind,
        ];
    }

    public string[] availableChecks()
    {
        return checkers.keys;
    }

    private string findMessage(string code, string custom_message)
    {
        auto prefix = min(words.length, _CONTEXT_SIZE);
        auto _context = join(words[$-prefix..$], " ");
        return _SEPARATOR ~ "[" ~ code ~ "]\n" ~ custom_message ~ "\n" ~
            "Contexto: ..." ~ _context ~ "...";
    }

    public void enable_check(string code)
    {
        if (code !in enabled)
            enabled[code] = true;

        if (code in disabled)
            disabled.remove(code);
    }

    public void disable_check(string code)
    {
        if (code !in disabled)
            disabled[code] = true;

        if (code in enabled)
            enabled.remove(code);
    }


    public string[] run_checks(string newWord)
    {
        words ~= newWord;

        if (words.length < 2 || is_common(newWord))
            return [];

        string[] res;

        foreach(checkCode; checkers.byKey) {
            if ((enabled.length > 0 && checkCode !in enabled) ||
                (disabled.length > 0 && checkCode in disabled)) {
                continue;
            }

            auto msgs = checkers[checkCode](newWord, words[0..$-1]);
            foreach(msg; msgs) {
                res ~= findMessage(checkCode, msg);
            }
        }

        return res;
    }
}

// FIXME: check if we need to specify params in the defs
extern(C) void PydMain() {
    module_init();

    wrap_class!(
        Checker,
        Def!(Checker.run_checks, string[] function(string)),
        Def!(Checker.availableChecks, string[] function()),
        Def!(Checker.enable_check, void function(string)),
        Def!(Checker.disable_check, void function(string)),
        Init!(uint),
    )();
}
