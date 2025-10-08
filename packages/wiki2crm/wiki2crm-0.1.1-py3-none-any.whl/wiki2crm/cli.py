# src/wiki2crm/cli.py
import sys
import argparse
from importlib import import_module
from . import __version__

MODMAP = {
    "authors":   "wiki2crm.authors",
    "works":     "wiki2crm.works",
    "relations": "wiki2crm.relations",
    "merge":     "wiki2crm.merge",
    "map-align": "wiki2crm.map_and_align",
}

HELP_BY_CMD = {
    "authors":   "Build authors.ttl from a CSV of QIDs",
    "works":     "Build works.ttl from a CSV of QIDs",
    "relations": "Build relations.ttl from a CSV of QIDs",
    "merge":     "Merge authors/works/relations TTL into one",
    "map-align": "Add extra IDs + ontology alignments",
}

def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)

    parser = argparse.ArgumentParser(prog="wiki2crm", description="Wikidata → CIDOC CRM")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--hello", action="store_true", help="Print a short greeting and exit")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # optional: zusätzliches Subcommand "version"
    ver = sub.add_parser("version", help="Print version and exit")
    ver.set_defaults(_cmd="__version__")

    for cmd, help_text in HELP_BY_CMD.items():
        sp = sub.add_parser(cmd, help=help_text)
        sp.set_defaults(_cmd=cmd)

    args, rest = parser.parse_known_args(argv)

    if args.hello:
        print("👋 hello from wiki2crm")
        return 0

    if getattr(args, "_cmd", None) == "__version__":
        print(f"wiki2crm {__version__}")
        return 0

    modname = MODMAP.get(args._cmd)
    if not modname:
        parser.error(f"Unknown command: {args._cmd}")

    mod = import_module(modname)
    if not hasattr(mod, "main"):
        parser.error(f"Subcommand module '{modname}' has no function main(argv=None)")

    return mod.main(argv=rest)

if __name__ == "__main__":
    raise SystemExit(main())
