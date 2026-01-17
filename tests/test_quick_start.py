"""
Test script that runs through the QUICK_START.md use cases.
This simulates what a user would do when interacting with Claude.
"""

import sys
import shutil
from pathlib import Path

# Fix Windows console encoding for unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.server import (
    ingest_hypothesis,
    connect_propositions,
    semantic_search,
    find_scientific_lineage,
    find_contradictions,
    list_propositions,
    get_unit,
)

# Store unit IDs for later use
units = {}


def get_action_tool(action):
    """Extract tool name from action (dict or Pydantic object)."""
    if isinstance(action, dict):
        return action.get("tool", "unknown")
    return getattr(action, "tool", "unknown")


def print_result(title: str, result: dict):
    """Pretty print a result."""
    print(f"\n{'='*60}")
    print(f"[RESULT] {title}")
    print(f"{'='*60}")
    if result.get("status") == "success":
        print(f"[OK] Status: SUCCESS")
    else:
        print(f"[FAIL] Status: {result.get('status', 'unknown')}")
        if "message" in result:
            print(f"   Message: {result['message']}")

    # Print key fields
    for key, value in result.items():
        if key in ["status", "available_actions"]:
            continue
        if isinstance(value, list) and len(value) > 3:
            print(f"   {key}: [{len(value)} items]")
            for i, item in enumerate(value[:3]):
                if isinstance(item, dict):
                    content = item.get("content", item.get("unit_id", str(item)))[:60]
                    print(f"      {i+1}. {content}...")
                else:
                    print(f"      {i+1}. {str(item)[:60]}...")
            if len(value) > 3:
                print(f"      ... and {len(value) - 3} more")
        elif isinstance(value, dict):
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {str(value)[:100]}")

    if result.get("available_actions"):
        actions = [get_action_tool(a) for a in result["available_actions"]]
        print(f"   [ACTIONS] Available: {actions}")


def run_use_case_1():
    """Use Case 1: Your First Hypothesis"""
    print("\n" + "[TEST] USE CASE 1: Your First Hypothesis".center(60, "="))

    result = ingest_hypothesis(
        hypothesis="Water boils at 100 degrees Celsius at sea level",
        idempotency_key="test-uc1"
    )
    print_result("Ingested first hypothesis", result)
    units["water"] = result.get("unit_id")
    return result.get("status") == "success"


def run_use_case_2():
    """Use Case 2: Adding a Source"""
    print("\n" + "[TEST] USE CASE 2: Adding a Source".center(60, "="))

    result = ingest_hypothesis(
        hypothesis="The speed of light is approximately 299,792 kilometers per second",
        source="Einstein's theory of special relativity",
        idempotency_key="test-uc2"
    )
    print_result("Ingested hypothesis with source", result)
    units["light"] = result.get("unit_id")
    return result.get("status") == "success"


def run_use_case_3():
    """Use Case 3: Multiple Related Claims"""
    print("\n" + "[TEST] USE CASE 3: Multiple Related Claims".center(60, "="))

    claims = [
        ("Neural networks are computational models inspired by biological brains", "test-uc3-nn1"),
        ("Neural networks consist of interconnected nodes organized in layers", "test-uc3-nn2"),
        ("Deep learning refers to neural networks with many hidden layers", "test-uc3-nn3"),
        ("Each layer in a neural network transforms its input before passing to the next", "test-uc3-nn4"),
    ]

    success = True
    for claim, key in claims:
        result = ingest_hypothesis(hypothesis=claim, idempotency_key=key)
        print_result(f"Ingested: {claim[:40]}...", result)
        units[key] = result.get("unit_id")
        if result.get("status") != "success":
            success = False

    return success


def run_use_case_4():
    """Use Case 4: Connecting Ideas"""
    print("\n" + "[TEST] USE CASE 4: Connecting Ideas".center(60, "="))

    # Connect neural networks inspired by brains -> interconnected nodes
    result1 = connect_propositions(
        id_a=units["test-uc3-nn1"],
        id_b=units["test-uc3-nn2"],
        relation="supports",
        reasoning="The node structure mimics how neurons connect in biological brains",
        idempotency_key="test-uc4-conn1"
    )
    print_result("Connected: brains -> nodes", result1)

    # Connect deep learning -> layers
    result2 = connect_propositions(
        id_a=units["test-uc3-nn3"],
        id_b=units["test-uc3-nn2"],
        relation="extends",
        reasoning="Deep learning is a specific case of neural networks with many layers",
        idempotency_key="test-uc4-conn2"
    )
    print_result("Connected: deep learning -> layers", result2)

    return result1.get("status") == "success" and result2.get("status") == "success"


def run_use_case_5():
    """Use Case 5: Your First Search"""
    print("\n" + "[TEST] USE CASE 5: Your First Search".center(60, "="))

    result = semantic_search(query="how brains inspire computing", limit=5)
    print_result("Search: 'how brains inspire computing'", result)

    # Try another search
    result2 = semantic_search(query="deep learning", limit=5)
    print_result("Search: 'deep learning'", result2)

    return result.get("status") == "success" and len(result.get("results", [])) > 0


def run_use_case_6():
    """Use Case 6: Exploring a Unit"""
    print("\n" + "[TEST] USE CASE 6: Exploring a Unit".center(60, "="))

    # Get details for the neural network unit
    unit_id = units.get("test-uc3-nn1")
    if not unit_id:
        print("[FAIL] No unit ID available for exploration")
        return False

    result = get_unit(unit_id=unit_id)
    print_result(f"Get unit details: {unit_id[:20]}...", result)

    return result.get("status") == "success"


def run_use_case_7():
    """Use Case 7: Building a Research Topic (Transformers)"""
    print("\n" + "[TEST] USE CASE 7: Building a Research Topic".center(60, "="))

    transformer_claims = [
        ("The Transformer architecture was introduced in 'Attention Is All You Need' in 2017", "Vaswani et al.", "test-uc7-t1"),
        ("Transformers use self-attention mechanisms to process sequences in parallel", None, "test-uc7-t2"),
        ("Self-attention allows each position in a sequence to attend to all other positions", None, "test-uc7-t3"),
        ("BERT uses transformer encoders for language understanding", "Devlin et al. 2018", "test-uc7-t4"),
        ("GPT uses transformer decoders for text generation", "OpenAI", "test-uc7-t5"),
    ]

    success = True
    for claim, source, key in transformer_claims:
        result = ingest_hypothesis(
            hypothesis=claim,
            source=source or "",
            idempotency_key=key
        )
        print_result(f"Ingested: {claim[:40]}...", result)
        units[key] = result.get("unit_id")
        if result.get("status") != "success":
            success = False

    # Connect self-attention to Transformer
    conn1 = connect_propositions(
        id_a=units["test-uc7-t2"],
        id_b=units["test-uc7-t1"],
        relation="supports",
        reasoning="Self-attention is the core mechanism that makes transformers work",
        idempotency_key="test-uc7-conn1"
    )
    print_result("Connected: self-attention -> Transformer", conn1)

    # Connect BERT to Transformer
    conn2 = connect_propositions(
        id_a=units["test-uc7-t4"],
        id_b=units["test-uc7-t1"],
        relation="extends",
        reasoning="BERT builds on the transformer encoder architecture",
        idempotency_key="test-uc7-conn2"
    )
    print_result("Connected: BERT -> Transformer", conn2)

    # Connect GPT to Transformer
    conn3 = connect_propositions(
        id_a=units["test-uc7-t5"],
        id_b=units["test-uc7-t1"],
        relation="extends",
        reasoning="GPT builds on the transformer decoder architecture",
        idempotency_key="test-uc7-conn3"
    )
    print_result("Connected: GPT -> Transformer", conn3)

    return success


def run_use_case_8():
    """Use Case 8: Finding Intellectual Lineage"""
    print("\n" + "[TEST] USE CASE 8: Finding Intellectual Lineage".center(60, "="))

    result = find_scientific_lineage(
        start_concept="neural networks",
        end_concept="GPT"
    )
    print_result("Lineage: neural networks -> GPT", result)

    return result.get("status") == "success"


def run_use_case_9():
    """Use Case 9: Checking for Contradictions"""
    print("\n" + "[TEST] USE CASE 9: Checking for Contradictions".center(60, "="))

    # First add a claim about RNNs
    result1 = ingest_hypothesis(
        hypothesis="Recurrent neural networks (RNNs) process sequences one step at a time",
        idempotency_key="test-uc9-rnn"
    )
    print_result("Ingested RNN claim", result1)
    units["rnn"] = result1.get("unit_id")

    # Check for contradiction
    result2 = find_contradictions(
        claim="RNNs process entire sequences in parallel"
    )
    print_result("Check contradiction: 'RNNs process in parallel'", result2)

    return result1.get("status") == "success"


def run_use_case_10():
    """Use Case 10: Building a Contradiction"""
    print("\n" + "[TEST] USE CASE 10: Building a Contradiction".center(60, "="))

    # Add conflicting claims
    result1 = ingest_hypothesis(
        hypothesis="Larger language models always perform better than smaller ones",
        idempotency_key="test-uc10-large"
    )
    print_result("Ingested: larger models claim", result1)
    units["larger"] = result1.get("unit_id")

    result2 = ingest_hypothesis(
        hypothesis="Some smaller, specialized models outperform larger general-purpose models on specific tasks",
        source="various benchmark studies",
        idempotency_key="test-uc10-small"
    )
    print_result("Ingested: smaller models claim", result2)
    units["smaller"] = result2.get("unit_id")

    # Connect as contradiction
    result3 = connect_propositions(
        id_a=units["smaller"],
        id_b=units["larger"],
        relation="contradicts",
        reasoning="Benchmark results show that 'bigger is always better' is oversimplified",
        idempotency_key="test-uc10-conn"
    )
    print_result("Connected as contradiction", result3)

    # Search for contradictions
    result4 = find_contradictions(claim="model size and performance")
    print_result("Find contradictions about model size", result4)

    return result1.get("status") == "success" and result2.get("status") == "success"


def run_use_case_11():
    """Use Case 11: Building a Literature Review"""
    print("\n" + "[TEST] USE CASE 11: Building a Literature Review".center(60, "="))

    papers = [
        ("Attention mechanisms were first applied to sequence-to-sequence models for machine translation", "Bahdanau et al. 2014", "test-uc11-p1"),
        ("The Transformer replaced recurrence with self-attention for improved parallelization", "Vaswani et al. 2017", "test-uc11-p2"),
        ("Multi-head attention allows the model to attend to information from different representation subspaces", "Vaswani et al. 2017", "test-uc11-p3"),
    ]

    success = True
    for claim, source, key in papers:
        result = ingest_hypothesis(hypothesis=claim, source=source, idempotency_key=key)
        print_result(f"Ingested: {claim[:40]}...", result)
        units[key] = result.get("unit_id")
        if result.get("status") != "success":
            success = False

    # Connect the evolution
    conn = connect_propositions(
        id_a=units["test-uc11-p2"],
        id_b=units["test-uc11-p1"],
        relation="extends",
        reasoning="Transformers generalized the attention concept from the earlier work",
        idempotency_key="test-uc11-conn"
    )
    print_result("Connected: Transformer -> Bahdanau attention", conn)

    # Search
    search = semantic_search(query="attention in neural networks", limit=5)
    print_result("Search: attention in neural networks", search)

    return success


def run_use_case_12():
    """Use Case 12: Cross-Domain Knowledge"""
    print("\n" + "[TEST] USE CASE 12: Cross-Domain Knowledge".center(60, "="))

    domains = [
        ("Entropy measures the disorder or randomness in a system", "thermodynamics", "test-uc12-d1"),
        ("Information entropy measures the average information content in a message", "Shannon 1948", "test-uc12-d2"),
        ("Cross-entropy loss measures the difference between predicted and true probability distributions", None, "test-uc12-d3"),
    ]

    success = True
    for claim, source, key in domains:
        result = ingest_hypothesis(hypothesis=claim, source=source or "", idempotency_key=key)
        print_result(f"Ingested: {claim[:40]}...", result)
        units[key] = result.get("unit_id")
        if result.get("status") != "success":
            success = False

    # Connect across domains
    conn1 = connect_propositions(
        id_a=units["test-uc12-d2"],
        id_b=units["test-uc12-d1"],
        relation="extends",
        reasoning="Shannon explicitly drew on thermodynamic entropy when formulating information entropy",
        idempotency_key="test-uc12-conn1"
    )
    print_result("Connected: information entropy -> thermodynamic entropy", conn1)

    conn2 = connect_propositions(
        id_a=units["test-uc12-d3"],
        id_b=units["test-uc12-d2"],
        relation="extends",
        reasoning="Cross-entropy in ML is a direct application of Shannon's information entropy",
        idempotency_key="test-uc12-conn2"
    )
    print_result("Connected: cross-entropy -> information entropy", conn2)

    # Search across domains
    search = semantic_search(query="measuring disorder or uncertainty", limit=5)
    print_result("Search: measuring disorder or uncertainty", search)

    # Find lineage
    lineage = find_scientific_lineage(
        start_concept="thermodynamics",
        end_concept="machine learning loss functions"
    )
    print_result("Lineage: thermodynamics -> ML loss functions", lineage)

    return success


def run_final_summary():
    """Final summary of the knowledge graph."""
    print("\n" + "[SUMMARY] FINAL SUMMARY".center(60, "="))

    result = list_propositions(limit=50)
    print_result("All propositions in knowledge graph", result)

    print(f"\n[STAT] Total units created: {len(units)}")
    print(f"[STAT] Total propositions in graph: {result.get('count', 0)}")


def main():
    """Run all use cases from QUICK_START.md"""
    print("\n" + "="*60)
    print("[START] KNOWLEDGE GRAPH CLI QUICK START TEST SUITE")
    print("="*60)
    print("Running all 12 use cases from QUICK_START.md")
    print("This will create a knowledge graph with scientific claims,")
    print("connections, and demonstrate search/lineage/contradiction features.")
    print("="*60)

    # Clean up old test data
    test_data_dir = Path(__file__).parent.parent / "data"
    if test_data_dir.exists():
        print(f"\n[WARN]  Cleaning up existing data in {test_data_dir}")
        shutil.rmtree(test_data_dir)
        print("[OK] Old data removed")

    results = {}

    try:
        results["UC1"] = run_use_case_1()
        results["UC2"] = run_use_case_2()
        results["UC3"] = run_use_case_3()
        results["UC4"] = run_use_case_4()
        results["UC5"] = run_use_case_5()
        results["UC6"] = run_use_case_6()
        results["UC7"] = run_use_case_7()
        results["UC8"] = run_use_case_8()
        results["UC9"] = run_use_case_9()
        results["UC10"] = run_use_case_10()
        results["UC11"] = run_use_case_11()
        results["UC12"] = run_use_case_12()

        run_final_summary()

    except Exception as e:
        print(f"\n[FAIL] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Print final results
    print("\n" + "="*60)
    print("[END] TEST RESULTS SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for uc, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"   {uc}: {status}")

    print(f"\n[SUMMARY] Total: {passed}/{total} use cases passed")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Your Knowledge Graph CLI installation is working correctly.")
        return 0
    else:
        print(f"\n[WARN]  {total - passed} test(s) failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
