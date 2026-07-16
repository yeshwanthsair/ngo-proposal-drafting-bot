"""
Week 3: Proposal Generation Routes.
Handles NGO proposal drafting, section generation, and export.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.services.proposal_generator import (
    generate_proposal_section,
    generate_full_proposal,
    generate_checklist,
)
from backend.services.llm_service import get_llm
from backend.utils.datetime_utils import get_human_readable_timestamp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/proposals", tags=["Proposals"])


class ProposalRequest(BaseModel):
    """Request body for proposal generation."""
    org_name: str = "Our Organization"
    project_title: str = "Community Development Project"
    problem: str = ""
    beneficiaries: str = ""
    location: str = ""
    duration: str = "12 months"
    budget: str = ""
    activities: str = ""
    section: str = "full_proposal"  # which section to generate


class ProposalResponse(BaseModel):
    """Response from proposal generation."""
    section: str
    content: str
    project_title: str
    generated_at: str


@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    """
    Generate an NGO grant proposal or a specific section.

    Sections available:
    - full_proposal: Complete proposal
    - executive_summary
    - problem_statement
    - objectives
    - methodology
    - budget
    - monitoring_evaluation
    """
    try:
        llm = get_llm()

        project_data = {
            "org_name": request.org_name,
            "project_title": request.project_title,
            "problem": request.problem,
            "beneficiaries": request.beneficiaries,
            "location": request.location,
            "duration": request.duration,
            "budget": request.budget,
            "activities": request.activities,
        }

        logger.info(f"Generating section '{request.section}' for: {request.project_title}")

        content = generate_proposal_section(
            section=request.section,
            project_data=project_data,
            llm=llm,
        )

        return ProposalResponse(
            section=request.section,
            content=content,
            project_title=request.project_title,
            generated_at=get_human_readable_timestamp(),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate proposal: {str(e)}"
        )


@router.post("/checklist")
async def get_checklist(request: ProposalRequest):
    """Generate a proposal submission checklist."""
    try:
        project_data = {
            "org_name": request.org_name,
            "project_title": request.project_title,
        }
        checklist = generate_checklist(project_data)
        return {
            "checklist": checklist,
            "project_title": request.project_title,
            "generated_at": get_human_readable_timestamp(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate checklist: {str(e)}"
        )


@router.get("/sections")
async def list_sections():
    """List all available proposal sections."""
    return {
        "sections": [
            {"id": "full_proposal", "name": "Complete Proposal", "description": "Full grant proposal with all sections"},
            {"id": "executive_summary", "name": "Executive Summary", "description": "Concise overview of the proposal"},
            {"id": "problem_statement", "name": "Problem Statement", "description": "Detailed problem description with evidence"},
            {"id": "objectives", "name": "Project Objectives", "description": "SMART objectives for the project"},
            {"id": "methodology", "name": "Methodology", "description": "Implementation plan and activities"},
            {"id": "budget", "name": "Budget Breakdown", "description": "Detailed budget with justifications"},
            {"id": "monitoring_evaluation", "name": "M&E Plan", "description": "Monitoring and evaluation framework"},
        ]
    }
