import os
import re
import sys

from google import genai

def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def extract_html(raw_text: str) -> str:
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("Gemini returned empty output.")

    fenced = re.findall(r"```(?:html|xml|javascript)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    for block in fenced:
        candidate = block.strip()
        if candidate.lower().startswith("<!doctype html>") or candidate.lower().startswith("<html"):
            return candidate

    if text.lower().startswith("<!doctype html>") or text.lower().startswith("<html"):
        return text

    raise ValueError("Gemini did not return valid HTML. Remove markdown and return raw HTML.")

def main():
    api_key = require_env("GEMINI_API_KEY")
    user_idea = require_env("USER_IDEA")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    client = genai.Client(api_key=api_key)

    prompt = f'''
You are an expert mobile game developer.
Create a complete, playable, single-file HTML5 mobile game based on this idea:
"{user_idea}"

Rules:
- Works on mobile screens and touch controls
- Includes start screen, gameplay loop, score, and game over
- Single-file HTML with CSS and JS inside
- No external libraries required
- Return only raw HTML starting with <!DOCTYPE html>
- Do not wrap in markdown blocks
'''

    response = client.models.generate_content(model=model_name, contents=prompt)
    html = extract_html(getattr(response, "text", "") or "")

    os.makedirs("www", exist_ok=True)
    output_path = os.path.join("www", "index.html")
    with open(output_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(html.strip())

    print(f"Game generated at {output_path}")

if __name__ == "__main__":
    main()
