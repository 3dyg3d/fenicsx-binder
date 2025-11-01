from lxml import etree

def merge_xdmf(filename_in, filename_out="results_merged.xdmf"):
    tree = etree.parse(filename_in)
    root = tree.getroot()

    # --- locate the <Domain> node ---
    domain = root.find("Domain")
    if domain is None:
        raise RuntimeError("❌ No <Domain> tag found in XDMF file.")

    # --- find all temporal collections ---
    collections = domain.findall(".//Grid[@GridType='Collection']")
    ncoll = len(collections)
    if ncoll < 2:
        print("Nothing to merge — file already has one collection.")
        return
    print(f"📦 Found {ncoll} collections to merge.")

    # --- use the first collection as the base (same mesh, same timesteps) ---
    merged = etree.Element("Grid", Name="Results",
                           GridType="Collection", CollectionType="Temporal")

    # collect all per-timestep <Grid> lists from each collection
    all_grids = [c.findall("Grid") for c in collections]
    nt = len(all_grids[0])
    print(f"🕒 Found {nt} timesteps (based on first collection).")

    for step_idx in range(nt):
        new_grid = etree.Element("Grid", Name=f"t={step_idx}", GridType="Uniform")

        # --- Add mesh topology/geometry from the first field ---
        for elem in all_grids[0][step_idx]:
            new_grid.append(elem)

        # --- Add attributes from other collections safely ---
        for coll_idx, c in enumerate(collections[1:], start=2):
            grids = c.findall("Grid")
            if step_idx >= len(grids):
                print(f"⚠️ Skipping collection #{coll_idx} (only {len(grids)} steps).")
                continue
            for a in grids[step_idx].findall("Attribute"):
                new_grid.append(a)

        merged.append(new_grid)

    # --- Replace old collections with the merged one ---
    for c in collections:
        domain.remove(c)
    domain.append(merged)

    etree.ElementTree(root).write(
        filename_out,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8"
    )
    print(f"✅ Wrote merged file: {filename_out}")


# ---------------------------------------------------------
if __name__ == "__main__":
    merge_xdmf("results_hyperelastic.xdmf")
