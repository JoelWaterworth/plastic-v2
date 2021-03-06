import sys
import plst_parser
import type_checker
import code_generator

class LLVMWriter:
    def __init__(self, fd):
        self.fd = fd

    def write(self, string):
        return self.fd.write(string)

    def writeout_csl(self, items, function):
        if len(items) == 0:
            return
        for item in items[:-1]:
            function(item)
            self.write(", ")
        function(items[-1])

    def writeout_type_list(self, tys):
        self.writeout_csl(tys, self.writeout_type)

    def writeout_type(self, ty):
        if ty.tag == 'ptr_to':
            self.writeout_type(ty.ty)
            self.write('*')
        elif ty.tag == 'number':
            self.write('i')
            self.write(str(ty.width))
        elif ty.tag == 'array':
            self.write('[')
            self.write(str(ty.size))
            self.write(' x ')
            self.writeout_type(ty.of)
            self.write(']')
        elif ty.tag == 'named_type':
            self.write('%')
            self.write(ty.name)
        elif ty.tag == 'void':
            self.write('void')
        elif ty.tag == 'func':
            self.writeout_type(ty.return_type)
            self.write(' (')
            self.writeout_type_list(ty.arg_types)
            self.write(')')
        else:
            print(ty)
            raise NotImplementedError()

    def writeout_declare(self, decl):
        fd.write('declare ')
        self.writeout_type(decl.return_type)
        self.write(' @')
        self.write(decl.name)
        if len(decl.arg_types) == 0:
            self.write('()')
        else:
            self.write('(')
            self.writeout_type_list(decl.arg_types)
            self.write(')')
        self.write('\n')

    def writeout_struct(self, decl):
        self.write("%")
        self.write(decl.name)
        self.write(" = type { ")
        self.writeout_type_list(decl.fields)
        self.write(" }\n")

    def writeout_arg(self, arg):
        (name, ty) = arg
        self.writeout_type(ty)
        self.write(' ')
        self.write(name)

    def writeout_define(self, decl):
        self.write('define ')
        self.writeout_type(decl.return_type)
        self.write(' @')
        self.write(decl.name)
        self.write('(')
        self.writeout_csl(decl.args, self.writeout_arg)
        self.write(') {\n')
        for basic_block in decl.basic_blocks:
            self.writeout_basic_block(basic_block)
        self.write('}\n')

    def writeout_basic_block(self, basic_block):
        self.write(basic_block.label)
        self.write(':\n')
        for instruction in basic_block.instructions:
           self.writeout_instruction(instruction)

    def writeout_instruction(self, instruction):
        self.write("  ")
        if instruction.tag == 'bitcast':
            self.write(instruction.ret_name)
            self.write(" = bitcast ")
            self.writeout_type(instruction.source_type)
            self.write(" ")
            self.write(instruction.value)
            self.write(" to ")
            self.writeout_type(instruction.dest_type)
        elif instruction.tag == 'store':
            self.write("store ")
            self.writeout_type(instruction.source_type)
            self.write(" ")
            self.write(instruction.value)
            self.write(", ")
            self.writeout_type(instruction.dest_type)
            self.write(" ")
            self.write(instruction.dest)
        else:
            raise NotImplementedError()
        self.write("\n")
    def writeout_decl(self, decl):
        if decl.tag == 'declare':
            self.writeout_declare(decl)
        elif decl.tag == 'struct':
            self.writeout_struct(decl)
        elif decl.tag == 'define':
            self.writeout_define(decl)
        else:
            raise NotImplementedError()

    def writeout_decls(self, decls):
        for decl in decls:
            self.writeout_decl(decl)

with open(sys.argv[1], 'r') as fd:
    decls = plst_parser.Parser(fd.read()).parse_file()

env = \
    type_checker.Environment(
        type_checker.global_type_environment,
        type_checker.global_term_environment,
    )
type_checked_decls = env.check_top_level_decls(decls)
llvm_decls = \
    code_generator. \
    CodeGenerator(). \
    generate_top_level_decls(type_checked_decls)

with open(sys.argv[2], 'w') as fd:
    LLVMWriter(fd).writeout_decls(llvm_decls)
