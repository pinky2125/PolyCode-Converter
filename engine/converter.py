from engine.python_to_java import convert as py_to_java
from engine.java_to_python import convert as java_to_py
from engine.python_to_c import convert as py_to_c
from engine.c_to_python import convert as c_to_py
from engine.c_to_java import convert as c_to_java
from engine.java_to_c import convert as java_to_c


def convert_code(code, source_lang, target_lang):

    if source_lang == "python" and target_lang == "java":
        return py_to_java(code)

    elif source_lang == "java" and target_lang == "python":
        return java_to_py(code)

    elif source_lang == "python" and target_lang == "c":
        return py_to_c(code)

    elif source_lang == "c" and target_lang == "python":
        return c_to_py(code)

    elif source_lang == "c" and target_lang == "java":
        return c_to_java(code)

    elif source_lang == "java" and target_lang == "c":
        return java_to_c(code)

    else:
        return "Conversion not supported yet."