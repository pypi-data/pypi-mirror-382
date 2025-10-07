"""
Animation engine for asciiquarium

Manages the curses screen, entity rendering, input handling, and main animation loop.
"""

import curses
import time
from typing import List, Callable, Optional
from .entity import Entity


class Animation:
    """Main animation controller that manages the screen and all entities"""
    
    def __init__(self):
        self.screen = None
        self.entities: List[Entity] = []
        self.color_enabled = True
        self.running = False
        self.screen_width = 0
        self.screen_height = 0
        self.color_pairs = {}
        self._init_color_pairs()
    
    def _init_color_pairs(self):
        """Initialize color pair mappings"""
        self.color_map = {
            'BLACK': curses.COLOR_BLACK,
            'RED': curses.COLOR_RED,
            'GREEN': curses.COLOR_GREEN,
            'YELLOW': curses.COLOR_YELLOW,
            'BLUE': curses.COLOR_BLUE,
            'MAGENTA': curses.COLOR_MAGENTA,
            'CYAN': curses.COLOR_CYAN,
            'WHITE': curses.COLOR_WHITE,
        }
        
        # Map letters to colors for color masks
        self.mask_color_map = {
            'r': 'RED', 'R': 'RED',
            'g': 'GREEN', 'G': 'GREEN',
            'y': 'YELLOW', 'Y': 'YELLOW',
            'b': 'BLUE', 'B': 'BLUE',
            'm': 'MAGENTA', 'M': 'MAGENTA',
            'c': 'CYAN', 'C': 'CYAN',
            'w': 'WHITE', 'W': 'WHITE',
            'k': 'BLACK', 'K': 'BLACK',
        }
    
    def init_screen(self, stdscr):
        """Initialize the curses screen"""
        self.screen = stdscr
        self.screen.nodelay(1)
        self.screen.keypad(1)
        curses.curs_set(0)
        
        # Enable colors
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            
            # Create color pairs (1-based indexing)
            pair_id = 1
            for fg_name, fg_code in self.color_map.items():
                try:
                    curses.init_pair(pair_id, fg_code, -1)
                    self.color_pairs[fg_name] = pair_id
                    pair_id += 1
                except:
                    pass
        
        self.update_term_size()
    
    def update_term_size(self):
        """Update terminal dimensions"""
        if self.screen:
            raw_height, self.screen_width = self.screen.getmaxyx()
            self.screen_height = raw_height - 1  # Leave room for bottom line
            
            # Check minimum terminal size (using raw height for check)
            if raw_height < 24 or self.screen_width < 80:
                raise ValueError(
                    f"Terminal too small! Need at least 80x24, got {self.screen_width}x{raw_height}.\n"
                    "Please resize your terminal and try again."
                )
    
    def width(self) -> int:
        """Get screen width"""
        return self.screen_width
    
    def height(self) -> int:
        """Get screen height"""
        return self.screen_height
    
    def color(self, enabled: bool):
        """Enable or disable color"""
        self.color_enabled = enabled
    
    def new_entity(self, **kwargs) -> Entity:
        """Create and add a new entity"""
        entity = Entity(**kwargs)
        self.add_entity(entity)
        return entity
    
    def add_entity(self, entity: Entity):
        """Add an existing entity"""
        self.entities.append(entity)
        # Sort by Z-depth (lower z drawn first, appears behind)
        self.entities.sort(key=lambda e: e.z)
    
    def del_entity(self, entity: Entity):
        """Remove an entity"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def remove_all_entities(self):
        """Clear all entities"""
        self.entities.clear()
    
    def get_entities_of_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        return [e for e in self.entities if e.entity_type == entity_type]
    
    def _check_collisions(self):
        """Check for collisions between physical entities"""
        physical_entities = [e for e in self.entities if e.physical]
        
        for entity in physical_entities:
            entity.collision_list.clear()
            
            for other in self.entities:
                if entity is other:
                    continue
                
                # Simple bounding box collision
                e_x, e_y, _ = entity.position()
                e_w, e_h = entity.size()
                o_x, o_y, _ = other.position()
                o_w, o_h = other.size()
                
                if (e_x < o_x + o_w and e_x + e_w > o_x and
                    e_y < o_y + o_h and e_y + e_h > o_y):
                    entity.collision_list.append(other)
    
    def _draw_entity(self, entity: Entity):
        """Draw a single entity to the screen"""
        shape = entity.get_current_shape()
        color_mask = entity.get_current_color()
        x, y, _ = entity.position()
        
        lines = shape.split('\n')
        color_lines = color_mask.split('\n') if color_mask else []
        
        for line_idx, line in enumerate(lines):
            draw_y = y + line_idx
            if draw_y < 0 or draw_y >= self.screen_height:
                continue
            
            color_line = color_lines[line_idx] if line_idx < len(color_lines) else ""
            
            for char_idx, char in enumerate(line):
                draw_x = x + char_idx
                if draw_x < 0 or draw_x >= self.screen_width:
                    continue
                
                # Skip transparent characters
                if entity.auto_trans and char == ' ':
                    continue
                
                # Determine color
                color_attr = 0
                if self.color_enabled and char_idx < len(color_line):
                    color_char = color_line[char_idx]
                    if color_char in self.mask_color_map:
                        color_name = self.mask_color_map[color_char]
                        if color_name in self.color_pairs:
                            color_attr = curses.color_pair(self.color_pairs[color_name])
                
                # Use default color if no mask
                if color_attr == 0 and entity.default_color in self.color_pairs:
                    color_attr = curses.color_pair(self.color_pairs[entity.default_color])
                
                try:
                    self.screen.addch(draw_y, draw_x, char, color_attr)
                except:
                    pass  # Ignore drawing errors at screen edges
    
    def redraw_screen(self):
        """Clear and redraw the entire screen"""
        if not self.screen:
            return
        
        try:
            self.screen.clear()
        except:
            pass
    
    def animate(self):
        """Update all entities and redraw the screen"""
        if not self.screen:
            return
        
        current_time = time.time()
        
        # Update all entities
        for entity in self.entities[:]:  # Copy list since we might modify it
            entity.update(self)
        
        # Check collisions
        self._check_collisions()
        
        # Remove dead entities
        for entity in self.entities[:]:
            if entity.should_die(self.screen_width, self.screen_height, current_time):
                if entity.death_cb:
                    entity.death_cb(entity, self)
                self.del_entity(entity)
        
        # Draw all entities
        try:
            self.screen.erase()
            for entity in self.entities:
                self._draw_entity(entity)
            self.screen.refresh()
        except:
            pass
    
    def run(self, setup_callback: Callable):
        """Main animation loop"""
        def _run(stdscr):
            self.init_screen(stdscr)
            self.running = True
            
            # Call setup to create initial entities
            setup_callback(self)
            
            paused = False
            last_time = time.time()
            
            try:
                while self.running:
                    # Handle input
                    try:
                        key = self.screen.getch()
                        if key != -1:
                            key_char = chr(key).lower() if key < 256 else ''
                            
                            if key_char == 'q':
                                self.running = False
                            elif key_char == 'r':
                                # Redraw - recreate all entities
                                self.remove_all_entities()
                                setup_callback(self)
                                self.redraw_screen()
                            elif key_char == 'p':
                                paused = not paused
                            elif key == curses.KEY_RESIZE:
                                self.update_term_size()
                                self.redraw_screen()
                    except:
                        pass
                    
                    # Animate if not paused
                    if not paused:
                        self.animate()
                    
                    # Control frame rate (~30 FPS)
                    current_time = time.time()
                    elapsed = current_time - last_time
                    sleep_time = max(0, 0.033 - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    last_time = current_time
            except KeyboardInterrupt:
                self.running = False
        
        try:
            curses.wrapper(_run)
        except KeyboardInterrupt:
            pass
