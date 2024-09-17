import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QRubberBand, QFileDialog, QMessageBox, QColorDialog, QVBoxLayout, QWidget, QShortcut)
from PyQt5.QtCore import QRect, QSize, QPoint, Qt
from PIL import ImageGrab, Image
from PyQt5.QtGui import QPainter, QPen, QColor, QKeySequence
import time

class SnippingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Snipping Tool')
        self.setGeometry(300, 200, 800, 600)  # Custom window size
        self.setWindowOpacity(0.10)  # Slight opacity for better visibility during capture

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.current_rect = QRect()
        self.drawing_mode = None
        self.color = QColor(0, 0, 0)  # Default color: Black
        self.last_image = None  # Store the last screenshot
        self.undo_stack = []  # Store actions for undo
        self.redo_stack = []  # Store actions for redo

        self.annotation_buttons()  # Add the toolbar for annotations
        self.add_shortcuts()  # Add undo/redo shortcuts

    def annotation_buttons(self):
        """Toolbar for drawing tools."""
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set it as the central widget

        layout = QVBoxLayout(central_widget)  # Apply layout to central widget

        # Add buttons for drawing tools
        line_button = QPushButton('Line', self)
        line_button.clicked.connect(lambda: self.set_drawing_mode('line'))
        layout.addWidget(line_button)

        rectangle_button = QPushButton('Rectangle', self)
        rectangle_button.clicked.connect(lambda: self.set_drawing_mode('rectangle'))
        layout.addWidget(rectangle_button)

        # Color selection
        color_button = QPushButton('Select Color', self)
        color_button.clicked.connect(self.select_color)
        layout.addWidget(color_button)

        # Clear button
        clear_button = QPushButton('Clear', self)
        clear_button.clicked.connect(self.clear_image)
        layout.addWidget(clear_button)

    def add_shortcuts(self):
        """Add undo and redo shortcuts."""
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.redo)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.current_rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.setGeometry(self.current_rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubber_band.hide()
            self.capture_selected_area()
            self.undo_stack.append(self.current_rect)  # Add the action to the undo stack
            self.redo_stack.clear()  # Clear redo stack after new action

    def capture_selected_area(self):
        """Capture the selected area."""
        x1 = self.current_rect.left()
        y1 = self.current_rect.top()
        x2 = self.current_rect.right()
        y2 = self.current_rect.bottom()

        if x1 < x2 and y1 < y2:
            self.hide()  # Hide the window for a better capture experience
            QApplication.processEvents()  # Ensure window hides fully
            time.sleep(0.3)
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.last_image = screenshot.copy()

            # Open save dialog
            file_dialog = QFileDialog(self, "Save Screenshot", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setOption(QFileDialog.DontConfirmOverwrite, False)

            if file_dialog.exec_():
                filename = file_dialog.selectedFiles()[0]

                # Convert RGBA to RGB for JPEG files
                if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    screenshot = screenshot.convert("RGB")

                screenshot.save(filename)
                self.show_save_confirmation(filename)
            else:
                print("Save operation cancelled.")

            self.show()
        else:
            print("Invalid selection area. Please try again.")
            self.show()

    def set_drawing_mode(self, mode):
        """Set the drawing mode (line or rectangle)."""
        self.drawing_mode = mode

    def select_color(self):
        """Select the drawing color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def clear_image(self):
        """Clear the current image (reset to last screenshot)."""
        if self.last_image:
            self.last_image = self.last_image.convert("RGBA")

    def undo(self):
        """Undo the last action."""
        if self.undo_stack:
            last_action = self.undo_stack.pop()
            self.redo_stack.append(last_action)
            self.repaint()  # Redraw after undo

    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            last_action = self.redo_stack.pop()
            self.undo_stack.append(last_action)
            self.repaint()  # Redraw after redo

    def show_save_confirmation(self, filename):
        """Displays a message box with the saved file details."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"Screenshot saved successfully!\nFile: {filename}")
        msg_box.setWindowTitle("Screenshot Saved")
        msg_box.exec_()

    def paintEvent(self, event):
        """Handle painting for drawing tools."""
        if self.drawing_mode and self.last_image:
            painter = QPainter(self)
            pen = QPen(self.color, 3)
            painter.setPen(pen)

            if self.drawing_mode == 'line':
                painter.drawLine(self.origin, self.current_rect.bottomRight())
            elif self.drawing_mode == 'rectangle':
                painter.drawRect(self.current_rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingTool()
    window.show()  # Show the window without fullscreen
    sys.exit(app.exec_())
