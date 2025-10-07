"""
Main entry point for asciiquarium

Cross-platform ASCII art aquarium animation for the terminal.
"""

import sys
import signal
from .animation import Animation
from .entities import (
    add_environment,
    add_castle,
    add_all_seaweed,
    add_all_fish,
    random_object,
)


def setup_aquarium(anim: Animation):
    """Initialize all aquarium entities"""
    add_environment(anim)
    add_castle(anim)
    add_all_seaweed(anim)
    add_all_fish(anim)
    random_object(None, anim)


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    sys.exit(0)


def main():
    """Main entry point for the asciiquarium application"""
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create animation and run
        anim = Animation()
        anim.run(setup_aquarium)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure clean exit
        print("\nThanks for watching! 🐠🐟🦈")


if __name__ == '__main__':
    main()
