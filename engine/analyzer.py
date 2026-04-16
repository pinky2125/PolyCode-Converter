import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_code(source_code, converted_code, source_lang, target_lang):
    """
    Analyzes the converted code to provide suggestions and a better solution using Gemini.
    If the API key is not set or an error occurs, it falls back to basic suggestions.
    """
    if not api_key:
        suggestion_text = f"Consider refactoring your code to use native {target_lang} structures. Managing your variables efficiently can improve memory utilization."
        
        if source_lang.lower() == "python" and target_lang.lower() == "java":
            suggestion_text = "Java requires strict variable typing. Ensure proper encapsulation and consider using Java Streams for loop optimization."
        elif target_lang.lower() == "cpp":
            suggestion_text = "In C++, utilize std::vectors and iterators for better memory safety over raw pointers."
        elif target_lang.lower() == "python":
            suggestion_text = "Python relies heavily on concise syntax. Try to use list comprehensions instead of raw loops where applicable."

        return {
            "suggestion": f"{suggestion_text}",
            "solution": f"{converted_code}"
        }

    prompt = f"""
    You are an expert programmer and code reviewer.
    A user has converted the following code from {source_lang} to {target_lang}.

    Source Code ({source_lang}):
    ```
    {source_code}
    ```

    Converted Code ({target_lang}):
    ```
    {converted_code}
    ```

    Please provide:
    1. A single best-practice suggestion on how to improve the {target_lang} converted code.
    2. An optimized and cleaner 'Solution' version of the {target_lang} code based on your suggestion.
    
    Format your output exactly as follows:
    [SUGGESTION_START]
    <Write your suggestion text here>
    [SUGGESTION_END]

    [SOLUTION_START]
    <Write only the raw optimized code here without any markdown formatter or explanations>
    [SOLUTION_END]
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse the output
        suggestion = "No explicit suggestion could be generated."
        solution = "No explicit solution could be generated."
        
        if "[SUGGESTION_START]" in text and "[SUGGESTION_END]" in text:
            suggestion = text.split("[SUGGESTION_START]")[1].split("[SUGGESTION_END]")[0].strip()
            
        if "[SOLUTION_START]" in text and "[SOLUTION_END]" in text:
            solution = text.split("[SOLUTION_START]")[1].split("[SOLUTION_END]")[0].strip()
            # Clean up potential markdown formatting that model might inject anyways
            if solution.startswith("```"):
                lines = solution.split("\\n")
                if len(lines) > 1:
                    solution = "\\n".join(lines[1:])
            if solution.endswith("```"):
                lines = solution.split("\\n")
                if len(lines) > 1:
                    solution = "\\n".join(lines[:-1])
            solution = solution.strip()
            
        return {
            "suggestion": suggestion,
            "solution": solution
        }

    except Exception as e:
        print(f"Error during AI analysis: {e}")
        return {
            "suggestion": "An error occurred while generating AI suggestions.",
            "solution": "Optimization failed due to an API error."
        }
