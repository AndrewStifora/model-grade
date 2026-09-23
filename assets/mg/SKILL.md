---
name: mg
description: Shorthand for /model-grade. Grades a prompt and picks the cheapest Claude model and effort level that will complete it well; takes the same arguments as /model-grade.
disable-model-invocation: true
argument-hint: "[--run] [--json] <prompt text | @file>   (no arguments = grade the previous request)"
model: sonnet
effort: medium
allowed-tools: Skill(model-grade), Read, Glob, Grep
---

This is an alias for the model-grade skill. Arguments passed to it: $ARGUMENTS

Invoke the model-grade skill now with the Skill tool (skill `model-grade`, args exactly as given above) and follow its instructions to the letter. If the arguments line above is empty or still reads `$ARGUMENTS`, pass no arguments, and model-grade grades the previous request as usual.
