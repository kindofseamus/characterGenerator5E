import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
from datetime import datetime
from random5E import (
    generate_ai_description,
    get_json,
    pick_random_race,
    pick_random_class_subclass,
    RACES_URL,
    CLASS_INDEX_URL
)

global generated_characters
generated_characters = []

# Create main window
root = tk.Tk()
root.title("5E Character Generator")
root.geometry("700x660")
root.resizable(False, False)

# Label and input for number of characters
tk.Label(root, text="Number of Characters to Generate (1-5):").pack(pady=5)
count_entry = tk.Entry(root, width=5)
count_entry.insert(0, "1")
count_entry.pack(pady=5)

# Text area for theme description
tk.Label(root, text="Theme Description:").pack(pady=5)
theme_entry = tk.Text(root, height=4, width=60, state="disabled", bg="#f0f0f0")
theme_entry.pack(pady=5)

# Grey out setting box when not in use
def toggle_theme_input():
    if use_theme.get():
        theme_entry.config(state="normal", bg="white")
    else:
        theme_entry.delete("1.0", tk.END)
        theme_entry.config(state="disabled", bg="#f0f0f0")

# Togglebox for using a custom theme
use_theme = tk.BooleanVar()
tk.Checkbutton(root, text="Use Custom Theme", variable=use_theme, command=toggle_theme_input).pack(pady=5)

# Toggle boxes frame
togglebox_frame = tk.Frame(root)
togglebox_frame.pack(pady=10)

# Togglebox for generating names
make_names = tk.BooleanVar()
tk.Checkbutton(togglebox_frame, text="Generate Names", variable=make_names).pack(side="left", padx=10)

# Togglebox for generating backstory
gen_backstory = tk.BooleanVar()
tk.Checkbutton(togglebox_frame, text="Generate Backstories", variable=gen_backstory).pack(side="left", padx=10)

# Togglebox for generating personality
gen_personality = tk.BooleanVar()
tk.Checkbutton(togglebox_frame, text="Generate Personalities", variable=gen_personality).pack(side="left", padx=10)

# Togglebox for generating playstyle
gen_playstyle = tk.BooleanVar()
tk.Checkbutton(togglebox_frame, text="Generate Playstyles", variable=gen_playstyle).pack(side="left", padx=10)

# Output display
tk.Label(root, text="Generated NPCs:").pack(pady=5)
output_box = scrolledtext.ScrolledText(root, wrap="word", width=80, height=20, state="disabled")
output_box.pack(pady=5)

# Function to generate characters
def generate_characters():
    # Set output box state
    output_box.config(state="normal")
    # Clear previous output
    output_box.delete("1.0", tk.END)
    
    # Check if proper # of characters
    try:
        count = int(count_entry.get())
        if count < 1 or count > 5:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a whole number between 1 and 5.")
        output_box.config(state="disabled")
        return

    # Set theme if toggled
    theme = theme_entry.get("1.0", tk.END).strip() if use_theme.get() else ""

    # Clear previously generated characters
    generated_characters.clear()
    
    # Get data from 5e.tools
    try:
        race_data = get_json(RACES_URL)
        class_index = get_json(CLASS_INDEX_URL)
    except Exception as e:
        messagebox.showerror("Network Error", f"Could not load 5e.tools data.\n{e}")
        output_box.config(state="disabled")
        return

    # If any toggles are true, use AI client
    if make_names.get() or gen_backstory.get() or gen_personality.get() or gen_playstyle.get():
        # Generate characters
        for _ in range(count):
            # Generate character
            race = pick_random_race(race_data)
            class_subclass = pick_random_class_subclass(class_index)
            desc = generate_ai_description(
                race,
                class_subclass,
                make_names.get(),
                theme,
                gen_backstory.get(),
                gen_personality.get(),
                gen_playstyle.get()
            )
            
            # Build output lines based on toggles
            lines = []
            lines.append(f"{race} {class_subclass}")
            if make_names.get() and desc.get("name"):
                lines.append(desc["name"])
            if gen_backstory.get():
                backstory = (desc.get("backstory") or "").strip()
                lines.append(f"Backstory: {backstory or '(not generated)'}")
            if gen_personality.get():
                personality = (desc.get("personality") or "").strip()
                lines.append(f"Personality: {personality or '(not generated)'}")
            if gen_playstyle.get():
                playstyle = (desc.get("playstyle") or "").strip()
                lines.append(f"Playstyle: {playstyle or '(not generated)'}")
            output_box.insert(tk.END, "\n".join(lines) + "\n\n")
            
            # Persist only generated sections for export
            char = {
                "race": race,
                "class": class_subclass
            }
            if make_names.get() and desc.get("name"):
                char["name"] = desc["name"]
            if gen_backstory.get():
                char["backstory"] = desc.get("backstory", "")
            if gen_personality.get():
                char["personality"] = desc.get("personality", "")
            if gen_playstyle.get():
                char["playstyle"] = desc.get("playstyle", "")
            generated_characters.append(char)
    
    # If no toggles are selected, don't use AI client
    else:
        # Generate character
        for _ in range(count):
            race = pick_random_race(race_data)
            class_subclass = pick_random_class_subclass(class_index)
            # Build output lines
            lines = []
            lines.append(f"{race} {class_subclass}")
            output_box.insert(tk.END, "\n".join(lines) + "\n\n")
            # Persist character for export
            char = {
                "race": race,
                "class": class_subclass
            }
            generated_characters.append(char)
    
    # Disable output box
    output_box.config(state="disabled")

def save_to_file():
    if not generated_characters:
        messagebox.showwarning("Nothing to Save", "Please generate Characters first.")
        return

    filename = f"generatedCharacters_{datetime.now().strftime('%d.%m.%Y@%H.%M')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(generated_characters, f, indent=4, ensure_ascii=False)

    messagebox.showinfo("Saved", f"Characters saved to {filename}")

# Buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Generate button
tk.Button(button_frame, text="Generate Characters", command=generate_characters).pack(side="left", padx=10)

# Export button
tk.Button(button_frame, text="Save to JSON File", command=save_to_file).pack(side="left", padx=10)

# Start the GUI loop
root.mainloop()