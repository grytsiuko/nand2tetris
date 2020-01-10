from enum import Enum

from compiler_token import Token, TokenType


class CompilerTokenizerState(Enum):
    NORMAL = 1
    LINE_COMMENT = 2
    BLOCK_COMMENT = 3
    STRING = 4
    INTEGER = 5
    WORD = 6


class CompilerTokenizer:
    symbols = {'{', '}', '(', ')', '[', ']',
               '.', ',', ';', '+', '-', '*', '/',
               '&', '|', '<', '>', '=', '~'}
    keywords = {'class', 'constructor', 'function', 'method', 'field', 'static',
                'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                'this', 'let', 'do', 'if', 'else', 'while', 'return'}
    token_type_str = {TokenType.STRING: 'stringConstant',
                      TokenType.INTEGER: 'integerConstant',
                      TokenType.IDENTIFIER: 'identifier',
                      TokenType.KEYWORD: 'keyword',
                      TokenType.SYMBOL: 'symbol'}

    def __init__(self, file_in):
        self._file_in = file_in
        self._tokens = []
        self._state = CompilerTokenizerState.NORMAL
        self._curr_line = None
        self._curr_token_val = None
        self._curr_pos = None
        self._tokenize()
        self._curr_token_num = -1

    def curr_token(self):
        return self._tokens[self._curr_token_num]

    def peek_token(self):
        if self._curr_token_num + 1 == len(self._tokens):
            raise IndexError
        return self._tokens[self._curr_token_num + 1]

    def advance(self):
        if self._curr_token_num + 1 == len(self._tokens):
            raise SyntaxError
        self._curr_token_num += 1
        return self.curr_token()

    def retreat(self):
        if self._curr_token_num - 1 == -1:
            raise IndexError
        self._curr_token_num -= 1
        return self.curr_token()

    def _parse_line(self):
        self._curr_pos = 0
        while self._curr_pos < len(self._curr_line):
            if self._state == CompilerTokenizerState.NORMAL:
                self._parse_normal_state()
            elif self._state == CompilerTokenizerState.LINE_COMMENT:
                self._parse_line_comment_state()
            elif self._state == CompilerTokenizerState.BLOCK_COMMENT:
                self._parse_block_comment_state()
            elif self._state == CompilerTokenizerState.STRING:
                self._parse_string_state()
            elif self._state == CompilerTokenizerState.INTEGER:
                self._parse_integer_state()
            elif self._state == CompilerTokenizerState.WORD:
                self._parse_word_state()
            self._curr_pos += 1

    def _parse_normal_state(self):
        if self._curr_line[self._curr_pos] == '/' and self._curr_line[self._curr_pos + 1] == '*':
            self._state = CompilerTokenizerState.BLOCK_COMMENT
            self._curr_pos += 1
        elif self._curr_line[self._curr_pos] == '/' and self._curr_line[self._curr_pos + 1] == '/':
            self._state = CompilerTokenizerState.LINE_COMMENT
            self._curr_pos += 1
        elif self._curr_line[self._curr_pos] == '"':
            self._state = CompilerTokenizerState.STRING
            self._curr_token_val = ''
        elif self._is_num(self._curr_line[self._curr_pos]):
            self._state = CompilerTokenizerState.INTEGER
            self._curr_token_val = ''
            self._curr_pos -= 1
        elif self._is_letter(self._curr_line[self._curr_pos]):
            self._state = CompilerTokenizerState.WORD
            self._curr_token_val = ''
            self._curr_pos -= 1
        elif self._curr_line[self._curr_pos] in self.symbols:
            self._tokens.append(Token(self._curr_line[self._curr_pos], TokenType.SYMBOL))
        elif not self._is_white_space(self._curr_line[self._curr_pos]):
            raise SyntaxError

    def _parse_line_comment_state(self):
        if self._curr_pos == len(self._curr_line) - 1:
            self._state = CompilerTokenizerState.NORMAL

    def _parse_block_comment_state(self):
        if self._curr_line[self._curr_pos] == '*' and self._curr_line[self._curr_pos + 1] == '/':
            self._state = CompilerTokenizerState.NORMAL
            self._curr_pos += 1

    def _parse_string_state(self):
        if self._curr_line[self._curr_pos] == '"':
            self._state = CompilerTokenizerState.NORMAL
            self._tokens.append(Token(self._curr_token_val, TokenType.STRING))
        else:
            self._curr_token_val += self._curr_line[self._curr_pos]

    def _parse_integer_state(self):
        if self._is_num(self._curr_line[self._curr_pos]):
            self._curr_token_val += self._curr_line[self._curr_pos]
        else:
            self._state = CompilerTokenizerState.NORMAL
            self._tokens.append(Token(self._curr_token_val, TokenType.INTEGER))
            self._curr_pos -= 1

    def _parse_word_state(self):
        if self._is_identifier_char(self._curr_line[self._curr_pos]):
            self._curr_token_val += self._curr_line[self._curr_pos]
        else:
            self._state = CompilerTokenizerState.NORMAL
            if self._curr_token_val in self.keywords:
                self._tokens.append(Token(self._curr_token_val, TokenType.KEYWORD))
            else:
                self._tokens.append(Token(self._curr_token_val, TokenType.IDENTIFIER))
            self._curr_pos -= 1

    def _is_num(self, char):
        return '0' <= char <= '9'

    def _is_letter(self, char):
        return 'a' <= char <= 'z' or 'A' <= char <= 'Z'

    def _is_identifier_char(self, char):
        return self._is_num(char) or self._is_letter(char) or char == '_'

    def _is_white_space(self, char):
        return char == ' ' or char == '\t' or char == '\n'

    def _tokenize(self):
        jack_file = open(self._file_in, 'r')
        # xml_file = open(self._file_in.replace('.jack', 'T.xml'), 'w')

        for line in jack_file.readlines():
            self._curr_line = line
            self._parse_line()

        # xml_file.write('<tokens>\n')
        # for token in self._tokens:
        #     xml_file.write(f'<{self.token_type_str[token.token_type]}>')
        #     xml_file.write(token.val.
        #                    replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))
        #     xml_file.write(f'</{self.token_type_str[token.token_type]}>\n')
        # xml_file.write('</tokens>\n')

        jack_file.close()
        # xml_file.close()
