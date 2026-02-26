## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

## Task 1: Verify the uploaded document is a financial report
verification = Task(
    description=(
        "Read the uploaded financial document and verify it is a legitimate financial report. "
        "Identify the document type (e.g., 10-K, 10-Q, earnings release), the issuing company, "
        "and the reporting period covered. If the document does not appear to be a financial report, "
        "clearly state that and explain why."
    ),
    expected_output=(
        "A concise verification summary including:\n"
        "- Document type and classification\n"
        "- Issuing entity name\n"
        "- Reporting period (e.g., Q2 2025, FY 2024)\n"
        "- Confirmation that the document contains structured financial data"
    ),
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Task 2: Core financial document analysis
document_analysis = Task(
    description=(
        "Analyze the financial document to address the user's query: {query}.\n"
        "Read the document carefully and extract relevant financial metrics including revenue, "
        "net income, margins, cash flow, debt levels, and key operating highlights.\n"
        "Identify significant trends, year-over-year changes, and any notable disclosures.\n"
        "Ground all findings in data from the document — do not fabricate figures."
    ),
    expected_output=(
        "A structured financial analysis report including:\n"
        "- Executive summary answering the user's query\n"
        "- Key financial metrics and trends extracted from the document\n"
        "- Notable highlights and management commentary\n"
        "- Data sources cited (page/section references where possible)"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
    context=[verification],
)

## Task 3: Investment considerations
investment_analysis = Task(
    description=(
        "Based on the financial analysis, provide balanced investment considerations relevant to: {query}.\n"
        "Evaluate valuation metrics, growth trajectory, competitive positioning, and capital allocation.\n"
        "Use search tools to add current market context where relevant.\n"
        "All investment considerations must be tied to documented evidence — no speculative claims."
    ),
    expected_output=(
        "An investment considerations summary including:\n"
        "- Bull case: key strengths and growth drivers supported by the document\n"
        "- Bear case: concerns and headwinds identified in the document\n"
        "- Relevant valuation context (P/E, EV/EBITDA, etc. if data is available)\n"
        "- Important disclaimer: this is not personalized financial advice"
    ),
    agent=investment_advisor,
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    async_execution=False,
    context=[document_analysis],
)

## Task 4: Risk assessment
risk_assessment = Task(
    description=(
        "Identify and assess key risks disclosed or implied in the financial document, "
        "in the context of the user's query: {query}.\n"
        "Examine financial risk (leverage, liquidity), operational risk, market risk, and regulatory risk.\n"
        "Rate each risk category (Low / Medium / High) with supporting evidence from the document."
    ),
    expected_output=(
        "A structured risk assessment including:\n"
        "- Risk summary table: category, description, severity (Low/Medium/High)\n"
        "- Top 3 risks with detailed explanation and document evidence\n"
        "- Mitigating factors mentioned in the document\n"
        "- Overall risk profile conclusion"
    ),
    agent=risk_assessor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
    context=[document_analysis],
)
