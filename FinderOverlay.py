from PySide.QtCore import Qt
from PySide.QtGui import QPainter, QWidget, QPalette, QBrush, QColor, QLabel, QGridLayout

class FinderOverlay(QWidget):    
    def __init__(self, parent=None):        
        super(FinderOverlay, self).__init__(parent)

        self.initUI()

    def initUI(self):
        # container = QWidget(self)
        # container.resize(200, 100);
        # container.setStyleSheet("background-color:black;")

        font_size = QLabel('Font Size')
        font_size.fillColor = QColor(30, 30, 30, 120)
        font_size.penColor = QColor("#333333")

        grid = QGridLayout()
        grid.setContentsMargins(50, 10, 10, 10)
        grid.addWidget(font_size, 0, 0)
        self.setLayout(grid)

        # palette = QPalette(self.palette())
        # palette.setColor(self.backgroundRole(), Qt.black)
        # palette.setColor(palette.Background, Qt.transparent)

        # self.setPalette(palette)

    # def paintEvent(self, event):        
    #     painter = QPainter()
    #     painter.begin(self)
    #     # painter.setRenderHint(QPainter.Antialiasing)
    #     painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
    #     painter.drawLine(self.width() / 8, self.height() / 8, 7 * self.width() / 8, 7 * self.height() / 8)
    #     painter.drawLine(self.width() / 8, 7 * self.height() / 8, 7 * self.width() / 8, self.height() / 8)
    #     # painter.setPen(QPen(Qt.NoPen)) 