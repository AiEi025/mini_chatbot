---
name: daily-planner
description: Plan and organize the user's day. Use this skill when the user asks for daily planning, task prioritization, or time blocking for their day.
---

# Daily Planner

When the user asks for help planning their day:

1. **Gather context**: Ask the user for their tasks, appointments, and priorities for today. If they haven't provided them, ask clarifying questions.

2. **Identify priorities**: Help the user distinguish between urgent vs. important tasks. Suggest prioritizing:
   - Time-sensitive appointments or deadlines
   - High-impact work that requires focus
   - Quick wins that can be batched together

3. **Estimate time**: For each task, ask for or estimate a realistic duration. Flag potential overcommitment if total time exceeds available hours.

4. **Use `write_todos`**: Create a structured TODO list with the following format for each task:
   - `content`: The specific task description
   - `activeForm`: What the agent is doing when working on it (e.g., "Writing report")
   - `status`: Start with "pending"

5. **Order the list**: Sequence tasks logically:
   - High-energy tasks during the user's peak focus hours
   - Meetings and appointments at fixed times
   - Administrative tasks batched together

6. **Update progress**: As the user completes tasks, use `write_todos` again to mark them "completed" and move the next task to "in_progress".

## Guidelines

- Always confirm the user's available working hours before planning.
- If the user is vague, ask specific questions: "What's the single most important thing to finish today?"
- Suggest breaks and buffer time between high-focus tasks.
- If the user has more tasks than time, ask them to choose what to defer.