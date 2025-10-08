from tooluniverse import ToolUniverse
from typing import Any, Dict, List

# Step 1: Initialize tool universe and load available tools
tooluni = ToolUniverse()
tooluni.load_tools()

# Sample biomedical text for testing
sample_abstract = """
Background: Drug-drug interactions (DDIs) are a major cause of adverse drug reactions and
represent a significant public health concern. This study aimed to develop and validate a
machine learning approach for predicting potential DDIs using molecular descriptors and
pharmacokinetic properties.

Methods: We collected data on 15,000 drug pairs from DrugBank and FDA databases. Molecular
descriptors were computed using RDKit, and pharmacokinetic parameters were extracted from
literature. A gradient boosting classifier was trained to predict DDI severity levels.

Results: The model achieved an accuracy of 89.2% with a precision of 0.91 and recall of 0.87
for high-severity DDI prediction. Feature importance analysis revealed that CYP450 enzyme
inhibition patterns and protein binding affinity were the most predictive features.

Conclusions: Our machine learning approach demonstrates high accuracy in predicting DDIs and
could serve as a valuable tool for clinical decision support and drug safety assessment.
"""

# Define test queries based on the agentic_tools.json configuration
test_queries: List[Dict[str, Any]] = [
    # {
    #     "name": "BiomedicalTextSummarizer",
    #     "arguments": {
    #         "text": sample_abstract,
    #         "summary_length": "100 words",
    #         "focus_area": "methodology and results"
    #     }
    # },
    # {
    #     "name": "BiomedicalTextSummarizer",
    #     "arguments": {
    #         "text": "Metformin is a first-line treatment for type 2 diabetes that works by reducing glucose production in the liver.",
    #         "summary_length": "25 words",
    #         "focus_area": "mechanism of action"
    #     }
    # },
    # {
    #     "name": "MedicalLiteratureReviewer",
    #     "arguments": {
    #         "research_topic": "Immunotherapy efficacy in triple-negative breast cancer",
    #         "literature_content": "Study 1: Pembrolizumab showed 23% response rate (n=150). Study 2: Atezolizumab combined with chemotherapy improved progression-free survival (HR=0.62, p=0.002).",
    #         "focus_area": "treatment efficacy",
    #         "study_types": "randomized controlled trials",
    #         "quality_level": "moderate and above",
    #         "review_scope": "rapid review"
    #     }
    # },
    # {
    #     "name": "HypothesisGenerator",
    #     "arguments": {
    #         "context": "Recent studies have shown that patients with Alzheimer's disease have altered gut microbiome composition. Additionally, inflammation markers in the brain correlate with cognitive decline. Some research suggests that certain probiotics can cross the blood-brain barrier and influence neuroinflammation.",
    #         "domain": "neuroscience",
    #         "number_of_hypotheses": "3",
    #         "hypothesis_format": "If-then statements"
    #     }
    # },
    # {
    #     "name": "HypothesisGenerator",
    #     "arguments": {
    #         "context": "Machine learning models trained on electronic health records show promise in predicting drug adverse events. However, most models focus on single drugs rather than drug combinations. Polypharmacy is common in elderly patients and drug-drug interactions are poorly understood.",
    #         "domain": "pharmacology",
    #         "number_of_hypotheses": "2"
    #     }
    # },
    {
        "name": "ExperimentalDesignScorer",
        "arguments": {
            "hypothesis": "Daily high-intensity interval training (HIIT) for 8 weeks will improve insulin sensitivity in overweight adults compared to moderate-intensity continuous training (MICT).",
            "design_description": """
Study Design: Randomized, parallel-group clinical trial

Participants: 120 overweight adults (BMI 25–30) aged 30–50, sedentary lifestyle
Inclusion: No history of diabetes, stable weight for 3 months
Exclusion: Cardiovascular disease, musculoskeletal injuries, current exercise regimen

Interventions:
- HIIT group (n=60): 4×4-minute intervals at 90% HRmax with 3-minute active recovery, 3×/week
- MICT group (n=60): 40 minutes at 60% HRmax, 3×/week

Randomization: Computer-generated simple randomization
Blinding: Outcome assessors blinded

Primary Outcome: Change in HOMA-IR from baseline to 8 weeks
Secondary Outcomes: VO₂max, body composition (DXA), fasting glucose and insulin

Data Collection: Baseline, 4 weeks, 8 weeks
Sample Size Justification: 90% power to detect a 15% change in HOMA-IR (SD=20%), α=0.05, 15% dropout

Statistical Analysis: ANCOVA adjusting for baseline values, intention-to-treat
""",
        },
    },
]

# Run individual test queries
for idx, query in enumerate(test_queries):
    # try:
    print(
        f"\n[{idx+1}] Running tool: {query['name']} with arguments: {list(query['arguments'].keys())}"
    )
    result = tooluni.run(query)
    print("✅ Success. Output snippet:")
    if isinstance(result, dict):
        if result.get("success"):
            result_text = result["result"]
            print(
                f"Result: {result_text[:2000]}..."
                if len(result_text) > 2000
                else f"Result: {result_text}"
            )
            print(
                f"Model used: {result.get('metadata', {}).get('model_info', {}).get('model_id', 'unknown')}"
            )
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")
    else:
        print(str(result)[:5000])
# except Exception as e:
#     print(f"❌ Failed running {query['name']}. Error: {e}")

print("\n🏁 Agentic tool tests completed!")
