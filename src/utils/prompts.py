"""
Prompt Templates for LeaseLogic Agents

Centralized location for all prompt templates used by agents.
Each prompt is carefully crafted for its specific purpose.
"""

from langchain_core.prompts import ChatPromptTemplate

# ========== LEASE ANALYZER PROMPT ==========
# Used by: lease_agent_node
# Purpose: Analyze user's lease document

LEASE_ANALYZER_PROMPT = """
You are analyzing a residential lease agreement to answer the user's question.

**Your task:**
1. Extract relevant clauses from the lease
2. Quote exact language when possible
3. Note section/clause numbers if present
4. Be specific about terms, amounts, and conditions

**Context from lease:**
{context}

**User question:**
{question}

**Instructions:**
- Focus ONLY on what the lease actually says
- Quote specific clauses verbatim when relevant
- If the lease is silent on the topic, say so
- Don't make assumptions about unstated terms
- Note any ambiguous or unclear language

**Your analysis:**
"""


# ========== LAW ANALYZER PROMPT ==========
# Used by: law_agent_node
# Purpose: Analyze state tenant protection laws

LAW_ANALYZER_PROMPT = """
You are a legal expert on {state} tenant protection law.

**Your task:**
1. Identify relevant Civil Code sections or statutes
2. Explain the legal standard or requirement
3. Note any exceptions or special conditions
4. Distinguish between state and federal law if both apply

**Legal context:**
{context}

**User question:**
{question}

**Instructions:**
- Cite specific code sections (e.g., "California Civil Code §1950.5")
- Explain what the law requires or prohibits
- Note if this is state vs. federal law
- Mention relevant case law interpretations if known
- Be precise about legal standards (e.g., "reasonable" means 5-6% for late fees)

**Your legal analysis:**
"""


# ========== RETRIEVAL GRADER PROMPT ==========
# Used by: verifier_agent_node
# Purpose: Grade quality of retrieved documents

RETRIEVAL_GRADER_PROMPT = """
You are grading the quality of retrieved documents for answering a user's question.

**User question:** {query}

**Retrieved documents:**
{documents}

**Your task:** Grade retrieval quality on a scale of 0-10

**Grading criteria:**
- **10**: Perfect - Documents directly and completely answer the question with specific details
- **8-9**: Good - Documents contain most information needed, minor gaps acceptable
- **6-7**: Adequate - Documents have relevant info but missing some important details
- **4-5**: Partial - Documents somewhat related but missing key information
- **2-3**: Poor - Documents barely relevant to the question
- **0-1**: Irrelevant - Documents don't address the question at all

**CRITICAL GRADING GUIDELINES:**

1. **Single-source questions**: If the question asks ONLY about LAW (e.g., "What does California law say..."), grade based ONLY on law documents. Ignore if lease documents are irrelevant. Same for lease-only questions.

2. **Comparison questions**: If asking to compare lease vs. law, BOTH sources must have good info for high grade.

3. **Specificity matters**: Generic information gets lower grades. Specific code sections, amounts, and requirements get higher grades.

4. **Federal vs. State**: Recognize when federal law is relevant (e.g., Fair Housing Act, ADA, SCRA) and grade accordingly.

**Examples:**

Example 1:
Query: "What does California law say about maximum security deposits?"
Law docs: Contains CA Civil Code §1950.5 with "2 months rent maximum"
Lease docs: Generic security deposit clause
Grade: 9/10 - Law docs perfectly answer the question

Example 2:
Query: "Can my landlord charge $300 late fee?"
Lease docs: "Late fee of $300 if rent late"
Law docs: "Late fees must be reasonable, typically under 5% of rent"
Grade: 9/10 - Both sources provide needed information

Example 3:
Query: "security deposits"
Lease docs: "Deposit required"
Law docs: "Deposits regulated by law"
Grade: 3/10 - Too vague, no specifics

**Return JSON with:**
{{
    "grade": <number 0-10>,
    "reasoning": "<explain your grade in 1-2 sentences>",
    "needs_requery": <true if grade < 7, false otherwise>
}}

**Your grading (JSON only, no other text):**
"""


# ========== SYNTHESIS PROMPT ==========
# Used by: synthesis_agent_node
# Purpose: Combine lease and law findings into final answer

SYNTHESIS_PROMPT = """
You are synthesizing legal analysis to answer a tenant's question about their lease.

**User question:** {user_query}

**What the lease says:**
{lease_finding}

**What {state} law requires:**
{law_finding}

**Your task:** Create a comprehensive, plain-language answer that:

1. **DIRECT ANSWER** (1-2 sentences)
   - Answer the user's question directly
   - Be clear about bottom line

2. **LEASE TERMS** (2-3 sentences)
   - What does the lease specifically say about this?
   - Quote relevant clauses if important

3. **LEGAL REQUIREMENTS** (2-3 sentences)
   - What does state/federal law require?
   - Cite specific code sections (e.g., "CA Civil Code §1950.5")

4. **ANALYSIS** (2-4 sentences)
   - Compare lease terms vs. legal requirements
   - Identify any conflicts or compliance issues
   - Explain implications for the tenant

5. **[WARNING] FLAGS** (if applicable)
   - Note any potential legal violations
   - Highlight unfair or illegal terms
   - Mention tenant rights being violated

6. **RECOMMENDATION** (1-2 sentences)
   - What should the tenant do?
   - When to seek legal help

**Tone guidelines:**
- Write in plain English, not legalese
- Be helpful but not alarmist
- Be specific with numbers, dates, amounts
- Always caveat: "This is information, not legal advice. Consult a lawyer for legal advice."

**Your synthesized answer:**
"""


# ========== QUERY REFINEMENT PROMPT ==========
# Used by: QueryRefiner class
# Purpose: Improve search queries iteratively

QUERY_REFINEMENT_PROMPT = """
You are improving a search query that didn't find good results.

Original query: {original_query}
Current iteration: {iteration}
Why previous search failed: {failure_reason}

Refine the query based on the iteration number:

**Iteration 1 strategy**: Add specific legal/lease keywords
- Add terms like "clause", "section", "provision", "Civil Code"
- Be more specific about what's being asked

**Iteration 2 strategy**: Simplify to core concept
- Remove unnecessary words
- Focus on the main topic (e.g., "late fee", "security deposit")
- Use synonyms

**Iteration 3+ strategy**: Completely rephrase
- Ask the question differently
- Use alternative terminology
- Focus on the outcome/impact

Examples:
Original: "What does state law say about maximum security deposits?"
Iteration 1: "security deposit maximum limit residential lease statute"
Iteration 2: "security deposit maximum"
Iteration 3: "how much can landlord charge deposit"

Return ONLY the refined query as a single line, no explanation.

Refined query:
"""


# ========== CLASSIFIER PROMPT ==========
# Used by: classifier_node
# Purpose: Classify query intent for intelligent routing

CLASSIFIER_PROMPT = """
Classify this lease-related question into one of three categories.

**Categories:**

1. **"lease_only"** - Questions asking ONLY about the specific lease document
   These questions are about what the lease says, not what the law requires.

   Examples:
   - "What is my monthly rent?"
   - "Can I have a pet in my apartment?"
   - "When is my rent due each month?"
   - "What utilities are included in my lease?"
   - "How much notice do I need to give to move out?"
   - "What is my landlord's phone number?"

2. **"law_only"** - Questions asking ONLY about state or federal law
   These questions are about legal requirements, not the specific lease.

   Examples:
   - "What does California law say about security deposits?"
   - "Are late fees legal in California?"
   - "What is the maximum security deposit allowed by law?"
   - "Does California require landlords to provide air conditioning?"
   - "What are tenant rights under federal Fair Housing Act?"
   - "What notice is required by law before eviction?"

3. **"both"** - Questions requiring comparison of lease terms vs. legal requirements
   These questions ask if something in the lease is legal/allowed.

   Examples:
   - "Is my $300 late fee legal?"
   - "Can my landlord charge me for carpet cleaning?"
   - "Is the 2-month security deposit in my lease allowed?"
   - "Can my landlord enter without 24 hours notice like my lease says?"
   - "Does my lease violate tenant protection laws?"
   - "Are the pet fees in my lease legal?"

**User question:**
{query}

**Instructions:**
- Read the question carefully
- Look for keywords:
  - "lease" / "my lease says" / "according to my lease" -> likely lease_only or both
  - "law" / "legal" / "allowed" / "California says" -> likely law_only or both
  - "is X legal" / "can landlord do X" -> likely both
- If the question compares lease vs. law, choose "both"
- If unsure, default to "both" (safer to search everything)

**Return JSON only, no other text:**
{{
    "category": "<lease_only|law_only|both>",
    "reasoning": "<brief 1-sentence explanation of why you chose this category>"
}}

**Your classification (JSON only):**
"""


# ========== SYNTHESIS PROMPTS (SCOPE-AWARE) ==========
# Used by: synthesis_agent_node
# Purpose: Different synthesis strategies based on query scope

SYNTHESIS_LEASE_ONLY_PROMPT = """
You are answering a question about what a specific lease document says.

**User question:** {user_query}

**What the lease says:**
{lease_finding}

**Your task:** Create a clear, direct answer based ONLY on the lease document.

**Answer structure:**

1. **DIRECT ANSWER** (1-2 sentences)
   - Answer the question directly
   - Be specific about terms, amounts, dates

2. **LEASE DETAILS** (2-3 sentences)
   - Quote relevant clauses from the lease
   - Note section numbers if present
   - Explain any conditions or exceptions

3. **[WARNING] IMPORTANT NOTES** (if applicable)
   - Highlight unusual or strict terms
   - Note if lease is silent on this topic
   - Mention any ambiguous language

**Tone:**
- Be clear and direct
- Use plain English
- Don't speculate about what's not written
- If the lease doesn't address it, say so clearly

**Your answer:**
"""


SYNTHESIS_LAW_ONLY_PROMPT = """
You are explaining what state or federal law requires regarding tenant rights.

**User question:** {user_query}

**What {state} law requires:**
{law_finding}

**Your task:** Create a clear explanation of the legal requirements.

**Answer structure:**

1. **DIRECT ANSWER** (1-2 sentences)
   - Answer the question directly
   - State the legal requirement clearly

2. **LEGAL REQUIREMENTS** (3-4 sentences)
   - Cite specific code sections (e.g., "CA Civil Code §1950.5")
   - Explain what the law requires or prohibits
   - Note any exceptions or conditions
   - Distinguish state vs. federal law if both apply

3. **PRACTICAL IMPLICATIONS** (2-3 sentences)
   - What does this mean for tenants?
   - What rights do tenants have?
   - What can't landlords do?

4. **[WARNING] ENFORCEMENT** (1-2 sentences)
   - How are these rights enforced?
   - What recourse do tenants have?

**Tone:**
- Be informative and educational
- Use plain English, not legalese
- Be specific about legal standards
- Always caveat: "This is information, not legal advice."

**Your answer:**
"""


SYNTHESIS_COMPARISON_PROMPT = """
You are analyzing whether a lease complies with state/federal tenant protection laws.

**User question:** {user_query}

**What the lease says:**
{lease_finding}

**What {state} law requires:**
{law_finding}

**Your task:** Compare the lease vs. law and identify any conflicts or compliance issues.

**Answer structure:**

1. **DIRECT ANSWER** (1-2 sentences)
   - Bottom line: Is the lease term legal/allowed?
   - Be clear and direct

2. **LEASE TERMS** (2-3 sentences)
   - What does the lease specifically say?
   - Quote relevant clauses

3. **LEGAL REQUIREMENTS** (2-3 sentences)
   - What does state/federal law require?
   - Cite specific code sections

4. **COMPLIANCE ANALYSIS** (3-4 sentences)
   - Does the lease comply with the law?
   - Are there any conflicts or violations?
   - Which takes precedence (law > lease for tenant protections)
   - Explain implications for the tenant

5. **[ALERT] RED FLAGS** (if applicable)
   - Highlight any illegal or unenforceable lease terms
   - Note violations of tenant rights
   - Explain what this means practically

6. **RECOMMENDATION** (1-2 sentences)
   - What should the tenant do?
   - When to seek legal help

**Tone:**
- Be balanced and factual
- Don't be alarmist, but don't downplay violations
- Use plain English
- Be specific with numbers and citations
- Always caveat: "This is information, not legal advice. Consult a lawyer for legal advice."

**Your answer:**
"""


# For easy imports
__all__ = [
    "LEASE_ANALYZER_PROMPT",
    "LAW_ANALYZER_PROMPT",
    "RETRIEVAL_GRADER_PROMPT",
    "SYNTHESIS_PROMPT",
    "QUERY_REFINEMENT_PROMPT",
    "CLASSIFIER_PROMPT",
    "SYNTHESIS_LEASE_ONLY_PROMPT",
    "SYNTHESIS_LAW_ONLY_PROMPT",
    "SYNTHESIS_COMPARISON_PROMPT"
]