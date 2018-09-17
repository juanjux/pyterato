module pyterato_native;

import checks;

import pyd.pyd;

import std.algorithm: min;
import std.array: join;
import std.stdio;
import std.typecons: tuple, Tuple;

class NativeFileException : Exception
{
    this(string msg, string file = __FILE__, size_t line = __LINE__) {
        super(msg, file, line);
    }
}

class NativeCheckException : Exception
{
    this(string msg, string file = __FILE__, size_t line = __LINE__) {
        super(msg, file, line);
    }
}

class StopIteration : Exception
{
    this(string file = __FILE__, size_t line = __LINE__) {
        super("", file, line);
    }
}

class TxtFileWordIterator
{
    private uint words_idx = 0;
    string[] words;

    void loadFile(string fname = "")
    {
        import std.file;
        import std.array;

        if (!exists(fname))
            throw new NativeFileException("File not found");

        words = split(readText(fname));
    }

    struct Range {
        string[] words;
        uint words_idx = 0;

        this(string[] w) {
            words = w;
        }

        @property bool empty() {
            return words_idx >= words.length;
        }

        @property Tuple!(string, int) front() {
            return tuple(words[words_idx], 0);
        }

        void popFront() {
            words_idx++;
        }
    }

    Range __iter__()
    {
        return Range(words);
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

    wrap_class!(
        TxtFileWordIterator,
        Def!(TxtFileWordIterator.loadFile, void function(string)),
        Def!(TxtFileWordIterator.__iter__, TxtFileWordIterator.Range function()),
    )();
}
