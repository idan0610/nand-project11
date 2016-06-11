__author__ = 'daph.kaplan'
from CompilationEngine import CompilationEngine
import os
import sys

def main(args):
    if os.path.isdir(args):

        if not args.endswith('/'):
            args = args + '/'

        for filename in os.listdir(args):
            if filename.endswith('.jack'):
                input_name = args + filename
                name_writer = filename.rsplit('.', 1)[0]
                output_name = args + name_writer + ".vm"
                compiler = CompilationEngine(input_name, output_name)

    elif os.path.isfile(args):
        if args.endswith('.jack'):
            name_writer = args.rsplit('.', 1)[0]
            input_name = args
            output_name = name_writer + ".vm"
            compiler = CompilationEngine(input_name, output_name)

    else:
        print("error: file or folders does not exist")

main(sys.argv[1])