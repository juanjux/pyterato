module checks;

import checks_data;

import std.algorithm.mutation;
import std.algorithm.searching: startsWith, endsWith, canFind;
import std.algorithm: min;
import std.array: join;
import std.format;
import std.path: globMatch;
import std.range;
import std.stdio;

bool check_set(in string word, in bool[string] set)
{
    auto found = word in set;
    return found != null;
}

bool is_common(in string word)
{
    return check_set(word, COMMON_WORDS);
}

string[] _checkExprList(in string word, in string[] words, in string[][] exprList,
                       in string msgFormatStr)
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
            return [format(msgFormatStr, join(reversed.reverse(), " "))];
        }
    }

    return [];
}

string[] pedanticSayword(in string word, in string[] words)
{
    if (check_set(word, USUALLY_PEDANTIC_SAYWORDS)) {
        return ["Verbo generalmente pedante en diálogos: " ~ word];
    }

    return [];
}

string[] misusedSayword(in string word, in string[] words)
{
    if (check_set(word, USUALLY_MISUSED_SAYWORDS)) {
        return ["Verbo generalmente mal usado en diálogos: " ~ word];
    }

    return [];
}

string[] overusedWord(in string word, in string[] words)
{
    string[] res;

    foreach(ow; OVERUSED_WORDS) {
        if (globMatch(word, ow)) {
            res ~= "Palabra/verbo comodín: " ~ word;
        }
    }

    return res;
}

enum MENTE_OLDWORDS = 100;
string[] menteFind(in string word, in string[] words)
{

    string[] res;
    auto numprev = min(MENTE_OLDWORDS, words.length);

    if (word != "mente" && endsWith(word, "mente")) {
        foreach(idx, oldword; words[$-numprev..$].enumerate(0)) {
            if (oldword != "mente" && endsWith(oldword, "mente")) {
                res ~= format("Repetición de palabra con sufijo mente ('%s') %d palabras atrás: %s",
                              word, idx, oldword);
            }
        }
    }

    return res;
}

enum CONTAINED_MIN_SIZE = 4;
enum CONTAINED_OLDWORDS = 15;
string[] containedFind(in string word, in string[] words)
{
    if (word.length < CONTAINED_MIN_SIZE)
        return [];

    string[] res;
    auto numprev = min(CONTAINED_OLDWORDS, words.length);

    foreach_reverse(idx, oldword; words[$-numprev..$].enumerate(0)) {
        if (oldword.length == 0 || is_common(oldword) || oldword.length < CONTAINED_MIN_SIZE)
            continue;

        if (!oldword.endsWith("mente") && oldword != word) {
            if (canFind(word, oldword) || canFind(oldword, word)) {
                res ~= format("Repetición de palabra contenida '%s' %d palabras atrás: %s",
                              word, numprev-idx, oldword);
            }
        }
    }

    return res;
}

enum REPETITION_OLDWORDS = 50;
// FIXME: search for approximate words or words containing this too
string[] repetitionFind(in string word, in string[] words)
{
    string[] res;
    auto numprev = min(REPETITION_OLDWORDS, words.length);

    foreach(idx, oldword; words[$-numprev..$].enumerate(0)) {
        if (oldword == word) {
            res ~= format("Repetición de palabra '%s' %d palabras atrás", word, idx);
        }
    }

    return res;
}

string[] clicheFind(in string word, in string[] words)
{
    auto wordStart = word[0..min(word.length, _CLICHE_EXPR_DICT_KEYLEN)];
    auto expr_list = wordStart in _CLICHE_EXPR_DICT;
    if (expr_list is null)
        return [];

    return _checkExprList(word, words, *expr_list, "Expesión cliché: %s");
}

string[] misusedVerbFind(in string word, in string[] words)
{
    foreach(misused; USUALLY_MISUSED_VERB_ROOTS) {
        auto root = misused[0];
        if (globMatch(word, misused[0])) {
            foreach(allowed; misused[1..$]) {
                if (word == allowed)
                    return [];

                return ["Verbo generalmente mal usado: " ~ word];
            }
        }
    }

    return [];
}

string[] misusedExpressionFind(in string word, in string[] words)
{
    return _checkExprList(word, words, USUALLY_MISUSED_EXPR,
                         "Expresión generalmente mal usada: %s");
}

string[] calcoFind(in string word, in string[] words)
{
    return _checkExprList(word, words, CALCO_EXPR,
                         "Calco / extranjerismo: %s");
}

