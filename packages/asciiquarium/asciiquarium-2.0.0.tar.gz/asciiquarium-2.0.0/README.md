# 🐠 Asciiquarium - Python Edition

An aquarium/sea animation in ASCII art for your terminal! This is a Python reimplementation of the classic Perl asciiquarium, designed to work cross-platform on Windows, Linux, and macOS.

## ✨ Features

- 🐟 Multiple fish species with different sizes and colors
- 🦈 Sharks that hunt small fish
- 🐋 Whales with animated water spouts
- 🚢 Ships sailing on the surface
- 🐙 Sea monsters lurking in the depths
- 🌊 Animated water lines and seaweed
- 🏰 Castle decoration
- 💨 Bubbles rising from fish
- 🎨 Full color support
- ⌨️ Interactive controls

## 🚀 Installation

### Using uv (Recommended)

```bash
# Install using uv
uv pip install -e .

# Or run directly with uv
uv run asciiquarium
```

### Using pip

```bash
# Install from source
pip install -e .

# Run the aquarium
asciiquarium
```

### From PyPI (when published)

```bash
pip install asciiquarium
asciiquarium
```

## 🎮 Controls

- **`q`** - Quit the aquarium
- **`r`** - Redraw and respawn all entities
- **`p`** - Pause/unpause the animation

## 🖥️ Requirements

- Python 3.7 or higher
- `windows-curses` (automatically installed on Windows)
- A terminal with color support (most modern terminals)

## 🌟 Features

### Cross-Platform Support

This implementation uses Python's `curses` library and automatically installs `windows-curses` on Windows systems, making it truly cross-platform.

### Entity System

- **Fish**: Multiple species with different ASCII art designs
- **Environment**: Seaweed, castle, water lines
- **Special Entities**: Sharks, whales, ships, monsters, and big fish
- **Animations**: Multi-frame animations for complex entities
- **Collision Detection**: Sharks can catch and eat small fish!

### Animation Engine

- Smooth 30 FPS animation
- Z-depth layering for proper overlapping
- Color masking system for detailed colorization
- Automatic cleanup of off-screen entities

## 📁 Project Structure

```
asciiquarium-python/
├── asciiquarium/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── entity.py            # Base entity class
│   ├── animation.py         # Animation engine
│   └── entities/
│       ├── __init__.py
│       ├── fish.py          # Fish entities
│       ├── environment.py   # Environment entities
│       └── special.py       # Special entities (sharks, whales, etc.)
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🎨 Customization

You can easily add new entities by creating them in the appropriate module:

```python
from asciiquarium.entity import Entity

def add_my_entity(old_ent, anim):
    anim.new_entity(
        entity_type='my_type',
        shape=my_ascii_art,
        color=my_color_mask,
        position=[x, y, z],
        callback_args=[dx, dy, dz, frame_speed],
        die_offscreen=True,
        death_cb=add_my_entity,
    )
```

## 🐛 Troubleshooting

### Windows Issues

If you encounter issues on Windows, ensure `windows-curses` is installed:

```bash
pip install windows-curses
```

### Terminal Size

For the best experience, use a terminal window of at least 80x24 characters.

### Color Support

If colors don't appear, check that your terminal supports color output.

## 📜 License

GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

## 🙏 Credits

- **Original Asciiquarium**: Kirk Baucom (kbaucom@schizoid.com)
- **ASCII Art**: Joan Stark and others
- **Python Port**: Mohammad Abu Mattar (info@mkabumattar.com)

## 🔗 Links

- [Original Asciiquarium](http://robobunny.com/projects/asciiquarium)
- [Author Website](https://mkabumattar.com/)
- [GitHub Repository](https://github.com/MKAbuMattar/asciiquarium-python)

## 🎯 Development

### Running from Source

```bash
# Clone the repository
git clone https://github.com/MKAbuMattar/asciiquarium-python.git
cd asciiquarium-python

# Install with uv
uv pip install -e .

# Run
uv run asciiquarium
```

### Testing

Simply run the program to test:

```bash
uv run asciiquarium
```

Press `r` to redraw and test entity spawning, and `p` to test pause functionality.

---

Enjoy your ASCII aquarium! 🐠🐟🦈🐋
