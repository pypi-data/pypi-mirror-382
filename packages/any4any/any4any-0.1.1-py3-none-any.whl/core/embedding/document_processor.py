import os
import PyPDF2
import docx
import chardet
import re
import logging
from config import Config
from typing import List, Dict, Any
from core.log import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or Config.DOC_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.DOC_CHUNK_OVERLAP
    
    def load_documents(self, docs_path: str) -> List[Dict[str, Any]]:
        """加载目录中的所有文档"""
        documents = []        
        for filename in os.listdir(docs_path):
            file_path = os.path.join(docs_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            try:
                # 检查文件是否为支持的类型
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in Config.SUPPORTED_FILE_TYPES:
                    if file_ext == '.pdf':
                        content = self._read_pdf(file_path)
                    elif file_ext == '.docx':
                        content = self._read_docx(file_path)
                    elif file_ext == '.txt':
                        content = self._read_txt(file_path)
                else:
                    continue
                
                if content:
                    documents.append({
                        'file_name': filename,
                        'file_path': file_path,
                        'content': content,
                        'chunks': []
                    })
                    logger.info(f"Successfully loaded document: {filename}")
                    
            except Exception as e:
                logger.error(f"Error loading document {filename}: {e}")
        
        return documents
    
    def _read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
        return content
    
    def _read_docx(self, file_path: str) -> str:
        """读取DOCX文件"""
        content = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {e}")
        return content
    
    def _read_txt(self, file_path: str) -> str:
        """读取TXT文件"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']
                return raw_data.decode(encoding, errors='ignore')
        except Exception as e:
            logger.error(f"Error reading TXT file {file_path}: {e}")
            return ""
    
    def split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        if not text.strip():
            return []
        
        # 按句子和长度分割-后续可自定义
        sentences = re.split(r'[。！？!?\.\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size: # 如果当前块加上新句子不会超长，就添加
                current_chunk += sentence + "。"
            else:                
                if current_chunk: # 如果当前块不为空，保存它
                    chunks.append(current_chunk.strip())                
                
                current_chunk = sentence + "。" # 开始新块        
        
        if current_chunk: # 添加最后一个块
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_documents(self, docs_path: str) -> List[Dict[str, Any]]:
        """处理所有文档并分割成块"""
        documents = self.load_documents(docs_path)
        
        for doc in documents:
            chunks = self.split_text(doc['content'])
            doc['chunks'] = [
                {
                    'text': chunk,
                    'metadata': {
                        'file_name': doc['file_name'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                }
                for i, chunk in enumerate(chunks)
            ]
        
        return documents