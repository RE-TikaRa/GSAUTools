import os
from typing import List, Dict, Tuple, Sequence
from bs4 import BeautifulSoup, Tag
from docx import Document

# 定义输出目录
OUTPUT_DIR = os.path.join(os.getcwd(), 'OutPut')
TEXT_DIR = os.path.join(OUTPUT_DIR, 'Text')
WORD_DIR = os.path.join(OUTPUT_DIR, 'Word')

# 确保目录存在
def ensure_directories():
    os.makedirs(TEXT_DIR, exist_ok=True)
    os.makedirs(WORD_DIR, exist_ok=True)

ensure_directories()

def find_html_files(input_dir):
    file_paths = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.html'):
                file_paths.append(os.path.join(root, file))
    return file_paths

def process_html_files(file_paths: list[str], log_func=None, progress_func=None):
    """Process HTML files and extract questions.
    Returns (questions_list, unprocessed_files)
    """
    questions = []
    unprocessed_files = []

    total_files = len(file_paths)
    for idx, file_path in enumerate(file_paths):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')

            question_blocks = soup.find_all('div', class_='answerCon')

            for block in question_blocks:
                if not isinstance(block, Tag):
                    continue

                title_div = block.find('i', class_='qtContent')
                if not isinstance(title_div, Tag):
                    continue
                question_text = title_div.text.strip()

                options = []
                option_divs = block.find_all('div', class_='optionCon')
                for opt in option_divs:
                    if isinstance(opt, Tag):
                        options.append(opt.text.strip().replace(' ', ''))

                answer_div = block.find('div', class_='answerInfo')
                answer = '未知'
                if isinstance(answer_div, Tag):
                    answer_p = answer_div.find('p')
                    if isinstance(answer_p, Tag):
                        answer = answer_p.text.strip()

                questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': answer
                })

            if not question_blocks:
                unprocessed_files.append(file_path)
                if log_func:
                    log_func(f"未找到题目: {file_path}\n")

        except Exception as e:
            unprocessed_files.append(file_path)
            if log_func:
                log_func(f"处理失败 {file_path}: {str(e)}\n")
        # update progress after each file (if callback provided)
        try:
            if progress_func:
                progress_func(idx + 1, total_files)
        except Exception:
            pass

    return questions, unprocessed_files

def save_results(questions, output_path):
    # 将输出路径调整到 OutPut/Text
    output_path = os.path.join(TEXT_DIR, os.path.basename(output_path))
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, q in enumerate(questions, 1):
            f.write(f"第{i}题: {q['question']}\n")
            f.write("选项:\n")
            for opt in q['options']:
                f.write(f"  {opt}\n")
            f.write(f"答案: {q['answer']}\n\n")

def convert_txt_to_word(txt_path, word_path):
    # 将输出路径调整到 OutPut/Word
    word_path = os.path.join(WORD_DIR, os.path.basename(word_path))
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    doc = Document()
    doc.add_paragraph(content)
    doc.save(word_path)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('output', help='output txt path')
    args = parser.parse_args()
    files = find_html_files(args.input_dir)
    qs, un = process_html_files(files, print)
    save_results(qs, args.output)
    print('done', len(qs), 'questions')
