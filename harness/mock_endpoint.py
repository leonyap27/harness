"""Mock LLM endpoint — returns deterministic or randomised responses without a real API key."""

import random
from typing import Optional


_FIXED_RESPONSES = [
    "14 days annual leave",
    "Direct manager",
    "Submit form HR-03 to the HR department within 30 days",
    "Medical certificates must be submitted within 3 working days",
    "Contact your department head for approval",
]


def call_endpoint(
    prompt: str,
    *,
    mode: str = "random",
    seed: Optional[int] = None,
    fail_rate: float = 0.0,
) -> str:
    """Simulate an LLM endpoint call.

    Args:
        prompt: The input question / prompt text.
        mode: "random" picks a random canned response; "echo" returns the prompt itself;
              "fixed" always returns the first canned response.
        seed: Optional RNG seed for reproducibility (applies when mode="random").
        fail_rate: Probability [0.0, 1.0] that this call raises an exception,
                   simulating a transient endpoint error.

    Returns:
        A non-empty string representing the model response.

    Raises:
        RuntimeError: Simulated endpoint failure when fail_rate > 0 and the RNG fires.
        ValueError: If mode is unrecognised.
    """
    rng = random.Random(seed)

    if fail_rate > 0 and rng.random() < fail_rate:
        raise RuntimeError("mock endpoint: simulated transient failure")

    if mode == "echo":
        return prompt
    if mode == "fixed":
        return _FIXED_RESPONSES[0]
    if mode == "random":
        return rng.choice(_FIXED_RESPONSES)

    raise ValueError(f"unknown mode {mode!r}; expected 'random', 'fixed', or 'echo'")
