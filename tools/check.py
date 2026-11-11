"""Run the clean-contour check over a repository's own diff (or all of it).

    python3 tools/check.py --repo DIR --diff A..B --cheap-cmd '<cmd>' [--strong-cmd '<cmd>']
    python3 tools/check.py --repo DIR --all --cheap-cmd '<cmd>' [--strong-cmd '<cmd>']
    python3 tools/check.py --repo DIR --diff A..B --dry-run
    python3 tools/check.py --selftest

Candidates come from tools/search.py (`load_signs`, `hits_for`); the skill
parser, `build_prompt`, `parse_verdict` and `call_model` come from
exam/bin/exam (loaded with importlib, it has no .py extension). Which cards go
to the cheap model and which to the strong one is read from
`skills/clean-contour-check/routing.json`, built from the exam results.

`--cheap-cmd` and `--strong-cmd` are shell commands with the same stdin→stdout
contract as `bin/exam --model-cmd`: the prompt on stdin, one answer line on
stdout. `--strong-cmd` may be omitted: then a cheap `dirty` is printed as
`candidate` and strong-card candidates are listed as not checked.

Output: one skill line per candidate, then a summary table per card.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ROUTING_PATH = ROOT / "skills" / "clean-contour-check" / "routing.json"
EXAM_PATH = ROOT / "exam" / "bin" / "exam"

FRAGMENT_LINES = 40          # lines centred on the hit line, clipped to the file
DEFAULT_MAX = 300


class CheckError(Exception):
    """Input error: routing, diff, call. The run is void."""


# --------------------------------------------------------------------------
# Reuse from tools/search.py and exam/bin/exam
# --------------------------------------------------------------------------

def _load_exam():
    loader = importlib.machinery.SourceFileLoader("exam", str(EXAM_PATH))
    spec = importlib.util.spec_from_loader("exam", loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["exam"] = mod          # @dataclass looks the module up by name
    loader.exec_module(mod)
    return mod


def _load_search():
    loader = importlib.machinery.SourceFileLoader("search", str(HERE / "search.py"))
    spec = importlib.util.spec_from_loader("search", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------

def load_routing() -> dict:
    with open(ROUTING_PATH, encoding="utf-8") as f:
        return json.load(f)


def card_route(routing: dict, card: str) -> str:
    if card in routing["cheap"]:
        return "cheap"
    if card in routing["strong"]:
        return "strong"
    raise CheckError(f"card {card} is in neither routing list (cheap/strong)")


# --------------------------------------------------------------------------
# Candidates and fragments
# --------------------------------------------------------------------------

@dataclass
class Candidate:
    card: str
    relpath: str
    line: int
    text: str
    code: str = ""          # the fragment build_prompt needs
    path: str = ""          # "relpath:line"


def fragment_for(repo: Path, relpath: str, line: int) -> str:
    """40 lines centred on the hit line, clipped to the file."""
    p = repo / relpath
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(0, line - 1 - FRAGMENT_LINES // 2)
    end = min(len(lines), start + FRAGMENT_LINES)
    return "\n".join(lines[start:end])


def collect_candidates(repo: Path, signs: dict, langs: list, cards: list) -> list[Candidate]:
    hits = _search.hits_for(repo, signs, langs, cards)
    out = []
    for card, rel, n, text in hits:
        c = Candidate(card=card, relpath=rel, line=n, text=text)
        c.code = fragment_for(repo, rel, n)
        c.path = f"{rel}:{n}"
        out.append(c)
    return out


def diff_hunks(repo: Path, diff_range: str) -> dict[str, set[int]]:
    """Map relpath -> set of line numbers on the new side that are in an
    added/changed hunk. `git -C <repo> diff -U0 A..B`."""
    p = subprocess.run(["git", "-C", str(repo), "diff", "-U0", diff_range],
                       capture_output=True, text=True, check=False)
    if p.returncode != 0:
        raise CheckError(f"git diff failed: {(p.stderr or '').strip()[:200]}")
    changed: dict[str, set[int]] = {}
    cur = None
    for ln in p.stdout.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]
            changed.setdefault(cur, set())
        elif ln.startswith("@@"):
            if cur is None:
                continue
            # @@ -a,b +c,d @@
            try:
                new = ln.split("+", 1)[1].split(" ", 1)[0]
                start, _, count = new.partition(",")
                start = int(start)
                count = int(count) if count else 1
            except (ValueError, IndexError):
                continue
            for i in range(start, start + count):
                changed[cur].add(i)
    return changed


def filter_by_diff(candidates: list[Candidate], changed: dict[str, set[int]]) -> list[Candidate]:
    return [c for c in candidates if c.line in changed.get(c.relpath, set())]


# --------------------------------------------------------------------------
# Model calls
# --------------------------------------------------------------------------

def run_models(candidates: list[Candidate], skill, routing: dict, cheap_cmd: str,
               strong_cmd: str | None, jobs: int, timeout: int, retries: int) -> dict[int, dict]:
    """Run the cheap model on cheap-card candidates and the strong model on
    strong-card candidates plus cheap `dirty`/`unclear`. Returns a map from
    candidate index to a result dict with `cheap` and `strong` sub-results."""
    exam = _exam
    results: dict[int, dict] = {}

    def ask(cmd: str, c: Candidate) -> dict:
        it = exam.Item(id="", card=c.card, expected="", path=c.path, why="", source="", code=c.code)
        r = exam.call_model(cmd, exam.build_prompt(skill, it), timeout, retries)
        v, reason = exam.parse_verdict(r["raw"]) if not r["error"] else (None, "")
        return dict(r, verdict=v, reason=reason)

    cheap_idx = [i for i, c in enumerate(candidates) if card_route(routing, c.card) == "cheap"]
    strong_idx = [i for i, c in enumerate(candidates) if card_route(routing, c.card) == "strong"]

    def one_cheap(i):
        return i, ask(cheap_cmd, candidates[i])

    def one_strong(i):
        return i, ask(strong_cmd, candidates[i])

    # Phase 1: cheap cards -> cheap model; strong cards -> strong model (or skip).
    with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        for i, r in ex.map(one_cheap, cheap_idx):
            results.setdefault(i, {})["cheap"] = r
        if strong_cmd:
            for i, r in ex.map(one_strong, strong_idx):
                results.setdefault(i, {})["strong"] = r

    # Phase 2: cheap dirty/unclear -> strong model.
    if strong_cmd:
        escalate = [i for i in cheap_idx
                    if results[i]["cheap"].get("verdict") in ("dirty", "unclear")]
        with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            for i, r in ex.map(one_strong, escalate):
                results.setdefault(i, {})["strong"] = r

    return results


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def model_line(c: Candidate, raw: str) -> str:
    """The model's output line with the real file:line and card substituted."""
    for ln in raw.strip().splitlines():
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) >= 4 and parts[3].lower() in ("dirty", "clean", "unclear"):
            return f"{c.path} | {c.card} | " + " | ".join(parts[2:])
    flat = " ".join(raw.split())[:200]
    return f"{c.path} | {c.card} |  | unclear | no answer line in the format: {flat}"


def render(candidates: list[Candidate], results: dict[int, dict], routing: dict,
           strong_cmd: str | None) -> str:
    out = []
    order = sorted(range(len(candidates)),
                   key=lambda i: (int(candidates[i].card[1:]), candidates[i].relpath, candidates[i].line))
    for i in order:
        c = candidates[i]
        route = card_route(routing, c.card)
        r = results.get(i, {})
        # The final verdict is the strong model's when it was asked.
        final = r.get("strong") or r.get("cheap")
        if route == "strong" and not strong_cmd:
            out.append(f"{c.path} | {c.card} |  | not checked | strong card, no --strong-cmd")
            continue
        if final is None:
            out.append(f"{c.path} | {c.card} |  | not checked | no model call")
            continue
        if final.get("error"):
            out.append(f"{c.path} | {c.card} |  | error | {final['error']}")
            continue
        if route == "cheap" and not strong_cmd and final.get("verdict") == "dirty":
            # No strong model to confirm: a cheap dirty is only a candidate.
            out.append(f"{c.path} | {c.card} |  | candidate | cheap model flagged dirty")
            continue
        out.append(model_line(c, final.get("raw", "")))

    # Summary per card.
    per: dict[str, dict] = {}
    for i, c in enumerate(candidates):
        route = card_route(routing, c.card)
        s = per.setdefault(c.card, {"candidates": 0, "cheap_dirty": 0, "strong_dirty": 0, "unclear": 0})
        s["candidates"] += 1
        r = results.get(i, {})
        cheap = r.get("cheap")
        strong = r.get("strong")
        if route == "cheap" and cheap and cheap.get("verdict") == "dirty":
            s["cheap_dirty"] += 1
        if strong and strong.get("verdict") == "dirty":
            s["strong_dirty"] += 1
        final = strong or cheap
        if final and final.get("verdict") == "unclear":
            s["unclear"] += 1

    out.append("")
    out.append(f"{'card':<6}{'candidates':>12}{'cheap dirty':>13}{'strong dirty':>14}{'unclear':>9}")
    for code in sorted(per, key=lambda x: int(x[1:])):
        s = per[code]
        out.append(f"{code:<6}{s['candidates']:>12}{s['cheap_dirty']:>13}"
                   f"{s['strong_dirty']:>14}{s['unclear']:>9}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Fake model for --fake (tests)
# --------------------------------------------------------------------------

def fake_model(kind: str) -> int:
    sys.stdin.read()
    verdict = {"dirty": "dirty", "clean": "clean", "unclear": "unclear"}.get(kind)
    if verdict is None:
        print("unknown fake kind", file=sys.stderr)
        return 1
    print(f"x.py:1 | C0 | yes, yes | {verdict} | fake answer")
    return 0


# --------------------------------------------------------------------------
# Self test
# --------------------------------------------------------------------------

def selftest() -> int:
    fails: list[str] = []
    n = 0

    def case(name, good):
        nonlocal n
        n += 1
        if good:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name}")
            fails.append(name)

    me = f"{sys.executable} {Path(__file__).resolve()}"

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "app.py").write_text(
            "def f():\n"
            "    x = 1\n"
            "    return x\n"
            "def g(old):\n"
            "    if not rows:\n"
            "        return 'none'\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True)

        # Change two lines: one that hits a sign, one that does not.
        (repo / "app.py").write_text(
            "def f():\n"
            "    x = 1\n"
            "    if not rows:\n"
            "        return 'empty'\n"
            "    return x\n"
            "def g(old):\n"
            "    if not rows:\n"
            "        return 'none'\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "change"], check=True)

        # --diff keeps only candidates on changed lines.
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--repo", str(repo), "--diff", "HEAD~1..HEAD",
                            "--cheap-cmd", f"{me} --fake clean", "--dry-run"],
                           capture_output=True, text=True, check=False)
        case("--diff keeps only candidates on changed lines",
             p.returncode == 0 and "app.py:3 " in p.stdout and "app.py:7 " not in p.stdout)

        # A cheap card's dirty goes to the strong command.
        marker = repo / "marker"
        strong = f"{me} --fake dirty; touch {marker}"
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--repo", str(repo), "--diff", "HEAD~1..HEAD",
                            "--cheap-cmd", f"{me} --fake dirty",
                            "--strong-cmd", strong],
                           capture_output=True, text=True, check=False)
        case("a cheap card's dirty goes to the strong command",
             p.returncode == 0 and marker.exists())

        # A cheap clean does not go to the strong command.
        marker.unlink(missing_ok=True)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--repo", str(repo), "--diff", "HEAD~1..HEAD",
                            "--cheap-cmd", f"{me} --fake clean",
                            "--strong-cmd", strong],
                           capture_output=True, text=True, check=False)
        case("a cheap clean does not go to the strong command",
             p.returncode == 0 and not marker.exists())

        # Over --max-candidates exits 2 without calling the model.
        marker.unlink(missing_ok=True)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--repo", str(repo), "--all",
                            "--cheap-cmd", f"{me} --fake dirty; touch {marker}",
                            "--max-candidates", "0"],
                           capture_output=True, text=True, check=False)
        case("over --max-candidates exits 2 without calling the model",
             p.returncode == 2 and not marker.exists())

        # An unknown card in routing is an error.
        bad_routing = {"cheap": ["C2"], "strong": ["C1"], "measured": "x"}
        try:
            card_route(bad_routing, "C99")
            refused = False
        except CheckError:
            refused = True
        case("an unknown card in routing is an error", refused)

    print()
    if fails:
        print(f"check --selftest: {len(fails)} of {n} failed")
        return 1
    print(f"check --selftest: {n} of {n} passed")
    return 0


# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="repository directory")
    ap.add_argument("--diff", help="git range A..B; only candidates on added/changed lines")
    ap.add_argument("--all", action="store_true", help="every candidate")
    ap.add_argument("--cheap-cmd", help="shell command for the cheap model")
    ap.add_argument("--strong-cmd", help="shell command for the strong model")
    ap.add_argument("--dry-run", action="store_true", help="print candidates and the plan, no model calls")
    ap.add_argument("--max-candidates", type=int, default=DEFAULT_MAX)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fake", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)

    if a.fake:
        return fake_model(a.fake)
    if a.selftest:
        return selftest()

    global _exam, _search
    _exam = _load_exam()
    _search = _load_search()

    try:
        if not a.repo:
            raise CheckError("--repo is required")
        if bool(a.diff) == bool(a.all):
            raise CheckError("exactly one of --diff or --all is required")
        routing = load_routing()

        repo = Path(a.repo)
        signs = _search.load_signs()
        langs = list(_search.ALL_LANGS)
        cards = list(signs["cards"].keys())

        candidates = collect_candidates(repo, signs, langs, cards)
        if a.diff:
            changed = diff_hunks(repo, a.diff)
            candidates = filter_by_diff(candidates, changed)

        # Validate routing for every candidate card.
        for c in candidates:
            card_route(routing, c.card)

        if len(candidates) > a.max_candidates:
            per: dict[str, int] = {}
            for c in candidates:
                per[c.card] = per.get(c.card, 0) + 1
            print(f"too many candidates: {len(candidates)} > {a.max_candidates}", file=sys.stderr)
            for code in sorted(per, key=lambda x: int(x[1:])):
                print(f"  {code}: {per[code]}", file=sys.stderr)
            return 2

        if a.dry_run:
            per: dict[str, int] = {}
            for c in candidates:
                per[c.card] = per.get(c.card, 0) + 1
            print("Candidates per card:")
            for code in sorted(per, key=lambda x: int(x[1:])):
                route = card_route(routing, code)
                print(f"  {code} ({route}): {per[code]}")
            print(f"\nPlan: {len(candidates)} candidates; "
                  f"cheap model on cheap cards, strong model on strong cards"
                  f"{' and cheap dirty/unclear' if a.strong_cmd else ''}.")
            for c in candidates:
                print(f"  {c.path} | {c.card}")
            return 0

        if not a.cheap_cmd:
            raise CheckError("--cheap-cmd is required (unless --dry-run)")

        skill = _exam.parse_skill(
            (ROOT / "skills" / "clean-contour-check" / "SKILL.md").read_text(encoding="utf-8"))
        results = run_models(candidates, skill, routing, a.cheap_cmd, a.strong_cmd,
                             a.jobs, a.timeout, a.retries)
        print(render(candidates, results, routing, a.strong_cmd))
        return 0
    except CheckError as e:
        print(f"check: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
