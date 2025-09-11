#!/usr/bin/env python3
"""
AI Murder Mystery Solver - Command Line Interface
Uses propositional logic to solve: Who killed whom, with what weapon, and where?

Based on CS50 AI concepts demonstrating knowledge representation and logical reasoning.
"""

from __future__ import annotations
import itertools
import sys
import shlex
from typing import List, Dict


class Sentence:
    """Base class for logical sentences"""
    pass


class Symbol(Sentence):
    """Propositional symbol (e.g., 'S_Lord_Alaric')"""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return self.name


class Not(Sentence):
    """Logical negation (¬)"""
    def __init__(self, x: Sentence):
        self.x = x
    
    def __repr__(self):
        return f"¬{self.x}"


class And(Sentence):
    """Logical conjunction (∧)"""
    def __init__(self, *xs: Sentence):
        self.xs = xs
    
    def __repr__(self):
        return "(" + " ∧ ".join(map(str, self.xs)) + ")"


class Or(Sentence):
    """Logical disjunction (∨)"""
    def __init__(self, *xs: Sentence):
        self.xs = xs
    
    def __repr__(self):
        return "(" + " ∨ ".join(map(str, self.xs)) + ")"


def eval_sentence(s: Sentence, model: dict) -> bool:
    """Evaluate a logical sentence in a given model"""
    if isinstance(s, Symbol):
        return bool(model.get(s.name, False))
    if isinstance(s, Not):
        return not eval_sentence(s.x, model)
    if isinstance(s, And):
        return all(eval_sentence(x, model) for x in s.xs)
    if isinstance(s, Or):
        return any(eval_sentence(x, model) for x in s.xs)
    raise TypeError(f"Unknown sentence type: {type(s)}")


def model_check(KB: List[Sentence], query: Sentence, symbols: List[Symbol]) -> bool:
    """Check if KB entails query using model checking"""
    names = [s.name for s in symbols]
    for vals in itertools.product([False, True], repeat=len(names)):
        model = dict(zip(names, vals))
        if all(eval_sentence(s, model) for s in KB):
            if not eval_sentence(query, model):
                return False
    return True


def exactly_one(symbols: List[Symbol]) -> List[Sentence]:
    """Generate constraints ensuring exactly one of the symbols is true"""
    axioms = [Or(*symbols)]  # At least one must be true
    # At most one can be true (mutual exclusion)
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            axioms.append(Not(And(symbols[i], symbols[j])))
    return axioms


# ===== Domain Knowledge =====
SUSPECTS = ["Lord Alaric", "Lady Morgana", "Butler Edwin"]
WEAPONS = ["Silver Dagger", "Broken Wine Bottle", "Piano Wire"]
ROOMS = ["Library", "Dining Hall", "Rose Garden"]


def build_symbols():
    """Create symbols for all suspects, weapons, and rooms"""
    S = {name: Symbol(f"S_{name}") for name in SUSPECTS}
    W = {name: Symbol(f"W_{name}") for name in WEAPONS}
    R = {name: Symbol(f"R_{name}") for name in ROOMS}
    ALL = list(S.values()) + list(W.values()) + list(R.values())
    return S, W, R, ALL


class MurderMystery:
    """Main class for the murder mystery logic solver"""
    
    def __init__(self):
        self.S, self.W, self.R, self.ALL = build_symbols()
        self.KB: List[Sentence] = []
        
        # Add exactly-one constraints for each category
        self.KB += exactly_one(list(self.S.values()))  # Exactly one suspect
        self.KB += exactly_one(list(self.W.values()))  # Exactly one weapon
        self.KB += exactly_one(list(self.R.values()))  # Exactly one room

    def add_fact(self, *sentences: Sentence):
        """Add facts to knowledge base, avoiding duplicates"""
        existing = {repr(s) for s in self.KB}
        for sentence in sentences:
            if repr(sentence) not in existing:
                self.KB.append(sentence)
                existing.add(repr(sentence))

    def _has_model(self, KB: List[Sentence]) -> bool:
        """Check if there exists at least one satisfying model for KB"""
        names = [s.name for s in self.ALL]
        for vals in itertools.product([False, True], repeat=len(names)):
            model = dict(zip(names, vals))
            if all(eval_sentence(s, model) for s in KB):
                return True
        return False

    def consistent_with(self, *facts: Sentence) -> bool:
        """Check if adding facts would keep KB consistent"""
        return self._has_model(self.KB + list(facts))

    def show_status(self):
        """Display current knowledge state (YES/MAYBE, hiding NO)"""
        if not self._has_model(self.KB):
            print("❌ Knowledge base is inconsistent — no valid solutions exist.")
            return
        
        # ANSI color codes for terminal output
        GREEN = "\033[92m" if sys.stdout.isatty() else ""
        RESET = "\033[0m" if sys.stdout.isatty() else ""
        
        print("\n📊 Current Status:")
        print("=" * 40)
        
        for category, symbols in [("Suspects", self.S), ("Weapons", self.W), ("Rooms", self.R)]:
            print(f"\n{category}:")
            for name, symbol in symbols.items():
                if model_check(self.KB, symbol, self.ALL):
                    print(f"  {GREEN}{name}: YES{RESET}")
                elif not model_check(self.KB, Not(symbol), self.ALL):
                    print(f"  {name}: MAYBE")

    def get_candidates(self):
        """Get all possible (suspect, weapon, room) combinations"""
        names = [s.name for s in self.ALL]
        candidates = set()
        
        for vals in itertools.product([False, True], repeat=len(names)):
            model = dict(zip(names, vals))
            if all(eval_sentence(s, model) for s in self.KB):
                suspect = next(k[2:] for k, v in model.items() if k.startswith("S_") and v)
                weapon = next(k[2:] for k, v in model.items() if k.startswith("W_") and v)
                room = next(k[2:] for k, v in model.items() if k.startswith("R_") and v)
                candidates.add((suspect, weapon, room))
        
        return sorted(candidates)

    def get_solution(self):
        """Return unique solution if KB forces exactly one possibility"""
        candidates = self.get_candidates()
        if not candidates:
            return None
        
        suspects = {s for s, _, _ in candidates}
        weapons = {w for _, w, _ in candidates}
        rooms = {r for _, _, r in candidates}
        
        if len(suspects) == 1 and len(weapons) == 1 and len(rooms) == 1:
            return (next(iter(suspects)), next(iter(weapons)), next(iter(rooms)))
        return None

    def exclude_item(self, category: str, name: str):
        """Exclude an item from consideration"""
        symbol_dict = {"s": self.S, "w": self.W, "r": self.R}[category]
        target = self._resolve_name(symbol_dict, name)
        
        if not target:
            print(f"❌ No match found for '{name}'")
            return
        
        fact = Not(target)
        
        # Check if already excluded
        if any(repr(fact) == repr(s) for s in self.KB):
            print(f"ℹ️  {target} is already excluded")
            return
        
        # Check consistency
        if not self.consistent_with(fact):
            print(f"❌ Cannot exclude {target} - would make knowledge base inconsistent")
            return
        
        self.add_fact(fact)
        print(f"✅ Added: {fact}")

    def assert_item(self, category: str, name: str):
        """Assert that an item is the answer"""
        symbol_dict = {"s": self.S, "w": self.W, "r": self.R}[category]
        target = self._resolve_name(symbol_dict, name)
        
        if not target:
            print(f"❌ No match found for '{name}'")
            return
        
        # Check if already asserted
        if any(repr(target) == repr(s) for s in self.KB):
            print(f"ℹ️  {target} is already asserted")
            return
        
        # Check consistency
        if not self.consistent_with(target):
            print(f"❌ Cannot assert {target} - would make knowledge base inconsistent")
            return
        
        self.add_fact(target)
        print(f"✅ Added: {target}")

    def _resolve_name(self, symbol_dict: Dict[str, Symbol], text: str):
        """Resolve partial name to symbol with fuzzy matching"""
        text_lower = text.lower()
        
        # Try exact match first
        for name, symbol in symbol_dict.items():
            if name.lower() == text_lower:
                return symbol
        
        # Try substring match
        matches = [symbol for name, symbol in symbol_dict.items() 
                  if text_lower in name.lower()]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print("🤔 Ambiguous name. Did you mean:")
            for name, symbol in symbol_dict.items():
                if text_lower in name.lower():
                    print(f"  - {name}")
            return None
        
        return None


def show_help():
    """Display help message"""
    help_text = """
🔍 AI Murder Mystery Solver - Commands

Basic Commands:
  help                         Show this help message
  list                         List all suspects, weapons, and rooms
  status                       Show current facts (YES/MAYBE)
  candidates                   Show all possible solutions
  solve                        Show solution if uniquely determined
  quit / exit                  Exit the program

Investigation Commands:
  s.no <name...>              Exclude suspect(s)
  w.no <name...>              Exclude weapon(s)
  r.no <name...>              Exclude room(s)
  s.yes <name>                Assert this suspect is guilty
  w.yes <name>                Assert this weapon was used
  r.yes <name>                Assert this room is the crime scene

Tips:
  • You can use partial names: 'w.no wire' excludes 'Piano Wire'
  • Multiple names with commas: 's.no Alaric, Edwin'
  • Names are case-insensitive

Example Investigation:
  > s.no Lord Alaric          # Exclude Lord Alaric
  > w.no Silver Dagger        # Exclude Silver Dagger
  > status                    # Check what we know
  > solve                     # See if solution is determined
"""
    print(help_text)


def list_domain():
    """Display all suspects, weapons, and rooms"""
    print("\n🏰 The Cast and Props:")
    print("=" * 40)
    print(f"🕵️  Suspects: {', '.join(SUSPECTS)}")
    print(f"⚔️   Weapons : {', '.join(WEAPONS)}")
    print(f"🏛️   Rooms   : {', '.join(ROOMS)}")


def parse_multiple_names(args: List[str]) -> List[str]:
    """Parse comma-separated names from command arguments"""
    raw_text = " ".join(args)
    parts = [p.strip() for p in raw_text.split(",") if p.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for part in parts:
        key = part.lower()
        if key not in seen:
            seen.add(key)
            result.append(part)
    
    return result


def main():
    """Main CLI loop"""
    mystery = MurderMystery()
    
    print("🔎 THE MANSION MURDER MYSTERY")
    print("=" * 50)
    print("Use logical reasoning to solve the crime!")
    print("Type 'help' for commands, 'quit' to exit.\n")
    
    list_domain()
    
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye, detective!")
            break
        
        if not user_input:
            continue
        
        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            continue
        
        command = args[0].lower()
        
        if command in ("quit", "exit", "q"):
            print("👋 Goodbye, detective!")
            break
        
        elif command == "help":
            show_help()
        
        elif command == "list":
            list_domain()
        
        elif command == "status":
            mystery.show_status()
        
        elif command in ("candidates", "cand"):
            candidates = mystery.get_candidates()
            print(f"\n🎯 {len(candidates)} possible solution(s):")
            for i, (suspect, weapon, room) in enumerate(candidates, 1):
                print(f"  {i}. {suspect} with {weapon} in {room}")
        
        elif command == "solve":
            solution = mystery.get_solution()
            if solution:
                suspect, weapon, room = solution
                print("\n🎉 CASE SOLVED!")
                print("=" * 30)
                print(f"🔍 Culprit: {suspect}")
                print(f"⚔️  Weapon : {weapon}")
                print(f"🏛️  Scene  : {room}")
            else:
                print("🤔 Not enough evidence yet. Keep investigating!")
        
        elif command in ("s.no", "w.no", "r.no", "s.yes", "w.yes", "r.yes"):
            if len(args) < 2:
                print("❌ Missing name. Usage: s.no <name>")
                continue
            
            category = command[0]  # 's', 'w', or 'r'
            is_assertion = command.endswith(".yes")
            
            names = parse_multiple_names(args[1:])
            for name in names:
                if is_assertion:
                    mystery.assert_item(category, name)
                else:
                    mystery.exclude_item(category, name)
        
        else:
            print(f"❌ Unknown command: '{command}'. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
