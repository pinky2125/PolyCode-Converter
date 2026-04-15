def convert(code):

    lines = code.split("\n")
    output = ['#include<iostream>', 'using namespace std;', 'int main(){']

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "System.out.println" in stripped:
            content = stripped.replace("System.out.println(", "").replace(");", "")
            output.append(f'cout << {content} << endl;')

        # VARIABLE
        elif "int " in stripped:
            output.append(stripped)

        else:
            if stripped and stripped not in ["{", "}"]:
                output.append(stripped)

    output.append("return 0;")
    output.append("}")

    return "\n".join(output)