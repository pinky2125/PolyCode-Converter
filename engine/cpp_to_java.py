def convert(code):

    lines = code.split("\n")
    output = ['public class Main {', 'public static void main(String[] args) {']

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "cout" in stripped:
            content = stripped.replace("cout <<", "").replace(";", "")
            content = content.replace("<<", " + ")
            output.append(f'System.out.println({content});')

        # VARIABLE
        elif "int " in stripped:
            output.append(stripped)

        # IF
        elif stripped.startswith("if"):
            output.append(stripped)

        # ELSE
        elif stripped.startswith("else"):
            output.append(stripped)

        else:
            if stripped and stripped != "}":
                output.append(stripped)

    output.append("}")
    output.append("}")

    return "\n".join(output)