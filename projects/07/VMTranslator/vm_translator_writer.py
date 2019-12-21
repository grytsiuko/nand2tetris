class VMTranslatorWriter:

    def __init__(self, file, file_name):
        self.cmp_num = 0
        self.file = file
        self.file_name = file_name
        self.segment_pointer = {'local': 1, 'argument': 2, 'this': 3, 'that': 4}
        self.tmp_reg = 15

    def _write(self, s):
        self.file.write(s)

    def _a_command(self, address):
        self._write('@' + str(address) + '\n')

    def _c_command(self, dest, comp, jmp=None):
        if dest is not None:
            self._write(dest + '=')
        self._write(comp)
        if jmp is not None:
            self._write(';' + jmp)
        self._write('\n')

    def _init_label(self, label):
        self._write(f'({label})\n')

    def _goto_label(self, dest, comp, jmp, label):
        self._a_command(label)
        self._c_command(dest, comp, jmp)

    def _stack_top(self):
        self._a_command('SP')
        self._c_command('A', 'M')
        self._c_command('A', 'A-1')

    def _stack_push(self):
        self._a_command('SP')
        self._c_command('A', 'M')
        self._c_command('M', 'D')
        self._a_command('SP')
        self._c_command('M', 'M+1')

    def _stack_pop(self):
        self._a_command('SP')
        self._c_command('M', 'M-1')
        self._c_command('A', 'M')
        self._c_command('D', 'M')

    def _stack_pop_then_top(self):
        self._stack_pop()
        self._c_command('A', 'A-1')

    def _translate_push_constant(self, number):
        self._a_command(number)
        self._c_command('D', 'A')
        self._stack_push()

    def _translate_push_static(self, number):
        self._a_command(f'{self.file_name}.{number}')
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_temp(self, number):
        self._a_command(5 + int(number))
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_pointer(self, number):
        if number == '0':
            self._a_command(self.segment_pointer['this'])
        else:
            self._a_command(self.segment_pointer['that'])
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_segment(self, segment, number):
        self._a_command(self.segment_pointer[segment])
        self._c_command('D', 'M')
        self._a_command(number)
        self._c_command('A', 'D+A')
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_pop_static(self, number):
        self._stack_pop()
        self._a_command(f'{self.file_name}.{number}')
        self._c_command('M', 'D')

    def _translate_pop_temp(self, number):
        self._stack_pop()
        self._a_command(5 + int(number))
        self._c_command('M', 'D')

    def _translate_pop_pointer(self, number):
        self._stack_pop()
        if number == '0':
            self._a_command(self.segment_pointer['this'])
        else:
            self._a_command(self.segment_pointer['that'])
        self._c_command('M', 'D')

    def _translate_pop_segment(self, segment, number):
        self._a_command(self.segment_pointer[segment])
        self._c_command('D', 'M')
        self._a_command(number)
        self._c_command('D', 'D+A')
        self._a_command(self.tmp_reg)
        self._c_command('M', 'D')
        self._stack_pop()
        self._a_command(self.tmp_reg)
        self._c_command('A', 'M')
        self._c_command('M', 'D')

    def translate_arithmetic_unary(self, comp):
        self._stack_top()
        self._c_command('M', comp)

    def translate_arithmetic_binary(self, comp):
        self._stack_pop_then_top()
        self._c_command('M', comp)

    def translate_cmp(self, condition):
        self.cmp_num += 1
        self._stack_pop_then_top()
        self._c_command('D', 'M-D')
        self._goto_label(None, 'D', condition, f'CMP_{self.cmp_num}_TRUE')
        self._stack_top()
        self._c_command('M', '0')
        self._goto_label(None, '0', 'JMP', f'CMP_{self.cmp_num}_END')
        self._init_label(f'CMP_{self.cmp_num}_TRUE')
        self._stack_top()
        self._c_command('M', '-1')
        self._init_label(f'CMP_{self.cmp_num}_END')

    def translate_push(self, args):
        if args[0] == 'constant':
            self._translate_push_constant(args[1])
        elif args[0] == 'static':
            self._translate_push_static(args[1])
        elif args[0] == 'temp':
            self._translate_push_temp(args[1])
        elif args[0] == 'pointer':
            self._translate_push_pointer(args[1])
        else:
            self._translate_push_segment(args[0], args[1])

    def translate_pop(self, args):
        if args[0] == 'static':
            self._translate_pop_static(args[1])
        elif args[0] == 'temp':
            self._translate_pop_temp(args[1])
        elif args[0] == 'pointer':
            self._translate_pop_pointer(args[1])
        else:
            self._translate_pop_segment(args[0], args[1])
