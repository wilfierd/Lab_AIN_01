# AI Knowledge & Reasoning Lab

A simple murder mystery solver demonstrating AI knowledge representation and logical reasoning.

## What it does

Uses propositional logic to solve: Who killed whom, with what weapon, and where?

- 3 suspects: Lord Alaric, Lady Morgana, Butler Edwin
- 3 weapons: Silver Dagger, Wine Bottle, Piano Wire
- 3 rooms: Library, Dining Hall, Rose Garden

## How it works

1. **Knowledge Base**: Stores facts using propositional logic (AND, OR, NOT)
2. **Constraints**: Exactly one suspect, weapon, and room must be true
3. **Reasoning**: When you eliminate options, the system deduces what must be true

## Usage

Run the notebook and use commands:

- `list` - Show suspects, weapons, rooms
- `status` - Display known facts (YES/MAYBE)
- `s.no <name>` - Exclude suspect
- `w.no <name>` - Exclude weapon
- `r.no <name>` - Exclude room
- `solve` - Show solution if determined

## Technical Implementation

- `eval_sentence(s, m)` - Evaluates logical sentences
- `model_check(KB, query, symbols)` - Checks entailment
- `exactly_one(symbols)` - Generates mutual exclusivity constraints

## Learning Goal

Demonstrates CS50-style AI concepts:

- How to represent knowledge in AI systems
- How AI makes logical deductions from facts
