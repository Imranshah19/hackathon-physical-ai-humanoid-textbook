---
id: 001
title: Physical AI Robotics Constitution
stage: constitution
date: 2026-01-07
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: hackathon
command: /sp.constitution
labels: ["constitution", "physical-ai", "humanoid-robotics", "ros2"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/constitution.md
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

Create a global Spec-Kit Plus constitution.

File path:
specs/constitution.md

Name:
/sp.constitution

Purpose:
This constitution governs the complete hackathon project
"Physical AI & Humanoid Robotics".

Rules:
- Constitution is written once and reused everywhere
- All modules must follow it
- Physical AI and embodied intelligence focus
- Simulation before real robots
- ROS 2 is mandatory
- No hallucinations
- Clear explanations only

Audience:
Global students learning humanoid robotics.

RAG Rules:
- Chatbot answers only from book content
- Must support answering from user-selected text only

Bonus Rules:
- Content must support personalization
- Content must support Urdu translation

Write in clear, simple technical English.

## Response snapshot

Created constitution v1.0.0 with 6 core principles:
1. ROS 2 Mandatory - All code must use ROS 2
2. Simulation-First Development - Validate in simulation before hardware
3. Physical AI & Embodied Intelligence Focus - Center on embodied AI concepts
4. No Hallucinations - Factually accurate and verifiable content only
5. Clear Technical Communication - Plain, accessible technical English
6. RAG-Based Answer Constraint - Chatbot answers from book content only

Additional constraints for personalization, Urdu translation, code standards, and safety requirements included.

## Outcome

- Impact: Created foundational governance document for entire project
- Tests: N/A (documentation)
- Files: 2 files created (specs/constitution.md, .specify/memory/constitution.md)
- Next prompts: Create feature specifications following constitution principles
- Reflection: Constitution establishes clear boundaries for ROS 2, simulation-first approach, and RAG-based learning assistant

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Apply constitution to first feature spec
