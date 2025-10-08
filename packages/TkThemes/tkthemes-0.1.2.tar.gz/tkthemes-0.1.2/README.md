# TkThemes

`TkThemes` is a collection of ready-to-use Tkinter themes for Python GUI applications.  
It provides visually appealing color schemes, fonts, and widget styles to quickly style your Tkinter apps.

---

## Features

- 14+ pre-defined themes including:
  - Dracula, Solarized Light, Nord, Monokai Pro
  - Gruvbox Dark, One Dark Pro, GitHub Light, Oceanic Next
  - Crimson Red, Forest Green, Royal Purple, Classic White
  - Sepia Tone, Cyberpunk, Pastel Sunset
- Theme elements for:
  - Background (`bg`) and foreground (`fg`) colors
  - Entry widget background (`entry_bg`) and foreground (`entry_fg`)
  - Button backgrounds (`btn_bg`, `btn_bg_2`) and active button background (`btn_active_bg`)
  - Plot background (`plot_bg`)
  - Accent color (`accent_color`)
- Pre-defined fonts (`font`) for consistent styling

---

## Installation

You can install directly from GitHub:

```bash
pip install git+https://github.com/TirthrajSG/TkThemes.git
```

Or 

```bash
pip install TkThemes
```

## Usage
```python
from TkThemes import Themes

# Get a theme dictionary
dracula_theme = Themes["Dracula"]

# Access theme properties
bg_color = dracula_theme["bg"]
fg_color = dracula_theme["fg"]
font = dracula_theme["font"]

```
Or import pre-defined theme variables:
```python
from TkThemes import Dracula, Nord, MonokaiPro

print(Nord["accent_color"])  # #88c0d0

```

## Contributing

Feel free to submit new themes, improvements, or bug fixes via pull requests!
Make sure to follow the same structure as existing themes.

