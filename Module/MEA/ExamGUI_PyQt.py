import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QTextEdit, QProgressBar, QStackedWidget, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from Module.MEA.exam_core import find_html_files, process_html_files, save_results
from docx import Document


class Worker(QObject):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished = pyqtSignal(list, list)

    def __init__(self, input_dir, output_path):
        super().__init__()
        self.input_dir = input_dir
        self.output_path = output_path

    def run(self):
        files = find_html_files(self.input_dir)
        total = len(files)
        self.log.emit(f'检测到 {total} 个 HTML 文件')

        def progress_cb(done, total):
            self.progress.emit(done, total)

        def log_cb(s):
            # ensure newline
            self.log.emit(str(s))

        questions, unprocessed = process_html_files(files, log_func=log_cb, progress_func=progress_cb)
        save_results(questions, self.output_path)
        self.finished.emit(questions, unprocessed)


class ExamGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Exam Analyzer')
        self.resize(900, 700)
        self.input_dir = os.getcwd()
        self.output_path = os.path.join(self.input_dir, 'exam_analysis.txt')
        self.thread: QThread | None = None  # 明确类型注解
        self.worker = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        title = QLabel('MOOC 考试解析')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 调整标题的字号和颜色
        title.setStyleSheet("font-size: 24px; color: #6C6F7D;")  # 莫兰迪色系的灰蓝色
        layout.addWidget(title)

        # input row
        row = QHBoxLayout()
        self.input_label = QLabel(self.input_dir)
        btn_browse = QPushButton('选择输入文件夹')
        btn_browse.clicked.connect(self.browse_input)
        row.addWidget(self.input_label)
        row.addWidget(btn_browse)
        layout.addLayout(row)

        # output row
        row2 = QHBoxLayout()
        self.output_label = QLabel(self.output_path)
        btn_out = QPushButton('选择输出文件')
        btn_out.clicked.connect(self.browse_output)
        row2.addWidget(self.output_label)
        row2.addWidget(btn_out)
        layout.addLayout(row2)

        # TXT -> Word 转换行
        row_txt = QHBoxLayout()
        self.txt_label = QLabel('未选择TXT文件')
        btn_txt = QPushButton('选择TXT文件')
        btn_txt.clicked.connect(self.browse_txt)
        btn_word_out = QPushButton('选择输出Word')
        btn_word_out.clicked.connect(self.browse_word_for_docx)
        btn_convert = QPushButton('TXT转Word')
        btn_convert.clicked.connect(self.convert_txt_to_word)
        row_txt.addWidget(self.txt_label)
        row_txt.addWidget(btn_txt)
        row_txt.addWidget(btn_word_out)
        row_txt.addWidget(btn_convert)
        layout.addLayout(row_txt)

        # action buttons
        row3 = QHBoxLayout()
        self.btn_run = QPushButton('开始解析')
        self.btn_run.clicked.connect(self.start_worker)
        row3.addWidget(self.btn_run)
        layout.addLayout(row3)

        # log and progress
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # 设置整体窗口的背景颜色为莫兰迪色系
        self.setStyleSheet("background-color: #EAEAEA;")  # 莫兰迪浅灰色

    def browse_input(self):
        d = QFileDialog.getExistingDirectory(self, '选择输入文件夹', self.input_dir)
        if d:
            self.input_dir = d
            self.input_label.setText(d)

    def browse_output(self):
        f, _ = QFileDialog.getSaveFileName(self, '选择输出文件', self.output_path, 'Text Files (*.txt)')
        if f:
            self.output_path = f
            self.output_label.setText(f)

    def browse_txt(self):
        f, _ = QFileDialog.getOpenFileName(self, '选择TXT文件', self.input_dir, 'Text Files (*.txt)')
        if f:
            self.txt_path = f
            self.txt_label.setText(f)

    def browse_word_for_docx(self):
        f, _ = QFileDialog.getSaveFileName(self, '选择输出Word文件', os.path.splitext(self.input_dir)[0] + '.docx', 'Word Documents (*.docx)')
        if f:
            self.word_output_path = f
            # 也更新 output_label 以便用户看到上次选择（可选）
            self.output_label.setText(self.output_path)

    def convert_txt_to_word(self):
        # 优先使用已选择路径
        txt = getattr(self, 'txt_path', None)
        word = getattr(self, 'word_output_path', None)

        if not txt:
            # 提示选择
            f, _ = QFileDialog.getOpenFileName(self, '选择TXT文件', self.input_dir, 'Text Files (*.txt)')
            if not f:
                self.log.append('未选择TXT文件，取消转换')
                return
            txt = f
            self.txt_label.setText(txt)

        if not word:
            # 自动生成同名docx
            word = os.path.splitext(txt)[0] + '.docx'

        try:
            with open(txt, 'r', encoding='utf-8') as rf:
                content = rf.read()

            doc = Document()
            doc.add_paragraph(content)
            doc.save(word)

            self.log.append(f'TXT转换成功: {txt} -> {word}')
        except Exception as e:
            self.log.append(f'TXT转换失败: {e}')

    def start_worker(self):
        # disable button to prevent double start
        self.btn_run.setEnabled(False)
        self.log.clear()

        self.thread = QThread()  # 创建 QThread 实例
        self.worker = Worker(self.input_dir, self.output_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.on_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_progress(self, done, total):
        self.progress.setMaximum(total if total>0 else 1)
        self.progress.setValue(done)

    def on_log(self, s):
        self.log.append(s)

    def on_finished(self, questions, unprocessed):
        self.log.append(f'解析完成: 共 {len(questions)} 道题, 未处理 {len(unprocessed)} 个文件')
        self.btn_run.setEnabled(True)

    def change_page(self, current, previous):
        # 删除语言设置和其他页面的引用
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ExamGUI()
    win.show()
    sys.exit(app.exec())
