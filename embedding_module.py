import numpy as np

def get_embedding(text: str) -> np.ndarray:
    """
    Generate a fake embedding for demonstration purposes.
    Replace this function with actual embedding logic using models such as `transformers`.
    """
    # Example: Create a random vector as a placeholder
    np.random.seed(0)  # For reproducibility
    return np.random.rand(300)  # Assuming the embedding dimension is 300
