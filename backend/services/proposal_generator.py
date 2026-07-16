"""
Week 3: NGO Proposal Draft Generator.
Generates structured grant proposals from user inputs using LLM + templates.
"""
import logging
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


# ── Proposal Section Prompts ─────────────────────────────────────────────────

EXECUTIVE_SUMMARY_PROMPT = """You are an expert NGO grant writer. Write a professional Executive Summary for the following NGO project.

Project Details:
- Organization: {org_name}
- Project Title: {project_title}
- Problem: {problem}
- Target Beneficiaries: {beneficiaries}
- Budget: {budget}
- Duration: {duration}

Write a concise, compelling Executive Summary (2-3 paragraphs) that covers:
1. Organization overview and credibility
2. The problem being addressed and its urgency
3. Proposed solution and expected impact
4. Funding request summary

Executive Summary:"""


PROBLEM_STATEMENT_PROMPT = """You are an expert NGO grant writer. Write a detailed Problem Statement for the following NGO project.

Project Details:
- Organization: {org_name}
- Project Title: {project_title}
- Problem: {problem}
- Location/Context: {location}
- Target Beneficiaries: {beneficiaries}

Write a compelling Problem Statement (3-4 paragraphs) that:
1. Clearly describes the problem with specific data/statistics
2. Explains the root causes
3. Describes who is affected and how
4. Explains why this problem needs urgent attention

Problem Statement:"""


OBJECTIVES_PROMPT = """You are an expert NGO grant writer. Write SMART Objectives for the following NGO project.

Project Details:
- Project Title: {project_title}
- Problem: {problem}
- Target Beneficiaries: {beneficiaries}
- Duration: {duration}

Write 4-5 SMART (Specific, Measurable, Achievable, Relevant, Time-bound) objectives.
Format as a numbered list.

Project Objectives:"""


METHODOLOGY_PROMPT = """You are an expert NGO grant writer. Write a detailed Methodology/Implementation Plan for the following NGO project.

Project Details:
- Organization: {org_name}
- Project Title: {project_title}
- Problem: {problem}
- Target Beneficiaries: {beneficiaries}
- Duration: {duration}
- Budget: {budget}

Write a comprehensive Methodology section that includes:
1. Project phases and timeline
2. Key activities for each phase
3. Team structure and responsibilities
4. Community engagement approach
5. Risk mitigation strategies

Methodology:"""


BUDGET_PROMPT = """You are an expert NGO grant writer. Create a detailed Budget Breakdown for the following NGO project.

Project Details:
- Project Title: {project_title}
- Total Budget: {budget}
- Duration: {duration}
- Key Activities: {activities}

Create a professional budget breakdown with:
1. Personnel costs (staff salaries, consultants)
2. Program/Activity costs
3. Equipment and materials
4. Travel and logistics
5. Administrative/overhead costs (max 15%)
6. Monitoring and evaluation costs

Format as a structured table with categories, items, quantities, unit costs, and totals.

Budget Breakdown:"""


MONITORING_EVALUATION_PROMPT = """You are an expert NGO grant writer. Write a Monitoring & Evaluation (M&E) Plan for the following NGO project.

Project Details:
- Project Title: {project_title}
- Objectives: {objectives}
- Duration: {duration}
- Target Beneficiaries: {beneficiaries}

Write a comprehensive M&E Plan that includes:
1. Key Performance Indicators (KPIs) for each objective
2. Data collection methods and tools
3. Reporting schedule (monthly, quarterly, annual)
4. Evaluation approach (baseline, midterm, endline)
5. Learning and adaptation mechanisms

M&E Plan:"""


FULL_PROPOSAL_PROMPT = """You are an expert NGO grant writer with 15+ years of experience. 
Write a complete, professional grant proposal for the following project.

Project Details:
- Organization Name: {org_name}
- Project Title: {project_title}
- Problem Being Addressed: {problem}
- Target Beneficiaries: {beneficiaries}
- Project Location: {location}
- Project Duration: {duration}
- Total Budget Requested: {budget}
- Key Activities: {activities}

Write a complete grant proposal with ALL of the following sections:

# {project_title}
## Grant Proposal

### 1. EXECUTIVE SUMMARY
(2-3 paragraphs summarizing the entire proposal)

### 2. ORGANIZATION BACKGROUND
(Brief overview of {org_name}, mission, track record)

### 3. PROBLEM STATEMENT
(Detailed description of the problem with data and context)

### 4. PROJECT OBJECTIVES
(4-5 SMART objectives)

### 5. METHODOLOGY / IMPLEMENTATION PLAN
(Detailed activities, timeline, team structure)

### 6. BUDGET BREAKDOWN
(Detailed budget with categories and justifications)

### 7. MONITORING & EVALUATION
(KPIs, data collection, reporting schedule)

### 8. SUSTAINABILITY PLAN
(How the project will continue after funding ends)

### 9. CONCLUSION
(Compelling closing statement)

Write the complete proposal now:"""


def generate_proposal_section(
    section: str,
    project_data: Dict[str, Any],
    llm,
) -> str:
    """
    Generate a specific section of the proposal.

    Args:
        section: Section name (executive_summary, problem_statement, etc.)
        project_data: Dict with project details
        llm: LLM instance

    Returns:
        Generated section text
    """
    prompt_map = {
        "executive_summary": EXECUTIVE_SUMMARY_PROMPT,
        "problem_statement": PROBLEM_STATEMENT_PROMPT,
        "objectives": OBJECTIVES_PROMPT,
        "methodology": METHODOLOGY_PROMPT,
        "budget": BUDGET_PROMPT,
        "monitoring_evaluation": MONITORING_EVALUATION_PROMPT,
        "full_proposal": FULL_PROPOSAL_PROMPT,
    }

    if section not in prompt_map:
        raise ValueError(f"Unknown section: {section}. Valid: {list(prompt_map.keys())}")

    template = prompt_map[section]

    # Fill in defaults for missing fields
    defaults = {
        "org_name": "Our Organization",
        "project_title": "Community Development Project",
        "problem": "Community needs support",
        "beneficiaries": "Local community members",
        "location": "Local community",
        "duration": "12 months",
        "budget": "₹500,000",
        "activities": "Community outreach, training, and support services",
        "objectives": "Improve community wellbeing",
    }
    data = {**defaults, **project_data}

    # Get variables needed for this template
    import re
    variables = re.findall(r'\{(\w+)\}', template)
    filtered_data = {k: data.get(k, defaults.get(k, "")) for k in variables}

    prompt = PromptTemplate(
        template=template,
        input_variables=list(filtered_data.keys()),
    )

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke(filtered_data)
    return result


def generate_full_proposal(project_data: Dict[str, Any], llm) -> str:
    """
    Generate a complete NGO grant proposal.

    Args:
        project_data: Dict with all project details
        llm: LLM instance

    Returns:
        Complete proposal text
    """
    logger.info(f"Generating full proposal for: {project_data.get('project_title', 'Unknown')}")
    return generate_proposal_section("full_proposal", project_data, llm)


def generate_checklist(project_data: Dict[str, Any]) -> str:
    """
    Generate a proposal submission checklist.

    Args:
        project_data: Dict with project details

    Returns:
        Formatted checklist text
    """
    org = project_data.get("org_name", "Your Organization")
    title = project_data.get("project_title", "Your Project")

    checklist = f"""# Grant Proposal Submission Checklist
## {title} | {org}

### ✅ DOCUMENTS REQUIRED
- [ ] Cover Letter (signed by authorized representative)
- [ ] Complete Grant Proposal Document
- [ ] Organization Registration Certificate
- [ ] Audited Financial Statements (last 2-3 years)
- [ ] Annual Report (most recent)
- [ ] Board of Directors List
- [ ] Organizational Chart
- [ ] Project Budget (detailed breakdown)
- [ ] Implementation Timeline / Gantt Chart
- [ ] M&E Framework
- [ ] CVs of Key Project Staff
- [ ] Letters of Support / MoUs from partners
- [ ] Tax Exemption Certificate (if applicable)

### ✅ PROPOSAL SECTIONS CHECKLIST
- [ ] Executive Summary (1-2 pages)
- [ ] Organization Background
- [ ] Problem Statement (with data/evidence)
- [ ] Project Objectives (SMART)
- [ ] Methodology / Implementation Plan
- [ ] Budget Breakdown (with justifications)
- [ ] Monitoring & Evaluation Plan
- [ ] Sustainability Plan
- [ ] Conclusion

### ✅ QUALITY CHECKS
- [ ] Spell-checked and proofread
- [ ] All figures/statistics cited with sources
- [ ] Budget adds up correctly
- [ ] Objectives are SMART
- [ ] Timeline is realistic
- [ ] Contact information is complete
- [ ] Proposal follows donor guidelines/format
- [ ] Page limits respected
- [ ] Font size and margins as required

### ✅ SUBMISSION CHECKLIST
- [ ] Submitted before deadline
- [ ] Correct number of copies (if physical)
- [ ] All required signatures obtained
- [ ] Submission confirmation received
- [ ] Copy kept for records

---
*Generated by NGO Proposal Drafting Bot | PRJ-032*
"""
    return checklist
