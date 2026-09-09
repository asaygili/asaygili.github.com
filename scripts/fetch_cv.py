"""
Google Scholar'dan atıf, h-indeks ve i10-indeks verilerini çeker.
scholarly kütüphanesi kullanır; bot engellemesi durumunda mevcut değerleri korur.
"""
import json, sys, time
from datetime import datetime
from pathlib import Path

SCHOLAR_ID = "-9oeVawAAAAJ"
DATA_FILE  = Path(__file__).parent.parent / "data.json"

def load_existing():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"stats": {}, "publications": [], "last_updated": ""}

def fetch_scholar():
    from scholarly import scholarly
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices"])
    return {
        "citations":  author.get("citedby", 0),
        "h_index":    author.get("hindex", 0),
        "i10_index":  author.get("i10index", 0),
    }

def main():
    existing = load_existing()
    today = datetime.now().strftime("%d.%m.%Y")

    stats = existing.get("stats", {})
    updated = False

    for attempt in range(3):
        try:
            print(f"[{attempt+1}/3] Google Scholar'dan veri çekiliyor...")
            new_stats = fetch_scholar()
            stats = {**new_stats, "updated": today}
            updated = True
            print(f"  Atıf: {stats['citations']}  h: {stats['h_index']}  i10: {stats['i10_index']}")
            break
        except Exception as e:
            print(f"  Hata: {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(10 * (attempt + 1))

    if not updated:
        print("[WARN] Veri çekilemedi, mevcut değerler korunuyor.", file=sys.stderr)
        stats["updated"] = stats.get("updated", today)

    data = {
        **existing,
        "stats": stats,
        "last_updated": datetime.now().isoformat(),
    }

    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] data.json güncellendi ({today})")
    sys.exit(0 if updated else 1)

if __name__ == "__main__":
    main()
