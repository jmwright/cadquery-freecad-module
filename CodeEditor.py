from PySide import QtCore
from PySide.QtCore import QSize, QSettings, QRect, Qt, QRegExp
from PySide.QtGui import QPainter, QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QTextCursor, QPlainTextEdit, QTextEdit, QWidget

class LineNumberArea(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.codeEditor = parent

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(),0)

    def paintEvent(self,event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    settings = QSettings('cqcad', 'settings')

    def __init__(self):
        # super(CodeEditor, self).__init__()
        QPlainTextEdit.__init__(self)
        self.lineNumberArea = LineNumberArea(self)
        self.setTabStopWidth(20)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self.highlighter = PythonHighlighter(self.document())
        self.dirty = False

        # Determine if the line number area needs to be shown or not
        lineNumbersCheckedState = self.settings.value('editor_line_numbers_visible', type=bool)
        if lineNumbersCheckedState:
            self.showLineNumberArea()
        else:
            self.hideLineNumberArea()

        self.initUI()

    def hideLineNumberArea(self):
        """
        Hides this editor's line number area.
        :return: None
        """
        self.lineNumberArea.setVisible(False)

    def showLineNumberArea(self):
        """
        Shows this editor's line number area.
        :return: None
        """
        self.lineNumberArea.setVisible(True)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while (block.isValid() and top <= event.rect().bottom()):
            if (block.isValid and bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(),
                                 self.fontMetrics().height(),
                                 QtCore.Qt.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = 1
        dMax = max(1, self.blockCount())
        while (dMax >= 10):
            dMax /= 10
            digits += 1
        return 3 + self.fontMetrics().width('9') * digits

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(),
                  cr.height()))

    # Loads the text of a script into the code editor
    def open(self, filename):
        self.file_path = filename

        with open(filename) as f: self.file_contents = f.read()

        self.setPlainText(self.file_contents)

    # Saves the text in the code editor to a file
    def save(self, filename):
        with open(filename, "w") as code_file:
            code_file.write(self.toPlainText())

    # Returns the path to the file with its text loaded into the code editor
    def get_path(self):
        return self.file_path

    def is_dirty(self):
        return self.dirty

    @QtCore.Slot(int)
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @QtCore.Slot(QRect, int)
    def updateLineNumberArea(self, rect, dy):
        if (dy != 0):
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(),
                                       self.lineNumberArea.width(),
                                       rect.height())
        if (rect.contains(self.viewport().rect())):
            self.updateLineNumberAreaWidth(0)

    @QtCore.Slot()
    def highlightCurrentLine(self):
        extraSelections = []
        if (not self.isReadOnly()):
            lineColor = QColor("#E0EEEE")
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor=self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def keyPressEvent(self,event):
        self.dirty = True
        customKey=False
        #AutoTab
        if (event.key()==Qt.Key_Enter or event.key()==16777220):
            customKey=True
            numTab=0
            #new line
            newBlock=self.textCursor().block()
            currLine=newBlock.text()
            tabRE=QRegExp("^[\t]*")
            tabRE.indexIn(currLine)
            numTab=tabRE.matchedLength()
            if (currLine != "" and currLine.strip()[-1] == "{"):
                numTab += 1
            QPlainTextEdit.keyPressEvent(self,event)
            if (numTab > 0):
                tCursor=self.textCursor()
                for _ in range(0,numTab):
                    tCursor.insertText("\t")

                #automatic close brace
                if currLine != "" and currLine.strip()[-1] == "{":
                    tCursor.insertText("\n")
                    for _ in range(0,numTab-1):
                        tCursor.insertText("\t")
                    tCursor.insertText("}")
                    tCursor.movePosition(QTextCursor.PreviousBlock)
                    tCursor.movePosition(QTextCursor.EndOfLine)
                    self.setTextCursor(tCursor)

        if event.key() == Qt.Key_Tab and self.textCursor().hasSelection():
            customKey = True
            selStart=self.textCursor().selectionStart()
            selEnd=self.textCursor().selectionEnd()
            cur=self.textCursor()
            endBlock=self.document().findBlock(selEnd)
            currBlock=self.document().findBlock(selStart)
            while currBlock.position()<=endBlock.position():
                cur.setPosition(currBlock.position())
                cur.insertText("\t")
                currBlock=currBlock.next()

        if event.key() == Qt.Key_Backtab and self.textCursor().hasSelection():
            customKey = True
            selStart=self.textCursor().selectionStart()
            selEnd=self.textCursor().selectionEnd()
            cur=self.textCursor()
            endBlock=self.document().findBlock(selEnd)
            currBlock=self.document().findBlock(selStart)
            while currBlock.position() <= endBlock.position():
                cur.setPosition(currBlock.position())
                if currBlock.text().left(1) == "\t":
                    cur.deleteChar()
                currBlock=currBlock.next()
        if not customKey:
            QPlainTextEdit.keyPressEvent(self, event)

    def initUI(self):
        pass

# Create the font styles that will highlight the code
keywordFormat = QTextCharFormat()
keywordFormat.setForeground(QColor('blue'))
operatorFormat = QTextCharFormat()
operatorFormat.setForeground(QColor('red'))
braceFormat = QTextCharFormat()
braceFormat.setForeground(QColor('darkGray'))
defClassFormat = QTextCharFormat()
defClassFormat.setForeground(QColor('black'))
stringFormat = QTextCharFormat()
stringFormat.setForeground(QColor('magenta'))
string2Format = QTextCharFormat()
string2Format.setForeground(QColor('darkMagenta'))
commentFormat = QTextCharFormat()
commentFormat.setForeground(QColor('darkGreen'))
commentFormat.setFontItalic(True)
selfFormat = QTextCharFormat()
selfFormat.setForeground(QColor('purple'))
selfFormat.setFontItalic(True)
numbersFormat = QTextCharFormat()
numbersFormat.setForeground(QColor('black'))

STYLES = {
    'keyword': keywordFormat,
    'operator': operatorFormat,
    'brace': braceFormat,
    'defclass': defClassFormat,
    'string': stringFormat,
    'string2': string2Format,
    'comment': commentFormat,
    'self': selfFormat,
    'numbers': numbersFormat
}

class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
