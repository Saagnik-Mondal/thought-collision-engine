<![CDATA["""
Text Connector — Process raw text input.
"""
class TextConnector:
    name = "text"

    def extract_text(self, content: str | bytes) -> str:
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return content
]]>
