## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from langchain_openai import ChatOpenAI

from tools import search_tool, FinancialDocumentTool

### Loading LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Senior Financial Analyst — reads and interprets financial documents
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Accurately analyze the uploaded financial document to answer the user's query: {query}. "
        "Extract key financial metrics, revenue trends, profitability indicators, and notable risks. "
        "Provide data-driven insights grounded strictly in the document content."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned CFA-certified financial analyst with 15+ years of experience evaluating "
        "corporate financial statements, earnings reports, and investment prospectuses. "
        "You rely on documented data and recognized financial frameworks (DCF, P/E analysis, ratio analysis) "
        "to deliver accurate, objective analysis. You never fabricate figures or cite sources you haven't verified."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)

# Document Verifier — confirms the document is a legitimate financial report
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Verify that the uploaded file is a valid financial document (e.g., annual report, earnings release, "
        "10-K, 10-Q, investor presentation). Confirm the document type, issuing entity, and reporting period."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a compliance officer with deep experience in financial reporting standards (GAAP, IFRS). "
        "You carefully examine documents for authenticity and structural validity before they are analyzed. "
        "You only validate documents that clearly contain financial data and properly structured disclosures."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False,
)

# Investment Advisor — provides evidence-based investment recommendations
investment_advisor = Agent(
    role="Certified Investment Advisor",
    goal=(
        "Based on the financial document analysis, provide balanced, evidence-based investment considerations "
        "relevant to the user's query: {query}. Highlight opportunities and risks without promoting specific products."
    ),
    verbose=True,
    backstory=(
        "You are a registered investment advisor (RIA) with fiduciary responsibility to clients. "
        "You base all recommendations on documented financial performance, valuation metrics, and publicly "
        "available market data. You always include appropriate risk disclosures and never guarantee returns."
    ),
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)

# Risk Assessor — evaluates financial and market risks objectively
risk_assessor = Agent(
    role="Financial Risk Assessment Specialist",
    goal=(
        "Identify and quantify key financial, operational, and market risks present in the document "
        "in response to the user's query: {query}. Provide a structured risk summary with severity ratings."
    ),
    verbose=True,
    backstory=(
        "You are a risk management professional with expertise in credit risk, market risk, and operational risk. "
        "You apply standard frameworks (VaR, stress testing, scenario analysis) to evaluate exposure levels. "
        "Your assessments are grounded in the actual data presented in the financial document."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)
