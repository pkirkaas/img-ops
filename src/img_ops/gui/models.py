"""
GUI-specific data models.

This module can define data models tailored for use with
PySide6's Model/View framework (e.g., QAbstractListModel,
QAbstractTableModel) or other data structures specifically
needed by the GUI layer that are distinct from core models.
"""
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from typing import List, Any

# Example: A simple list model for displaying a list of strings


class SimpleStringListModel(QAbstractListModel):
    """
    A basic list model for displaying a list of strings.
    """

    def __init__(self, data: List[str] = None, parent=None):
        super().__init__(parent)
        self._data = data or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """ Returns the number of rows in the model. """
        if parent.isValid():
            return 0
        return len(self._data)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """ Returns the data stored under the given role for the item referred to by the index. """
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]
        return None

    def setDataList(self, data: List[str]):
        """
        Resets the model with new data.
        """
        self.beginResetModel()
        self._data = data or []
        self.endResetModel()

    def appendString(self, string_item: str):
        """
        Appends a string to the model.
        """
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(string_item)
        self.endInsertRows()

# Add other GUI-specific models as needed.
# For instance, models for tree views, table views, or more complex item views.
