# brass/cli/analyze_runs.py
import os, sys, glob, argparse, yaml, difflib
import brass as br

def get_by_path(d, dotted, default=None):
    cur = d
    for p in dotted.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur

def _list_analyses():
    try:
        names = br.list_analyses()
        if not isinstance(names, (list, tuple)):
            raise TypeError("list_analyses did not return a list/tuple")
    except Exception as e:
        print(f"[ERROR] unable to query registered analyses: {e}", file=sys.stderr)
        return 2
    print("Available analyses:")
    for n in names:
        print(f" - {n}")
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Scan run dirs, build meta labels from keys, check Quantities, run brass.run_analysis."
    )
    ap.add_argument("--list-analyses", action="store_true",
                    help="List registered analyses and exit")
    ap.add_argument("output_dir", nargs="?", help="Top directory containing run subfolders")
    ap.add_argument("analysis_name", nargs="?", help="Name passed to brass.run_analysis")
    ap.add_argument("--pattern", default="out-*", help="Glob for run folders (default: out-*)")
    ap.add_argument("--keys", nargs="+", required=False,
                    help="Dotted keys for labels (last segment used in label), e.g.: "
                         "Modi.Collider.Sqrtsnn General.Nevents")
    ap.add_argument("--results-subdir", default="data", help="Where to store analysis results (default: data)")
    ap.add_argument("--strict-quantities", action="store_true",
                    help="Fail if Quantities differ across runs (default: warn and use first)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    # Handle --list-analyses early
    if args.list_analyses:
        return _list_analyses()

    # Require positionals if not just listing
    if not args.output_dir or not args.analysis_name:
        ap.error("output_dir and analysis_name are required unless --list-analyses is used")

    # Validate requested analysis against registry
    try:
        available = list(br.list_analyses())
    except Exception as e:
        print(f"[ERROR] unable to query registered analyses: {e}", file=sys.stderr)
        return 2

    if args.analysis_name not in available:
        print(f"[ERROR] unknown analysis: '{args.analysis_name}'", file=sys.stderr)
        suggestion = difflib.get_close_matches(args.analysis_name, available, n=1)
        if suggestion:
            print(f"        did you mean: '{suggestion[0]}'?", file=sys.stderr)
        print("        use --list-analyses to see options.", file=sys.stderr)
        return 2

    out_top = os.path.abspath(args.output_dir)
    runs = sorted(glob.glob(os.path.join(out_top, args.pattern)))
    if not runs:
        print(f"[ERROR] no runs match {args.pattern} under {out_top}", file=sys.stderr)
        return 2

    file_and_meta = []
    first_quantities = None
    mismatches = []

    for rd in runs:
        binf = os.path.join(rd, "particles_binary.bin")
        ymlf = os.path.join(rd, "config.yaml")
        if not (os.path.isfile(binf) and os.path.isfile(ymlf)):
            if args.verbose:
                print(f"[SKIP] {rd} (missing binary or YAML)")
            continue

        try:
            with open(ymlf, "r") as f:
                cfg = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[WARN] bad YAML {ymlf}: {e}", file=sys.stderr)
            continue

        q = get_by_path(cfg, "Output.Particles.Quantities", [])
        q = list(q) if isinstance(q, list) else []

        if first_quantities is None:
            first_quantities = q
        elif q != first_quantities:
            mismatches.append((rd, q))

        # label from requested keys (use only the last segment as name)
        parts = []
        for k in (args.keys or []):
            val = get_by_path(cfg, k, "NA")
            last = k.split(".")[-1]
            parts.append(f"{last}={val}")
        meta = ",".join(parts)

        file_and_meta.append((binf, meta))
        if args.verbose:
            print(f"[OK] {rd} -> {meta}")

    if not file_and_meta:
        print("[ERROR] no valid runs found.", file=sys.stderr)
        return 2

    if mismatches:
        msg = ["[ERROR] Quantities mismatch detected:" if args.strict_quantities
               else "[WARN] Quantities mismatch detected (using first set):"]
        msg.append(f"  First: {first_quantities}")
        for rd, q in mismatches:
            msg.append(f"  {rd}: {q}")
        print("\n".join(msg), file=sys.stderr)
        if args.strict_quantities:
            return 3

    results_dir = os.path.join(out_top, args.results_subdir)
    os.makedirs(results_dir, exist_ok=True)

    if args.verbose:
        print(f"[INFO] N files: {len(file_and_meta)}")
        print(f"[INFO] Quantities: {first_quantities}")
        print(f"[INFO] Results dir: {results_dir}")

    br.run_analysis(
        file_and_meta=file_and_meta,
        analysis_name=args.analysis_name,
        quantities=first_quantities or [],
        output_folder=results_dir,
    )

    if args.verbose:
        print("[DONE]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
