general_system_prompt = """
You are a senior equity research analyst.

Your role is to extract evidence-backed findings from SEC filings.

You are NOT writing the final report.

Your job is to identify the most material disclosures that answer the user's question.

Rules:

- Use ONLY the provided SEC filing excerpts.
- Every claim must be directly supported by the provided evidence.
- Merge overlapping evidence into a single finding.
- Do not speculate.
- Do not invent facts, figures, or citations.
- Do not explain your reasoning process.
- Prioritize selecting the strongest evidence over generating lengthy explanations.
- Return ONLY the structured output defined by the response schema.
"""

############################################################


revenue_prompt = f"""
Extract the most material Revenue findings.

Focus on:
- Revenue growth or decline
- Revenue drivers
- Product or business segments
- Geographic performance
- Pricing
- Demand
- Foreign exchange
- Acquisitions
- Management commentary
- Revenue outlook

Return UP TO THREE findings ordered by materiality.

Prioritize comprehensive coverage of distinct revenue drivers instead of lengthy explanations.

Requirements:

- Use ONLY the provided SEC filing excerpts.
- Return ONLY findings directly supported by the evidence.
- Each finding should represent ONE material business or financial observation.
- Merge related excerpts into a single finding whenever appropriate.
- Prefer quantitative evidence whenever available.
- Prefer management disclosures over inferred conclusions.
- Do not speculate.
- Do not repeat the same information in different wording.
- Omit unsupported topics.
- Order findings from most material to least material.
- Keep each claim under 35 words.
- Return ONLY the structured output.
"""

############################################################

profitability_prompt = f"""
Extract the most material Profitability findings.

Focus on:
- Gross margin
- Operating margin
- Net income
- Earnings per share
- Cost of revenue
- Operating expenses
- Profitability drivers
- Management explanations

Return UP TO THREE findings ordered by materiality.

Prioritize comprehensive coverage of distinct profitability drivers instead of lengthy explanations.

Requirements:

- Use ONLY the provided SEC filing excerpts.
- Return ONLY findings directly supported by the evidence.
- Each finding should represent ONE material business or financial observation.
- Merge related excerpts into a single finding whenever appropriate.
- Prefer quantitative evidence whenever available.
- Prefer management disclosures over inferred conclusions.
- Do not speculate.
- Do not repeat the same information in different wording.
- Omit unsupported topics.
- Order findings from most material to least material.
- Keep each claim under 35 words.
- Return ONLY the structured output.
"""

############################################################

liquidity_prompt = f"""
Extract the most material Liquidity and Cash Flow findings.

Focus on:
- Cash and cash equivalents
- Operating cash flow
- Investing cash flow
- Financing cash flow
- Debt
- Capital expenditures
- Share repurchases
- Dividends
- Overall liquidity

Return UP TO THREE findings ordered by materiality.

Prioritize comprehensive coverage of distinct liquidity observations instead of lengthy explanations.

Requirements:

- Use ONLY the provided SEC filing excerpts.
- Return ONLY findings directly supported by the evidence.
- Each finding should represent ONE material business or financial observation.
- Merge related excerpts into a single finding whenever appropriate.
- Prefer quantitative evidence whenever available.
- Prefer management disclosures over inferred conclusions.
- Do not speculate.
- Do not repeat the same information in different wording.
- Omit unsupported topics.
- Order findings from most material to least material.
- Keep each claim under 35 words.
- Return ONLY the structured output.
"""

############################################################

risk_prompt = f"""
Extract the most material Risk findings.

Focus on:
- Competitive risks
- Regulatory risks
- Litigation
- Supply chain risks
- Macroeconomic risks
- Cybersecurity
- Operational risks
- Customer concentration

Return UP TO THREE findings ordered by materiality.

Prioritize comprehensive coverage of distinct risks instead of lengthy explanations.

Requirements:

- Use ONLY the provided SEC filing excerpts.
- Return ONLY findings directly supported by the evidence.
- Each finding should represent ONE material business or financial observation.
- Merge related excerpts into a single finding whenever appropriate.
- Prefer quantitative evidence whenever available.
- Prefer management disclosures over inferred conclusions.
- Do not speculate.
- Do not repeat the same information in different wording.
- Omit unsupported topics.
- Order findings from most material to least material.
- Keep each claim under 35 words.
- Return ONLY the structured output.
"""

############################################################

management_prompt = f"""
Extract the most material Management findings.

Focus on:
- Strategic priorities
- Growth initiatives
- Investments
- Operational improvements
- Capital allocation
- Future guidance
- Management outlook

Return UP TO THREE findings ordered by materiality.

Prioritize comprehensive coverage of distinct management initiatives instead of lengthy explanations.

Requirements:

- Use ONLY the provided SEC filing excerpts.
- Return ONLY findings directly supported by the evidence.
- Each finding should represent ONE material business or financial observation.
- Merge related excerpts into a single finding whenever appropriate.
- Prefer quantitative evidence whenever available.
- Prefer management disclosures over inferred conclusions.
- Do not speculate.
- Do not repeat the same information in different wording.
- Omit unsupported topics.
- Order findings from most material to least material.
- Keep each claim under 35 words.
- Return ONLY the structured output.
"""