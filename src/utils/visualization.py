from typing import Dict, List, Tuple


def get_top_k_predictions(
    class_probabilities: Dict[str, float],
    k: int = 3
) -> List[Tuple[str, float]]:
    """
    Return the top-k predictions sorted by probability in descending order.

    Args:
        class_probabilities: Dictionary of {class_name: probability}
        k: Number of top predictions to return

    Returns:
        List of tuples: [(class_name, probability), ...]
    """
    return sorted(
        class_probabilities.items(),
        key=lambda x: x[1],
        reverse=True
    )[:k]


def format_class_name(class_name: str) -> str:
    """
    Convert class name from snake_case to readable Title Case.

    Example:
        'bacterial_leaf_blight' -> 'Bacterial Leaf Blight'
    """
    return class_name.replace("_", " ").title()


def format_percentage(probability: float) -> str:
    """
    Convert probability value to percentage string.

    Example:
        0.9234 -> '92.34%'
    """
    return f"{probability * 100:.2f}%"


def prepare_prediction_rows(
    class_probabilities: Dict[str, float],
    k: int = 3
) -> List[Dict[str, str]]:
    """
    Prepare top-k predictions in a display-friendly format.

    Returns:
        [
            {"class_name": "Blast", "probability": "91.24%"},
            ...
        ]
    """
    top_predictions = get_top_k_predictions(class_probabilities, k=k)

    rows = []
    for class_name, prob in top_predictions:
        rows.append({
            "class_name": format_class_name(class_name),
            "probability": format_percentage(prob)
        })

    return rows