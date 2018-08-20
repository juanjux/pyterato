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

struct CheckSettings
{
    bool[string] enabled;
    bool[string] disabled;

    bool avoidCheck(string code)
    {
        return ((enabled.length > 0 && code !in enabled) ||
                (disabled.length > 0 && code in disabled)) ;
    }

    bool avoidChecks(string[] codes)
    {
        foreach (code; codes) {
            if (!avoidCheck(code))
                return false;
        }

        return true;
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
Finding[] _checkExprList(string code, in string word, in string[] words,
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
            return [Finding(code, format(msgFormatStr, join(reversed.reverse(), " ")))];
        }
    }

    return [];
}

Finding[] pedanticSayword(in string word, in string[] words)
{
    auto CODE = "pedanticsayword";
    if (checkSettings.avoidCheck(CODE))
        return [];

    if (word in USUALLY_PEDANTIC_SAYWORDS)
        return [Finding(CODE, "Verbo generalmente pedante en diálogos: " ~ word)];

    return [];
}

Finding[] misusedSayword(in string word, in string[] words)
{
    auto CODE = "misusedsayword";
    if (checkSettings.avoidCheck(CODE))
        return [];

    if (word in USUALLY_MISUSED_SAYWORDS)
        return [Finding(CODE, "Verbo generalmente mal usado en diálogos: " ~ word)];

    return [];
}

Finding[] overusedWord(in string word, in string[] words)
{
    auto CODE = "overused";
    if (checkSettings.avoidCheck(CODE))
        return [];

    Finding[] res;

    foreach(ow; OVERUSED_WORDS) {
        if (globMatch(word, ow))
            res ~= Finding(CODE, "Palabra/verbo comodín: " ~ word);
    }

    return res;
}

// FIXME: merge mente, contained and repetition
enum MENTE_OLDWORDS = 100;
enum CONTAINED_MIN_SIZE = 4;
enum CONTAINED_OLDWORDS = 15;
enum REPETITION_OLDWORDS = 50;

Finding[] wordCompareMultiCheck(in string word, in string[] words)
{
    // FIXME: uuuuugly! move the predicates to functions
    if (checkSettings.avoidChecks(["mente", "contained", "repetition"]))
        return [];

    Finding[] res;

    auto maxPrev = min(words.length,
                       max(MENTE_OLDWORDS, CONTAINED_OLDWORDS, REPETITION_OLDWORDS));

    foreach_reverse(idx, oldword; words[$-maxPrev..$].enumerate(0)) {
        if (oldword == word) {
            // check: repetition
            if (!checkSettings.avoidCheck("repetition") &&
                (maxPrev - idx <= REPETITION_OLDWORDS))
            {
                res ~= Finding("repetition",
                        format("Repetición de palabra '%s' %d palabras atrás", word,
                            maxPrev-idx));
            }

        } else {
            // check: mente
            if (!checkSettings.avoidCheck("mente") &&
                (maxPrev - idx <= MENTE_OLDWORDS) &&
                word != "mente" && oldword != "mente" &&
                endsWith(word, "mente") && endsWith(oldword, "mente"))

            {
                res ~= Finding("mente", format("Repetición de palabra con sufijo mente " ~
                            "('%s') %d palabras atrás: %s", word, maxPrev-idx, oldword));
            }

            // check: contained
            if (!checkSettings.avoidCheck("contained") &&
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
    auto CODE = "contained";
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
    auto CODE = "misusedverb";
    if (checkSettings.avoidCheck(CODE))
        return [];

    foreach(misused; USUALLY_MISUSED_VERB_ROOTS) {
        auto root = misused[0];
        if (globMatch(word, misused[0])) {
            foreach(allowed; misused[1..$]) {
                if (word == allowed)
                    return [];

                return [Finding(CODE, "Verbo generalmente mal usado: " ~ word)];
            }
        }
    }

    return [];
}

Finding[] misusedExpressionFind(in string word, in string[] words)
{
    auto CODE = "misusedexpression";
    if (checkSettings.avoidCheck(CODE))
        return [];

    return _checkExprList(CODE, word, words, USUALLY_MISUSED_EXPR,
                         "Expresión generalmente mal usada: %s");
}

Finding[] calcoFind(in string word, in string[] words)
{
    auto CODE = "calco";
    if (checkSettings.avoidCheck(CODE))
        return [];

    return _checkExprList(CODE, word, words, CALCO_EXPR, "Calco / extranjerismo: %s");
}
