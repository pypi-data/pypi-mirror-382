from tooluniverse import ToolUniverse

# Step 1: Initialize tool universe
tooluni = ToolUniverse()
tooluni.load_tools()

# Step 2: Define test queries for the ChEMBLTool
test_queries = [
    # {"name": "ChEMBL_search_similar_molecules", "arguments": {"query": "aspirin"}},
    # {"name": "ChEMBL_search_similar_molecules", "arguments": {"query": "aspirin", "similarity_threshold": 90}},
    # {"name": "ChEMBL_search_similar_molecules", "arguments": {"query": "aspirin", "max_results": 5}},
    # {"name": "ChEMBL_search_similar_molecules", "arguments": {"query": "aspirin", "similarity_threshold": 85, "max_results": 3}},
    # {"name": "ChEMBL_search_similar_molecules", "arguments": {"query": "CC(=O)OC1=CC=CC=C1C(=O)O", "similarity_threshold": 80, "max_results": 10}},  # SMILES for aspirin
    # {'name': 'ChEMBL_search_similar_molecules', 'arguments': {'query': 'FENOFIBRATE', 'similarity_threshold': 70, 'max_results': 20}}
    {
        "name": "ChEMBL_search_similar_molecules",
        "arguments": {
            "query": "Gadavist",
            "similarity_threshold": 70,
            "max_results": 20,
        },
    }
]

# Step 3: Run all test queries
for idx, query in enumerate(test_queries):
    # try:
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    result = tooluni.run(query)
    print("✅ Success. Example output snippet:")
    print(
        result if isinstance(result, dict) else str(result)
    )  # Print snippet if result is big
# except Exception as e:
#     print(f"❌ Failed. Error: {str(e)}")
