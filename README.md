# Character Generator for 5E
The generator uses a combination of 5e.tools's library of content and OpenAI's agents to make a customizable character generator compatible with 5E.

The tool has many toggleable options such as custom theme use, name, backstory, playstyle, and personality generation. Very useful for DM's when trying to come up with detailed NPCs but can also be helpful on the player side for coming up with out of the box character ideas.

<img width="507" height="500" alt="characterGenerator" src="https://github.com/user-attachments/assets/2bbedda1-0537-4fd5-b0ba-2f590d7eb58b" />

(You can use the script without sending prompts to the AI if you just want random race/class combos powered by 5e.tools)

To use this tool you will need to setup an environment variable using your OpenAI api key which can be found here: https://platform.openai.com/api-keys

Once you have your key, run whichever command fits your system:
- Windows (PowerShell)
```
$env:OPENAI_API_KEY='put-key-here'
```
- Mac/Linux (Bash)
```
export OPENAI_API_KEY='put-key-here'
```
Once your key variable is set, run the main.py file to launch the gui and start generating :)
