# TimeWarp Compiler Documentation

## Overview

The TimeWarp Compiler is a command-line tool that compiles TimeWarp programs (PILOT, BASIC, Logo) into native Linux executables. This allows you to distribute your programs as standalone binaries without requiring the TimeWarp IDE to be installed.

## Installation

The compiler is included with TimeWarp IDE:

```bash
pip install timewarp-ide
```

## Usage

### Basic Compilation

```bash
# Compile a BASIC program
timewarp-compiler program.bas

# Compile with custom output name
timewarp-compiler program.bas -o myprogram

# Compile a Logo program
timewarp-compiler drawing.logo -o logo_app

# Compile a PILOT program
timewarp-compiler lesson.pilot -o quiz
```

### Command Line Options

```
usage: timewarp-compiler [-h] [-o OUTPUT] [--list-languages] [--version] input_file

TimeWarp Compiler - Compile educational programs to native executables

positional arguments:
  input_file           Source file to compile (.bas, .logo, .pilot)

options:
  -h, --help           show this help message and exit
  -o OUTPUT, --output OUTPUT
                       Output executable name (default: same as input file)
  --list-languages     List supported languages and exit
  --version            show program's version number and exit
```

### Supported Languages

#### BASIC (.bas)
Classic BASIC with line numbers and procedural programming.

**Features:**
- Variables and arrays
- FOR/NEXT loops
- IF/THEN/ELSE conditionals
- PRINT and INPUT statements
- Mathematical functions (SIN, COS, etc.)
- String operations

#### Logo (.logo)
Turtle graphics programming language.

**Features:**
- Turtle movement (FORWARD, BACK, LEFT, RIGHT)
- Pen control (PENUP, PENDOWN)
- Procedures and recursion
- Variables and arithmetic
- Graphics output to PPM files

#### PILOT (.pilot)
Educational programming language.

**Features:**
- Text output (T:)
- Input acceptance (A:)
- Conditional jumping (J:, Y:, N:)
- Variable computation (C:)
- Pattern matching (M:)
- Educational constructs

## Compilation Process

1. **Parsing**: Source code is parsed into an abstract syntax tree
2. **Code Generation**: C code is generated from the AST
3. **Native Compilation**: GCC compiles the C code into a binary executable

## Output

Compiled programs are native Linux executables that can run on any compatible system:

```bash
# Run the compiled program
./myprogram

# Check file type
file myprogram
# Output: myprogram: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=..., for GNU/Linux 3.2.0, not stripped
```

## Examples

### BASIC Calculator

Create `calculator.bas`:
```
10 PRINT "BASIC Calculator"
20 PRINT "Enter two numbers to add:"
30 INPUT "First number: ", A
40 INPUT "Second number: ", B
50 PRINT "Sum: "; A + B
60 END
```

Compile and run:
```bash
timewarp-compiler calculator.bas
./calculator
```

### Logo Square Drawing

Create `square.logo`:
```
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END

SQUARE 100
```

Compile and run:
```bash
timewarp-compiler square.logo
./square
```

### PILOT Quiz

Create `quiz.pilot`:
```
T:Mathematics Quiz
A:What is 2 + 2?
J:(#INPUT = 4)*CORRECT
T:Sorry, wrong answer.
J:*END

*CORRECT
T:Correct! Well done.

*END
T:Quiz complete.
E:
```

Compile and run:
```bash
timewarp-compiler quiz.pilot
echo "4" | ./quiz
```

## Technical Details

### Generated Code Structure

The compiler generates C code with the following components:

1. **Runtime Library**: Variable management, string operations, math functions
2. **Program Logic**: Switch-based execution engine
3. **Graphics Support**: Turtle graphics simulation (for Logo)
4. **I/O Handling**: Input/output operations

### Dependencies

Compiled programs require:
- Linux operating system
- Standard C library (glibc)
- No additional dependencies

### Performance

- **Compilation Speed**: Typically < 1 second for small programs
- **Executable Size**: 50-200KB depending on program complexity
- **Runtime Performance**: Native machine code execution

## Troubleshooting

### Compilation Errors

**"Unsupported file extension"**
- Ensure your file has the correct extension (.bas, .logo, .pilot)

**"Syntax error in source"**
- Check your program syntax against the language reference
- Use the TimeWarp IDE for syntax checking

**"GCC not found"**
- Install GCC: `sudo apt install gcc` (Ubuntu/Debian)
- Or: `sudo dnf install gcc` (Fedora/RHEL)

### Runtime Issues

**"Permission denied"**
- Make the executable runnable: `chmod +x program`

**"No such file or directory"**
- Ensure you're in the correct directory
- Check the executable name

**Graphics not displaying**
- Logo programs generate PPM image files
- Use an image viewer to see the graphics

## Advanced Usage

### Batch Compilation

```bash
# Compile multiple files
for file in *.bas; do
    timewarp-compiler "$file"
done
```

### Integration with Build Systems

```makefile
# Makefile example
.PHONY: all clean

PROGRAMS = calculator quiz drawing

all: $(PROGRAMS)

%: %.bas
    timewarp-compiler $< -o $@

%: %.pilot
    timewarp-compiler $< -o $@

%: %.logo
    timewarp-compiler $< -o $@

clean:
    rm -f $(PROGRAMS)
```

### Distribution

Compiled executables can be distributed as standalone binaries:

```bash
# Create distribution package
mkdir myprogram-v1.0
cp myprogram myprogram-v1.0/
cp README.md myprogram-v1.0/
tar czf myprogram-v1.0.tar.gz myprogram-v1.0/
```

## API Reference

### CompilerResult Class

```python
class CompilerResult:
    success: bool          # True if compilation succeeded
    executable_path: str   # Path to generated executable
    error_message: str     # Error message if compilation failed
    c_code: str           # Generated C code (for debugging)
```

### Language Compilers

Each language has a corresponding compiler class:

- `BasicCompiler()` - For BASIC programs
- `LogoCompiler()` - For Logo programs
- `PilotCompiler()` - For PILOT programs

All inherit from `BaseCompiler` and implement:
- `parse_source(source: str) -> List[Dict]` - Parse source code
- `create_code_generator() -> CodeGenerator` - Create code generator

## Contributing

To add support for new languages:

1. Create a new compiler class inheriting from `BaseCompiler`
2. Implement language-specific parsing and code generation
3. Add the language to the compiler CLI
4. Update documentation and tests

## See Also

- [TimeWarp IDE User Guide](user_guide.md)
- [Language Reference](languages/)
- [API Documentation](api/)
- [GitHub Repository](https://github.com/James-HoneyBadger/Time_Warp)