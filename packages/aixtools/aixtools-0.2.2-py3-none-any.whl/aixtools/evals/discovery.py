"""
Dataset discovery functionality for LLM evaluations.

This module handles discovering and loading Dataset objects from eval_*.py files.
"""

import importlib.util
import inspect
import sys
import traceback
from pathlib import Path
from typing import Any

from pydantic_evals.dataset import Dataset


def find_eval_files(evals_dir: Path) -> list[Path]:
    """Find all eval_*.py files in the evals directory."""
    if not evals_dir.exists():
        print(f"Error: Evals directory '{evals_dir}' does not exist")
        sys.exit(1)

    eval_files = list(evals_dir.glob("eval_*.py"))
    if not eval_files:
        print(f"No eval_*.py files found in '{evals_dir}'")
        sys.exit(1)

    return eval_files


def find_datasets_in_module(module: Any) -> list[tuple[str, Dataset]]:
    """Find all Dataset objects with names matching dataset_* in a module."""
    datasets = []

    for name, obj in inspect.getmembers(module):
        if name.startswith("dataset_") and isinstance(obj, Dataset):
            datasets.append((name, obj))

    return datasets


def load_module_from_file(file_path: Path) -> Any:
    """Load a Python module from a file path."""
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def matches_filter(module_name: str, file_name: str, dataset_name: str, name_filter: str | None) -> bool:
    """Check if the dataset matches the name filter."""
    if name_filter is None:
        return True

    # Check if filter matches any of: module name, file name, dataset name, or full qualified name
    full_name = f"{module_name}.{dataset_name}"
    return (
        name_filter in module_name
        or name_filter in file_name
        or name_filter in dataset_name
        or name_filter in full_name
    )


def find_target_function(module: Any) -> Any | None:
    """Find the first async function in a module that doesn't start with underscore."""
    for name, obj in inspect.getmembers(module):
        if inspect.iscoroutinefunction(obj) and not name.startswith("_"):
            return obj
    return None


def get_async_function_names(module: Any) -> list[str]:
    """Get names of all async functions in a module that don't start with underscore."""
    return [
        name
        for name, obj in inspect.getmembers(module)
        if inspect.iscoroutinefunction(obj) and not name.startswith("_")
    ]


def process_datasets_from_module(
    module: Any, eval_file: Path, name_filter: str | None, verbose: bool
) -> list[tuple[str, Dataset, Any]]:
    """Process all datasets from a single module and return valid dataset tuples."""
    datasets = find_datasets_in_module(module)
    if verbose:
        print(f"  Found {len(datasets)} datasets: {[name for name, _ in datasets]}")

    valid_datasets = []

    for dataset_name, dataset in datasets:
        full_name = f"{eval_file.stem}.{dataset_name}"

        if not matches_filter(module.__name__, eval_file.stem, dataset_name, name_filter):
            if verbose:
                print(f"    ✗ Skipping dataset: {dataset_name} (doesn't match filter: {name_filter})")
            continue

        if verbose:
            print(f"    ✓ Including dataset: {dataset_name}")

        # Find the target function
        target_function = find_target_function(module)
        async_functions = get_async_function_names(module)

        if verbose:
            print(f"      Found async functions: {async_functions}")
            if target_function:
                print(f"      Using target function: {target_function.__name__}")

        if target_function is None:
            if verbose:
                print(f"Warning: No async function found in {eval_file.name} for dataset {dataset_name}")
            continue

        valid_datasets.append((full_name, dataset, target_function))

    return valid_datasets


def discover_all_datasets(
    eval_files: list[Path], name_filter: str | None, verbose: bool
) -> list[tuple[str, Dataset, Any]]:
    """Discover all datasets from eval files."""
    all_datasets = []

    for eval_file in eval_files:
        if verbose:
            print(f"\nProcessing file: {eval_file}")

        try:
            module = load_module_from_file(eval_file)
            if verbose:
                print(f"  Loaded module: {module.__name__}")

            datasets = process_datasets_from_module(module, eval_file, name_filter, verbose)
            all_datasets.extend(datasets)

        except Exception as e:  # pylint: disable=W0718
            if verbose:
                print(f"Error loading {eval_file}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
            continue

    # Check if any datasets were found
    if not all_datasets:
        print("No datasets found to evaluate")
        if verbose:
            print("This could be because:")
            print("  - No eval_*.py files contain dataset_* objects")
            print("  - The filter excluded all datasets")
            print("  - There were errors loading the modules")
        sys.exit(1)

    # Print summary of discovered datasets
    if verbose:
        print(f"\n{'=' * 60}")
        print("Datasets to Evaluate:")
        print(f"{'=' * 60}")
        for i, (dataset_name, dataset, target_function) in enumerate(all_datasets, 1):
            print(f"{i}. {dataset_name}")
            print(f"   Target function: {target_function.__name__}")
            print(f"   Cases: {len(dataset.cases)}")
            print(f"   Evaluators: {len(dataset.evaluators)}")
        print(f"{'=' * 60}")
    else:
        print(f"Found {len(all_datasets)} datasets to evaluate")

    return all_datasets
