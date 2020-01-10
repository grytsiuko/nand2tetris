import sys
import os

from singleton import Singleton
from compiler_tokenizer import CompilerTokenizer
from compiler_engine import CompilerEngine


class CompilerSyntaxAnalyzer(metaclass=Singleton):

    def _explore_source(self, source):

        if os.path.isfile(source):
            if source.endswith('.jack'):
                return [source]
            else:
                raise ValueError
        else:
            return [os.path.join(source, file)
                    for file in os.listdir(source) if file.endswith('.jack')]

    def analyze(self, source):
        files_in = self._explore_source(source)
        for file_in in files_in:
            tokenizer = CompilerTokenizer(file_in)
            engine = CompilerEngine(tokenizer, file_in.replace('.jack', '.xml'))
            engine.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('No arguments')
    else:
        for arg in sys.argv[1:]:
            CompilerSyntaxAnalyzer().analyze(arg)
