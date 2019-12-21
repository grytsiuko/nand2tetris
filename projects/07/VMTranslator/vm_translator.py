import sys
import re

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

    def translate_file(self, file_in_name):
        dot_pos = re.search(r'\.', file_in_name).start()
        file_out_name = file_in_name[:dot_pos] + '.asm'
        static_name = file_out_name[:dot_pos].split('/')[-1].split('\\')[-1]

        file_in = open(file_in_name)
        file_out = open(file_out_name, 'w')
        writer = VMTranslatorWriter(file_out, static_name)

        for line in file_in.readlines():
            # delete comment
            comment = re.search('//', line)
            if comment is not None:
                line = line[:comment.start()]

            # check if empty
            line = line.strip()
            if line == '':
                continue

            file_out.write('// ' + line + '\n')
            self._translate_command(line, writer)

        file_in.close()
        file_out.close()


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        VMTranslator().translate_file(arg)
