import sys
import re

from singleton import Singleton


class Assembler(metaclass=Singleton):

    def __init__(self):
        self.COMMAND_LEN = 16
        self.NEXT_VAR_ADDRESS = 16
        self.names_map = {
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576,
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4
        }

        self.comp_map = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            'M': '1110000',
            '!D': '0001101',
            '!A': '0110001',
            '!M': '1110001',
            '-D': '0001111',
            '-A': '0110011',
            '-M': '1110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'M+1': '1110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'M-1': '1110010',
            'D+A': '0000010',
            'D+M': '1000010',
            'D-A': '0010011',
            'D-M': '1010011',
            'A-D': '0000111',
            'M-D': '1000111',
            'D&A': '0000000',
            'D&M': '1000000',
            'D|A': '0010101',
            'D|M': '1010101'
        }

        self.dest_map = {
            '': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }

        self.jump_map = {
            '': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }

    def delete_comments_and_labels(self, lines):
        lines_out = []

        for line in lines:

            # delete comment
            comment = re.search('//', line)
            if comment is not None:
                line = line[:comment.start()]

            # check if empty
            line = line.strip()
            if line == '':
                continue

            # check if label
            if line[0] == '(' and line[-1] == ')':
                line = line[1:-1]
                line = line.strip()
                line_num = len(lines_out)
                self.names_map[line] = line_num
                continue

            lines_out.append(line)

        return lines_out

    def delete_variable(self, line):
        if line[0] != '@':
            return line

        var = line[1:]
        if line[1:].isdecimal():
            return line

        if var not in self.names_map:
            self.names_map[var] = self.NEXT_VAR_ADDRESS
            self.NEXT_VAR_ADDRESS += 1

        return '@' + str(self.names_map[var])

    def translate_lines(self, lines):
        lines_out = []

        for line in lines:

            line = self.delete_variable(line)

            if line[0] == '@':
                # A-instruction

                num = int(line[1:])
                bin_num = bin(num)[2:]
                zeros = '0' * (self.COMMAND_LEN - len(bin_num))
                line = zeros + bin_num

            else:
                # C-instruction

                dest_str = ''
                comp_str = line
                jump_str = ''

                jumping = re.search(';', line)
                if jumping is not None:
                    jump_str = line[jumping.end():]
                    comp_str = comp_str[:jumping.start()]

                assignment = re.search('=', line)
                if assignment is not None:
                    dest_str = line[:assignment.start()]
                    comp_str = comp_str[assignment.end():]

                line = '111'
                line += self.comp_map[comp_str]
                line += self.dest_map[dest_str]
                line += self.jump_map[jump_str]

            lines_out.append(line)

        return lines_out

    def translate_file(self, file_in_name):
        dot_pos = re.search(r'\.', file_in_name).start()
        file_out_name = file_in_name[:dot_pos] + '.hack'

        file_in = open(file_in_name)
        file_out = open(file_out_name, 'w')

        lines = file_in.readlines()
        lines = self.delete_comments_and_labels(lines)
        lines = self.translate_lines(lines)

        for line in lines:
            file_out.write(line + '\n')

        file_in.close()
        file_out.close()


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        Assembler().translate_file(arg)
