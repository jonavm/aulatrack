from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QTableView, QVBoxLayout, QWidget


class TablePreviewDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        source_table: QTableView,
        subtitle: str = "",
        delegate=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1360, 860)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("Caption")
        subtitle_label.setWordWrap(True)

        self.table = source_table.__class__()
        self.table.setModel(source_table.model())
        if delegate is not None:
            self.table.setItemDelegate(delegate)
        self.table.setSelectionBehavior(source_table.selectionBehavior())
        self.table.setSelectionMode(source_table.selectionMode())
        self.table.setAlternatingRowColors(source_table.alternatingRowColors())
        self.table.setShowGrid(source_table.showGrid())
        self.table.setSortingEnabled(source_table.isSortingEnabled())
        self.table.verticalHeader().setVisible(source_table.verticalHeader().isVisible())
        self.table.horizontalHeader().setStretchLastSection(
            source_table.horizontalHeader().stretchLastSection()
        )

        layout.addWidget(title_label)
        if subtitle:
            layout.addWidget(subtitle_label)
        layout.addWidget(self.table, 1)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        self.table.resizeColumnsToContents()
