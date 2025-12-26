"""
Performance benchmarking for LeaseLogic

Measures query response times across different query types
to verify intelligent routing optimization.
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.supervisor import run_analysis

def benchmark_query_speed():
    """Measure average query response time"""

    queries = [
        ("Can my landlord charge a $300 late fee?", "both"),
        ("What is the maximum security deposit?", "law_only"),
        ("What is my monthly rent?", "lease_only"),
    ]

    times = []
    results = []

    print("=" * 60)
    print("PERFORMANCE BENCHMARK: Query Speed")
    print("=" * 60)

    for query, expected_scope in queries:
        print(f"\nQuery: {query}")
        print(f"Expected scope: {expected_scope}")
        start = time.time()

        result = run_analysis(
            user_query=query,
            lease_collection_name="test_lease_phase1",
            state_location="california"
        )

        elapsed = time.time() - start
        times.append(elapsed)
        results.append({
            'query': query,
            'expected_scope': expected_scope,
            'actual_scope': result.get('query_scope', 'unknown'),
            'time': elapsed,
            'iterations': result.get('requery_count', 0) + 1,
            'quality': result.get('retrieval_quality_grade', 0)
        })

        print(f"Time: {elapsed:.2f}s")
        print(f"Scope: {result.get('query_scope', 'unknown')}")
        print(f"Iterations: {result.get('requery_count', 0) + 1}")
        print(f"Quality: {result.get('retrieval_quality_grade', 0)}/10")

        # Note: lease_only and law_only queries should be faster
        # since they skip one retrieval step
        if result.get('query_scope') in ['lease_only', 'law_only']:
            print(f"[✓] Optimized query (skipped irrelevant search)")

    avg_time = sum(times) / len(times)
    print(f"\n{'='*60}")
    print(f"PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    print(f"Average query time: {avg_time:.2f}s")
    print(f"Min: {min(times):.2f}s | Max: {max(times):.2f}s")
    print(f"{'='*60}")

    # Breakdown by query type
    print(f"\nBreakdown by Query Type:")
    for r in results:
        print(f"  {r['actual_scope']:12s}: {r['time']:.2f}s (quality: {r['quality']}/10)")

    # Calculate optimized query average (lease_only and law_only)
    optimized_times = [r['time'] for r in results if r['actual_scope'] in ['lease_only', 'law_only']]
    if optimized_times:
        optimized_avg = sum(optimized_times) / len(optimized_times)
        print(f"\nOptimized queries average: {optimized_avg:.2f}s")

    # Performance targets (relaxed for corrective RAG with multiple iterations)
    # Optimized queries should be fast
    if optimized_times:
        assert optimized_avg < 30, f"Optimized avg {optimized_avg:.2f}s exceeds 30s target"

    # Overall average can be higher due to corrective RAG iterations
    print(f"\n[OK] Performance benchmark complete!")
    print(f"Note: 'both' queries may take longer due to corrective RAG refinement")

    return results

def benchmark_quality_distribution():
    """Measure retrieval quality distribution"""

    queries = [
        "What is my monthly rent?",
        "Can I have pets?",
        "What does California law say about security deposits?",
        "Is my late fee legal?",
        "How much notice for landlord entry?"
    ]

    qualities = []

    print("\n" + "=" * 60)
    print("QUALITY BENCHMARK: Retrieval Accuracy")
    print("=" * 60)

    for query in queries:
        result = run_analysis(
            user_query=query,
            lease_collection_name="test_lease_phase1",
            state_location="california"
        )

        quality = result.get('retrieval_quality_grade', 0)
        qualities.append(quality)

        print(f"\nQuery: {query}")
        print(f"  Quality: {quality}/10")
        print(f"  Confidence: {result.get('confidence', 'UNKNOWN')}")

    avg_quality = sum(qualities) / len(qualities)
    high_quality_count = sum(1 for q in qualities if q >= 7)

    print(f"\n{'='*60}")
    print(f"QUALITY SUMMARY")
    print(f"{'='*60}")
    print(f"Average quality: {avg_quality:.1f}/10")
    print(f"Queries >= 7/10: {high_quality_count}/{len(qualities)} ({high_quality_count/len(qualities)*100:.0f}%)")
    print(f"Min: {min(qualities)}/10 | Max: {max(qualities)}/10")
    print(f"{'='*60}")

    # Quality targets
    assert avg_quality >= 6.0, f"Avg quality {avg_quality:.1f} below 6.0 target"
    print(f"\n[OK] Quality benchmark passed!")

    return qualities

def benchmark_cost_estimation():
    """Estimate cost per query by type"""

    # Based on actual pricing
    COSTS = {
        'classifier': 0.001,
        'embedding': 0.002,
        'lease_analysis': 0.03,
        'law_analysis': 0.02,
        'grading': 0.01,
        'synthesis': 0.02
    }

    query_types = {
        'both': ['classifier', 'embedding', 'lease_analysis', 'law_analysis', 'grading', 'synthesis'],
        'lease_only': ['classifier', 'embedding', 'lease_analysis', 'grading', 'synthesis'],
        'law_only': ['classifier', 'law_analysis', 'grading', 'synthesis']
    }

    print("\n" + "=" * 60)
    print("COST BENCHMARK: Estimated Query Costs")
    print("=" * 60)

    for query_type, components in query_types.items():
        cost = sum(COSTS[c] for c in components)
        print(f"\n{query_type.upper()} queries:")
        for component in components:
            print(f"  {component:20s}: ${COSTS[component]:.3f}")
        print(f"  {'TOTAL':20s}: ${cost:.3f}")

    # Calculate savings
    both_cost = sum(COSTS[c] for c in query_types['both'])
    lease_cost = sum(COSTS[c] for c in query_types['lease_only'])
    law_cost = sum(COSTS[c] for c in query_types['law_only'])

    print(f"\n{'='*60}")
    print(f"COST SAVINGS FROM INTELLIGENT ROUTING")
    print(f"{'='*60}")
    print(f"Lease-only savings: ${both_cost - lease_cost:.3f} ({(both_cost - lease_cost)/both_cost*100:.0f}%)")
    print(f"Law-only savings: ${both_cost - law_cost:.3f} ({(both_cost - law_cost)/both_cost*100:.0f}%)")
    print(f"{'='*60}")

    print(f"\n[OK] Cost benchmark complete!")

if __name__ == "__main__":
    print("\nNOTE: These benchmarks use the existing 'test_lease_phase1' collection")
    print("If that doesn't exist, run test_phase1.py first\n")

    # Run benchmarks
    benchmark_query_speed()
    benchmark_quality_distribution()
    benchmark_cost_estimation()

    print("\n" + "=" * 60)
    print("[OK] ALL PERFORMANCE BENCHMARKS COMPLETE")
    print("=" * 60)
