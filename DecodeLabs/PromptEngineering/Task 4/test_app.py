import json
from guardrail_engine import GuardrailEngine

def test_full_guardrail_system():
    print("==================================================")
    print("   RUNNING RED TEAMING HEADLESS BENCHMARK")
    print("==================================================")
    
    engine = GuardrailEngine()
    print(f"Active Persona: {engine.current_persona.name}")
    print(f"Target Model: {engine.model}")
    print("Executing 10 Adversarial Attack Vectors...\n")
    
    res = engine.run_red_team_benchmark(
        progress_callback=lambda idx, total, name: print(f"[{idx}/{total}] Testing Attack: {name}...")
    )
    
    print("\n--------------------------------------------------")
    print(f"BENCHMARK COMPLETED")
    print(f"Resilience Score: {res['resilience_score']}%")
    print(f"Defended: {res['defended_count']} / {res['total_tests']}")
    print(f"Bypassed: {res['bypassed_count']} / {res['total_tests']}")
    print("--------------------------------------------------\n")
    
    for item in res["details"]:
        print(f"[{item['attack_id']}] {item['name']:<40} -> {item['status']} (Risk: {item['risk_score']:.2f}, Latency: {item['latency_ms']:.0f}ms)")
        
    print("\n==================================================")
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_full_guardrail_system()
