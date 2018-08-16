#!/usr/bin/env python3

from enum import Enum
import re

from utils import *

COMMENT_SYM = ';'
ESCAPE_SYM = '\\'

ALIAS_SYM = '~'
SLOT_SYM = '@'
INTENT_SYM = '%'
UNIT_OPEN_SYM = '['
UNIT_CLOSE_SYM = ']'

VARIATION_SYM = '#'
RAND_GEN_SYM = '?'
PERCENT_GEN_SYM = '/'
CASE_GEN_SYM = '&'

ALT_SLOT_VALUE_NAME_SYM = '='

INCLUDE_FILE_SYM = '|'

# This regex finds patterns like this `[name#variation?randgen/percentgen]`
# with `variation`, `randgen` and `percentgen` optional
# TODO make this reflect the state of the symbols defined before
pattern_modifiers = re.compile(r"\[(?P<casegen>&)?(?P<name>[^#\[\]\?]*)(?:#(?P<variation>[^#\[\]\?]*))?(?:\?(?P<randgen>[^#\[\]\?/]*)(?:/(?P<percentgen>[^#\[\]\?]*))?)?\]")
pattern_nb_gen_asked = re.compile(r"\]\((?P<nbgen>[0-9]+)\)")
pattern_comment = re.compile(r"(?<!\\);")


class Unit(Enum):
    word = 1  # simple word, no other info needed
    word_group = 2  # word group with modifiers
    alias = 3  # alias with modifiers
    slot = 4  # slot with modifiers
    intent = 5  # intent with modifiers and generation number

class LineType(Enum):
    empty = 1
    comment = 2
    alias_declaration = 3
    slot_declaration = 4
    intent_declaration = 5
    include_file = 6


def strip_comments(text):
    match = pattern_comment.search(text)
    if match is None:
        return text
    return text[:match.start()].rstrip()

def is_start_unit_sym(char):
    return (char == UNIT_OPEN_SYM or char == ALIAS_SYM or \
            char == SLOT_SYM or char == INTENT_SYM)
def is_unit(text):
    return (len(text) > 0 and is_start_unit_sym(text[0]))

def get_top_level_line_type(line, stripped_line):
    """
    Returns the type of a top-level line (Note: this is expected to never
    be called for something else than a top-level line).
    Raises an error if the top-level line is not valid
    """
    if stripped_line == "":
        return LineType.empty
    elif stripped_line.startswith(COMMENT_SYM):
        return LineType.comment
    elif line.startswith(ALIAS_SYM):
        return LineType.alias_declaration
    elif line.startswith(SLOT_SYM):
        return LineType.slot_declaration
    elif line.startswith(INTENT_SYM):
        return LineType.intent_declaration
    elif line.startswith(INCLUDE_FILE_SYM):
        return LineType.include_file
    else:
        SyntaxError("Invalid syntax",
            (self.in_file.name, self.line_nb, 1, line))
def get_unit_type(unit):
    if unit.startswith(UNIT_OPEN_SYM):
        return Unit.word_group
    elif unit.startswith(ALIAS_SYM):
        return Unit.alias
    elif unit.startswith(SLOT_SYM):
        return Unit.slot
    elif unit.startswith(INTENT_SYM):
        return Unit.intent
    else:
        raise RuntimeError("Internal error: tried to get the unit type of "+
            "something that was not a unit")


def split_contents(text, accept_alt_solt_val=False):
    """
    Splits `text` into a list of words and units
    (word groups, aliases, slots and intents).
    Keeps also track of units that have no space between them (this info is
    placed in the returned list).
    If `accept_alt_solt_val` is `True`, expressions after a `=` will be considered
    to be the slot value name for the splitted expression. In this case, the
    return value will be `(alt_name, list)`.
    """
    # Split string in list of words and raw units (as strings)
    words_and_units_raw = []
    current = ""
    escaped = False
    space_just_seen = False
    must_parse_alt_slot_val = False
    for c in text:
        # Manage character escapement
        if escaped:
            current += c
            escaped = False
            continue
        # Manage spaces
        if c.isspace():
            space_just_seen = True
            if current == "":
                continue
            elif not is_unit(current):
                # New word
                words_and_units_raw.append(current)
                current = ""
                continue
            else:
                current += c
                continue
        elif c == COMMENT_SYM:
            break
        elif c == ESCAPE_SYM:
            escaped = True
        # End unit
        elif c == UNIT_CLOSE_SYM:
            current += c
            words_and_units_raw.append(current)
            current = ""
        # New unit
        elif is_start_unit_sym(c):
            if space_just_seen and current == "":
                words_and_units_raw.append(' ')  # TODO do this even for words
            elif current != "" and  not is_start_unit_sym(current):
                words_and_units_raw.append(current)
                current = ""
            current += c
        elif accept_alt_solt_val and c == ALT_SLOT_VALUE_NAME_SYM:
            must_parse_alt_slot_val = True
            break
        # Any other character
        else:
            current += c

        if not c.isspace():
            space_just_seen = False

    print(words_and_units_raw)

    # Find the alternative slot value name if needed
    alt_slot_val_name = None
    if must_parse_alt_slot_val:
        alt_slot_val_name = \
            text[text.find(ALT_SLOT_VALUE_NAME_SYM):][1:].lstrip()

    # Make a list of unit from this parsing
    words_and_units = []
    for (i, string) in enumerate(words_and_units_raw):
        if string == ' ':
            continue
        elif not is_unit(string):
            words_and_units.append({
                "type": Unit.word,
                "word": string,
            })
        else:
            no_leading_space = i == 0 or (i != 0 and words_and_units_raw[i-1] != ' ')
            unit_type = get_unit_type(string)
            if unit_type == Unit.word_group:
                (name, variation, randgen, percentgen, casegen) = parse_unit(string)
                if variation is not None:
                    raise SyntaxError("Word groups cannot have a variation as found with word group '"+
                        name+"'")
                words_and_units.append({
                    "type": Unit.word_group,
                    "words": name,
                    "randgen": randgen,
                    "percentgen": percentgen,
                    "casegen": casegen,
                    "leading-space": not no_leading_space,
                })
            else:
                (name, variation, randgen, percentgen, casegen) = parse_unit(string)
                words_and_units.append({
                    "type": unit_type,
                    "name": name,
                    "variation": variation,
                    "randgen": randgen,
                    "percentgen": percentgen,
                    "casegen": casegen,
                    "leading-space": not no_leading_space,
                })

    if accept_alt_solt_val:
        return (alt_slot_val_name, words_and_units)
    return words_and_units


def parse_unit(unit):
    """
    Parses a unit (left stripped) and returns
    (unit name, variation, randgen, percentgen, casegen) with `None` values for
    those not provided in the file. NB: `casegen` is a boolean.
    For a word group, the name will be its text.
    If an anonymous randgen is used '' will be its value.
    """
    name = None
    variation = None
    randgen = None
    percentgen = None
    casegen = False
    one_found = False
    for match in pattern_modifiers.finditer(unit):
        start_index = match.start()
        if one_found:  # this error would happen only when `unit` is a whole line (i.e. a declaration)
            raise SyntaxError("Expected only one unit here: only one declaration is allowed per line",
                (self.in_file.name, self.line_nb, start_index, unit))
        else:
            one_found = True
        match = match.groupdict()

        name = match["name"]
        variation = match["variation"]
        randgen = match["randgen"]
        percentgen = match["percentgen"]
        casegen = (match["casegen"] is not None)
        if name == "":
            raise SyntaxError("Units must have a name (or a content for word groups)",
                (self.in_file.name, self.line_nb, start_index, unit))
        if variation == "":
            raise SyntaxError("Precision must be named (e.g. [text#variation])",
                (self.in_file.name, self.line_nb, start_index, unit))
        if percentgen == "":
            raise SyntaxError("Percentage for generation cannot be empty",
                (self.in_file.name, self.line_nb, start_index, unit))

    return (name, variation, randgen, percentgen, casegen)

def find_nb_gen_asked(intent):
    """
    Finds the number of generation asked for the provided intent string and
    returns it (or `None` if it wasn't provided).
    """
    nb_gen_asked = None
    one_found = False
    for match in pattern_nb_gen_asked.finditer(intent):
        start_index = match.start()
        if one_found:
            raise SyntaxError("Expected only one number of generation asked",
                (self.in_file.name, self.line_nb, start_index, unit))
        else:
            one_found = True
        match = match.groupdict()

        nb_gen_asked = match["nbgen"]
    return nb_gen_asked


def check_indentation(indentation_nb, line, stripped_line):
    """
    Given the indentation of the previous line,
    checks the indentation of the line is correct (raises a `SyntaxError`
    otherwise) and returns the number of spaces its indented with.
    If this is the first line (`indentation_nb` is `None`),
    considers the indentation correct and returns the number of spaces
    the line is indented with.
    """
    current_indentation_nb = len(line) - len(stripped_line)
    if indentation_nb is None:
        return current_indentation_nb
    else:
        if current_indentation_nb == indentation_nb:
            return current_indentation_nb
        else:
            raise SyntaxError("Incorrect indentation",
                (self.in_file.name, self.line_nb, indentation_nb, line))