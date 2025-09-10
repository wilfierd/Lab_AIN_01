# Logic-Based Mystery Solver

A Python implementation of propositional logic and model checking for solving murder mystery puzzles.

## Overview

This project demonstrates AI logical reasoning by solving a murder mystery with 3 suspects, 3 weapons, and 3 rooms using propositional logic and model checking algorithms.

## Key Features

- Propositional logic framework (Symbol, Not, And, Or)
- Model checking algorithm for logical entailment
- Interactive shell for adding clues and solving mysteries
- Exactly-one constraints ensuring unique solutions

### Basic Commands

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

## Learning Objectives

- Propositional logic and model checking
- Knowledge representation in AI
- Constraint satisfaction problems
- Logical inference algorithms

## Requirements

Python 3.7+ (no external dependencies)
