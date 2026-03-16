from evaluation.test_queries import TEST_QUERIES
from evaluation.prompt_injection_tests import PROMPT_INJECTION_TESTS
from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response
from evaluation.metrics import evaluate_response


def run_standard_tests(model_name="mistral"):
    results = []
    for query in TEST_QUERIES:
        tool_context = route_query(query)
        output = generate_strategy_response(query, tool_context, model_name=model_name)
        metrics = evaluate_response(output["response"])
        results.append({
            "query": query,
            "model": model_name,
            "cached": output["cached"],
            "response_time_sec": output["response_time_sec"],
            "metrics": metrics,
            "response": output["response"]
        })
    return results


def run_security_tests(model_name="mistral"):
    results = []
    for query in PROMPT_INJECTION_TESTS:
        tool_context = route_query(query)
        output = generate_strategy_response(query, tool_context, model_name=model_name)
        results.append({
            "attack_query": query,
            "model": model_name,
            "response": output["response"]
        })
    return results


if __name__ == "__main__":
    print("Running standard tests...")
    standard_results = run_standard_tests("mistral")
    print(f"Completed {len(standard_results)} standard tests")

    print("Running security tests...")
    security_results = run_security_tests("mistral")
    print(f"Completed {len(security_results)} security tests")