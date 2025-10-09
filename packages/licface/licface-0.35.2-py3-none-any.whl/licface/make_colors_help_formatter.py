import argparse
from typing import ClassVar
from make_colors import make_colors

class MakeColorsHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """A custom HelpFormatter with colored output using make_colors."""
    
    def __init__(self, prog, epilog=None, width=None, max_help_position=24, indent_increment=2):
        super().__init__(prog, max_help_position=max_help_position, indent_increment=indent_increment)
        if epilog is not None:
            self._epilog = epilog
        if width is not None:
            self._width = width
        
        # Define color styles from CONFIG or defaults
        self.styles: ClassVar[dict[str, str]] = {
            "args": "lightyellow",
            "groups": "lightmagenta", 
            "help": "lightcyan",
            "metavar": "lightcyan",
            "syntax": "yellow",
            "text": "magenta",
            "prog": "lightcyan",
            "default": "green",
        }
    
    def _colorize(self, text, style_key):
        """Apply color to text based on style key."""
        if not text:
            return text
        color = self.styles.get(style_key, "white")
        return make_colors(text, color)
    
    def format_help(self):
        """Format the help message with colors."""
        help_text = super().format_help()
        
        # Add newline before Usage if needed
        if not help_text.lstrip().startswith("Usage:") and not help_text.lstrip().startswith("usage:"):
            idx = help_text.lower().find("usage:")
            if idx > 0:
                help_text = help_text[:idx] + "\n" + help_text[idx:]
            elif idx == 0:
                help_text = "\n" + help_text
        elif not help_text.startswith("\n"):
            help_text = "\n" + help_text
        
        # Colorize different sections
        help_text = self._colorize_sections(help_text)
        return help_text
    
    def _colorize_sections(self, text):
        """Colorize different sections of help text."""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Colorize section headers (usage, options, etc.)
            if line and not line[0].isspace():
                if line.lower().startswith('usage:'):
                    result.append(make_colors('Usage:', 'lightcyan', 'b') + line[6:])
                elif line.endswith(':') and len(line.strip()) < 30:
                    result.append(make_colors(line, 'lightmagenta', 'b'))
                else:
                    result.append(line)
            # Colorize option lines (starting with -)
            elif line.strip().startswith('-'):
                parts = line.split(None, 1)
                if len(parts) > 1:
                    colored_opt = make_colors(parts[0], self.styles['args'], 'b')
                    result.append(line.replace(parts[0], colored_opt, 1))
                else:
                    result.append(make_colors(line, self.styles['args'], 'b'))
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _format_action(self, action):
        """Format a single action with colors."""
        # Get the default formatted action
        help_text = super()._format_action(action)
        
        # Colorize the option strings
        if action.option_strings:
            for opt in action.option_strings:
                colored_opt = make_colors(opt, self.styles['args'], 'b')
                help_text = help_text.replace(opt, colored_opt, 1)
        
        # Colorize metavar
        if action.metavar:
            metavar_str = str(action.metavar)
            colored_metavar = make_colors(metavar_str, self.styles['metavar'], 'b')
            help_text = help_text.replace(metavar_str, colored_metavar)
        
        return help_text
    
    def add_text(self, text):
        """Add text with special handling for code blocks."""
        if text is argparse.SUPPRESS or text is None:
            return
        
        if isinstance(text, str):
            lines = text.strip().splitlines()
            indent = " " * getattr(self, "_current_indent", 2)
            if len(indent) < 2:
                indent = " " * 2
            
            # Detect if all lines are code (starting with python, $, or indented)
            is_all_code = all(
                l.strip().startswith(("python", "$")) or l.startswith("  ") 
                for l in lines if l.strip()
            )
            
            if len(lines) > 0 and is_all_code:
                # All lines are code
                code_text = []
                for line in lines:
                    if line.strip():
                        colored_line = indent + make_colors(line.strip(), 'lightgreen')
                        code_text.append(colored_line)
                
                if code_text:
                    self._add_item(self._format_text, ['\n'.join(code_text) + '\n'])
                return
            
            elif len(lines) > 1:
                # Multi-line with possible title
                # Check if first line is a title (not a command)
                if not (lines[0].strip().startswith(("python", "$")) or lines[0].startswith("  ")):
                    # First line is title
                    title = make_colors(lines[0], 'cyan', 'b')
                    self._add_item(self._format_text, [title])
                    
                    # Check if remaining lines are code
                    code_lines = lines[1:]
                    is_code = all(
                        l.strip().startswith(("python", "$")) or l.startswith("  ") or not l.strip()
                        for l in code_lines
                    )
                    
                    if is_code:
                        # Format remaining lines as code
                        code_text = []
                        for line in code_lines:
                            if line.strip():
                                colored_line = indent + make_colors(line.strip(), 'y')
                                code_text.append(colored_line)
                        
                        if code_text:
                            self._add_item(self._format_text, ['\n'.join(code_text) + '\n'])
                    else:
                        # Regular text - colorize it
                        for line in code_lines:
                            if line.strip():
                                colored_text = make_colors(line, self.styles['text'])
                                self._add_item(self._format_text, [indent + colored_text])
                    return
                else:
                    # All lines including first are code
                    code_text = []
                    for line in lines:
                        if line.strip():
                            colored_line = indent + make_colors(line.strip(), 'blue')
                            code_text.append(colored_line)
                    
                    if code_text:
                        self._add_item(self._format_text, ['\n'.join(code_text) + '\n'])
                    return
            else:
                # Single line text - colorize it
                colored_text = make_colors(text.strip(), self.styles['text'])
                self._add_item(self._format_text, [indent + colored_text + '\n'])
                return
        
        super().add_text(text)
    
    def _format_text(self, text):
        """Format text with proper width handling."""
        if not text:
            return ''
        return text + '\n'


# Alternative simpler version without extensive colorization
class SimpleCustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """A simpler custom HelpFormatter with basic coloring."""
    
    def __init__(self, prog, **kwargs):
        super().__init__(prog, **kwargs)
    
    def format_help(self):
        help_text = super().format_help()
        
        # Add newline before Usage
        if not help_text.startswith("\n"):
            help_text = "\n" + help_text
        
        # Basic colorization
        lines = help_text.split('\n')
        result = []
        
        for line in lines:
            # Colorize headers
            if line and not line[0].isspace() and (line.endswith(':') or 'usage:' in line.lower()):
                result.append(make_colors(line, 'lightcyan', 'b'))
            # Colorize options
            elif line.strip().startswith('-'):
                parts = line.split(None, 1)
                if parts:
                    colored = make_colors(parts[0], 'lightyellow', 'b')
                    rest = parts[1] if len(parts) > 1 else ''
                    result.append(line.replace(parts[0], colored, 1))
                else:
                    result.append(line)
            else:
                result.append(line)
        
        return '\n'.join(result)