def convert(code):

    lines = code.split("\n")
    output = ['#include<iostream>', 'using namespace std;']

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "printf" in stripped:
            content = stripped.replace("printf(", "").replace(");", "")
            output.append(f'cout << {content} << endl;')

        else:
            if stripped:
                output.append(stripped)

    return "\n".join(output)