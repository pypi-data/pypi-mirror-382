from tooluniverse import ToolUniverse
from typing import Any, Dict, List

tooluni = ToolUniverse()
tooluni.load_tools()

TEST_ACC = "P05067"  # A4_HUMAN

test_queries: List[Dict[str, Any]] = [
    {"name": "UniProt_get_entry_by_accession", "arguments": {"accession": TEST_ACC}},
    {"name": "UniProt_get_function_by_accession", "arguments": {"accession": TEST_ACC}},
    {
        "name": "UniProt_get_recommended_name_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
    {
        "name": "UniProt_get_alternative_names_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
    {"name": "UniProt_get_organism_by_accession", "arguments": {"accession": TEST_ACC}},
    {
        "name": "UniProt_get_subcellular_location_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
    {
        "name": "UniProt_get_disease_variants_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
    {
        "name": "UniProt_get_ptm_processing_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
    {"name": "UniProt_get_sequence_by_accession", "arguments": {"accession": TEST_ACC}},
    {
        "name": "UniProt_get_isoform_ids_by_accession",
        "arguments": {"accession": TEST_ACC},
    },
]


def format_value(value, max_items=5, max_length=200):
    """Helper function to format output values with more detail"""
    if isinstance(value, dict):
        dict_str = str(value)
        return f"Dict ({len(dict_str)} chars): {dict_str[:500]}{'...' if len(dict_str) > 500 else ''}"
    elif isinstance(value, list):
        if not value:
            return "Empty list"
        items_to_show = value[:max_items]
        items_str = "\n  - ".join(
            [
                str(item)[:max_length] + ("..." if len(str(item)) > max_length else "")
                for item in items_to_show
            ]
        )
        remaining = len(value) - max_items
        return f"List with {len(value)} items:\n  - {items_str}" + (
            f"\n  ... and {remaining} more items" if remaining > 0 else ""
        )
    elif isinstance(value, str):
        return f"String ({len(value)} chars): {value[:max_length]}{'...' if len(value) > max_length else ''}"
    else:
        return f"Type: {type(value)}, Value: {value}"


for idx, q in enumerate(test_queries, 1):
    print(f"\n{'='*80}\n[{idx}] {q['name']}({q['arguments']['accession']})")
    res = tooluni.run(q)

    if isinstance(res, dict) and "error" in res:
        print(f"ERROR: {res['error']}")
    else:
        print(format_value(res))
    print()
