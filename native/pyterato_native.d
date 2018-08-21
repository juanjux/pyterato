module pyterato_native;

import checks;

import pyd.pyd;

import std.algorithm: min;
import std.array: join;

class NativeCheckException : Exception
{
    this(string msg, string file = __FILE__, size_t line = __LINE__) {
        super(msg, file, line);
    }
}

// FIXME: should be a Singleton
class Checker
{
    private string currentWord;
    private string[] words;
    private bool[string] disabled;
    private bool[string] enabled;
    private string _SEPARATOR = "------------------------------";
    private uint _CONTEXT_SIZE = 6;
    private Finding[] function(string, string[])[] checkers;

    this(uint numwords = 2048)
    {
        import std.array: reserve;

        words.reserve(numwords);

        checkers = [
            &nonContextWordCheck,
            &proximityChecks,
            &clicheFind,
            &misusedVerbFind,
            &misusedExpressionFind,
            &calcoFind,
        ];
    }

    // FIXME: use compile time programming to inspect the checks.d module
    // and generate this list
    public string[] available_checks()
    {
        return check2str.values();
    }

    public void enable_check(string code)
    {
        checkSettings.enable_check(code);
    }

    public void disable_check(string code)
    {
        checkSettings.disable_check(code);
    }

    private string findMessage(string code, string custom_message)
    {
        auto prefix = min(words.length, _CONTEXT_SIZE);
        auto _context = join(words[$-prefix..$], " ");
        return _SEPARATOR ~ "[" ~ code ~ "]\n" ~ custom_message ~ "\n" ~
            "Contexto: ..." ~ _context ~ "...";
    }

    public string[] run_checks(string newWord)
    {
        words ~= newWord;

        if (words.length < 2 || is_common(newWord))
            return [];

        string[] res;

        foreach(checker; checkers) {
            foreach(finding; checker(newWord, words[0..$-1])) {
                res ~= findMessage(finding.code, finding.msg);
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
        Def!(Checker.available_checks, string[] function()),
        Def!(Checker.enable_check, void function(string)),
        Def!(Checker.disable_check, void function(string)),
        Init!(uint),
    )();
}
