import sys
import re
import os

from singleton import Singleton
from vm_translator_writer import VMTranslatorWriter


class VMTranslator(metaclass=Singleton):

    def _translate_command(self, line, writer):
        words = line.split()
        command = words[0]
        args = words[1:]

        if command == 'push':
            writer.translate_push(args)
        elif command == 'pop':
            writer.translate_pop(args)
        elif command == 'goto':
            writer.translate_goto(args)
        elif command == 'if-goto':
            writer.translate_if_goto(args)
        elif command == 'label':
            writer.translate_label(args)
        elif command == 'call':
            writer.translate_call(args)
        elif command == 'function':
            writer.translate_function(args)
        elif command == 'return':
            writer.translate_return()
        elif command == 'add':
            writer.translate_arithmetic_binary('D+M')
        elif command == 'sub':
            writer.translate_arithmetic_binary('M-D')
        elif command == 'and':
            writer.translate_arithmetic_binary('D&M')
        elif command == 'or':
            writer.translate_arithmetic_binary('D|M')
        elif command == 'neg':
            writer.translate_arithmetic_unary('-M')
        elif command == 'not':
            writer.translate_arithmetic_unary('!M')
        elif command == 'eq':
            writer.translate_cmp('JEQ')
        elif command == 'lt':
            writer.translate_cmp('JLT')
        elif command == 'gt':
            writer.translate_cmp('JGT')

    def _explore_source(self, source):
        abs_source = os.path.abspath(source)
        source_name = os.path.split(abs_source)[-1]

        if os.path.isfile(source):
            if source.endswith('.vm'):
                files_in = [source]
                file_out = source.replace('.vm', '.asm')
            else:
                raise ValueError
        else:
            files_in = [os.path.join(source, file)
                        for file in os.listdir(source) if file.endswith('.vm')]
            file_out = os.path.join(source, source_name + '.asm')

        return files_in, file_out

    def translate(self, source):
        files_in, file_out = self._explore_source(source)

        output = open(file_out, 'w')
        writer = VMTranslatorWriter(output)

        if len(files_in) > 1:
            output.write('// Bootstrap\n')
            writer.bootstrap()

        for file_in in files_in:
            vm_file = open(file_in, 'r')
            for line in vm_file.readlines():
                # delete comment
                comment = re.search('//', line)
                if comment is not None:
                    line = line[:comment.start()]

                # check if empty
                line = line.strip()
                if line == '':
                    continue

                output.write('// ' + line + '\n')
                self._translate_command(line, writer)
            vm_file.close()

        output.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('No arguments')
    else:
        for arg in sys.argv[1:]:
            VMTranslator().translate(arg)
