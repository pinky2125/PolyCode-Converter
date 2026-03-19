def convert(code):

    lines = code.split("\n")
    output = []

    indent_stack = []

    for line in lines:
        stripped = line.strip()

        # PRINT
        if stripped.startswith("print"):
            new_line = stripped.replace("print(", "System.out.println(")
            output.append(new_line + ";")

        # VARIABLE (basic int)
        elif "=" in stripped and "==" not in stripped:
            parts = stripped.split("=")
            var = parts[0].strip()
            val = parts[1].strip()

            if val.isdigit():
                output.append(f"int {var} = {val};")
            else:
                output.append(f"{var} = {val};")

        # IF CONDITION
        elif stripped.startswith("if"):
            condition = stripped[3:-1]
            output.append(f"if ({condition}) "+"{")
            indent_stack.append("}")

        # FOR LOOP (range)
        elif "range" in stripped:
            var = stripped.split("for")[1].split("in")[0].strip()
            num = stripped.split("range(")[1].replace("):","")
            output.append(f"for(int {var}=0; {var}<{num}; {var}++) "+"{")
            indent_stack.append("}")

        # ELSE
        elif stripped.startswith("else"):
            output.append("else {")
            indent_stack.append("}")

        # NORMAL LINE
        else:
            output.append(stripped + ";")

    # CLOSE BRACES
    while indent_stack:
        output.append(indent_stack.pop())

    return "\n".join(output)