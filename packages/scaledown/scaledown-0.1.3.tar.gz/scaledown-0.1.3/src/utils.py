import re


def get_absolute_path(path_relative_to_project_root):
    import os
    current_directory = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    final_directory = os.path.join(
        current_directory,
        rf'../{path_relative_to_project_root}'
    )
    return final_directory

def extract_final_answer_section(response: str) -> str:
    """
    Extract the final answer section from the response.
    
    Args:
        response: The full LLM response text
        
    Returns:
        The final answer section as a string (empty if not found)
    """
    
    # Look for the delimited final answer section
    final_answer_pattern = r'=== FINAL ANSWER ===(.*?)=== END FINAL ANSWER ==='
    match = re.search(final_answer_pattern, response, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # If no delimited section found, return empty string
    return ""