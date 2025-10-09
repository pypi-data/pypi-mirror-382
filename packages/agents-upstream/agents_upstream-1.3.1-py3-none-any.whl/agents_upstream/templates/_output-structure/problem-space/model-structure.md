---
version: "2.0.0"
last_updated: "2025-01-09"
author: "Marcelus Fernandes"
template_type: "directory_structure_model"
used_by: ["agent-0-product-service-specialist.md", "agent-workflow-orchestrator.mdc"]
purpose: "Define AI agent workflow directory structure and output conventions for Cursor AI"
---

# AI Agent Workflow Directory Structure

```
project-root/
├── 0-documentation/
│   ├── 0a-projectdocs/
│   │   ├── context.md
│   │   └── annotations.md
│   └── 0b-Interviews/
│       ├── interview-1.md
│       ├── interview-2.md
│       └── ...
│
├── problem-analysis/
│   ├── interviews/
│   │   ├── {name}-analysis.md
│   │   └── consolidated-insights.md
│   ├── pain-points/
│   │   ├── pain-point-clusters.md
│   │   └── pain-point-mapping.md
│   ├── journeys/
│   │   ├── {team}-journey.md
│   │   ├── consolidated-journey.md
│   │   └── journey-breakdowns/
│   └── reports/
│       ├── problem-report.md
│       ├── pain-report.md
│       └── journey-output.md
│
├── solution-design/
│   ├── opportunities/
│   │   ├── opportunities-identification.md
│   │   ├── prioritization-matrix.md
│   │   └── strategic-roadmap.md
│   ├── processes/
│   │   ├── automation-assessment.md
│   │   ├── current-vs-future-state.md
│   │   └── optimized-process-flows.md
│   └── communications/
│       ├── executive-presentation.md
│       ├── change-management-plan.md
│       └── stakeholder-communications.md
│
└── _agents/
    ├── problem-space/
    │   ├── agent-0-product-service-specialist.md
    │   ├── agent-1-qualitative-research-specialist.md
    │   ├── agent-2-painpoint-analysis-specialist.md
    │   ├── agent-3-asis-journey-mapper.md
    │   ├── agent-4-journey-consolidation-specialist.md
    │   └── agent-5-strategic-report-generator.md
    └── solution-space/
        ├── agent-6-strategic-analysis-specialist.md
        ├── agent-7-process-optimization-specialist.md
        └── agent-8-communication-specialist.md
```

## Agent Output Mapping

### Problem Space (Agents 0-5)
| Agent | Output Directory | Files Created |
|-------|------------------|---------------|
| **Agent 0** | `0-documentation/` | Context setup and project initialization |
| **Agent 1** | `problem-analysis/interviews/` | Individual interview analyses |
| **Agent 2** | `problem-analysis/pain-points/` | Pain point clusters and mappings |
| **Agent 3** | `problem-analysis/journeys/` | Individual team journeys |
| **Agent 4** | `problem-analysis/journeys/` | Consolidated journey and breakdowns |
| **Agent 5** | `problem-analysis/reports/` | Strategic problem reports |

### Solution Space (Agents 6-8)
| Agent | Output Directory | Files Created |
|-------|------------------|---------------|
| **Agent 6** | `solution-design/opportunities/` | Strategic opportunities and roadmaps |
| **Agent 7** | `solution-design/processes/` | Process optimization and automation |
| **Agent 8** | `solution-design/communications/` | Executive presentations and change plans |

## File Naming Conventions

### Problem Analysis
- **Interview files:** `{interviewee-name}-analysis.md`
- **Journey files:** `{team-name}-journey.md`
- **Cluster files:** Use descriptive names based on content

### Solution Design
- **Strategic files:** Use template-based naming from `_output-structure/`
- **Process files:** Follow optimization sequence naming
- **Communication files:** Audience-specific naming

### General Rules
1. **Directories:** Use hyphen-case for multi-word names
2. **Files:** Use hyphen-case with .md extension
3. **Variables:** Use `{variable-name}` format for dynamic naming
4. **Consistency:** Follow template naming patterns from `_output-structure/`

## Cursor AI Workflow Support

This structure enables:
1. **Agent Orchestration:** Clear input/output paths for each agent
2. **Template Integration:** Direct mapping to `_output-structure/` templates
3. **Sequential Processing:** Agents 0→1→2→3→4→5→6→7→8 workflow
4. **File Discovery:** Predictable locations for agent file consumption
5. **Output Organization:** Phase-based separation (problem vs solution)
6. **Local Efficiency:** Optimized for Cursor AI local file operations

## Directory Creation Rules

- **Auto-create:** Agents create directories as needed during execution
- **No pre-scaffolding:** Directories emerge from agent workflow execution
- **Template-driven:** Use `_output-structure/` templates for file formats
- **Dynamic naming:** File names adapt based on actual content being processed
