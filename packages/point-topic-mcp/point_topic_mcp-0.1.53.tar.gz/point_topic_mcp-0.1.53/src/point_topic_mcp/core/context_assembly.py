import importlib
from pathlib import Path
from point_topic_mcp.context.general_db_instructions import GENERAL_DB_INSTRUCTIONS


def get_available_datasets() -> list[str]:
    """Get list of available dataset names from the datasets directory."""
    datasets_dir = Path(__file__).parent.parent / "context" / "datasets"
    dataset_files = [f.stem for f in datasets_dir.glob("*.py") if f.name != "__init__.py"]
    return dataset_files


def get_dataset_summary(dataset_name: str) -> str:
    """Get summary for a specific dataset."""
    try:
        module = importlib.import_module(f"point_topic_mcp.context.datasets.{dataset_name}")
        if hasattr(module, "get_dataset_summary"):
            return module.get_dataset_summary()
        else:
            return f"Dataset '{dataset_name}' (no summary available)"
    except ImportError:
        raise ValueError(f"Dataset '{dataset_name}' not found")


def list_datasets() -> str:
    """List all available datasets with their summaries."""
    available = get_available_datasets()
    summaries = []
    
    for dataset_name in available:
        try:
            summary = get_dataset_summary(dataset_name)
            summaries.append(f"• **{dataset_name}**: {summary}")
        except Exception as e:
            summaries.append(f"• **{dataset_name}**: Error loading summary - {e}")
    
    return "Available datasets:\n" + "\n".join(summaries)


def assemble_context(db_names: list[str]) -> str:
    """Assemble context from multiple datasets."""
    context_parts = [GENERAL_DB_INSTRUCTIONS]

    
    for db_name in db_names:
        try:
            module = importlib.import_module(f"point_topic_mcp.context.datasets.{db_name}")
            if hasattr(module, "get_db_info"):
                context_parts.append(module.get_db_info())
            else:
                context_parts.append(f"# {db_name.upper()} Dataset\nError: get_db_info() function not found")
        except ImportError:
            context_parts.append(f"# {db_name.upper()} Dataset\nError: Dataset module not found")
    
    return "\n\n".join(context_parts)