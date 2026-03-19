def convert(code):

    lines = code.split("\n")
    output = []

    for line in lines:
        stripped = line.strip()

        # PRINT
        if stripped.startswith("print"):
            content = stripped.replace("print(", "").replace(")", "")
            output.append(f'printf("{content}\\n");')

        # VARIABLE
        elif "=" in stripped and "==" not in stripped:
            var, val = stripped.split("=")
            output.append(f"int {var.strip()} = {val.strip()};")

        # IF
        elif stripped.startswith("if"):
            condition = stripped[3:-1]
            output.append(f"if ({condition}) "+"{")

        # FOR LOOP
        elif "range" in stripped:
            var = stripped.split("for")[1].split("in")[0].strip()
            num = stripped.split("range(")[1].replace("):","")
            output.append(f"for(int {var}=0; {var}<{num}; {var}++) "+"{")

        else:
            output.append(stripped + ";")

    output.append("}")

    return "\n".join(output)