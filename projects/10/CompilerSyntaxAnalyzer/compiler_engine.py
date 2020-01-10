from compiler_tokenizer import CompilerTokenizer
from compiler_token import TokenType


class CompilerEngine:

    def __init__(self, tokenizer, file_out):
        self._tokenizer = tokenizer
        self.file_out = file_out
        self.output = None

    def start(self):
        self.output = open(self.file_out, 'w')
        self._compile_class()
        self.output.close()

    def _open_tag(self, tag):
        self.output.write(f'<{tag}>\n')

    def _close_tag(self, tag):
        self.output.write(f'</{tag}>\n')

    def _write_token_tag(self, token):
        self.output.write(f'<{CompilerTokenizer.token_type_str[token.token_type]}>')
        self.output.write(token.val.
                          replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))
        self.output.write(f'</{CompilerTokenizer.token_type_str[token.token_type]}>\n')

    def _read(self, *options):
        token = self._tokenizer.advance()
        for option in options:
            if token.token_type == option or token.val == option:
                self._write_token_tag(token)
                return
        raise SyntaxError

    def _compile_class(self):
        self._open_tag('class')
        self._read('class')
        self._read(TokenType.IDENTIFIER)
        self._read('{')
        while self._tokenizer.peek_token().val in {'static', 'field'}:
            self._compile_class_var_dec()
        while self._tokenizer.peek_token().val in {'constructor', 'function', 'method'}:
            self._compile_subroutine_dec()
        self._read('}')
        self._close_tag('class')

    def _compile_class_var_dec(self):
        self._open_tag('classVarDec')
        self._read('static', 'field')
        self._compile_type()
        self._read(TokenType.IDENTIFIER)
        while self._tokenizer.peek_token().val == ',':
            self._read(',')
            self._read(TokenType.IDENTIFIER)
        self._read(';')
        self._close_tag('classVarDec')

    def _compile_type(self):
        self._read('int', 'char', 'boolean', TokenType.IDENTIFIER)

    def _compile_type_void(self):
        self._read('int', 'char', 'boolean', 'void', TokenType.IDENTIFIER)

    def _compile_subroutine_dec(self):
        self._open_tag('subroutineDec')
        self._read('constructor', 'function', 'method')
        self._compile_type_void()
        self._read(TokenType.IDENTIFIER)
        self._read('(')
        self._compile_parameter_list()
        self._read(')')
        self._compile_subroutine_body()
        self._close_tag('subroutineDec')

    def _compile_parameter_list(self):
        self._open_tag('parameterList')
        if self._tokenizer.peek_token().val != ')':
            self._compile_type()
            self._read(TokenType.IDENTIFIER)
            while self._tokenizer.peek_token().val == ',':
                self._read(',')
                self._compile_type()
                self._read(TokenType.IDENTIFIER)
        self._close_tag('parameterList')

    def _compile_subroutine_body(self):
        self._open_tag('subroutineBody')
        self._read('{')
        while self._tokenizer.peek_token().val == 'var':
            self._compile_var_dec()
        self._compile_statements()
        self._read('}')
        self._close_tag('subroutineBody')

    def _compile_var_dec(self):
        self._open_tag('varDec')
        self._read('var')
        self._compile_type()
        self._read(TokenType.IDENTIFIER)
        while self._tokenizer.peek_token().val == ',':
            self._read(',')
            self._read(TokenType.IDENTIFIER)
        self._read(';')
        self._close_tag('varDec')

    def _compile_statements(self):
        self._open_tag('statements')
        while self._tokenizer.peek_token().val in {'let', 'if', 'while', 'do', 'return'}:
            statement_type = self._tokenizer.peek_token().val
            if statement_type == 'let':
                self._compile_let_statement()
            elif statement_type == 'if':
                self._compile_if_statement()
            elif statement_type == 'while':
                self._compile_while_statement()
            elif statement_type == 'do':
                self._compile_do_statement()
            elif statement_type == 'return':
                self._compile_return_statement()
        self._close_tag('statements')

    def _compile_let_statement(self):
        self._open_tag('letStatement')
        self._read('let')
        self._read(TokenType.IDENTIFIER)
        if self._tokenizer.peek_token().val == '[':
            self._read('[')
            self._compile_expression()
            self._read(']')
        self._read('=')
        self._compile_expression()
        self._read(';')
        self._close_tag('letStatement')

    def _compile_if_statement(self):
        self._open_tag('ifStatement')
        self._read('if')
        self._read('(')
        self._compile_expression()
        self._read(')')
        self._read('{')
        self._compile_statements()
        self._read('}')
        if self._tokenizer.peek_token().val == 'else':
            self._read('else')
            self._read('{')
            self._compile_statements()
            self._read('}')
        self._close_tag('ifStatement')

    def _compile_while_statement(self):
        self._open_tag('whileStatement')
        self._read('while')
        self._read('(')
        self._compile_expression()
        self._read(')')
        self._read('{')
        self._compile_statements()
        self._read('}')
        self._close_tag('whileStatement')

    def _compile_do_statement(self):
        self._open_tag('doStatement')
        self._read('do')
        self._compile_subroutine_call()
        self._read(';')
        self._close_tag('doStatement')

    def _compile_return_statement(self):
        self._open_tag('returnStatement')
        self._read('return')
        if self._tokenizer.peek_token().val != ';':
            self._compile_expression()
        self._read(';')
        self._close_tag('returnStatement')

    def _compile_expression(self):
        self._open_tag('expression')
        self._compile_term()
        while self._tokenizer.peek_token().val in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            self._read('+', '-', '*', '/', '&', '|', '<', '>', '=')
            self._compile_term()
        self._close_tag('expression')

    def _compile_term(self):
        self._open_tag('term')
        try:
            self._read(TokenType.INTEGER, TokenType.STRING, TokenType.IDENTIFIER,
                       'true', 'false', 'null', 'this')
            if self._tokenizer.curr_token().token_type == TokenType.IDENTIFIER:
                if self._tokenizer.peek_token().val == '[':
                    self._read('[')
                    self._compile_expression()
                    self._read(']')
                elif self._tokenizer.peek_token().val in {'.', '('}:
                    self._compile_subroutine_call()
        except SyntaxError:
            self._tokenizer.retreat()
            if self._tokenizer.peek_token().val == '(':
                self._read('(')
                self._compile_expression()
                self._read(')')
            else:
                self._read('-', '~')
                self._compile_term()
        self._close_tag('term')

    def _compile_subroutine_call(self):
        if self._tokenizer.curr_token().token_type != TokenType.IDENTIFIER:
            self._read(TokenType.IDENTIFIER)
        if self._tokenizer.peek_token().val == '(':
            self._read('(')
            self._compile_expression_list()
            self._read(')')
        else:
            self._read('.')
            self._read(TokenType.IDENTIFIER)
            self._read('(')
            self._compile_expression_list()
            self._read(')')

    def _compile_expression_list(self):
        self._open_tag('expressionList')
        if self._tokenizer.peek_token().val != ')':
            self._compile_expression()
            while self._tokenizer.peek_token().val == ',':
                self._read(',')
                self._compile_expression()
        self._close_tag('expressionList')
