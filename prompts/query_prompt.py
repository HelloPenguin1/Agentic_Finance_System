from langchain_core.prompts import ChatPromptTemplate

query_prompt = """
    You are a financial query routing agent. Analyze the user query and extract the following:
    Make sure to only output YEAR for the start and date. do not folow or begin with '-', month, or date of month
    1) company
    2) start date (in year)
    3) end date (in year)
"""