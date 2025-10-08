from tooluniverse import ToolUniverse

# ...existing code initializing ToolUniverse...
tooluni = ToolUniverse()
tooluni.load_tools()

test_queries = [
    {
        "name": "EuropePMC_search_articles",
        "arguments": {"query": "cancer immunotherapy", "limit": 3},
    },
]

for idx, query in enumerate(test_queries):
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    result = tooluni.run(query)
    print("✅ Success. Example output snippet:")
    print(result if isinstance(result, dict) else str(result))
