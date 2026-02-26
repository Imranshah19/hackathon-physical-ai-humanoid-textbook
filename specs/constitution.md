# Physical AI & Humanoid Robotics Constitution

<!--
Sync Impact Report
- Version: 1.0.0 (initial)
- Created: 2026-01-07
- Templates updated: N/A (initial creation)
- Follow-up: None
-->

## Purpose

This constitution governs the complete hackathon project "Physical AI & Humanoid Robotics". It establishes non-negotiable principles for building educational content that teaches global students humanoid robotics through embodied intelligence and simulation-first development.

## Audience

Global students learning humanoid robotics. Content MUST be accessible to learners with varying backgrounds while maintaining technical accuracy.

## Core Principles

### I. ROS 2 Mandatory

All robotics code, examples, and tutorials MUST use ROS 2 (Robot Operating System 2).

- No ROS 1 code permitted
- Use standard ROS 2 packages and conventions
- Follow ROS 2 naming conventions for nodes, topics, services, and actions
- Target ROS 2 Humble or later distributions
- All dependencies MUST be available in standard ROS 2 repositories

### II. Simulation-First Development

All robot behaviors MUST be validated in simulation before deployment to physical hardware.

- Gazebo or Isaac Sim required for all motion and control examples
- Simulation environments MUST closely match physical robot specifications
- Test coverage in simulation required before any real-robot instructions
- Clear separation between simulation code and hardware-specific code
- Failure modes MUST be tested in simulation first

### III. Physical AI & Embodied Intelligence Focus

Content MUST center on physical AI concepts and embodied intelligence.

- Emphasize sensor-motor integration and real-world interaction
- Cover perception, planning, and control as unified systems
- Include proprioception, force feedback, and environmental awareness
- Demonstrate learning from physical interaction
- Avoid purely theoretical or disembodied AI approaches

### IV. No Hallucinations

All content MUST be factually accurate and verifiable.

- Every claim MUST be traceable to source material or reproducible code
- No invented APIs, functions, or package names
- No fabricated research citations or statistics
- Code examples MUST compile and run as written
- If uncertain, explicitly state uncertainty rather than fabricate

### V. Clear Technical Communication

Explanations MUST be clear, simple, and accessible.

- Use plain technical English
- Define all technical terms on first use
- Provide context before introducing complexity
- Use diagrams and visual aids where helpful
- Avoid jargon without explanation
- Each concept builds on previously introduced material

### VI. RAG-Based Answer Constraint

The chatbot assistant MUST answer only from book content.

- Responses MUST be grounded in textbook material
- Support answering from user-selected text passages only
- Cite specific chapters, sections, or pages when answering
- If information is not in the book, state this explicitly
- Never supplement with external knowledge not in the source material

## Additional Constraints

### Content Personalization

Content MUST support personalized learning paths.

- Modular chapter structure allowing non-linear progression
- Difficulty indicators for each section
- Prerequisites clearly stated per module
- Adaptive examples based on learner background
- Multiple explanation depths available per concept

### Urdu Translation Support

Content MUST be structured to support Urdu translation.

- Use consistent terminology throughout (enables glossary mapping)
- Avoid idioms and culturally-specific references
- Maintain simple sentence structures
- Provide translation hooks for technical terms
- Right-to-left text rendering considerations in code examples

### Code Standards

- Python 3.10+ for all non-ROS code
- Type hints required for all functions
- Docstrings required for all public interfaces
- Unit tests required for all utility functions
- Examples MUST include expected output

### Safety Requirements

- All robot control code MUST include emergency stop handling
- Force/torque limits MUST be explicitly defined
- Workspace boundaries MUST be enforced in code
- Human-robot interaction examples MUST include safety protocols

## Governance

### Amendment Process

1. Propose change with rationale
2. Review impact on existing content
3. Update version number per semantic versioning
4. Document in change log
5. Propagate changes to dependent materials

### Compliance

- All pull requests MUST verify constitution compliance
- Code reviews MUST check principle adherence
- Content additions require principle alignment review
- Deviations require explicit justification and approval

### Version Policy

- MAJOR: Principle removal or incompatible redefinition
- MINOR: New principle added or significant expansion
- PATCH: Clarifications and non-semantic refinements

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
