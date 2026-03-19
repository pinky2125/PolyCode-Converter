def convert(code):

    lines = code.split("\n")
    output = []

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "System.out.println" in stripped:
            content = stripped.replace("System.out.println(", "").replace(");", "")
            output.append(f"print({content})")

        # VARIABLE
        elif "int " in stripped:
            parts = stripped.replace("int ", "").replace(";", "").split("=")
            var = parts[0].strip()
            val = parts[1].strip()
            output.append(f"{var} = {val}")

        # IF
        elif stripped.startswith("if"):
            condition = stripped.replace("if", "").replace("(", "").replace(")", "").replace("{","").strip()
            output.append(f"if {condition}:")

        # ELSE
        elif stripped.startswith("else"):
            output.append("else:")

        # FOR LOOP
        elif "for" in stripped and "int" in stripped:
            # simple for(int i=0; i<5; i++)
            var = stripped.split("int")[1].split("=")[0].strip()
            num = stripped.split("<")[1].split(";")[0].strip()
            output.append(f"for {var} in range({num}):")

        else:
            if stripped and stripped != "}":
                output.append(stripped.replace(";", ""))

    return "\n".join(output)