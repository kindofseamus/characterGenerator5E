import requests
import random
from openai import OpenAI
import os
import re

# Define OpenAPI key
try:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "\n[ERROR] OpenAI API Key not found.\n"
            "Set the variable using one of the following commands:\n"
            "Windows (PowerShell) - $env:OPENAI_API_KEY='put-key-here'\n"
            "Mac/Linux (Bash) - export OPENAI_API_KEY='put-key-here'\n"
        )
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(
        "\n" + "*" * 50 + "\n"
        "CRITICAL ERROR: OPENAI API KEY MISSING.\n"
        "Full error text below.\n"
        f"{str(e)}"
        "\n" + "*" * 50 + "\n")

# Raw JSON URLs from 5etools-mirror-3
RACES_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/races.json"
CLASS_INDEX_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/class/index.json"
CLASS_BASE_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/class/"

# Define valid sources
OFFICIAL_SOURCES = {
    "PHB", "XGE", "TCE", "SCAG", "DMG", "VGM", "MTOF", "FTD",
    "AI", "BGDIA", "OOTDQ", "WBtW", "SACoC", "MPMM", "RMR", "LR"
}

BANNED_TOKENS = ("sidekick", "mystic")
def _is_index_candidate(name: str, path: str) -> bool:
    n = (name or "").lower()
    p = (path or "").lower()
    return not any(t in n or t in p for t in BANNED_TOKENS)

def get_json(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()

def pick_random_race(index_data):
    official_races = [
        r for r in index_data["race"]
        if r.get("source") in OFFICIAL_SOURCES and r.get("name") != "Custom Lineage"
    ]
    race = random.choice(official_races)
    return f"{race['name']}"

def pick_random_class_subclass(index_data):
    valid_classes = [class_file for name, class_file in index_data.items() if _is_index_candidate(name, class_file)]
    if not valid_classes:
        return "No valid class found"
    
    random.shuffle(valid_classes)
    
    while valid_classes:
        class_file = valid_classes.pop()
        data = get_json(f"{CLASS_BASE_URL}{class_file}")
        info = data["class"][0]
        if info.get("source") not in OFFICIAL_SOURCES:
            continue
            
        subs = [s for s in data.get("subclass", [])
                if s.get("source") in OFFICIAL_SOURCES]
        if subs:
            return f"{info['name']} ({random.choice(subs)['name']})"
        else:
            continue
    
    return "No valid class found"

def generate_ai_description(race, class_subclass, genName, theme, genBackstory, genPersonality, genPlaystyle):
    # Check variables and set prompt sections
    theme_str = (theme or "").strip()
    has_theme = bool(theme_str)
    sections = []
    if genName:
        sections.append(("Name", "Generate a fitting fantasy name."))
    if genBackstory:
        sections.append(("Backstory", "Write a concise 3-sentence backstory."))
    if genPersonality:
        sections.append(("Personality", "Write a tight 2-sentence personality description."))
    if genPlaystyle:
        sections.append(("Playstyle", "Write a 2 sentence playstyle summary: combat approach, strengths, and typical tactics."))
    theme_line = f" in this theme: '{theme_str}'" if has_theme else ""
    task_lines = " ".join(str(instr) for _, instr in sections if instr)
    label_lines = "\n".join(f"{label}: <text>" for label, _ in sections)

    # Forbid name generation when toggled off
    forbid_names = ""
    if not genName:
        forbid_names = " Do not invent or include proper names of nouns in your response. Refer to the character generically (e.g., 'this character', 'they'). Do not start any sentences with a personal name."
    
    # Construct the prompt
    prompt = (
        f"Complete the following tasks for a TTRPG character who is a(n) {race} {class_subclass}{theme_line}. "
        f"{task_lines}{forbid_names} "
        "Label each generated part exactly as shown below and do not use bold or markdown formatting:\n"
        f"{label_lines}"
    )
    
    # Next line is for debugging only, leave commented otherwise
    # print(f"Sending the following prompt to AI client:\n{prompt}")
    # Send prompt to AI client
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=350
        )
    except Exception as e:
        messagebox.showerror("Network Error", f"Could not send prompt to AI client.\n{e}")
    
    # Check if response came back and set fallback variables
    if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
        result = {label.lower(): "" for label, _ in sections}
        if any(s[0] == "Name" for s in sections):
            result["name"] = "Error: No response from AI."
        if any(s[0] == "Backstory" for s in sections):
            result["backstory"] = "No character generated."
        if any(s[0] == "Personality" for s in sections):
            result["personality"] = "Please try again."
        if any(s[0] == "Playstyle" for s in sections):
            result["playstyle"] = "Please try again."
        return result
    
    # Set response variable if received properly
    full_response = response.choices[0].message.content.strip()

    # Build regex to parse response by labels
    labels = [lbl for lbl, _ in sections]
    label_union = "|".join(re.escape(l) for l in labels)
    pattern = re.compile(rf"^({label_union}):[ \t]*(.*?)(?=^(?:{label_union}):|\Z)", re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    found = {m.group(1).capitalize(): m.group(2).strip() for m in pattern.finditer(full_response)}
    
    # Build return dictionary
    result = {}
    try:
        for label, _ in sections:
            key = label.lower()
            result[key] = found.get(label, "")
    except:
        return {"Error": "Unable to extract data properly",
                "raw": full_response}
    
    return result