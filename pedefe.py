import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QImage
from PyQt5.QtCore import Qt, QRectF
import fitz  # PyMuPDF

class PDFViewer(QWidget):
    def __init__(self, pdf_path):
        super().__init__()
        self.doc = fitz.open(pdf_path)
        self.current_page = 0
        self.scale = 1.0
        self.highlights = []
        self.updatePagePixmap()

    def updatePagePixmap(self):
        page = self.doc[self.current_page]
        mat = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        fmt = QImage.Format_RGB888
        self.image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        self.setFixedSize(self.image.width(), self.image.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        
        for highlight in self.highlights:
            painter.fillRect(QRectF(*highlight), QColor(255, 255, 0, 100))

    def scrollPage(self, direction):
        if direction == "down" and self.current_page < len(self.doc) - 1:
            self.current_page += 1
        elif direction == "up" and self.current_page > 0:
            self.current_page -= 1
        self.updatePagePixmap()
        self.update()

    def highlightText(self, rect):
        self.highlights.append(rect)
        self.update()

    def saveHighlights(self):
        page = self.doc[self.current_page]
        for highlight in self.highlights:
            page.add_highlight_annot(highlight)
        self.doc.save(self.doc.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)

class MainWindow(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        self.setWindowTitle("PDF Reader")
        self.setGeometry(100, 100, 800, 600)

        self.pdf_viewer = PDFViewer(pdf_path)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.pdf_viewer)
        self.scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.pdf_viewer.scrollPage("down")
        elif event.key() == Qt.Key_Up:
            self.pdf_viewer.scrollPage("up")
        elif event.key() == Qt.Key_S:
            self.pdf_viewer.saveHighlights()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        print("Please provide a PDF file path as an argument.")
        sys.exit(1)
    pdf_path = sys.argv[1]
    window = MainWindow(pdf_path)
    window.show()
    sys.exit(app.exec_())