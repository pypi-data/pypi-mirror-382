from tooluniverse import ToolUniverse

# Step 1: Initialize tool universe
tooluni = ToolUniverse()
tooluni.load_tools()

#
test_queries = [
    {
        "name": "Tool_Finder",
        "arguments": {
            "description": "a tool for finding tools related to diseases",
            "limit": 10,
            "return_call_result": False,
        },
    },
    {"name": "Tool_Finder_Keyword", "arguments": {"description": "disease", "limit": 5}},
]

for idx, query in enumerate(test_queries):
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {query['arguments']}"
    )
    result = tooluni.run(query)
    print("✅ Success. Example output snippet:")
    print(result if isinstance(result, dict) else str(result))
