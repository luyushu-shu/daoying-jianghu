import json, os, pathlib
from collections import defaultdict
root = pathlib.Path(r"C:\Users\luyus\Downloads\刀影江湖-概念图")
xfer = root / "_transfer"
man = json.loads((xfer / "manifest.json").read_text(encoding="utf-8"))
groups = defaultdict(list)
for ch in man["chunks"]:
    idx = int(ch["name"].split("_")[0])
    groups[idx].append(ch)
ok, fail, skip = 0, [], 0
for idx in sorted(groups):
    chunks = sorted(groups[idx], key=lambda c: c["chunk"])
    rel = chunks[0]["rel"]
    dest = root / pathlib.Path(*rel.split("/"))
    parts = []
    missing = False
    for ch in chunks:
        p = xfer / ch["name"]
        if not p.exists() or p.stat().st_size != ch["size"]:
            missing = True
            break
        parts.append(p.read_bytes())
    if missing:
        skip += 1
        continue
    data = b"".join(parts)
    if len(data) != chunks[0]["file_size"]:
        fail.append(f"{rel} size {len(data)}!={chunks[0]['file_size']}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    ok += 1
    print("OK", rel, len(data))
print("ASSEMBLED", ok, "SKIP_INCOMPLETE", skip, "FAIL", len(fail))
for f in fail:
    print("FAIL", f)
# count final files excluding _transfer
count=0; total=0
for dp, dns, fns in os.walk(root):
    if "_transfer" in dp: continue
    for f in fns:
        fp=os.path.join(dp,f)
        count+=1; total+=os.path.getsize(fp)
print("FINAL_FILES", count, "BYTES", total)
