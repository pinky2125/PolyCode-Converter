def convert(code):

    lines = code.split("\n")
    output = []

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "System.out.println" in stripped:
            content = stripped.replace("System.out.println(", "").replace(");", "")
            output.append(f'printf("{content}\\n");')

        # VARIABLE
        elif "int " in stripped:
            output.append(stripped)

        # IF
        elif stripped.startswith("if"):
            output.append(stripped)

        # ELSE
        elif stripped.startswith("else"):
            output.append("else {")

        # FOR LOOP
        elif "for" in stripped:
            output.append(stripped)

        else:
            if stripped:
                output.append(stripped)

    return "\n".join(output)