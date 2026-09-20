import base64, pathlib, zipfile, os, sys
root = pathlib.Path(r'C:\Users\luyus\Downloads\刀影江湖-概念图')
b64path = root / '_transfer' / 'zip.b64'
zippath = root / '_transfer' / 'daoying-concept.zip'
data = base64.b64decode(b64path.read_text(encoding='ascii'))
zippath.write_bytes(data)
print('zip bytes', len(data))
# extract
with zipfile.ZipFile(zippath, 'r') as z:
    z.extractall(root.parent)
# zip contains 刀影江湖-概念图/... so extract to Downloads
print('extracted')
# count
count=0
total=0
target = root
for dp, dns, fns in os.walk(target):
    if '_transfer' in dp: continue
    for f in fns:
        fp=os.path.join(dp,f)
        count+=1
        total+=os.path.getsize(fp)
print('files', count, 'bytes', total)
