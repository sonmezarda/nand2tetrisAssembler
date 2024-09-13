import json

class HackAssembler():
    def __init__(self, reference_file='settings/hack_language_reference.json'):
        self.referenceJson = json.load(open(reference_file, 'r'))
        self.comp_dict = self.referenceJson['comp']
        self.dest_dict = self.referenceJson['dest']
        self.jump_dict = self.referenceJson['jump']
        self.defined_symbols = self.referenceJson['predefined_symbols']

    def assemble_to_file(self, asm_file, hack_file):
        instructions = self.assemble(asm_file)
        self.write_to_file(hack_file, instructions)

    def assemble(self, file_path):
        instructions = self.read_from_file(file_path)
        instructions = [self.remove_comments(self.remove_whitespace(instruction)) for instruction in instructions]
        instructions = [instruction for instruction in instructions if instruction]
        print(instructions)
        instructions = self.attach_symbols(instructions)
        print(instructions)
        instructions = [self.convert_instruction(instruction) for instruction in instructions]
        return instructions
    
    def write_to_file(self, file_path, instructions):
        with open(file_path, 'w') as file:
            for instruction in instructions:
                file.write(instruction + '\n')

    def attach_symbols(self, instructions):
        label_count = 0
        symbol_table = self.defined_symbols
        for i, instruction in enumerate(instructions):
            if instruction.startswith('('):
                symbol_table[instruction[1:-1]] = i - label_count
                label_count += 1
        instructions = [instruction for instruction in instructions if not instruction.startswith('(')]
        for i, instruction in enumerate(instructions):
            if instruction.startswith('@') and not instruction[1:].isdigit():
                symbol = instruction[1:]
                if symbol not in symbol_table:
                    symbol_table[symbol] = len(symbol_table) + 16
                instructions[i] = '@' + str(symbol_table[symbol])
        return instructions
    
    def read_from_file(self, file_path): 
        with open(file_path, 'r') as file:
            return file.readlines()

    def remove_whitespace(self, line):
        return line.replace(' ', '')
    
    def remove_comments(self, line):
        if '//' in line:
            line = line.split('//')[0]
        return line.strip()

    def convert_instruction(self, instruction):
        if instruction.startswith('@'):
            return self.convert_A_instruction(instruction)
        else:
            return self.convert_C_instruction(instruction)

    def convert_A_instruction(self, instruction):
        instruction = instruction[1:]
        instruction = bin(int(instruction))[2:]
        instruction = instruction.zfill(16)
        return instruction
    
    def convert_C_instruction(self, instruction):
        dest = comp = jump = '000'
        if '=' in instruction:
            dest, comp = instruction.split('=')
            return '111' + self.comp_dict[comp] + self.dest_dict[dest] + jump
        if ';' in instruction:
            comp, jump = instruction.split(';')
            return '111' + self.comp_dict[comp] + dest + self.jump_dict[jump]
    

if __name__ == '__main__':
    assembler = HackAssembler("settings/hack_language_reference.json")
    #print(assembler.assemble("Prog.asm"))
    print(assembler.assemble_to_file("Prog.asm", "Prog.hack"))