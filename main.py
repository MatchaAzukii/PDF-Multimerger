import os
import math
import re
import tempfile
from functools import partial
from multiprocessing import Pool, cpu_count
from pypdf import PdfReader, PdfWriter, PageObject, Transformation


class PDFMergerProcessor:
    def __init__(self, input_folder, output_file, pages_per_sheet=4):
        self.input_folder = input_folder
        self.output_file = output_file
        self.merger = PdfWriter()
        self.pages_per_sheet = max(1, pages_per_sheet)  # 确保最小值为1

    def _calculate_layout(self, n):
        """计算最优行列布局"""
        if n < 1:
            raise ValueError("pages_per_sheet 必须大于等于1")

        cols = math.ceil(math.sqrt(n))  # 优先接近正方形
        rows = math.ceil(n / cols)
        return cols, rows

    @staticmethod
    def _generate_positions(cols, rows, width, height):
        """
        生成页面布局坐标（从左上到右下）
        """
        cell_width = width / cols
        cell_height = height / rows
        return [
            (col * cell_width, (rows - 1 - row) * cell_height)
            for row in range(rows)
            for col in range(cols)
        ]

    def _get_scale_factor(self, cols, rows):
        """计算缩放比例"""
        return (1.0 / cols, 1.0 / rows)

    def _extract_number_from_filename(self, filename):
        """自然排序提取文件名中的数字"""
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    def process_pdfs(self):
        """主处理函数"""
        try:
            # 获取并排序PDF文件
            all_files = os.listdir(self.input_folder)
            pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
            pdf_files.sort(key=self._extract_number_from_filename)

            self.total_files = len(pdf_files)
            print(f"找到 {self.total_files} 个PDF文件")

            # 并行处理每个文件
            for i, filename in enumerate(pdf_files, 1):
                file_path = os.path.join(self.input_folder, filename)
                print(f"处理文件 {i}/{self.total_files}: {filename}")
                self.process_pdf_file(file_path)

            self.save_merged_pdf()

        except Exception as e:
            print(f"发生致命错误: {str(e)}")
        finally:
            print("程序结束")

    def process_pdf_file(self, file_path):
        """处理单个PDF文件"""
        try:
            reader = PdfReader(file_path)
            if not reader.pages:
                print(f"跳过空文件: {file_path}")
                return

            # 获取页面尺寸和总页数
            first_page = reader.pages[0]
            width = float(first_page.mediabox.width)
            height = float(first_page.mediabox.height)
            total_pages = len(reader.pages)

            # 计算布局参数
            cols, rows = self._calculate_layout(self.pages_per_sheet)
            scale_x, scale_y = self._get_scale_factor(cols, rows)
            positions = self._generate_positions(cols, rows, width, height)

            # 分块处理
            with tempfile.TemporaryDirectory() as temp_dir:
                chunk_size = self.pages_per_sheet
                chunks = [
                    (file_path, start, min(start + chunk_size, total_pages),
                     width, height, temp_dir, cols, rows, scale_x, scale_y)
                    for start in range(0, total_pages, chunk_size)
                ]

                # 多进程处理
                with Pool(processes=min(cpu_count(), len(chunks))) as pool:
                    results = pool.map(partial(self._process_chunk), chunks)

                # 合并结果
                for temp_pdf in results:
                    if temp_pdf:
                        temp_reader = PdfReader(temp_pdf)
                        for page in temp_reader.pages:
                            self.merger.add_page(page)

        except Exception as e:
            print(f"处理文件失败: {file_path} - {str(e)}")

    @staticmethod
    def _process_chunk(args):
        """子进程处理单元（静态方法避免pickle问题）"""
        (file_path, start, end, width, height, temp_dir,
         cols, rows, scale_x, scale_y) = args

        try:
            # 生成布局参数
            positions = PDFMergerProcessor._generate_positions(cols, rows, width, height)

            # 创建空白页面
            new_page = PageObject.create_blank_page(width=width, height=height)

            # 读取源文件
            reader = PdfReader(file_path)
            chunk = reader.pages[start:end]

            # 合并页面
            for idx, page in enumerate(chunk):
                if idx >= len(positions):
                    break
                tx, ty = positions[idx]
                trans = Transformation().scale(scale_x, scale_y).translate(tx, ty)
                new_page.merge_transformed_page(page, trans)

            # 保存临时文件
            temp_pdf_path = os.path.join(temp_dir, f"chunk_{start}_{end}.pdf")
            writer = PdfWriter()
            writer.add_page(new_page)
            with open(temp_pdf_path, "wb") as f:
                writer.write(f)

            return temp_pdf_path

        except Exception as e:
            print(f"处理分块失败 [{start}-{end}]: {str(e)}")
            return None

    def save_merged_pdf(self):
        """保存最终结果"""
        print("正在保存合并后的PDF...")
        with open(self.output_file, 'wb') as f:
            self.merger.write(f)
        print(f"文件已保存至: {self.output_file}")


# ==============================
#           使用示例
# ==============================
if __name__ == "__main__":
    input_folder = r"C:\Users\ROG\Desktop\2025 s2\convert\res"
    output_file = "merged_presentation1-2.pdf"

    # 支持不同布局模式：
    # - 1页/页：原样输出
    # - 2页/页：横向排列
    # - 4页/页：四象限
    # - 6页/页：两行三列
    # - 9页/页：三行三列
    processor = PDFMergerProcessor(
        input_folder=input_folder,
        output_file=output_file,
        pages_per_sheet=1  # 可修改此值测试不同布局
    )
    processor.process_pdfs()