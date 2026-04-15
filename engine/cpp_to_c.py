def convert(code):

    lines = code.split("\n")
    output = ['#include<stdio.h>']

    for line in lines:
        stripped = line.strip()

        # PRINT
        if "cout" in stripped:
            content = stripped.replace("cout <<", "").replace(";", "")
            output.append(f'printf({content});')

        else:
            if stripped:
                output.append(stripped)

    return "\n".join(output)