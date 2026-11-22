import glob, json, os, re

data_file = 'tools/progress/data/emulator_exports.json'
emu = json.load(open(data_file, 'r', encoding='utf-8'))

cdir = os.path.join('crates', 'compat')
count_updated = 0
for crate in sorted(os.listdir(cdir), key=str.lower):
    table = os.path.join(cdir, crate, 'exports.txt')
    if not os.path.isfile(table):
        continue
    cargo_path = os.path.join(cdir, crate, 'Cargo.toml')
    lib = re.search(r'\[lib\][^\[]*?name\s*=\s*"([^"]+)"', open(cargo_path, encoding='utf-8').read())
    dll = (lib.group(1) if lib else crate) + '.dll'
    matched_dll = next((n for n in emu if n.lower() == dll.lower()), dll)
    funcs, notes = {}, {}
    for line in open(table, encoding='utf-8'):
        body, _, note = line.strip().partition(' | ')
        f = body.split()
        if len(f) < 3:
            continue
        funcs[f[1]] = f[2]
        if note:
            notes[f[1]] = note.strip()
    old_funcs = emu.get(matched_dll, {}).get('functions', {})
    if old_funcs != funcs:
        print(f"Updating {matched_dll}: {old_funcs} -> {funcs}")
        count_updated += 1
    emu[matched_dll] = {'file': f'crates/compat/{crate}/src/lib.rs', 'functions': funcs, 'notes': notes}

json.dump(emu, open(data_file, 'w', encoding='utf-8'), indent=1)
print(f"Done. Updated {count_updated} DLL entries.")
