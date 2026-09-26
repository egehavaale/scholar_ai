"""
Desktop GUI Application for SmartDoc Summarizer & Entity Extractor.
Built with PySide6, implementing a dark corporate analytics design.
"""

from __future__ import annotations

import os

# Prevent OpenMP runtime conflict on Windows platforms
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import sys
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from database import Document, db_manager
from nlp_engine import DocumentReader, nlp_engine


DARK_THEME_QSS = """
QMainWindow {
    background-color: #0e1117;
}

QWidget {
    background-color: #0e1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Panels and Containers */
QFrame#sidebarFrame {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

QFrame#mainContentFrame {
    background-color: #0e1117;
}

QFrame#cardFrame {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
}

/* Headers and Labels */
QLabel#sectionHeader {
    font-size: 14px;
    font-weight: 600;
    color: #f0f6fc;
    padding-bottom: 4px;
}

QLabel#mutedLabel {
    color: #8b949e;
    font-size: 12px;
}

QLabel#statusLabel {
    color: #58a6ff;
    font-size: 12px;
    font-weight: 500;
}

/* Text Inputs */
QLineEdit, QPlainTextEdit, QTextBrowser {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 8px;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}

QLineEdit:focus, QPlainTextEdit:focus, QTextBrowser:focus {
    border: 1px solid #58a6ff;
}

QLineEdit {
    padding: 6px 10px;
}

/* Buttons */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

QPushButton#primaryButton {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #2ea043;
}

QPushButton#primaryButton:pressed {
    background-color: #1e7e34;
}

QPushButton#dangerButton {
    background-color: #21262d;
    color: #f85149;
    border: 1px solid #30363d;
}

QPushButton#dangerButton:hover {
    background-color: #da3633;
    color: #ffffff;
    border-color: #f85149;
}

/* Sidebar List */
QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 4px;
}

QListWidget::item {
    background-color: transparent;
    padding: 8px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
    border: 1px solid transparent;
}

QListWidget::item:hover {
    background-color: #161b22;
    border: 1px solid #30363d;
}

QListWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #30363d;
    background-color: #161b22;
    border-radius: 4px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0d1117;
    color: #8b949e;
    border: 1px solid #30363d;
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #161b22;
    color: #f0f6fc;
    border-bottom: 1px solid #161b22;
}

QTabBar::tab:hover:!selected {
    background-color: #1a1f27;
    color: #c9d1d9;
}

/* Table Widget */
QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 4px;
    gridline-color: #21262d;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 6px;
    border: 1px solid #30363d;
    font-weight: 600;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
    text-align: center;
    color: #c9d1d9;
    font-size: 11px;
    height: 14px;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 3px;
}

/* Splitter */
QSplitter::handle {
    background-color: #30363d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


class AnalysisWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str, int)

    def __init__(self, raw_text: str, filename: str) -> None:
        super().__init__()
        self.raw_text = raw_text
        self.filename = filename

    def run(self) -> None:
        try:
            result = nlp_engine.analyze_document(
                self.raw_text,
                self.filename,
                progress_callback=self.emit_progress
            )
            doc = db_manager.save_document(
                filename=result["filename"],
                raw_text=result["raw_text"],
                summary=result["summary"],
                keywords_data={
                    "keywords": result["keywords"],
                    "entities": result["entities"],
                    "metrics": result["metrics"],
                },
                status="COMPLETED",
            )
            result["db_id"] = doc.id
            result["created_at"] = doc.created_at.strftime("%Y-%m-%d %H:%M:%S")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def emit_progress(self, message: str, percent: int) -> None:
        self.progress.emit(message, percent)


class SmartDocApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SmartDoc Summarizer & Entity Extractor")
        self.resize(1240, 820)
        self.setMinimumSize(960, 640)

        self.current_filename = "Manual_Input.txt"
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[AnalysisWorker] = None

        self._setup_ui()
        self._load_archive_history()

    def _setup_ui(self) -> None:
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_splitter = QSplitter(Qt.Horizontal)

        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebarFrame")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(10)

        sidebar_title = QLabel("DOCUMENT ARCHIVE")
        sidebar_title.setObjectName("sectionHeader")
        sidebar_layout.addWidget(sidebar_title)

        self.archive_search = QLineEdit()
        self.archive_search.setPlaceholderText("Search archive...")
        self.archive_search.textChanged.connect(self._filter_archive)
        sidebar_layout.addWidget(self.archive_search)

        self.archive_list = QListWidget()
        self.archive_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.archive_list.itemClicked.connect(self._on_archive_item_selected)
        sidebar_layout.addWidget(self.archive_list)

        archive_btn_layout = QHBoxLayout()
        self.btn_refresh_archive = QPushButton("Refresh")
        self.btn_refresh_archive.clicked.connect(self._load_archive_history)
        self.btn_delete_doc = QPushButton("Delete")
        self.btn_delete_doc.setObjectName("dangerButton")
        self.btn_delete_doc.clicked.connect(self._delete_selected_doc)
        archive_btn_layout.addWidget(self.btn_refresh_archive)
        archive_btn_layout.addWidget(self.btn_delete_doc)
        sidebar_layout.addLayout(archive_btn_layout)

        content_frame = QFrame()
        content_frame.setObjectName("mainContentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)

        self.btn_load_file = QPushButton("Import Document (.txt, .pdf, .docx)")
        self.btn_load_file.clicked.connect(self._open_file_dialog)
        toolbar_layout.addWidget(self.btn_load_file)

        self.btn_clear_input = QPushButton("Clear")
        self.btn_clear_input.clicked.connect(self._clear_editor)
        toolbar_layout.addWidget(self.btn_clear_input)

        toolbar_layout.addStretch()

        self.btn_analyze = QPushButton("Execute Analysis")
        self.btn_analyze.setObjectName("primaryButton")
        self.btn_analyze.setMinimumWidth(160)
        self.btn_analyze.clicked.connect(self._start_analysis)
        toolbar_layout.addWidget(self.btn_analyze)

        content_layout.addLayout(toolbar_layout)

        v_splitter = QSplitter(Qt.Vertical)

        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        input_header_layout = QHBoxLayout()
        self.lbl_editor_title = QLabel("Source Document Input")
        self.lbl_editor_title.setObjectName("sectionHeader")
        input_header_layout.addWidget(self.lbl_editor_title)

        input_header_layout.addStretch()

        self.lbl_doc_stats = QLabel("Words: 0 | Characters: 0")
        self.lbl_doc_stats.setObjectName("mutedLabel")
        input_header_layout.addWidget(self.lbl_doc_stats)
        input_layout.addLayout(input_header_layout)

        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlaceholderText("Paste raw document text here or import a file...")
        self.text_editor.textChanged.connect(self._update_text_counters)
        input_layout.addWidget(self.text_editor)

        v_splitter.addWidget(input_container)

        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 4, 0, 4)
        progress_layout.setSpacing(4)

        prog_info_layout = QHBoxLayout()
        self.lbl_status = QLabel("System Ready")
        self.lbl_status.setObjectName("statusLabel")
        prog_info_layout.addWidget(self.lbl_status)
        prog_info_layout.addStretch()

        progress_layout.addLayout(prog_info_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        content_layout.addWidget(self.progress_container)

        self.output_tabs = QTabWidget()

        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(8)

        summary_actions_layout = QHBoxLayout()
        lbl_sum_title = QLabel("Synthesized Summary")
        lbl_sum_title.setObjectName("sectionHeader")
        summary_actions_layout.addWidget(lbl_sum_title)
        summary_actions_layout.addStretch()

        self.btn_copy_summary = QPushButton("Copy Summary")
        self.btn_copy_summary.clicked.connect(self._copy_summary_to_clipboard)
        summary_actions_layout.addWidget(self.btn_copy_summary)
        summary_layout.addLayout(summary_actions_layout)

        self.txt_summary = QTextBrowser()
        self.txt_summary.setReadOnly(True)
        summary_layout.addWidget(self.txt_summary)
        self.output_tabs.addTab(summary_tab, "Executive Summary")

        entities_tab = QWidget()
        entities_layout = QVBoxLayout(entities_tab)
        entities_layout.setContentsMargins(12, 12, 12, 12)
        entities_layout.setSpacing(8)

        self.table_entities = QTableWidget()
        self.table_entities.setColumnCount(3)
        self.table_entities.setHorizontalHeaderLabels(["Category", "Detected Item", "Context / Score"])
        self.table_entities.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_entities.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_entities.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_entities.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_entities.setEditTriggers(QAbstractItemView.NoEditTriggers)
        entities_layout.addWidget(self.table_entities)
        self.output_tabs.addTab(entities_tab, "Keywords & Entities")

        meta_tab = QWidget()
        meta_layout = QVBoxLayout(meta_tab)
        meta_layout.setContentsMargins(12, 12, 12, 12)
        meta_layout.setSpacing(8)

        self.txt_json_view = QTextBrowser()
        self.txt_json_view.setReadOnly(True)
        self.txt_json_view.setFont(QFont("Courier New", 10))
        meta_layout.addWidget(self.txt_json_view)
        self.output_tabs.addTab(meta_tab, "Raw Analytics JSON")

        v_splitter.addWidget(self.output_tabs)
        v_splitter.setStretchFactor(0, 4)
        v_splitter.setStretchFactor(1, 5)

        content_layout.addWidget(v_splitter)

        main_splitter.addWidget(sidebar_frame)
        main_splitter.addWidget(content_frame)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 7)

        main_layout.addWidget(main_splitter)

    def _update_text_counters(self) -> None:
        text = self.text_editor.toPlainText()
        word_count = len(text.split())
        char_count = len(text)
        self.lbl_doc_stats.setText(f"Words: {word_count:,} | Characters: {char_count:,}")

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.txt *.pdf *.docx);;Text Files (*.txt);;PDF Files (*.pdf);;Word Documents (*.docx)"
        )
        if not file_path:
            return

        try:
            content = DocumentReader.read_file(file_path)
            self.text_editor.setPlainText(content)
            self.current_filename = os.path.basename(file_path)
            self.lbl_editor_title.setText(f"Source: {self.current_filename}")
            self.lbl_status.setText(f"Loaded {self.current_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file:\n{str(e)}")

    def _clear_editor(self) -> None:
        self.text_editor.clear()
        self.txt_summary.clear()
        self.table_entities.setRowCount(0)
        self.txt_json_view.clear()
        self.current_filename = "Manual_Input.txt"
        self.lbl_editor_title.setText("Source Document Input")
        self.progress_bar.setValue(0)
        self.lbl_status.setText("System Ready")

    def _start_analysis(self) -> None:
        text = self.text_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Validation Warning", "Input text area is empty. Please enter or import text.")
            return

        self.btn_analyze.setEnabled(False)
        self.btn_load_file.setEnabled(False)
        self.btn_clear_input.setEnabled(False)
        self.progress_bar.setValue(5)
        self.lbl_status.setText("Initializing NLP Pipeline...")

        self.worker_thread = QThread()
        self.worker = AnalysisWorker(text, self.current_filename)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_analysis_progress)
        self.worker.finished.connect(self._on_analysis_finished)
        self.worker.error.connect(self._on_analysis_error)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def _on_analysis_progress(self, message: str, percent: int) -> None:
        self.lbl_status.setText(message)
        self.progress_bar.setValue(percent)

    def _on_analysis_finished(self, result: Dict[str, Any]) -> None:
        self.btn_analyze.setEnabled(True)
        self.btn_load_file.setEnabled(True)
        self.btn_clear_input.setEnabled(True)

        self.progress_bar.setValue(100)
        self.lbl_status.setText("Analysis completed successfully.")

        self._render_results(result)
        self._load_archive_history()

    def _on_analysis_error(self, err_msg: str) -> None:
        self.btn_analyze.setEnabled(True)
        self.btn_load_file.setEnabled(True)
        self.btn_clear_input.setEnabled(True)

        self.progress_bar.setValue(0)
        self.lbl_status.setText("Analysis failed.")
        QMessageBox.critical(self, "Analysis Failure", f"An error occurred during analysis:\n{err_msg}")

    def _render_results(self, result: Dict[str, Any]) -> None:
        summary_text = result.get("summary", "")
        self.txt_summary.setPlainText(summary_text)

        self.table_entities.setRowCount(0)

        keywords = result.get("keywords", [])
        entities = result.get("entities", {})

        row = 0
        for kw in keywords:
            self.table_entities.insertRow(row)
            self.table_entities.setItem(row, 0, QTableWidgetItem(f"Keyword ({kw.get('type', 'Term')})"))
            self.table_entities.setItem(row, 1, QTableWidgetItem(str(kw.get("term", ""))))
            self.table_entities.setItem(row, 2, QTableWidgetItem(f"Freq: {kw.get('frequency', 1)} | Score: {kw.get('score', 0)}"))
            row += 1

        category_labels = {
            "acronyms": "Acronym / Org",
            "citations": "Citation Reference",
            "dates": "Date",
            "emails": "Email Address",
            "urls": "URL / DOI",
            "metrics": "Quantitative Value",
        }

        for cat_key, items in entities.items():
            label = category_labels.get(cat_key, cat_key.capitalize())
            for item in items:
                self.table_entities.insertRow(row)
                self.table_entities.setItem(row, 0, QTableWidgetItem(label))
                self.table_entities.setItem(row, 1, QTableWidgetItem(str(item)))
                self.table_entities.setItem(row, 2, QTableWidgetItem("Matched Pattern"))
                row += 1

        json_output = {
            "filename": result.get("filename"),
            "metrics": result.get("metrics"),
            "summary": summary_text,
            "keywords": keywords,
            "entities": entities,
        }
        self.txt_json_view.setPlainText(json.dumps(json_output, indent=2, ensure_ascii=False))

    def _load_archive_history(self) -> None:
        self.archive_list.clear()
        documents = db_manager.get_all_documents()
        for doc in documents:
            item = QListWidgetItem()
            display_title = f"{doc.filename}\n{doc.created_at.strftime('%Y-%m-%d %H:%M')}"
            item.setText(display_title)
            item.setData(Qt.UserRole, doc.id)
            self.archive_list.addItem(item)

    def _filter_archive(self, query: str) -> None:
        query = query.lower().strip()
        for i in range(self.archive_list.count()):
            item = self.archive_list.item(i)
            match = query in item.text().lower()
            item.setHidden(not match)

    def _on_archive_item_selected(self, item: QListWidgetItem) -> None:
        doc_id = item.data(Qt.UserRole)
        doc = db_manager.get_document_by_id(doc_id)
        if not doc:
            return

        self.text_editor.setPlainText(doc.raw_text)
        self.current_filename = doc.filename
        self.lbl_editor_title.setText(f"Archived: {doc.filename}")

        keywords_data = json.loads(doc.keywords_json) if doc.keywords_json else {}

        render_payload = {
            "filename": doc.filename,
            "raw_text": doc.raw_text,
            "summary": doc.summary or "",
            "keywords": keywords_data.get("keywords", []),
            "entities": keywords_data.get("entities", {}),
            "metrics": keywords_data.get("metrics", {
                "word_count": len(doc.raw_text.split()),
                "char_count": len(doc.raw_text),
                "reading_time_minutes": max(1, round(len(doc.raw_text.split()) / 200, 1))
            })
        }
        self._render_results(render_payload)
        self.lbl_status.setText(f"Loaded archive ID #{doc.id}")

    def _delete_selected_doc(self) -> None:
        current_item = self.archive_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Selection", "Select a document from the archive list to delete.")
            return

        doc_id = current_item.data(Qt.UserRole)
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete document #{doc_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db_manager.delete_document_by_id(doc_id)
            self._load_archive_history()
            self._clear_editor()

    def _copy_summary_to_clipboard(self) -> None:
        summary_text = self.txt_summary.toPlainText().strip()
        if summary_text:
            QApplication.clipboard().setText(summary_text)
            self.lbl_status.setText("Summary copied to clipboard.")


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)

    window = SmartDocApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
