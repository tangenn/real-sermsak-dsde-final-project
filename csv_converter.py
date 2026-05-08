# ============================================================
# json_to_csv_wide.py
# One row per polling unit, each party becomes columns
# Includes summary + validation columns
# Only includes units where error < threshold%
#
# Usage:
#   python json_to_csv_wide.py
#   python json_to_csv_wide.py --output_dir "output_v2" --threshold 50
# ============================================================

import json, csv, argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="output_v2")
    parser.add_argument("--threshold",  default=50.0, type=float,
                        help="Only include units with error < this %% (default 50)")
    return parser.parse_args()


PARTY_LIST_PARTIES = [
    "ไทยทรัพย์ทวี", "เพื่อชาติไทย", "ใหม่", "มิติใหม่", "รวมใจไทย",
    "รวมไทยสร้างชาติ", "พลวัต", "ประชาธิปไตยใหม่", "เพื่อไทย", "ทางเลือกใหม่",
    "เศรษฐกิจ", "เสรีรวมไทย", "รวมพลังประชาชน", "ท้องที่ไทย", "อนาคตไทย",
    "พลังเพื่อไทย", "ไทยชนะ", "พลังสังคมใหม่", "สังคมประชาธิปไตยไทย", "ฟิวชัน",
    "ไทรวมพลัง", "ก้าวอิสระ", "ปวงชนไทย", "วิชชั่นใหม่", "เพื่อชีวิตใหม่",
    "คลองไทย", "ประชาธิปัตย์", "ไทยก้าวหน้า", "ไทยภักดี", "แรงงานสร้างชาติ",
    "ประชากรไทย", "ครูไทยเพื่อประชาชน", "ประชาชาติ", "สร้างอนาคตไทย", "รักชาติ",
    "ไทยพร้อม", "ภูมิใจไทย", "พลังธรรมใหม่", "กรีน", "ไทยธรรม",
    "แผ่นดินธรรม", "กล้าธรรม", "พลังประชารัฐ", "โอกาสใหม่", "เป็นธรรม",
    "ประชาชน", "ประชาไทย", "ไทยสร้างไทย", "ไทยก้าวใหม่", "ประชาอาสาชาติ",
    "พร้อม", "เครือข่ายชาวนาแห่งประเทศไทย", "ไทยพิทักษ์ธรรม", "ความหวังใหม่",
    "ไทยรวมไทย", "เพื่อบ้านเมือง", "พลังไทยรักชาติ",
]

CONSTITUENCY_PARTIES = [
    "กล้าธรรม", "ภูมิใจไทย", "เพื่อไทย", "ประชาชน", "ไทรวมพลัง",
    "ประชาธิปไตยใหม่", "พลังประชารัฐ", "ประชาธิปัตย์", "เศรษฐกิจ", "ไทยก้าวใหม่",
]

VALID_PL_SET  = set(PARTY_LIST_PARTIES)
VALID_CON_SET = set(CONSTITUENCY_PARTIES)

SUMMARY_COLS = [
    "eligible_voters", "turnout", "ballots_allocated",
    "ballots_used", "valid_ballots", "spoiled_ballots",
    "abstain_ballots", "ballots_remaining",
]
VALIDATION_COLS = [
    "total_votes_in_table", "effective_vote_sum",
    "valid_ballots", "vote_diff",
]


def get_error_ratio(data: dict) -> float:
    """Get error ratio from _validation. Returns 0.0 if not available."""
    v = data.get("_validation", {})

    # Rich format
    if "error_ratio" in v and v["error_ratio"] is not None:
        return float(v["error_ratio"])

    # Simple format — compute from totals
    vote_sum      = v.get("total_votes_in_table") or v.get("effective_vote_sum")
    valid_ballots = v.get("valid_ballots")

    if vote_sum is None:
        vote_sum = sum(r.get("votes", 0) for r in data.get("results", []))
    if valid_ballots is None:
        valid_ballots = data.get("summary", {}).get("valid_ballots")

    if valid_ballots and valid_ballots > 0 and vote_sum is not None:
        return abs(vote_sum - valid_ballots) / valid_ballots
    return 0.0


def main():
    args       = parse_args()
    output_dir = Path(args.output_dir)
    threshold  = args.threshold / 100.0   # convert % to ratio

    if not output_dir.exists():
        print(f"ERROR: '{output_dir}' not found")
        return

    all_jsons = sorted(output_dir.rglob("*.json"))
    all_jsons = [j for j in all_jsons if not j.name.startswith("_")]
    print(f"Found     : {len(all_jsons)} JSON files in '{output_dir}'")
    print(f"Threshold : error < {args.threshold}%")
    print()

    party_list_units   = {}
    constituency_units = {}
    skipped   = 0
    included  = 0
    excluded  = 0

    for jf in all_jsons:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠️  skip {jf.name}: {e}")
            skipped += 1
            continue

        records = data if isinstance(data, list) else [data]
        records = [r for r in records if isinstance(r, dict)]

        for record in records:
            meta       = record.get("metadata", {})
            form_type  = record.get("form_type", "unknown")
            results    = record.get("results", [])
            summary    = record.get("summary", {})
            validation = record.get("_validation", {})

            # ── Skip if error too high ────────────────────
            error_ratio = get_error_ratio(record)
            if error_ratio >= threshold:
                excluded += 1
                continue

            included += 1

            # ── Unique key per polling unit ───────────────
            key = (
                meta.get("province", ""),
                meta.get("constituency", ""),
                meta.get("amphoe", ""),
                meta.get("tambon", ""),
                str(meta.get("unit", "")),
                form_type,
            )

            # If this unit already recorded, skip duplicate
            if form_type == "party_list" and key in party_list_units:
                continue
            if form_type == "constituency" and key in constituency_units:
                continue

            base = {
                "province":     meta.get("province", ""),
                "constituency": meta.get("constituency", ""),
                "amphoe":       meta.get("amphoe", ""),
                "tambon":       meta.get("tambon", ""),
                "unit":         meta.get("unit", ""),
                "form_type":    form_type,
            }

            summary_data = {
                col: summary.get(col, "") for col in SUMMARY_COLS
            }

            validation_data = {
                f"val_{col}": validation.get(col, "")
                for col in VALIDATION_COLS
            }

            # Party data — only valid party names, filter garbage
            valid_set  = VALID_PL_SET if form_type == "party_list" else VALID_CON_SET
            party_data = {}
            for r in results:
                party = r.get("party", "").strip()
                if not party:
                    continue
                if party.lstrip("-").isdigit():
                    continue
                if party not in valid_set:
                    continue
                party_data[party] = {
                    "votes":          r.get("votes") if r.get("votes") is not None else 0,
                    "votes_th_value": r.get("votes_th_value") if r.get("votes_th_value") is not None else 0,
                }

            unit_record = {
                "base":       base,
                "summary":    summary_data,
                "validation": validation_data,
                "parties":    party_data,
            }

            if form_type == "party_list":
                party_list_units[key] = unit_record
            elif form_type == "constituency":
                constituency_units[key] = unit_record

    print(f"Included  : {included} records (error < {args.threshold}%)")
    print(f"Excluded  : {excluded} records (error >= {args.threshold}%)")
    print(f"Skipped   : {skipped} files (read error)")
    print()

    def write_wide_csv(path, units, fixed_parties):
        base_cols  = ["province", "constituency", "amphoe", "tambon", "unit", "form_type"]
        sum_cols   = SUMMARY_COLS
        val_cols   = [f"val_{c}" for c in VALIDATION_COLS]
        p_cols     = []
        for p in fixed_parties:
            p_cols.append(f"{p}_votes")
            p_cols.append(f"{p}_votes_th")

        fieldnames = base_cols + sum_cols + val_cols + p_cols

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for key, unit in sorted(units.items()):
                row = {
                    **unit["base"],
                    **unit["summary"],
                    **unit["validation"],
                }
                for p in fixed_parties:
                    d = unit["parties"].get(p, {})
                    row[f"{p}_votes"]    = d.get("votes", 0)
                    row[f"{p}_votes_th"] = d.get("votes_th_value", 0)
                writer.writerow(row)

        print(f"Saved → {path}")
        print(f"  Units   : {len(units)}")
        print(f"  Columns : {len(fieldnames)}")
        print(f"  Layout  : {len(base_cols)} base | {len(sum_cols)} summary | "
              f"{len(val_cols)} validation | {len(p_cols)} party")

    if party_list_units:
        write_wide_csv(
            output_dir / "party_list_wide.csv",
            party_list_units,
            PARTY_LIST_PARTIES
        )
    else:
        print("No party_list units found")

    print()

    if constituency_units:
        write_wide_csv(
            output_dir / "constituency_wide.csv",
            constituency_units,
            CONSTITUENCY_PARTIES
        )
    else:
        print("No constituency units found")

    print(f"\n{'='*45}")
    print(f"Done!")
    print(f"  party_list units   : {len(party_list_units)}")
    print(f"  constituency units : {len(constituency_units)}")
    if skipped:
        print(f"  skipped files      : {skipped}")


if __name__ == "__main__":
    main()