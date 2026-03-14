# ASGARD Project Memory & Instructions

This file serves as a memory for the AI assistant (Antigravity/Claude/etc.) to maintain project-specific design philosophies and conventions.

## Documentation Policy

### 1. Multi-language Support
- **Standard**: All major documentation (especially root README) must be maintained in both English and Chinese.
- **Root README**:
  - `README.md`: English version (Default).
  - `README_CN.md`: Chinese version.
- **Language Switch**: English README must lead with language switch links (e.g., `[English] | [简体中文](README_CN.md)`).

### 2. Design Philosophy
- **Occam's Razor**: Prioritize simplicity. Entities should not be multiplied beyond necessity.
- **Product Perspective**: READMEs should be written from a Product Manager's perspective, focusing on vision, value, and quick onboarding.
- **Progressive Disclosure (渐进式披露)**: 
  - Documentation should be layered. The root README provides the high-level vision and quick start.
  - Deeper complexity, such as detailed architecture and algorithm design, should be "disclosed" progressively through links to the `产品设计` (Product Design) folder for both human and AI agents.
- **Ontological Philosophy (本体论)**:
  - Each BAS (Battery Analysis Skill) should be defined by its electrochemical and physical "essence" (What it is).
  - The orchestration logic (Planner) should rely on these ontological definitions to match algorithms to physical scenarios with "Documentation-Driven" precision.
- **Documentation-Driven Orchestration**: All orchestration logic must be explicitly linked to the `## When to use this skill` section in Skill documentation.

## Technical Conventions
- **Skill Identification**: All skill applicability must be documented under the standardized header `## When to use this skill`.
- **Validation**: Core algorithm changes must be validated against real/mock ESS data (e.g., Huanggang project) and results documented in `BAS/L3-云端层级/test_results.txt`.
