#!/usr/bin/env python3
"""
Simple demo for SimpleLiteratureTool - Perfect for paper screenshots
Shows clean, minimal compose tool functionality
"""

from tooluniverse import ToolUniverse


def main():
    print("🔬 LiteratureReviewAgent Tool Demo")
    print("=" * 40)

    # Initialize ToolUniverse and load all tools
    engine = ToolUniverse()
    engine.load_tools()  # Load all available tools

    # Check available tools
    all_tools = engine.return_all_loaded_tools()
    print(f"Total tools loaded: {len(all_tools)}")

    # Get tool names (for dictionary-based tools, extract the 'name' field)
    tool_names = []
    for tool in all_tools:
        if isinstance(tool, dict) and "name" in tool:
            tool_names.append(tool["name"])
        elif isinstance(tool, str):
            tool_names.append(tool)

    # Look for compose tools
    compose_tools = [
        t for t in tool_names if "Safety" in t or "Literature" in t or "Simple" in t
    ]
    print(f"Compose tools available: {compose_tools}")

    if "LiteratureReviewAgent" in tool_names:
        # Run the simple compose tool
        result = engine.run_one_function(
            {
                "name": "LiteratureReviewAgent",
                "arguments": {"research_topic": "CRISPR gene editing"},
            }
        )
        print(result)

        # Display clean results if it's a dict
        if isinstance(result, dict):
            print(f"📚 Topic: {result.get('topic', 'N/A')}")
            print(f"📄 Papers Found: {result.get('papers_found', 0)}")
            print("🗂️ Sources: Europe PMC, OpenAlex, PubTator")
            print(
                f"🤖 AI Summary: {'✅ Generated' if result.get('ai_summary') else '❌ Failed'}"
            )
        else:
            print(f"Result: {result}")
    else:
        print("LiteratureReviewAgent not found in loaded tools")

    print("\n✅ Demo Complete!")


if __name__ == "__main__":
    main()
