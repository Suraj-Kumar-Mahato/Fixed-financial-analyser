## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader
from crewai.tools import tool

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool:

    @staticmethod
    @tool("Read Financial Document")
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a PDF file at the given path.

        Args:
            path (str): Path to the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full text content of the financial document.
        """
        loader = PyPDFLoader(file_path=path)
        docs = loader.load()

        full_report = ""
        for data in docs:
            content = data.page_content

            # Remove extra whitespaces and format properly
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")

            full_report += content + "\n"

        return full_report


## Creating Investment Analysis Tool
class InvestmentTool:
    @staticmethod
    @tool("Analyze Investment Data")
    def analyze_investment_tool(financial_document_data: str) -> str:
        """Processes and cleans financial document text for investment analysis.

        Args:
            financial_document_data (str): Raw text from the financial document.

        Returns:
            str: Cleaned financial data.
        """
        processed_data = financial_document_data

        # Clean up the data format — remove double spaces
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1

        return processed_data


## Creating Risk Assessment Tool
class RiskTool:
    @staticmethod
    @tool("Create Risk Assessment")
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """Evaluates financial data and generates a risk assessment summary.

        Args:
            financial_document_data (str): Raw text from the financial document.

        Returns:
            str: Risk assessment summary.
        """
        risk_keywords = [
            "debt", "loss", "decline", "risk", "uncertainty",
            "litigation", "volatility", "deficit", "impairment"
        ]
        findings = []
        lower_data = financial_document_data.lower()
        for kw in risk_keywords:
            count = lower_data.count(kw)
            if count > 0:
                findings.append(f"'{kw}' mentioned {count} time(s)")

        if findings:
            return "Risk indicators found in document:\n" + "\n".join(findings)
        return "No significant risk indicators detected in the document."
