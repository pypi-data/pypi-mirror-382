"""
Evaluation execution functionality for LLM evaluations.

This module handles running evaluations and printing results.
"""

import sys
from typing import Any

from pydantic_evals.dataset import Dataset


async def run_dataset_evaluation(  # noqa: PLR0913, pylint: disable=too-many-arguments,too-many-positional-arguments
    dataset_name: str,
    dataset: Dataset,
    target_function: Any,
    print_options: dict[str, bool],
    min_assertions: float,
    verbose: bool = False,
) -> tuple[str, bool]:
    """Run evaluation for a single dataset and return (name, success)."""
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Running evaluation: {dataset_name}")
        print(f"{'=' * 60}")
    else:
        print(f"Running {dataset_name}...", end=" ")

    try:
        # Execute the evaluation
        report = await dataset.evaluate(target_function)

        # Print the results
        report.print(
            include_input=print_options["include_input"],
            include_output=print_options["include_output"],
            include_evaluator_failures=print_options["include_evaluator_failures"],
            include_reasons=print_options["include_reasons"],
        )

        # Check if evaluation passed based on assertions average
        averages = report.averages()
        if averages and averages.assertions is not None:
            success = averages.assertions >= min_assertions
            if verbose:
                print(f"\nEvaluation Summary for {dataset_name}:")
                print(f"  Assertions Average: {averages.assertions:.3f}")
                print(f"  Minimum Required: {min_assertions:.3f}")
                print(f"  Status: {'PASSED' if success else 'FAILED'}")
            else:
                print(f"{'PASSED' if success else 'FAILED'} ({averages.assertions:.3f})")
        else:
            success = False
            if verbose:
                print(f"\nEvaluation Summary for {dataset_name}:")
                print("  No assertions found or evaluation failed")
                print(f"  Minimum Required: {min_assertions:.3f}")
                print("  Status: FAILED")
            else:
                print("FAILED (no assertions)")

        return dataset_name, success

    except Exception as e:  # pylint: disable=broad-exception-caught
        if verbose:
            print(f"Error running evaluation {dataset_name}: {e}")
        else:
            print(f"ERROR ({e})")
        return dataset_name, False


async def run_all_evaluations_and_print_results(
    datasets: list[tuple[str, Dataset, Any]], print_options: dict[str, bool], min_assertions: float, verbose: bool
) -> None:
    """Run all evaluations and print results with summary."""
    # Run all evaluations
    results = []
    for dataset_name, dataset, target_function in datasets:
        result = await run_dataset_evaluation(
            dataset_name, dataset, target_function, print_options, min_assertions, verbose
        )
        results.append(result)

    # Print summary
    passed = sum(1 for _, success in results if success)
    total = len(results)
    failed_results = [(name, success) for name, success in results if not success]

    if verbose:
        print(f"\n{'=' * 60}")
        print("EVALUATION SUMMARY")
        print(f"{'=' * 60}")

        for name, success in results:
            status = "PASSED" if success else "FAILED"
            print(f"  {name}: {status}")

        print(f"\nTotal: {passed}/{total} evaluations passed")
    # Only show failed evaluations when not verbose
    elif failed_results:
        print("\nFailed evaluations:")
        for name, _ in failed_results:
            print(f"  {name}: FAILED")

    # Exit with non-zero code if any evaluations failed
    if passed < total:
        print(f"\n{total - passed} evaluation(s) failed")
        sys.exit(1)
    else:
        print("\nAll evaluations passed!")
