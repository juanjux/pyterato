module checks;

import checks_data;

import std.algorithm.mutation;
import std.algorithm.searching: startsWith, endsWith, canFind;
import std.algorithm: min, max;
import std.array: join;
import std.container.rbtree;
import std.format;
import std.path: globMatch;
import std.range;
import std.stdio;

// FIXME: turn the check functions into objects with:
// - CODE
// - check method.
// - mustRun method.

enum Check
{
    MENTE,
    CONTAINED,
    REPETITION,
    CLICHE,
    OVERUSED,
    PEDANTICSAYWORD,
    MISUSEDSAYWORD,
    MISUSEDVERB,
    MISUSEDEXPR,
    CALCO
}

// FIXME: generate at compile time so it's always updated
enum string[Check] check2str = [
    Check.MENTE: "mente",
    Check.CONTAINED: "contained",
    Check.REPETITION: "repetition",
    Check.CLICHE: "cliche",
    Check.OVERUSED: "overused",
    Check.PEDANTICSAYWORD: "pedanticsayword",
    Check.MISUSEDSAYWORD: "misusedsayword",
    Check.MISUSEDVERB: "misusedverb",
    Check.MISUSEDEXPR: "misusedexpression",
    Check.CALCO: "calco",
];

struct CheckSettings
{
    bool[Check] enabled;
    bool[Check] disabled;

    bool avoidCheck(Check code)
    {
        return ((enabled.length > 0 && code !in enabled) ||
                (disabled.length > 0 && code in disabled)) ;
    }

    bool avoidChecks(Check[] codes)
    {
        foreach (code; codes) {
            if (!avoidCheck(code))
                return false;
        }

        return true;
    }

    private Check getCheckCode(string code)
    {
        foreach(i; check2str.byKeyValue) {
            if (i.value == code)
                return i.key;
        }

        throw new Exception("No check found named '" ~ code ~ "'");
    }

    public void enable_check(string code)
    {
        auto enumCode = getCheckCode(code);

        if (enumCode !in enabled)
            enabled[enumCode] = true;

        if (enumCode in disabled)
            disabled.remove(enumCode);
    }

    public void disable_check(string code)
    {
        auto enumCode = getCheckCode(code);

        if (enumCode !in disabled)
            disabled[enumCode] = true;

        if (enumCode in enabled)
            enabled.remove(enumCode);
    }
}

CheckSettings checkSettings;

struct Finding
{
    string code;
    string msg;
}

pragma(inline, true)
bool is_common(in string word)
{
    return word in COMMON_WORDS;
}

// FIXME: optimize this merging all the expression checking in a single pass
Finding[] _checkExprList(Check code, in string word, in string[] words,
                        in string[][] exprList, in string msgFormatStr)
{
    foreach (expr; exprList) {
        if (!globMatch(word, expr[0]) || expr.length > (words.length + 1)) {
            continue;
        }

        // match: check the previous words in the expression
        auto prevcount = 1;
        bool fullMatch = true;

        foreach(exp_word; expr[1..$]) {
            if (!globMatch(words[$-prevcount], exp_word)) {
                fullMatch = false;
                break;
            }
            prevcount += 1;
        }

        if (fullMatch) {
            auto reversed = expr.dup;
            return [Finding(check2str[code], format(msgFormatStr, join(reversed.reverse(), " ")))];
        }
    }

    return [];
}

Finding[] nonContextWordCheck(in string word, in string[] words)
{
    Finding[] res;

    if (!checkSettings.avoidCheck(Check.MISUSEDSAYWORD) && word in USUALLY_MISUSED_SAYWORDS)
        res ~= Finding("misusedsayword",
                "Verbo generalmente mal usado en diálogos: " ~ word);

    if (!checkSettings.avoidCheck(Check.PEDANTICSAYWORD) && word in USUALLY_PEDANTIC_SAYWORDS)
        res ~= Finding("pedanticsayword", "Verbo generalmente pedante en diálogos: " ~ word);

    if (!checkSettings.avoidCheck(Check.OVERUSED)) {
        foreach(ow; OVERUSED_WORDS) {
            if (globMatch(word, ow))
                res ~= Finding("overused", "Palabra/verbo comodín: " ~ word);
        }
    }

    return res;
}

enum MENTE_OLDWORDS = 100;
enum CONTAINED_MIN_SIZE = 4;
enum CONTAINED_OLDWORDS = 15;
enum REPETITION_OLDWORDS = 50;

Finding[] proximityChecks(in string word, in string[] words)
{
    if (checkSettings.avoidChecks([Check.MENTE, Check.CONTAINED, Check.REPETITION]))
        return [];

    Finding[] res;

    auto maxPrev = min(words.length,
                       max(MENTE_OLDWORDS, CONTAINED_OLDWORDS, REPETITION_OLDWORDS));

    foreach_reverse(idx, oldword; words[$-maxPrev..$].enumerate(0)) {
        if (oldword == word) {
            // check: repetition
            if (!checkSettings.avoidCheck(Check.REPETITION) &&
                (maxPrev - idx <= REPETITION_OLDWORDS))
            {
                res ~= Finding("repetition",
                        format("Repetición de palabra '%s' %d palabras atrás", word,
                            maxPrev-idx));
            }

        } else {
            // check: mente
            if (!checkSettings.avoidCheck(Check.MENTE) &&
                (maxPrev - idx <= MENTE_OLDWORDS) &&
                word != "mente" && oldword != "mente" &&
                endsWith(word, "mente") && endsWith(oldword, "mente"))

            {
                res ~= Finding("mente", format("Repetición de palabra con sufijo mente " ~
                            "('%s') %d palabras atrás: %s", word, maxPrev-idx, oldword));
            }

            // check: contained
            if (!checkSettings.avoidCheck(Check.CONTAINED) &&
                (maxPrev - idx <= CONTAINED_OLDWORDS) &&
                // FIXME: this length is not in graphemes...
                (word.length >= CONTAINED_MIN_SIZE && oldword.length >= CONTAINED_MIN_SIZE) &&
                !oldword.endsWith("mente") &&
                (canFind(word, oldword) || canFind(oldword, word)))
            {
                res ~= Finding("contained",
                        format("Repetición de palabra contenida '%s' %d palabras atrás: %s",
                            word, maxPrev-idx, oldword));
            }
        }
    }

    return res;
}

Finding[] clicheFind(in string word, in string[] words)
{
    auto CODE = Check.CLICHE;
    if (checkSettings.avoidCheck(CODE))
        return [];

    auto wordStart = word[0..min(word.length, _CLICHE_EXPR_DICT_KEYLEN)];
    auto expr_list = wordStart in _CLICHE_EXPR_DICT;
    if (expr_list is null)
        return [];

    return _checkExprList(CODE, word, words, *expr_list, "Expesión cliché: %s");
}

Finding[] misusedVerbFind(in string word, in string[] words)
{
    auto CODE = Check.MISUSEDVERB;
    if (checkSettings.avoidCheck(CODE))
        return [];

    foreach(misused; USUALLY_MISUSED_VERB_ROOTS) {
        auto root = misused[0];
        if (globMatch(word, misused[0])) {
            foreach(allowed; misused[1..$]) {
                if (word == allowed)
                    return [];

                return [Finding(check2str[CODE], "Verbo generalmente mal usado: " ~ word)];
            }
        }
    }

    return [];
}

Finding[] misusedExpressionFind(in string word, in string[] words)
{
    auto CODE = Check.MISUSEDEXPR;
    if (checkSettings.avoidCheck(CODE))
        return [];

    return _checkExprList(CODE, word, words, USUALLY_MISUSED_EXPR,
                         "Expresión generalmente mal usada: %s");
}

Finding[] calcoFind(in string word, in string[] words)
{
    auto CODE = Check.CALCO;
    if (checkSettings.avoidCheck(CODE))
        return [];

    return _checkExprList(CODE, word, words, CALCO_EXPR, "Calco / extranjerismo: %s");
}
