from engine.analyzer import analyze_code


def test_analyze_code_returns_suggestion_and_solution():
    source_code = "def greet():\n    print('Hello World')\n"
    converted_code = "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World\");\n    }\n}\n"
    result = analyze_code(source_code, converted_code, "python", "java")
    assert isinstance(result, dict)
    assert "suggestion" in result
    assert "solution" in result
    assert result["solution"] != ""
