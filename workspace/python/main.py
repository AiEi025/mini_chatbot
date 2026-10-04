# main.py
# Fixed version of the intentionally buggy Python code.

from typing import Any, Dict, List, Optional, Sequence


def calculate_average(numbers: Sequence[float]) -> float:
    """Calculate the average of a list of numbers.

    Raises:
        ValueError: if `numbers` is empty.
    """
    # Bug 1 fix: guard against ZeroDivisionError on an empty sequence.
    if not numbers:
        raise ValueError("cannot calculate the average of an empty sequence")
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def find_max(items: Sequence[Any]) -> Any:
    """Find the maximum value in a list.

    Raises:
        ValueError: if `items` is empty.
    """
    # Bug 2 fix: guard against IndexError on an empty sequence.
    if not items:
        raise ValueError("find_max() arg is an empty sequence")
    max_val = items[0]
    for item in items:
        if item > max_val:
            max_val = item
    return max_val


def reverse_string(s: str) -> str:
    """Reverse a string."""
    # Bug 3 fix: the loop returned the string unchanged; slicing does the reversal.
    return s[::-1]


def is_palindrome(word: str) -> bool:
    """Check if a word is a palindrome."""
    cleaned = word.lower().replace(" ", "")
    return cleaned == reverse_string(cleaned)  # now correct, relies on fixed reverse_string


def process_data(data: Dict[Any, Any]) -> List[str]:
    """Process a dictionary of data."""
    results = []
    for key, value in data.items():
        try:
            is_high = value > 10
        except TypeError:
            # Non-numeric values aren't comparable with 10.
            is_high = False
        # Bug 4 fix: build the label with an f-string so non-str keys don't raise.
        results.append(f"{key}: {'high' if is_high else 'low'}")
    return results


def factorial(n: int) -> int:
    """Calculate factorial of n.

    Raises:
        TypeError: if `n` is not an int.
        ValueError: if `n` is negative.
    """
    if not isinstance(n, int):
        raise TypeError("factorial() only accepts integers")
    if n < 0:
        raise ValueError("factorial() is not defined for negative values")
    if n == 0:
        return 1
    # Bug 5 fix: recurse on n - 1 instead of n (was infinite recursion).
    return n * factorial(n - 1)


def safe_divide(a: float, b: float) -> float:
    """Safely divide a by b.

    Raises:
        ValueError: if `b` is zero.
    """
    # Bug 6 fix: check for a zero divisor instead of raising ZeroDivisionError.
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


def get_user_age(user: Dict[str, Any]) -> Optional[Any]:
    """Get age from a user dictionary, or None if the key is missing."""
    # Bug 7 fix: .get() avoids the KeyError for a missing "age" key.
    return user.get("age")


def main() -> None:
    def show(label: str, fn, *args) -> None:
        """Run fn(*args), printing the result or the error it raises."""
        try:
            print(f"{label}: {fn(*args)}")
        except (ValueError, TypeError, KeyError) as exc:
            print(f"{label}: error -> {exc}")

    show("Average", calculate_average, [1, 2, 3, 4, 5])
    show("Average empty", calculate_average, [])

    show("Max", find_max, [3, 1, 4, 1, 5])
    show("Max empty", find_max, [])

    show("Reverse 'hello'", reverse_string, "hello")

    show("Palindrome 'racecar'", is_palindrome, "racecar")
    show("Palindrome 'hello'", is_palindrome, "hello")

    show("Process", process_data, {"a": 15, "b": 5, 123: 20})

    show("Factorial 5", factorial, 5)

    show("Safe divide 10 / 0", safe_divide, 10, 0)

    show("User age", get_user_age, {"name": "Alice"})


if __name__ == "__main__":
    main()
