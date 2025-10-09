---
version: "1.0.0"
last_updated: "2025-09-02"
author: "Marcelus Fernandes"
template_type: "workflow_rules"
used_by: ["all agents"]
purpose: "Define workflow progression rules and file operation guidelines"
---

# Product Development Workflow Rules

## 1. CONTEXT FIRST
- Always check `/0-documentation/broad-context.md` first
- All new concepts must be documented in `/0-documentation/`
- Reference materials go in `/0-documentation/0a-projectdocs/`

## 2. SEQUENTIAL PROGRESSION
### Main Phases
- Problem (1) → Solution (2) → Development (3)
- Never skip steps in the numerical sequence
- Higher numbers can reference lower, but not vice-versa

### Sub-Phase Progression
Each main phase follows an alphabetical progression (a→b→c→d→e) representing specific steps:

#### 0-documentation/
- 0a-projectdocs/: Project documentation and references

#### 1-problem/
- 1a-research/: Initial research and data gathering
- 1b-analysis/: Problem analysis
- 1c-validation/: Problem statement validation
- 1d-problem-output/: Final problem documentation

#### 2-solution/
- 2a-ideation/: Solution brainstorming
- 2b-validation/: Solution validation
- 2c-priotization/: Feature prioritization
- 2d-refinement/: Solution refinement
- 2e-solution-output/: Final solution documentation

#### 3-development/
- 3a-planning/: Development planning
- 3b-technical-specs/: Technical specifications
- 3c-implementation/: Implementation details
- 3d-development-output/: Development documentation

## 3. OUTPUT HANDLING
- Each major phase has an output folder (ends with `-output`)
- Outputs are immutable once finalized
- New iterations create new files, don't modify outputs

## 4. DOCUMENT TYPES
- `*-template.md`: Base structure for new documents
- `*-list.md`: Enumeration of items
- `*-report.md`: Analysis and conclusions
- `*-export.md`: External system format (e.g., Jira)

## 5. TASK HIERARCHY
- Epics → User Stories → Tasks
- Always maintain this order
- Each level must reference its parent

## 6. FILE OPERATIONS
- New files follow existing naming patterns in their directory
- Templates must be used when available
- Related files stay in the same subfolder

## 7. CROSS-REFERENCES
- Use relative paths for references
- Always reference the most recent output document
- Link to specific sections when possible

## 8. VERSION CONTROL
- Don't modify completed phase documents
- Create new versions in the next phase
- Keep change history in annotations.md

## 9. SEARCH PRIORITY
1. Check phase-specific output folder
2. Look in current phase main folder
3. Reference previous phase outputs
4. Consult documentation if needed

## 10. AUTOMATION RULES
- Templates guide document structure
- Follow folder letter sequence (a→b→c→d)
- Respect phase boundaries (0→1→2→3)
