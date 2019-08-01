# -*- coding: utf-8 -*-
"""
Module `chatette.refactor_parsing`
Contains the lexer used by the parser and the definition of the tokens it uses.
"""

from enum import Enum

import chatette.refactor_parsing.utils as putils
from chatette.refactor_parsing.input_file_manager import InputFileManager
from chatette.refactor_parsing.lexing.rule_line import RuleLine


# Supported tokens
class TerminalType(Enum):
    """Enum of terminals types that will be used by the lexer."""
    # Special
    ignore = 0
    indentation = 1
    whitespace = 2
    comment = 3
    # File inclusion
    file_inclusion_marker = 4
    file_path = 5
    # Unit declaration
    alias_decl_start = 6
    alias_decl_end = 7
    slot_decl_start = 8
    slot_decl_end = 9
    intent_decl_start = 10
    intent_decl_end = 11
    unit_identifier = 12
    # Annotations
    annotation_start = 13
    annotation_end = 14
    separator = 15
    key = 16
    value = 17
    key_value_connector = 18
    separator = 19
    encloser = 20
    # Rule contents
    word = 21
    choice_start = 22
    choice_end = 23
    choice_sep = 24
    unit_ref_start = 25
    unit_ref_end = 26
    slot_val_marker = 27  # '='
    slot_val = 28
    # Modifiers
    casegen_marker = 29
    arg_marker = 30
    arg_name = 31
    arg_value = 32
    arg_start = 33  # '('
    arg_end = 34  # ')'
    randgen_marker = 35
    randgen_name = 36
    percentgen_marker = 37
    percentgen = 38


class Lexer(object):
    """
    This class is intended to transform each string it is provided
    into a "lexed" one, that is a list of dicts containing a label
    (the type of the terminal) and the token as a str.
    """
    def __init__(self):
        self._file_manager = InputFileManager.get_or_create()


    def lex(self, text):
        """
        Returns a "lexed" version of the str `text`, that is
        a list of `LexedItem`s representing each token in `text`.
        Those `LexedItem`s contain a `TerminalType` representing
        the token's terminal type and a str with the token.
        """
        rule = RuleLine(text)
        if not rule.matches():
            rule.print_error()
        else:
            return rule.get_labelled_tokens()


    # def lex(self, text):
    #     """
    #     Returns a "lexed" version of the str `text`, that is
    #     a list of `LexedItem`s representing each token in `text`.
    #     Those `LexedItem`s contain a `TerminalType` representing
    #     the token's terminal type and a str with the token.
    #     """
    #     if len(text.strip()) == 0:
    #         return []
    #     lexed_tokens = []
    #     current_index = 0

    #     (index, results) = self._apply_rule_comment_line(text, current_index)
    #     if index == current_index:
    #         (index, results) = self._apply_rule_include_file(text, current_index)
    #         if index == current_index:
    #             (index, results) = self._apply_rule_unit_decl(text, current_index)
    #             if index == current_index:
    #                 (index, results) = \
    #                     self._apply_rule_rule_line(text, current_index)
    #                 if index == current_index:
    #                     self._file_manager.syntax_error(
    #                         "Couldn't parse the line: it is neither " + \
    #                         "an empty line, a file inclusion, " + \
    #                         "a unit declaration or " + \
    #                         "an indented rule.", current_index
    #                     )

    #     lexed_tokens.extend(results)

    #     current_index = index
    #     if current_index < len(text):
    #         self._file_manager.syntax_error(
    #             "Expected end of line. " + \
    #             "Couldn't parse the line starting from here."
    #         )

    #     return lexed_tokens
    

    # def _check_not_empty(self, text, start_index):
    #     """
    #     Checks that the index `start_index` doesn't point to the end of the
    #     text. Raises a `SyntaxError` if it does.
    #     """
    #     if start_index >= len(text):
    #         self._file_manager.syntax_error(
    #             "Did not expect end of line here.",
    #             start_index
    #         )

    # ########### Rules ############
    # def _apply_rule_comment_line(self, text, start_index):
    #     if start_index > 0:
    #         raise ValueError(
    #             "Tried to apply a 'line level' rule with an index > 0."
    #         )

    #     (index, lexed_comment) = self._get_comment(text, start_index)
    #     if index > start_index:
    #         return (index, [lexed_comment])
    #     return (start_index, None)

    # def _apply_rule_include_file(self, text, start_index):
    #     if start_index > 0:
    #         raise ValueError(
    #             "Tried to apply a 'line level' rule with an index > 0."
    #         )

    #     self._check_not_empty(text, start_index)

    #     index = start_index
    #     lexed_tokens = []
    #     if text[index] == '|':
    #         index += 1
    #         lexed_tokens.append(
    #             LexedItem(TerminalType.file_inclusion_marker, '|')
    #         )
    #     else:
    #         return (start_index, None)
        
    #     (index, lexed_file_path) = self._get_file_path(text, index)
    #     lexed_tokens.append(lexed_file_path)

    #     if index == len(text):
    #         return (index, lexed_tokens)
    #     (index, lexed_comment) = self._get_comment(text, index)
    #     if index == len(text):
    #         lexed_tokens.append(lexed_comment)
    #         return (index, lexed_tokens)
    #     self._file_manager.syntax_error(
    #         "Didn't expect anything (except a comment) after file path " + \
    #         "when including a file.", index
    #     )
    
    # def _apply_rule_unit_decl_line(self, text, start_index):
    #     if start_index > 0:
    #         raise ValueError(
    #             "Tried to apply a 'line level' rule with an index > 0."
    #         )
            
    #     self._check_not_empty(text, start_index)

    #     current_index = start_index
    #     lexed_tokens = []

    #     (index, lexed_unit_decl) = \
    #                 self._apply_rule_unit_decl(text, current_index)
    #     if index == current_index:
    #         return (current_index, None)
    #     current_index = index
    #     lexed_tokens.extend(lexed_unit_decl)

    #     (index, lexed_annotation) = \
    #         self._apply_rule_annotation(text, current_index)
    #     current_index = index
    #     lexed_tokens.extend(lexed_annotation)

    #     (index, lexed_comment) = self._get_comment(text, current_index)
    #     if index > current_index:
    #         lexed_tokens.append(lexed_comment)
        
    
    # ####### Terminal rules ########
    # def _get_comment(self, text, start_index):
    #     length = len(text)

    #     index = start_index
    #     while index < length and text[index].isspace():
    #         index += 1
    #     if text.startswith('//', index):
    #         return (
    #             length,
    #             LexedItem(TerminalType.comment, text[start_index:])
    #         )
    #     if index > start_index:
    #         return (index, LexedItem(TerminalType.comment, ' '))
    #     return (start_index, None)

    # def _get_file_path(self, text, start_index):
    #     self._check_not_empty(text, start_index)

    #     comment_index = putils.find_unescaped(text, '//', start_index)
    #     if comment_index is None:  # no comment
    #         file_path = text[start_index:].rstrip()
    #     else:
    #         file_path = text[start_index:comment_index].rstrip()
        
    #     if len(file_path) == 0:
    #         self._file_manager.syntax_error(
    #             "Invalid file path: a file path cannot be 0 characters long.",
    #             start_index
    #         )
    #     return (
    #         start_index + len(file_path),
    #         LexedItem(TerminalType.file_path, file_path)
    #     )
