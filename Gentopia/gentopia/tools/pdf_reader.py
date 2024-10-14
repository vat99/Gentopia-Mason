from typing import AnyStr
import arxiv
import requests
import io
from PyPDF2 import PdfReader
from gentopia.tools.basetool import *


class PDFReaderArgs(BaseModel):
    title: str = Field(..., description="title name")


class PDFReader(BaseTool):
    """Tool that adds the capability to query the given paper pdf."""

    name = "pdf_reader"
    description = ("search a paper with the title relevant to the input text."
                   "input title and return pdf text of the relevant title "
                   )

    args_schema: Optional[Type[BaseModel]] = PDFReaderArgs

    def _get_pdf_text(self, title: str):
        search = arxiv.Search(
            query=title,
            max_results=1,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        try:
            paper = next(search.results())
        except StopIteration:
            return "Paper not found."

        # Get the PDF URL
        pdf_url = paper.pdf_url

        # Download the PDF
        response = requests.get(pdf_url)
        if response.status_code != 200:
            return "Failed to download the PDF."

        # Read the PDF content
        pdf_content = io.BytesIO(response.content)

        # Extract text from the PDF
        pdf_reader = PdfReader(pdf_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        return text
    
    def _run(self, title: AnyStr) -> str:
        return self._get_pdf_text(title=title)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = PDFReader()._run("Attention for transformer")
    print(ans)
