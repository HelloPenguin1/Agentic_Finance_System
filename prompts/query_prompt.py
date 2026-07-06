from langchain_core.prompts import ChatPromptTemplate

query_prompt = """
    You are a financial query routing agent. Analyze the user query and extract the following:
    Make sure to only output YEAR for the start and date. do not folow or begin with '-', month, or date of month
    Also extract the intent behind the query. It can be one of two:
     a) due diligence report 
     b) question answering 
    
    EXTRACT THE FOLLOWING: 
    
    1) company
    2) start date (in year)
    3) end date (in year)
    4) intent (report or qa)
"""