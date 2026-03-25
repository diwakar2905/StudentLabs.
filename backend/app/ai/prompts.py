"""
Prompt templates for AI generation.

This centralized file contains all prompts for the LLM.
Makes the system maintainable and easy to tune prompts without touching code.
"""

# ============= Abstract Generation =============

ABSTRACT_PROMPT = """You are an academic researcher writing a formal abstract.

Write a professional abstract on the topic: {topic}

Research Context:
{context}

Requirements:
- 150-200 words
- Academic tone
- Synthesize key findings from research context
- Include problem statement and significance
- Do NOT cite specific papers, focus on synthesizing knowledge

Abstract:"""

# ============= Introduction Generation =============

INTRODUCTION_PROMPT = """You are an academic writer crafting a research introduction.

Write an introduction for a research assignment on: {topic}

Research Context from Papers:
{context}

Your introduction should:
1. Hook the reader with the importance of the topic
2. Provide relevant background information
3. Explain why this topic matters
4. Outline what the research addresses
5. Use citations from research context to support claims
6. End with research objectives

Use academic tone throughout (3-5 paragraphs).

Introduction:"""

# ============= Literature Review Synthesis =============

LITERATURE_SYNTHESIS_PROMPT = """You are synthesizing academic literature into a cohesive narrative.

Synthesize the following research papers on {topic}:

{context}

Create a synthesis that:
1. Identifies major themes and patterns
2. Shows connections between papers
3. Highlights agreements and disagreements
4. Traces evolution of thinking
5. Points out research gaps

Write in academic prose (3-4 paragraphs).

Synthesis:"""

# ============= Discussion Generation =============

DISCUSSION_PROMPT = """You are writing a research discussion section.

Write a discussion section analyzing research on: {topic}

Key Research Context:
{context}

Your discussion should:
1. Interpret the findings from the literature
2. Connect findings to the research topic
3. Discuss implications of the findings
4. Compare/contrast different approaches in literature
5. Identify limitations in current research
6. Suggest future directions

Use academic tone and refer to research context (4-5 paragraphs).

Discussion:"""

# ============= Conclusion Generation =============

CONCLUSION_PROMPT = """You are writing a research conclusion.

Write a conclusion for a research assignment on: {topic}

Research Context:
{context}

Your conclusion should:
1. Summarize key findings from the literature
2. Reiterate the significance of the topic
3. Show how research advances the field
4. Discuss practical implications
5. Suggest future research directions
6. End with a strong closing statement

Write in academic tone (2-3 paragraphs).

Conclusion:"""

# ============= Methodology Section =============

METHODOLOGY_PROMPT = """You are writing a research methodology section.

Write a methodology section for research on: {topic}

Research Papers Analyzed:
{context}

Describe:
1. The research approach used in this literature review
2. Papers included and selection criteria
3. Analysis framework employed
4. Key methodologies found in literature
5. Limitations of the literature review

Write in academic tone (3-4 paragraphs).

Methodology:"""

# ============= RAG Generate Section (Generic) =============

RAG_SECTION_PROMPT = """You are an academic AI assistant writing a research section.

Write the {section_type} section for a research assignment on: {topic}

Use this research context to inform your writing:
{context}

Requirements for {section_type}:
- Academic tone
- 3-5 paragraphs
- Support assertions with research context
- Use "{section_type}" as header if needed
- Do NOT make up citations
- Do NOT hallucinate facts

{section_type} Section:"""

# ============= Quick Reference =============

SECTION_PROMPTS = {
    "abstract": ABSTRACT_PROMPT,
    "introduction": INTRODUCTION_PROMPT,
    "literature_review": LITERATURE_SYNTHESIS_PROMPT,
    "discussion": DISCUSSION_PROMPT,
    "conclusion": CONCLUSION_PROMPT,
    "methodology": METHODOLOGY_PROMPT,
}


def get_prompt(section_type: str, **kwargs) -> str:
    """
    Get prompt for a section type and format with kwargs.
    
    Args:
        section_type: Type of section (abstract, introduction, etc.)
        **kwargs: Variables to format into prompt (topic, context, etc.)
        
    Returns:
        Formatted prompt string
        
    Example:
        prompt = get_prompt("abstract", topic="AI in Healthcare", context="...")
    """
    if section_type not in SECTION_PROMPTS:
        # Use generic prompt
        prompt = RAG_SECTION_PROMPT
    else:
        prompt = SECTION_PROMPTS[section_type]
    
    return prompt.format(**kwargs)
