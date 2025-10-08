import json
import os
from typing import Any, Dict, List
from tooluniverse import ToolUniverse

# Load all tool schemas from JSON
schema_path = os.path.join(
    os.path.dirname(__file__), "..", "data", "alphafold_tools.json"
)
with open(schema_path) as f:
    tools_json = json.load(f)

schemas = {tool["name"]: tool["return_schema"] for tool in tools_json}

tooluni = ToolUniverse()
tooluni.load_tools()

test_queries: List[Dict[str, Any]] = [
    # Hemoglobin subunit alpha (valid)
    {
        "name": "alphafold_get_prediction",
        "arguments": {"qualifier": "P69905"},
    },
    # Invalid
    {
        "name": "alphafold_get_prediction",
        "arguments": {"qualifier": "XXX123"},
    },
    # Missing param
    {
        "name": "alphafold_get_prediction",
        "arguments": {},
    },
    # Summary: valid
    {
        "name": "alphafold_get_summary",
        "arguments": {"qualifier": "P69905"},
    },
    # Annotations (valid + invalid type)
    {
        "name": "alphafold_get_annotations",
        "arguments": {"qualifier": "P69905", "type": "MUTAGEN"},
    },
    {
        "name": "alphafold_get_annotations",
        "arguments": {"qualifier": "P69905", "type": "INVALID"},
    },
]

for idx, query in enumerate(test_queries, 1):
    print(f"\n[{idx}] Running {query['name']} with {query['arguments']}")
    result = tooluni.run(query)

    # Handle errors
    if isinstance(result, dict) and "error" in result:
        print(f"INVALID: {result['error']}")
        if "detail" in result:
            print(f"   Detail: {result['detail']}")
        continue

    # Handle success
    data = result.get("data")
    if not data:
        print("No data returned.")
        continue

    # Schema validation (check only top-level keys)
    schema = schemas[query["name"]]
    expected_keys = schema.get("properties", {}).keys()

    # Handle list vs dict results
    if isinstance(data, list) and data:
        record = data[0]
    elif isinstance(data, dict):
        record = data
    else:
        record = {}

    missing = [k for k in expected_keys if k not in record]
    if missing:
        print(f"   INVALID Missing expected fields: {missing}")
    else:
        print("   SUCCESS All expected schema fields present")

    # Show highlights depending on tool
    if query["name"] == "alphafold_get_prediction":
        if "uniprotDescription" in record:
            print(
                f"   {record.get('uniprotDescription')} ({record.get('uniprotAccession')})"
            )
            print(f"   Organism: {record.get('organismScientificName')}")
            print(f"   Avg pLDDT: {record.get('globalMetricValue')}")

    elif query["name"] == "alphafold_get_summary":
        entry = record.get("uniprot_entry", {})
        structures = record.get("structures", [])
        print(f"   UniProt AC: {entry.get('ac')}, ID: {entry.get('id')}")
        print(f"   Sequence length: {entry.get('sequence_length')}")
        print(f"   Structures returned: {len(structures)}")

    elif query["name"] == "alphafold_get_annotations":
        annotations = record.get("annotation", [])
        print(f"   Accession: {record.get('accession')}")
        print(f"   Total annotations: {len(annotations)}")
        if annotations:
            first_ann = annotations[0]
            print(f"   First annotation type: {first_ann.get('type')}")
            print(f"   First annotation description: {first_ann.get('description')}")
