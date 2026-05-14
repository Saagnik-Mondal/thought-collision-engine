<![CDATA["""
PDF Connector — Extract text from PDF documents using PyMuPDF.
"""
from loguru import logger

class PDFConnector:
    name = "pdf"

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            text = "\n".join(text_parts)
            logger.info("📄 Extracted {} characters from PDF", len(text))
            return text
        except ImportError:
            logger.warning("PyMuPDF not installed, returning empty text")
            return file_content.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error("PDF extraction failed: {}", e)
            return ""
]]>
