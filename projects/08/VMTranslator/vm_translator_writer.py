class VMTranslatorWriter:

    def __init__(self, file):
        self._file = file
        self._segment_pointer = {'local': 1, 'argument': 2, 'this': 3, 'that': 4}
        self._stack_beginning = 256
        self._temp_beginning = 5
        self._tmp_reg = 13
        self._end_frame_reg = 14
        self._return_address_reg = 15

        self._static_name = None
        self._function_name = ''
        self._function_calls = 0
        self._cmp_num = 0

    def _write(self, s):
        self._file.write(s)

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
        self._a_command(f'{self._static_name}.{number}')
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_temp(self, number):
        self._a_command(self._temp_beginning + int(number))
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_pointer(self, number):
        if number == '0':
            self._a_command(self._segment_pointer['this'])
        else:
            self._a_command(self._segment_pointer['that'])
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_push_segment(self, segment, number):
        self._a_command(self._segment_pointer[segment])
        self._c_command('D', 'M')
        self._a_command(number)
        self._c_command('A', 'D+A')
        self._c_command('D', 'M')
        self._stack_push()

    def _translate_pop_static(self, number):
        self._stack_pop()
        self._a_command(f'{self._static_name}.{number}')
        self._c_command('M', 'D')

    def _translate_pop_temp(self, number):
        self._stack_pop()
        self._a_command(self._temp_beginning + int(number))
        self._c_command('M', 'D')

    def _translate_pop_pointer(self, number):
        self._stack_pop()
        if number == '0':
            self._a_command(self._segment_pointer['this'])
        else:
            self._a_command(self._segment_pointer['that'])
        self._c_command('M', 'D')

    def _translate_pop_segment(self, segment, number):
        self._a_command(self._segment_pointer[segment])
        self._c_command('D', 'M')
        self._a_command(number)
        self._c_command('D', 'D+A')
        self._a_command(self._tmp_reg)
        self._c_command('M', 'D')
        self._stack_pop()
        self._a_command(self._tmp_reg)
        self._c_command('A', 'M')
        self._c_command('M', 'D')

    def translate_arithmetic_unary(self, comp):
        self._stack_top()
        self._c_command('M', comp)

    def translate_arithmetic_binary(self, comp):
        self._stack_pop_then_top()
        self._c_command('M', comp)

    def translate_cmp(self, condition):
        self._cmp_num += 1
        self._stack_pop_then_top()
        self._c_command('D', 'M-D')
        self._goto_label(None, 'D', condition, f'CMP.{self._cmp_num}.TRUE')
        self._stack_top()
        self._c_command('M', '0')
        self._goto_label(None, '0', 'JMP', f'CMP.{self._cmp_num}.END')
        self._init_label(f'CMP.{self._cmp_num}.TRUE')
        self._stack_top()
        self._c_command('M', '-1')
        self._init_label(f'CMP.{self._cmp_num}.END')

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

    def translate_goto(self, args):
        self._goto_label(None, '0', 'JMP', self._function_name + '$' + args[0])

    def translate_if_goto(self, args):
        self._stack_pop()
        self._goto_label(None, 'D', 'JNE', self._function_name + '$' + args[0])

    def translate_label(self, args):
        self._init_label(self._function_name + '$' + args[0])

    def translate_call(self, args):
        self._function_calls += 1

        # push return address
        self._a_command(self._function_name + '$ret.' + str(self._function_calls))
        self._c_command('D', 'A')
        self._stack_push()

        # push states
        for i in range(1, 5):
            self._a_command(i)
            self._c_command('D', 'M')
            self._stack_push()

        # set ARG
        self._a_command(5)
        self._c_command('D', 'A')
        self._a_command(args[1])
        self._c_command('D', 'D+A')
        self._a_command('SP')
        self._c_command('D', 'M-D')
        self._a_command(self._segment_pointer['argument'])
        self._c_command('M', 'D')

        # set LCL
        self._a_command('SP')
        self._c_command('D', 'M')
        self._a_command(self._segment_pointer['local'])
        self._c_command('M', 'D')

        # goto function
        self._goto_label(None, '0', 'JMP', args[0])

        # return label
        self._init_label(self._function_name + '$ret.' + str(self._function_calls))

    def translate_function(self, args):
        self._init_label(args[0])
        self._static_name = args[0].split('.')[0]
        self._function_name = args[0]
        self._function_calls = 0
        self._a_command(0)
        self._c_command('D', 'A')
        for i in range(int(args[1])):
            self._stack_push()

    def translate_return(self):
        # copy LCL
        self._a_command(self._segment_pointer['local'])
        self._c_command('D', 'M')
        self._a_command(self._end_frame_reg)
        self._c_command('M', 'D')

        # copy return address
        self._a_command(5)
        self._c_command('D', 'D-A')
        self._c_command('A', 'D')
        self._c_command('D', 'M')
        self._a_command(self._return_address_reg)
        self._c_command('M', 'D')

        # pop return value
        self._stack_pop()
        self._a_command(self._segment_pointer['argument'])
        self._c_command('A', 'M')
        self._c_command('M', 'D')

        # restore SP
        self._c_command('D', 'A')
        self._a_command('SP')
        self._c_command('M', 'D+1')

        # restore states
        for i in range(4, 0, -1):
            self._a_command(self._end_frame_reg)
            self._c_command('M', 'M-1')
            self._c_command('A', 'M')
            self._c_command('D', 'M')
            self._a_command(i)
            self._c_command('M', 'D')

        # goto prev function
        self._a_command(self._return_address_reg)
        self._c_command('A', 'M')
        self._c_command(None, '0', 'JMP')

    def bootstrap(self):
        self._a_command(self._stack_beginning)
        self._c_command('D', 'A')
        self._a_command('SP')
        self._c_command('M', 'D')
        self.translate_call(['Sys.init', '0'])
