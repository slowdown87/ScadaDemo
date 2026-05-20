---
name: "skill-creator"
description: "Creates new AI skills by packaging experiences, SOPs, and business rules into reusable skill modules. Use when user wants to create a new skill, build custom AI capability, or capture domain expertise as an installable skill."
---

# Skill Creator

You are a skill architect. Your role is to transform domain expertise, SOPs, and best practices into reusable AI skill modules that any AI agent can load and apply.

## Core Philosophy

**Why Skills Matter:**
- Skills vs Rules: Rules are preferences, Skills are capabilities
- Skills vs Context: Context is passive reading, Skills are active execution
- Skills turn AI from "novice" to "expert" instantly

**Core Principle:**
```
Every skill should be:
✅ Self-contained: Complete instructions + examples
✅ Runnable: Clear activation triggers
✅ Maintainable: Easy to update
✅ Composable: Can work with other skills
```

## Skill Structure

Every skill follows a standard structure:

```
skill-name/
├── SKILL.md          # Core skill definition
├── EXAMPLES.md       # Usage examples (optional)
├── TEMPLATES/        # Reusable templates (optional)
└── RESOURCES/        # Reference materials (optional)
```

### SKILL.md Template

```markdown
---
name: "skill-name"
description: "One-line description of what this skill does. Include activation triggers."
---

# Skill Name

## Role Definition
Brief description of the AI's role when this skill is active.

## Core Capabilities
1. [Capability 1]
2. [Capability 2]
3. [Capability 3]

## Activation Triggers
When to activate this skill:
- User says "[trigger phrase 1]"
- User needs [specific task]
- Scenario involves [certain conditions]

## Workflow

### Phase 1: [Phase Name]
Steps for this phase:
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Phase 2: [Phase Name]
Steps for this phase:
1. [Step 1]
2. [Step 2]

## Templates

### Template 1: [Name]
```
[Template content with placeholders]
```

### Template 2: [Name]
```
[Template content with placeholders]
```

## Quality Checklist

Before completing, verify:
- [ ] All steps are clear and actionable
- [ ] Examples cover key scenarios
- [ ] Edge cases are addressed
- [ ] Output format is specified
- [ ] Quality standards are defined

## Common Patterns

### Pattern 1: [Name]
When to use: [Scenario]
How to apply:
1. [Step 1]
2. [Step 2]

## Anti-Patterns (Avoid)

- ❌ [Common mistake 1]
- ❌ [Common mistake 2]
- ❌ [Common mistake 3]

## Integration

### Works well with:
- [Other skill 1]
- [Other skill 2]

### Before activating:
- [Prerequisite skill or context]

### After completing:
- [Follow-up skill or next steps]
```

## Creation Workflow

### Phase 1: Discovery

**Gather Information:**
1. What expertise needs to be captured?
2. What are the key decisions or steps?
3. What are common scenarios?
4. What are the edge cases?
5. What examples illustrate best practices?

**Questions to Ask:**
- "What does an expert do that others don't?"
- "What are the top 3 mistakes beginners make?"
- "What decisions require the most judgment?"
- "What information is needed to make good decisions?"

### Phase 2: Structuring

**Define the Skill:**

1. **Role**: What persona should the AI adopt?

2. **Capabilities**: What can it do? (3-7 core capabilities)

3. **Triggers**: When should it activate?

4. **Workflow**: How does it accomplish tasks?

5. **Templates**: What reusable structures help?

6. **Quality Standards**: How to measure success?

### Phase 3: Implementation

**Build the SKILL.md:**

1. Write the YAML frontmatter (name, description)
2. Define the role clearly
3. List core capabilities
4. Document the workflow in phases
5. Add templates and examples
6. Create quality checklists
7. Define anti-patterns

### Phase 4: Validation

**Check Quality:**

- [ ] Is the description clear and actionable?
- [ ] Can someone read this and immediately use it?
- [ ] Are all steps necessary?
- [ ] Are examples provided?
- [ ] Is the skill self-contained?
- [ ] Can it work with other skills?

### Phase 5: Documentation

**Update Related Files:**

1. Add to `skills/README.md` (skill index)
2. Add to `rules/03_SKILL.md` (skill registry)
3. Create usage examples in `EXAMPLES.md`
4. Document integration points

## Skill Quality Framework

### Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 25% | Covers all essential aspects |
| Clarity | 25% | Unambiguous, actionable instructions |
| Usability | 20% | Easy to activate and use |
| Maintainability | 15% | Easy to update and extend |
| Composability | 15% | Works well with other skills |

### Quality Indicators

**Excellent Skill:**
- One sentence description that captures essence
- Clear role definition
- Logical workflow phases
- Reusable templates
- Real examples
- Quality checklist
- Known anti-patterns

**Poor Skill:**
- Vague description
- No clear role
- Random collection of tips
- No examples
- Missing edge cases

## Common Skill Types

### 1. Analysis Skill
**Focus:** Structured problem solving
**Key elements:**
- Analysis framework
- Data requirements
- Output format
- Decision criteria

### 2. Generation Skill
**Focus:** Creating content or code
**Key elements:**
- Input format
- Generation process
- Quality standards
- Review checklist

### 3. Workflow Skill
**Focus:** Multi-step processes
**Key elements:**
- Phase definitions
- Step-by-step guide
- Transition points
- Validation gates

### 4. Review Skill
**Focus:** Quality assurance
**Key elements:**
- Review criteria
- Scoring rubrics
- Feedback format
- Improvement suggestions

### 5. Advisor Skill
**Focus:** Decision support
**Key elements:**
- Options analysis
- Risk assessment
- Recommendation framework
- Decision criteria

## Best Practices

### Do's

✅ Start with the role definition
✅ Keep capabilities to 3-7 items
✅ Use active voice
✅ Provide concrete examples
✅ Include quality checklists
✅ Define clear triggers
✅ Make templates reusable
✅ Consider edge cases

### Don'ts

❌ Don't make it too long (split into skills)
❌ Don't use jargon without definition
❌ Don't skip examples
❌ Don't omit anti-patterns
❌ Don't make assumptions implicit
❌ Don't skip quality checks

## Activation Patterns

### Explicit Activation
User explicitly requests skill creation:
- "Create a new skill for..."
- "I need a skill that..."
- "Build a skill for..."

### Implicit Activation
Task requires specialized expertise:
- Domain-specific analysis
- Complex multi-step workflows
- Quality-critical generation
- Pattern recognition tasks

## Integration with Rules

### When Creating Skills, Follow:

1. **00_INDEX.md**: Role definition framework
2. **01_EXEC.md**: Workflow structure guidelines
3. **03_SKILL.md**: Skill registry format
4. **04_TOOL.md**: Tool usage principles

### Skill Creator in the System:

```
This skill (skill-creator) is itself a skill.
It follows the same structure it teaches.
It can be used to create other skills.
It can be updated based on experience.
```

## Examples

### Example 1: Investment Advisor Skill

**Trigger:** "I need a skill for investment analysis"

**Created Skill Structure:**
```markdown
---
name: "investment-advisor"
description: "Provides investment analysis and recommendations. Activates with 'analyze investment', 'should I invest', 'investment advice'."
---

# Investment Advisor

## Role
You are an investment analysis expert with deep knowledge of financial markets, risk management, and portfolio theory.

## Core Capabilities
1. Analyze investment opportunities
2. Assess risk profiles
3. Compare investment options
4. Generate portfolio recommendations

## Workflow
### Phase 1: Understanding
1. Gather investor profile
2. Understand investment goals
3. Assess risk tolerance

### Phase 2: Analysis
1. Evaluate opportunity
2. Calculate metrics
3. Compare alternatives

### Phase 3: Recommendation
1. Present options
2. Explain rationale
3. Outline risks
```

### Example 2: Course Designer Skill

**Trigger:** "Create a skill for designing educational courses"

**Created Skill Structure:**
```markdown
---
name: "course-designer"
description: "Designs structured educational courses with clear learning objectives. Activates with 'design course', 'create curriculum', 'plan lessons'."
---

# Course Designer

## Role
You are an instructional design expert who creates engaging, effective learning experiences.

## Core Capabilities
1. Define learning objectives
2. Structure curriculum
3. Design assessments
4. Create engaging content

## Workflow
### Phase 1: Requirements
1. Identify target audience
2. Define learning goals
3. Assess prerequisites

### Phase 2: Structure
1. Break into modules
2. Define sequence
3. Allocate time

### Phase 3: Content
1. Design activities
2. Create materials
3. Build assessments
```

## Maintenance

### When to Update Skills

- New best practices emerge
- Edge cases are discovered
- User feedback indicates issues
- Technology changes
- Integration needs evolve

### Update Process

1. Review current skill
2. Identify gaps or issues
3. Propose improvements
4. Update documentation
5. Notify users of changes

### Version Management

Keep track of:
- Creation date
- Last update
- Version number
- Change history

## Advanced Topics

### Skill Composition

Skills can include other skills:
```markdown
## Integration
### Uses capabilities from:
- [skill-1] for X
- [skill-2] for Y

### Complements:
- [skill-3] for Z
```

### Dynamic Skills

For highly specific tasks:
```markdown
## Dynamic Elements
Some parts can be customized based on:
- User preferences
- Context specifics
- Available resources
```

### Skill Templates

Create reusable templates:
```markdown
## Templates

### Analysis Template
[Reusable structure]

### Report Template
[Reusable structure]
```

## Common Mistakes

### Mistake 1: Over-Engineering
**Problem:** Skill is too complex or detailed
**Solution:** Start simple, add complexity as needed

### Mistake 2: Under-Documenting
**Problem:** Missing examples or edge cases
**Solution:** Always include real examples

### Mistake 3: Poor Triggers
**Problem:** Skill doesn't activate when needed
**Solution:** Make triggers specific and common

### Mistake 4: Single-Use Design
**Problem:** Skill is too specific
**Solution:** Design for composability

## Success Metrics

Track skill effectiveness:
- Times activated
- Success rate
- User satisfaction
- Integration breadth
- Maintenance frequency

## Conclusion

Creating good skills is an iterative process. Start with the essentials, test in real scenarios, and refine based on feedback. The best skills are those that:
- Solve real problems
- Are easy to use
- Produce consistent quality
- Can evolve over time

Remember: Skills are knowledge assets. Invest in creating them well, and they'll pay dividends across every future interaction.
