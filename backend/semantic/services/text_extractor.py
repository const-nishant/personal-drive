"""Text extraction service for various file formats."""

import logging
import io
from typing import Optional
import PyPDF2

try:
    import mammoth
    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False
    logging.warning("mammoth not available. DOCX extraction will not work.")

logger = logging.getLogger(__name__)


class TextExtractor:
    """Service for extracting text from various file formats."""

    @staticmethod
    def extract_text(file_content: bytes, mime_type: str) -> Optional[str]:
        """
        Extract text from file content based on MIME type.

        Args:
            file_content: File content as bytes
            mime_type: MIME type of the file

        Returns:
            Extracted text or None if extraction fails or format not supported
        """
        try:
            if mime_type == "application/pdf":
                return TextExtractor._extract_from_pdf(file_content)
            elif mime_type in [
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ]:
                return TextExtractor._extract_from_docx(file_content)
            elif mime_type == "text/plain":
                return file_content.decode("utf-8", errors="ignore")
            else:
                logger.warning(f"Text extraction not supported for MIME type: {mime_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> Optional[str]:
        """
        Extract text from PDF file.

        Args:
            file_content: PDF file content as bytes

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            extracted_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            return extracted_text if extracted_text.strip() else None
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return None

    @staticmethod
    def _extract_from_docx(file_content: bytes) -> Optional[str]:
        """
        Extract text from DOCX file.

        Args:
            file_content: DOCX file content as bytes

        Returns:
            Extracted text or None if extraction fails
        """
        if not MAMMOTH_AVAILABLE:
            logger.error("mammoth library not available for DOCX extraction")
            return None

        try:
            docx_file = io.BytesIO(file_content)
            result = mammoth.extract_raw_text(docx_file)
            extracted_text = result.value
            logger.info(f"Extracted {len(extracted_text)} characters from DOCX")
            return extracted_text if extracted_text.strip() else None
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {e}")
            return None

    @staticmethod
    def is_supported(mime_type: str) -> bool:
        """
        Check if text extraction is supported for a given MIME type.

        Args:
            mime_type: MIME type to check

        Returns:
            True if extraction is supported, False otherwise
        """
        supported_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]
        return mime_type in supported_types

