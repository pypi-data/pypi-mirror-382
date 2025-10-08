# test_pubchem_tools.py

from tooluniverse import ToolUniverse

# Step 1: Initialize ToolUniverse and load all tools (including PubChem tools)
tooluni = ToolUniverse()
tooluni.load_tools()

# Step 2: Define example inputs
# Please confirm before execution:
#  - 2244 (Aspirin) is actually available in PubChem
#  - "Aspirin" matches its CID
#  - "CC(=O)OC1=CC=CC=C1C(=O)O" is the standard SMILES for aspirin
VALID_CID = 1983  # 2244                  # Aspirin CID
VALID_NAME = "Aspirin"  # Name query
VALID_SMILES = (
    "C1=NC2=C(N1)C(=O)N=C(N2)N"  # "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin SMILES
)
VALID_SUBSTRUCTURE = "c1ccccc1"  # Benzene ring substructure
VALID_THRESHOLD = 0.95  # 90              # 90% similarity threshold (integer)
INVALID_CID = -1  # Intentionally invalid

# For XRefs test, specify at least one external resource, e.g. "RegistryID", "RN"
VALID_XREF_TYPES = ["RegistryID", "RN"]

# Step 3: Define test case list
test_queries = [
    # 1. Get molecular properties by CID
    {"name": "PubChem_get_compound_properties_by_CID", "arguments": {"cid": VALID_CID}},
    # 1.5 Get associated patents by CID
    {"name": "PubChem_get_associated_patents_by_CID", "arguments": {"cid": VALID_CID}},
    {
        "name": "get_webpage_title",
        "arguments": {"url": "https://pubchem.ncbi.nlm.nih.gov/patent/US6015577"},
    },
    # 2. Query CID by name
    {"name": "PubChem_get_CID_by_compound_name", "arguments": {"name": VALID_NAME}},
    # 3. Query CID by SMILES
    {"name": "PubChem_get_CID_by_SMILES", "arguments": {"smiles": VALID_SMILES}},
    # 4. Substructure search
    {
        "name": "PubChem_search_compounds_by_substructure",
        "arguments": {"smiles": VALID_SUBSTRUCTURE},
    },
    # 5. Similarity search (using SMILES and threshold)
    {
        "name": "PubChem_search_compounds_by_similarity",
        "arguments": {"smiles": VALID_SMILES, "threshold": VALID_THRESHOLD},
    },
    # 6. Get 2D structure image (PNG)
    {
        "name": "PubChem_get_compound_2D_image_by_CID",
        "arguments": {"cid": VALID_CID, "image_size": "150x150"},
    },
    # 7. Get synonyms
    {"name": "PubChem_get_compound_synonyms_by_CID", "arguments": {"cid": VALID_CID}},
    # 8. Get external references (XRefs), need to pass at least one resource name
    {
        "name": "PubChem_get_compound_xrefs_by_CID",
        "arguments": {"cid": VALID_CID, "xref_types": VALID_XREF_TYPES},
    },
    # 9. Invalid CID test → expect error
    {
        "name": "PubChem_get_compound_properties_by_CID",
        "arguments": {"cid": INVALID_CID},
    },
]

# Step 4: Loop through all test cases and print example output
for idx, query in enumerate(test_queries):
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    result = tooluni.run(query)

    # Check if contains "error"
    if isinstance(result, dict) and "error" in result:
        print("⚠️ Received error response:")
        print(result)
        continue

    # Otherwise print example based on return type
    print("✅ Success. Example output snippet:")
    if isinstance(result, dict):
        # Dictionary: print first 3 key-value pairs
        print("Returned JSON, example first 3 key-value pairs:")
        # cnt = 0
        # for k, v in result.items():
        #     print(f"  {k}: {v}")
        #     cnt += 1
        #     if cnt >= 3:
        #         break
        print(result)
    elif isinstance(result, list):
        # List: print length and first item
        print(f"Returned list with {len(result)} items, example first item:")
        print(result[0])
    elif isinstance(result, str):
        # Text (CSV, TXT): print first line
        # snippet = result.strip().split("\n")[0]
        # print(f"Returned text (first line): {snippet} …")
        print(result)
    elif isinstance(result, (bytes, bytearray)):
        # Binary (PNG): check PNG file header
        if result.startswith(b"\x89PNG"):
            print(
                f"Returned PNG image ({len(result)} bytes), file header matches PNG signature."
            )
        else:
            print(f"Returned binary ({len(result)} bytes).")
    else:
        # Other unexpected cases
        repr_str = repr(result)
        print(repr_str if len(repr_str) <= 200 else repr_str[:200] + "…")

print("\n🎉 PubChem testing completed!")
