from engine.python_to_java import convert as py_to_java
from engine.java_to_python import convert as java_to_py
from engine.python_to_c import convert as py_to_c
from engine.c_to_python import convert as c_to_py
from engine.c_to_java import convert as c_to_java
from engine.java_to_c import convert as java_to_c
from engine.python_to_cpp import convert as py_to_cpp
from engine.cpp_to_python import convert as cpp_to_py
from engine.cpp_to_java import convert as cpp_to_java
from engine.java_to_cpp import convert as java_to_cpp
from engine.c_to_cpp import convert as c_to_cpp
from engine.cpp_to_c import convert as cpp_to_c


def convert_code(code, source_lang, target_lang):

    # 🔥 FIX (STEP 1)
    source_lang = source_lang.lower()
    target_lang = target_lang.lower()

    print("SOURCE:", source_lang)
    print("TARGET:", target_lang)

    # 🔹 EXISTING
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

    # 🔥 C++ CONVERSIONS
    elif source_lang == "python" and target_lang == "cpp":
        return py_to_cpp(code)

    elif source_lang == "cpp" and target_lang == "python":
        return cpp_to_py(code)

    elif source_lang == "cpp" and target_lang == "java":
        return cpp_to_java(code)

    elif source_lang == "java" and target_lang == "cpp":
        return java_to_cpp(code)

    elif source_lang == "c" and target_lang == "cpp":
        return c_to_cpp(code)

    elif source_lang == "cpp" and target_lang == "c":
        return cpp_to_c(code)

    else:
        return f"Conversion not supported yet ({source_lang} → {target_lang})"