from tooluniverse import ToolUniverse

# Step 1: Initialize tool universe
tooluni = ToolUniverse()
tooluni.load_tools()

test_queries = [
    # Test 1: Search for a specific drug by name
    {"name": "drugbank_vocab_search", "arguments": {"query": "aspirin"}},
    # Test 2: Exact match search for a DrugBank ID
    {
        "name": "drugbank_vocab_search",
        "arguments": {
            "query": "DB00001",
            "search_fields": ["DrugBank ID"],
            "exact_match": True,
        },
    },
    # Test 3: Search in synonyms with case sensitivity
    {
        "name": "drugbank_vocab_search",
        "arguments": {
            "query": "Lepirudin",
            "search_fields": ["Synonyms", "Common name"],
            "case_sensitive": True,
            "limit": 10,
        },
    },
    # Test 4: Filter drugs that have CAS numbers
    {
        "name": "drugbank_vocab_filter",
        "arguments": {"field": "CAS", "condition": "not_empty", "limit": 5},
    },
    # Test 5: Filter drugs starting with "DB000"
    {
        "name": "drugbank_vocab_filter",
        "arguments": {
            "field": "DrugBank ID",
            "condition": "starts_with",
            "value": "DB000",
            "limit": 10,
        },
    },
    # Test 6: Filter drugs containing "interferon" in common name
    {
        "name": "drugbank_vocab_filter",
        "arguments": {
            "field": "Common name",
            "condition": "contains",
            "value": "interferon",
            "limit": 5,
        },
    },
    # Test 7: Complex search with multiple fields
    {
        "name": "drugbank_vocab_search",
        "arguments": {
            "query": "insulin",
            "search_fields": ["Common name", "Synonyms"],
            "case_sensitive": False,
            "exact_match": False,
            "limit": 3,
        },
    },
    # ---------- drugbank_full_search ----------
    # 1. Partial common-name query
    {
        "name": "drugbank_full_search",
        "arguments": {
            "query": "acetylsalicylic",
            "search_fields": ["name"],
            "limit": 5,
        },
    },
    # 2. Exact-match lookup by DrugBank ID
    {
        "name": "drugbank_full_search",
        "arguments": {
            "query": "DB00003",
            "search_fields": ["drugbank_id"],
            "exact_match": True,
        },
    },
    # 3. Case-sensitive synonym search
    {
        "name": "drugbank_full_search",
        "arguments": {
            "query": "Olanzapine",
            "search_fields": ["synonyms"],
            "case_sensitive": True,
            "limit": 3,
        },
    },
    # ---------- drugbank_links_search ----------
    # 4. Exact CAS-number lookup
    {
        "name": "drugbank_links_search",
        "arguments": {
            "query": "205923-56-4",
            "search_fields": ["CAS Number"],
            "exact_match": True,
        },
    },
    # 5. Search by PharmGKB identifier
    {
        "name": "drugbank_links_search",
        "arguments": {"query": "PA10040", "search_fields": ["PharmGKB ID"]},
    },
    # 6. Search by KEGG Drug ID
    {
        "name": "drugbank_links_search",
        "arguments": {"query": "D03455", "search_fields": ["KEGG Drug ID"]},
    },
    # ---------- dict_search (DICTrank) ----------
    # 7. Search by trade name
    {
        "name": "dict_search",
        "arguments": {"query": "ZYPREXA", "search_fields": ["Trade Name"], "limit": 2},
    },
    # 8. Search by active ingredient (case-insensitive)
    {
        "name": "dict_search",
        "arguments": {
            "query": "trimethobenzamide",
            "search_fields": ["Active Ingredient(s)"],
            "case_sensitive": False,
        },
    },
    # ---------- dili_search (DILIrank) ----------
    # 9. Exact compound-name search
    {
        "name": "dili_search",
        "arguments": {
            "query": "acetaminophen",
            "search_fields": ["Compound Name"],
            "exact_match": True,
        },
    },
    # 10. Partial compound-name query
    {
        "name": "dili_search",
        "arguments": {
            "query": "mercap",
            "search_fields": ["Compound Name"],
            "limit": 5,
        },
    },
    # ---------- diqt_search (DIQTA) ----------
    # 11. Exact DrugBank ID lookup
    {
        "name": "diqt_search",
        "arguments": {
            "query": "DB00637",
            "search_fields": ["DrugBank ID"],
            "exact_match": True,
        },
    },
    # 12. Generic name search (case-insensitive)
    {
        "name": "diqt_search",
        "arguments": {
            "query": "dofetilide",
            "search_fields": ["Generic/Proper Name(s)"],
            "case_sensitive": False,
        },
    },
]

for idx, query in enumerate(test_queries):
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    try:
        result = tooluni.run(query)
        print("✅ Success. Example output snippet:")

        # Pretty print the result based on its structure
        if isinstance(result, dict):
            if "results" in result:
                print(
                    f"Found {result.get('total_results', result.get('total_matches', 0))} results"
                )
                if result["results"]:
                    # Show first result
                    first_result = result["results"][0]
                    # print(f"First result: {first_result.get('Common name', 'N/A')} (ID: {first_result.get('DrugBank ID', 'N/A')})")
                    print(f"First result: {first_result})")
                    if "matched_fields" in first_result:
                        print(f"Matched fields: {first_result['matched_fields']}")
            elif "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(
                    str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                )
        else:
            print(str(result)[:200] + "..." if len(str(result)) > 200 else str(result))

    except Exception as e:
        print(f"❌ Error: {e}")
