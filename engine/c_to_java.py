def convert(code):

    lines = code.split("\n")
    output = []

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "printf" in stripped:
            content = stripped.replace("printf(", "").replace(");", "")
            output.append(f"System.out.println({content});")

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