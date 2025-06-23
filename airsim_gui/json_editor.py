import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QFileDialog, 
                             QAction, QVBoxLayout, QWidget, QMenu, QMessageBox, 
                             QInputDialog, QLineEdit, QComboBox, QDialog, 
                             QDialogButtonBox, QFormLayout, QLabel, QCheckBox,
                             QToolBar, QStatusBar, QSplitter, QTextEdit, QHBoxLayout,
                             QStyledItemDelegate, QPushButton)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class JsonItemDelegate(QStyledItemDelegate):
    """Custom delegate to handle different data types during editing"""
    
    def createEditor(self, parent, option, index):
        # For value column, create appropriate editor based on content
        if index.column() == 1:  # Value column
            # Get type info from the type column
            type_index = index.sibling(index.row(), 2)
            type_text = type_index.data(Qt.DisplayRole)
            
            if type_text == 'Boolean':
                editor = QComboBox(parent)
                editor.addItems(['true', 'false'])
                return editor
            else:
                editor = QLineEdit(parent)
                return editor
        else:
            # For key column, use default string editor
            return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index):
        if isinstance(editor, QLineEdit):
            editor.setText(index.data(Qt.DisplayRole) or "")
        elif isinstance(editor, QComboBox):
            value = index.data(Qt.DisplayRole).lower()
            editor.setCurrentText(value if value in ['true', 'false'] else 'false')
        else:
            super().setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.DisplayRole)
        elif isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.DisplayRole)
        else:
            super().setModelData(editor, model, index)

class AddEditDialog(QDialog):
    def __init__(self, parent=None, key="", value="", is_edit=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Item" if is_edit else "Add Item")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout()
        
        self.key_edit = QLineEdit(key)
        self.value_edit = QLineEdit(str(value))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['String', 'Number', 'Boolean', 'Object', 'Array', 'Null'])
        
        # Auto-detect type
        if isinstance(value, bool):
            self.type_combo.setCurrentText('Boolean')
            self.value_edit.setText(str(value).lower())
        elif isinstance(value, (int, float)):
            self.type_combo.setCurrentText('Number')
        elif isinstance(value, dict):
            self.type_combo.setCurrentText('Object')
            self.value_edit.setText('')
        elif isinstance(value, list):
            self.type_combo.setCurrentText('Array')
            self.value_edit.setText('')
        elif value is None:
            self.type_combo.setCurrentText('Null')
            self.value_edit.setText('')
        
        layout.addRow("Key:", self.key_edit)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Value:", self.value_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Connect type change to update value field
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
    
    def on_type_changed(self, type_name):
        if type_name == 'Boolean':
            self.value_edit.setText('false')
        elif type_name == 'Number':
            self.value_edit.setText('0')
        elif type_name == 'Null':
            self.value_edit.setText('')
        elif type_name in ['Object', 'Array']:
            self.value_edit.setText('')
    
    def get_values(self):
        key = self.key_edit.text()
        value_text = self.value_edit.text()
        type_name = self.type_combo.currentText()
        
        if type_name == 'Boolean':
            value = value_text.lower() == 'true'
        elif type_name == 'Number':
            try:
                value = int(value_text) if '.' not in value_text else float(value_text)
            except ValueError:
                value = 0
        elif type_name == 'Object':
            value = {}
        elif type_name == 'Array':
            value = []
        elif type_name == 'Null':
            value = None
        else:
            value = value_text
        
        return key, value

class JsonEditorWidget(QWidget):
    """A reusable JSON editor widget that can be embedded in other applications"""
    
    # Signals
    jsonChanged = pyqtSignal(dict)  # Emitted when JSON data is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_data = {}
        self.is_modified = False
        
        # Font scaling
        self.font_scale = 1.0
        self.base_font_size = 10
        
        self.setup_ui()
    
    def handle_key_press(self, event):
        """Custom key press handler for the tree view"""
        if event.key() == Qt.Key_Delete:
            # Handle delete key to remove selected items
            self.delete_selected_items()
        else:
            # Call the original implementation for other keys
            QTreeView.keyPressEvent(self.tree, event)
            
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item)
        toolbar_layout.addWidget(add_button)
        
        expand_button = QPushButton("Expand All")
        expand_button.clicked.connect(lambda: self.tree.expandAll())
        toolbar_layout.addWidget(expand_button)
        
        collapse_button = QPushButton("Collapse All")
        collapse_button.clicked.connect(lambda: self.tree.collapseAll())
        toolbar_layout.addWidget(collapse_button)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # Create splitter for tree and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Setup tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Key', 'Value', 'Type'])
        self.model.itemChanged.connect(self.on_item_changed)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setSelectionMode(QTreeView.ExtendedSelection)
        self.tree.setEditTriggers(QTreeView.DoubleClicked | QTreeView.EditKeyPressed | QTreeView.SelectedClicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        self.tree.setAlternatingRowColors(True)
        
        # Set custom delegate for better editing
        self.delegate = JsonItemDelegate()
        self.tree.setItemDelegate(self.delegate)
        
        # Install key press event handler for delete key
        self.tree.keyPressEvent = self.handle_key_press
        
        # Make tree columns resizable
        header = self.tree.header()
        header.setStretchLastSection(False)  # Changed from True to False
        # header.setMinimumSectionSize(200)
        header.setDefaultSectionSize(150)  # Ensures default width for all columns

        header.setSectionResizeMode(0, header.Interactive)
        header.setSectionResizeMode(1, header.Interactive)
        header.setSectionResizeMode(2, header.Interactive)

        header.resizeSection(0, 200)  # explicitly set Key column
        header.resizeSection(1, 100)  # value
        header.resizeSection(2, 100)  # type
        
        # Create JSON preview
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Consolas", 10))
        
        # Add widgets to splitter
        splitter.addWidget(self.tree)
        splitter.addWidget(self.json_preview)
        splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter, 1)  # 1 = stretch factor
        
        # Install event filters for zoom support
        self.tree.viewport().installEventFilter(self)
        self.json_preview.viewport().installEventFilter(self)
    
    def eventFilter(self, source, event):
        """Handle zoom in/out with Ctrl+Scroll"""
        if event.type() == event.Wheel and event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                # Zoom in
                self.zoom_view(1.1)
            else:
                # Zoom out
                self.zoom_view(0.9)
            return True
        return super().eventFilter(source, event)
    
    def zoom_view(self, factor):
        """Zoom the view content rather than just the font"""
        self.font_scale *= factor
        
        # Update tree view - scale the indentation, row height, and column widths
        self.tree.setIndentation(int(self.tree.indentation() * factor))
        header = self.tree.header()
        for i in range(header.count()):
            width = header.sectionSize(i)
            header.resizeSection(i, int(width * factor))
        
        # Update font in the tree view and preview
        new_font_size = int(self.base_font_size * self.font_scale)
        
        # Update tree view font
        tree_font = self.tree.font()
        tree_font.setPointSize(new_font_size)
        self.tree.setFont(tree_font)
        
        # Update JSON preview font
        preview_font = self.json_preview.font()
        preview_font.setPointSize(new_font_size)
        self.json_preview.setFont(preview_font)
        
        # Adjust the row height in the tree view to match the font size
        self.tree.setStyleSheet(f"QTreeView::item {{ height: {max(20, int(20 * self.font_scale))}px; }}")
    
    def set_json(self, json_data):
        """Set the JSON data to display in the editor"""
        self.json_data = json_data
        self.is_modified = False
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Key', 'Value', 'Type'])
        self.load_json(self.json_data, self.model.invisibleRootItem())
        self.update_preview()
    
    def get_json(self):
        """Get the current JSON data from the editor"""
        return self.model_to_dict(self.model.invisibleRootItem())
    
    def load_json(self, data, parent):
        if isinstance(data, dict):
            for key, value in data.items():
                item = QStandardItem(str(key))
                value_item = QStandardItem(str(value) if not isinstance(value, (dict, list)) else '')
                type_item = QStandardItem(self.get_type_string(value))
                
                # Make items editable
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                value_item.setFlags(value_item.flags() | Qt.ItemIsEditable)
                
                parent.appendRow([item, value_item, type_item])
                if isinstance(value, (dict, list)):
                    self.load_json(value, item)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                item = QStandardItem(f'[{index}]')
                value_item = QStandardItem(str(value) if not isinstance(value, (dict, list)) else '')
                type_item = QStandardItem(self.get_type_string(value))
                
                # Make items editable
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                value_item.setFlags(value_item.flags() | Qt.ItemIsEditable)
                
                parent.appendRow([item, value_item, type_item])
                if isinstance(value, (dict, list)):
                    self.load_json(value, item)
    
    def get_type_string(self, value):
        if isinstance(value, bool):
            return 'Boolean'
        elif isinstance(value, int):
            return 'Integer'
        elif isinstance(value, float):
            return 'Float'
        elif isinstance(value, str):
            return 'String'
        elif isinstance(value, dict):
            return 'Object'
        elif isinstance(value, list):
            return 'Array'
        elif value is None:
            return 'Null'
        return 'Unknown'
    
    def model_to_dict(self, parent):
        if parent.rowCount() == 0:
            return {}
        
        # Check if this looks like an array (all keys are numeric indices)
        keys = []
        for row in range(parent.rowCount()):
            key_item = parent.child(row, 0)
            key = key_item.text()
            if key.startswith('[') and key.endswith(']'):
                try:
                    keys.append(int(key[1:-1]))
                except ValueError:
                    keys = None
                    break
            else:
                keys = None
                break
        
        if keys is not None:
            # This is an array
            result = [None] * len(keys)
            for row in range(parent.rowCount()):
                key_item = parent.child(row, 0)
                value_item = parent.child(row, 1)
                index = int(key_item.text()[1:-1])
                if key_item.hasChildren():
                    result[index] = self.model_to_dict(key_item)
                else:
                    result[index] = self.parse_value(value_item.text())
            return result
        else:
            # This is an object
            result = {}
            for row in range(parent.rowCount()):
                key_item = parent.child(row, 0)
                value_item = parent.child(row, 1)
                if key_item.hasChildren():
                    result[key_item.text()] = self.model_to_dict(key_item)
                else:
                    result[key_item.text()] = self.parse_value(value_item.text())
            return result
    
    def parse_value(self, text):
        if text.lower() == 'true':
            return True
        elif text.lower() == 'false':
            return False
        elif text.lower() == 'null':
            return ""
        # Empty string handling - explicitly return empty string
        elif text == '':
            return ""
        try:
            if '.' in text:
                return float(text)
            elif text and text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
                return int(text)
            return text  # Return as string for everything else
        except ValueError:
            return text
    
    def add_item(self):
        dialog = AddEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            key, value = dialog.get_values()
            if key:
                # Get selected parent or root
                indexes = self.tree.selectedIndexes()
                if indexes:
                    parent_item = self.model.itemFromIndex(indexes[0])
                    if not parent_item.hasChildren():
                        parent_item = parent_item.parent() or self.model.invisibleRootItem()
                else:
                    parent_item = self.model.invisibleRootItem()
                
                # Add new item
                key_item = QStandardItem(str(key))
                value_item = QStandardItem(str(value) if not isinstance(value, (dict, list)) else '')
                type_item = QStandardItem(self.get_type_string(value))
                
                # Make items editable
                key_item.setFlags(key_item.flags() | Qt.ItemIsEditable)
                value_item.setFlags(value_item.flags() | Qt.ItemIsEditable)
                
                parent_item.appendRow([key_item, value_item, type_item])
                
                if isinstance(value, (dict, list)):
                    self.load_json(value, key_item)
                
                self.is_modified = True
                self.update_preview()
                self.jsonChanged.emit(self.get_json())
    
    def edit_current_item(self):
        """Start editing the currently selected item"""
        indexes = self.tree.selectedIndexes()
        if indexes:
            # Edit the first selected item
            self.tree.edit(indexes[0])
    
    def delete_selected_items(self):
        """Delete all selected items"""
        indexes = self.tree.selectedIndexes()
        if not indexes:
            return
        
        # Get unique rows to delete
        rows_to_delete = {}
        for index in indexes:
            parent = index.parent()
            # Use the parent's row as a key rather than the pointer
            parent_key = parent.row() if parent.isValid() else -1
            if parent_key not in rows_to_delete:
                rows_to_delete[parent_key] = []
            rows_to_delete[parent_key].append(index.row())
        
        # Count total items for confirmation
        total_items = sum(len(set(rows)) for rows in rows_to_delete.values())
        
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            f'Are you sure you want to delete {total_items} selected item(s)?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete rows in reverse order to prevent index shifting
            for parent_key, rows in rows_to_delete.items():
                parent_index = None
                for index in indexes:
                    # Match the parent by row
                    current_parent = index.parent()
                    current_parent_key = current_parent.row() if current_parent.isValid() else -1
                    if current_parent_key == parent_key:
                        parent_index = index.parent()
                        break
                
                for row in sorted(set(rows), reverse=True):
                    self.model.removeRow(row, parent_index)
            
            self.is_modified = True
            self.update_preview()
            self.jsonChanged.emit(self.get_json())
    
    def open_context_menu(self, position):
        indexes = self.tree.selectedIndexes()
        menu = QMenu()
        
        add_action = menu.addAction("Add Item")
        add_action.triggered.connect(self.add_item)
        
        if indexes:
            edit_action = menu.addAction("Edit Item")
            edit_action.triggered.connect(self.edit_current_item)
            
            delete_action = menu.addAction("Delete Selected")
            delete_action.triggered.connect(self.delete_selected_items)
            
            menu.addSeparator()
            expand_action = menu.addAction("Expand")
            expand_action.triggered.connect(lambda: self.tree.expand(indexes[0]))
            
            collapse_action = menu.addAction("Collapse")
            collapse_action.triggered.connect(lambda: self.tree.collapse(indexes[0]))
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def on_item_changed(self, item):
        """Handle item changes and update type column"""
        self.is_modified = True
        
        # Update type column if value column was changed
        if item.column() == 1:  # Value column
            row = item.row()
            parent = item.parent()
            type_item = parent.child(row, 2) if parent else self.model.item(row, 2)
            if type_item:
                parsed_value = self.parse_value(item.text())
                type_item.setText(self.get_type_string(parsed_value))
        
        self.update_preview()
        self.jsonChanged.emit(self.get_json())
    
    def update_preview(self):
        """Update the JSON preview pane"""
        try:
            data = self.model_to_dict(self.model.invisibleRootItem())
            json_text = json.dumps(data, indent=2, ensure_ascii=False)
            self.json_preview.setPlainText(json_text)
        except Exception as e:
            self.json_preview.setPlainText(f"Error generating preview: {str(e)}")

class JsonEditor(QMainWindow):
    """Standalone JSON editor application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JSON Editor')
        self.setGeometry(200, 100, 1200, 800)
        
        self.current_file = None
        
        # Create central JSON editor widget
        self.editor_widget = JsonEditorWidget()
        self.editor_widget.jsonChanged.connect(self.on_json_changed)
        self.setCentralWidget(self.editor_widget)
        
        # Create menu and toolbar
        self.create_menu()
        self.create_toolbar()
        self.create_status_bar()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def create_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')
    
    def on_json_changed(self, json_data):
        self.update_title(True)
    
    def update_title(self, modified=False):
        title = 'JSON Editor'
        if self.current_file:
            title += f' - {self.current_file}'
        if modified:
            title += ' *'
        self.setWindowTitle(title)
    
    def new_file(self):
        if self.check_save_changes():
            self.editor_widget.set_json({})
            self.current_file = None
            self.update_title()
            self.status_bar.showMessage('New file created')
    
    def open_file(self):
        if not self.check_save_changes():
            return
            
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open JSON File', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    self.editor_widget.set_json(json_data)
                    self.current_file = path
                    self.update_title()
                    self.status_bar.showMessage(f'Opened: {path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to open file:\n{str(e)}')
    
    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save JSON File', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        if path:
            if not path.endswith('.json'):
                path += '.json'
            self.save_to_file(path)
    
    def save_to_file(self, path):
        try:
            data = self.editor_widget.get_json()
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            self.current_file = path
            self.update_title(False)  # Not modified after save
            self.status_bar.showMessage(f'Saved: {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save file:\n{str(e)}')
    
    def check_save_changes(self):
        if self.editor_widget.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                'You have unsaved changes. Do you want to save them?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.editor_widget.is_modified  # Return False if save failed
            elif reply == QMessageBox.Cancel:
                return False
        return True
    
    def closeEvent(self, event):
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.json'):
                if self.check_save_changes():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            json_data = json.load(file)
                            self.editor_widget.set_json(json_data)
                            self.current_file = file_path
                            self.update_title()
                            self.status_bar.showMessage(f'Opened: {file_path}')
                    except Exception as e:
                        QMessageBox.critical(self, 'Error', f'Failed to open file:\n{str(e)}')
                break

# Only run the standalone app if directly executed
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = JsonEditor()
    editor.show()
    sys.exit(app.exec_())