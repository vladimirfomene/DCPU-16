import assembler
import sys
import wx
import wx.stc as stc

FONT = 'Courier New'
SIZE = 14 if sys.platform == 'darwin' else 10

class Style(object):
    instances = []
    def __init__(self, color, bold=False):
        Style.instances.append(self)
        self.number = len(Style.instances) - 1
        self.color = color
        self.bold = bold

COMMENT = Style((0, 64, 0))
OPCODE = Style((0, 64, 128), True)
OPERAND = Style((128, 0, 64))
LITERAL = Style((255, 0, 0))
STRING = Style((128, 128, 128))
SYMBOL = Style((0, 0, 0), True)
LABEL = Style((0, 0, 0))
ID = Style((0, 0, 0))
UNKNOWN = Style((255, 0, 110))

class Editor(stc.StyledTextCtrl):
    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.styles = self.build_styles()
        self.StyleSetFontAttr(stc.STC_STYLE_DEFAULT, SIZE, FONT, 0, 0, 0)
        self.StyleClearAll()
        for style in Style.instances:
            self.StyleSetForeground(style.number, wx.Colour(*style.color))
            self.StyleSetBold(style.number, style.bold)
        self.SetLexer(stc.STC_LEX_CONTAINER)
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 0)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetBackSpaceUnIndents(True)
        self.Bind(stc.EVT_STC_STYLENEEDED, self.on_style_needed)
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_update_ui)
        self.Bind(stc.EVT_STC_CHARADDED, self.on_charadded)
    def build_styles(self):
        result = {}
        for name in assembler.BASIC_OPCODES:
            result[name] = OPCODE
        for name in assembler.SPECIAL_OPCODES:
            result[name] = OPCODE
        for name in assembler.COMMAND_OPCODES:
            result[name] = OPCODE
        for name in ['DAT', 'RESERVE']:
            result[name] = OPCODE
        for name in assembler.REGISTERS:
            result[name] = OPERAND
        for name in assembler.SRC_CODES:
            result[name] = OPERAND
        for name in assembler.DST_CODES:
            result[name] = OPERAND
        for name in ['PICK']:
            result[name] = OPERAND
        for name in ['DECIMAL', 'HEX', 'OCT']:
            result[name] = LITERAL
        for name in ['STRING', 'CHAR']:
            result[name] = STRING
        for name in ['INC', 'DEC', 'LBRACK', 'RBRACK', 'PLUS', 'AT']:
            result[name] = SYMBOL
        for name in ['LABEL']:
            result[name] = LABEL
        for name in ['ID']:
            result[name] = ID
        return result
    def stylize(self, line):
        position = 0
        text = self.GetLine(line)
        self.StartStyling(self.PositionFromLine(line), 0x1f)
        lexer = assembler.LEXER
        lexer.input(text)
        while True:
            try:
                token = lexer.token()
            except Exception:
                break
            if token is None:
                break
            style = self.styles.get(token.type, UNKNOWN)
            start = token.lexpos
            end = lexer.lexpos
            length = start - position
            self.SetStyling(length, 0)
            position += length
            length = end - position
            self.SetStyling(length, style.number)
            position += length
    def on_style_needed(self, event):
        start = self.GetFirstVisibleLine()
        end = self.LineFromPosition(event.GetPosition())
        for line in xrange(start, end + 1):
            self.stylize(line)
    def on_charadded(self, event):
        code = event.GetKey()
        if code == ord('\n'):
            line = self.GetCurrentLine() - 1
            if line >= 0:
                text = self.GetLine(line)
                for index, ch in enumerate(text):
                    if ch not in ' \t':
                        self.ReplaceSelection(text[:index])
                        break
    def on_update_ui(self, event):
        wx.CallAfter(self.update_line_numbers)
    def update_line_numbers(self):
        text = ' %d' % self.GetLineCount()
        width = self.TextWidth(stc.STC_STYLE_LINENUMBER, text)
        self.SetMarginWidth(0, width)
