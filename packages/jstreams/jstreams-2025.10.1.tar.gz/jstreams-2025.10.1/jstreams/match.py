from typing import Generic, Optional, TypeVar, Union, final, overload
from collections.abc import Callable
from jstreams.stream import Opt
from jstreams.predicate import Predicate, _extract_predicate_fn

T = TypeVar("T")
V = TypeVar("V")


@final
class Case(Generic[T, V]):
    """
    Represents a single case in a match expression.

    A case consists of a matching condition (a value, a predicate function,
    or a Predicate object) and a resulting value or supplier function.
    """

    __slots__ = ("__matching", "__resulting")

    def __init__(
        self,
        matching: Union[T, Callable[[T], bool]],
        resulting: Union[V, Callable[[], V]],
    ) -> None:
        """
        Initializes a Case.

        Args:
            matching: The value, predicate function, or Predicate object to match against.
                        - If a value, it's compared using equality (==).
                        - If a callable/Predicate, it's called with the input value.
            resulting: The result value or a supplier function to generate the result.
                        - If a value, it's returned directly.
                        - If a callable, it's invoked to produce the result.
        """
        self.__matching = (
            _extract_predicate_fn(matching)
            if (callable(matching) or isinstance(matching, Predicate))
            else matching
        )
        self.__resulting = resulting

    def matches(self, value: T) -> bool:
        """
        Checks if the provided value matches this case's condition.

        Args:
            value: The value to check against the matching condition.

        Returns:
            True if the value matches the condition, False otherwise.
        """
        match_condition = self.__matching
        if callable(match_condition):
            # If it's a Predicate function, apply it to the value
            return match_condition(value)
        # Otherwise, perform direct equality check
        return value == match_condition

    def result(self) -> V:
        """
        Gets the result for this case.

        If the result defined during initialization was a callable (supplier function),
        it is invoked now to produce the result. Otherwise, the direct value is returned.

        Returns:
            The resulting value (V) for this case.
        """
        # Use built-in callable()
        if callable(self.__resulting):
            # If it's a callable (supplier function), call it
            return self.__resulting()
        # Otherwise, return the direct value
        return self.__resulting


@final
class Match(Generic[T]):
    """
    Holds the value to be matched and provides the 'of' method to evaluate cases.

    This class facilitates a functional-style pattern matching approach.
    It is typically instantiated via the `match()` or `match_opt()` factory functions.

    Example:
        result = match(5).of(
            case(1, "one"),
            case(lambda x: x > 3, "greater than three"),
            default_case("other")
        )
        # result will be "greater than three"
    """

    __slots__ = ("__value",)

    def __init__(self, value: T) -> None:
        """
        Initializes the Match object with the value to be compared against cases.

        Args:
            value: The value to match.
        """
        self.__value = value

    # --- Overloads for type hinting ---
    # Kept for static analysis benefits, despite verbosity.
    # These overloads help type checkers understand the return type based on the
    # number of cases provided, ensuring all cases return the same type V.
    @overload
    def of(self, case1: Case[T, V]) -> Optional[V]: ...

    @overload
    def of(self, case1: Case[T, V], case2: Case[T, V]) -> Optional[V]: ...

    @overload
    def of(
        self, case1: Case[T, V], case2: Case[T, V], case3: Case[T, V]
    ) -> Optional[V]: ...

    @overload
    def of(
        self, case1: Case[T, V], case2: Case[T, V], case3: Case[T, V], case4: Case[T, V]
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
        case14: Case[T, V],
    ) -> Optional[V]: ...

    @overload
    def of(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
        case14: Case[T, V],
        case15: Case[T, V],
    ) -> Optional[V]: ...

    # --- End Overloads ---

    def of(
        self,
        case1: Case[T, V],
        case2: Optional[Case[T, V]] = None,
        case3: Optional[Case[T, V]] = None,
        case4: Optional[Case[T, V]] = None,
        case5: Optional[Case[T, V]] = None,
        case6: Optional[Case[T, V]] = None,
        case7: Optional[Case[T, V]] = None,
        case8: Optional[Case[T, V]] = None,
        case9: Optional[Case[T, V]] = None,
        case10: Optional[Case[T, V]] = None,
        case11: Optional[Case[T, V]] = None,
        case12: Optional[Case[T, V]] = None,
        case13: Optional[Case[T, V]] = None,
        case14: Optional[Case[T, V]] = None,
        case15: Optional[Case[T, V]] = None,
        case16: Optional[
            Case[T, V]
        ] = None,  # Added one more optional case for symmetry
    ) -> Optional[V]:
        """
        Evaluates the provided cases against the stored value and returns the result
        of the first matching case.

        The cases are evaluated in the order they are provided. The evaluation stops
        as soon as a matching case is found (short-circuiting).

        Args:
            case1: The first case (required).
            case2..16: Optional subsequent cases.

        Returns:
            An Optional containing the result (V) of the first matching case.
            Returns None if no case matches the stored value.
        """
        return self.of_list(
            [
                case1,
                case2,
                case3,
                case4,
                case5,
                case6,
                case7,
                case8,
                case9,
                case10,
                case11,
                case12,
                case13,
                case14,
                case15,
                case16,
            ]
        )

    @overload
    def opt(self, case1: Case[T, V]) -> Opt[V]: ...

    @overload
    def opt(self, case1: Case[T, V], case2: Case[T, V]) -> Opt[V]: ...

    @overload
    def opt(
        self, case1: Case[T, V], case2: Case[T, V], case3: Case[T, V]
    ) -> Opt[V]: ...

    @overload
    def opt(
        self, case1: Case[T, V], case2: Case[T, V], case3: Case[T, V], case4: Case[T, V]
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
        case14: Case[T, V],
    ) -> Opt[V]: ...

    @overload
    def opt(
        self,
        case1: Case[T, V],
        case2: Case[T, V],
        case3: Case[T, V],
        case4: Case[T, V],
        case5: Case[T, V],
        case6: Case[T, V],
        case7: Case[T, V],
        case8: Case[T, V],
        case9: Case[T, V],
        case10: Case[T, V],
        case11: Case[T, V],
        case12: Case[T, V],
        case13: Case[T, V],
        case14: Case[T, V],
        case15: Case[T, V],
    ) -> Opt[V]: ...

    # --- End Overloads ---

    def opt(
        self,
        case1: Case[T, V],
        case2: Optional[Case[T, V]] = None,
        case3: Optional[Case[T, V]] = None,
        case4: Optional[Case[T, V]] = None,
        case5: Optional[Case[T, V]] = None,
        case6: Optional[Case[T, V]] = None,
        case7: Optional[Case[T, V]] = None,
        case8: Optional[Case[T, V]] = None,
        case9: Optional[Case[T, V]] = None,
        case10: Optional[Case[T, V]] = None,
        case11: Optional[Case[T, V]] = None,
        case12: Optional[Case[T, V]] = None,
        case13: Optional[Case[T, V]] = None,
        case14: Optional[Case[T, V]] = None,
        case15: Optional[Case[T, V]] = None,
        case16: Optional[
            Case[T, V]
        ] = None,  # Added one more optional case for symmetry
    ) -> Opt[V]:
        """
        Evaluates the provided cases against the stored value and returns the result
        of the first matching case.

        The cases are evaluated in the order they are provided. The evaluation stops
        as soon as a matching case is found (short-circuiting).

        Args:
            case1: The first case (required).
            case2..16: Optional subsequent cases.

        Returns:
            An Optional containing the result (V) of the first matching case.
            Returns None if no case matches the stored value.
        """
        return self.opt_list(
            [
                case1,
                case2,
                case3,
                case4,
                case5,
                case6,
                case7,
                case8,
                case9,
                case10,
                case11,
                case12,
                case13,
                case14,
                case15,
                case16,
            ]
        )

    def opt_list(self, cases: list[Optional[Case[T, V]]]) -> Opt[V]:
        """
        Evaluates the provided cases against the stored value and returns the result
        of the first matching case.

        The cases are evaluated in the order they are provided. The evaluation stops
        as soon as a matching case is found (short-circuiting).

        Args:
            cases: The list of cases

        Returns:
            An Opt containing the result (V) of the first matching case.
            Returns an empty Opt if no case matches the stored value.
        """
        for case_item in cases:
            if case_item is not None and case_item.matches(self.__value):
                return Opt(case_item.result())
        return Opt.empty()

    def of_list(self, cases: list[Optional[Case[T, V]]]) -> Optional[V]:
        """
        Evaluates the provided cases against the stored value and returns the result
        of the first matching case.

        The cases are evaluated in the order they are provided. The evaluation stops
        as soon as a matching case is found (short-circuiting).

        Args:
            cases: The list of cases

        Returns:
            An Optional containing the result (V) of the first matching case.
            Returns None if no case matches the stored value.
        """
        return self.opt_list(cases).get_actual()

    def of_list_exhaustive(self, cases: list[Optional[Case[T, V]]]) -> V:
        """
        Evaluates the provided cases against the stored value and returns the result
        of the first matching case. Raises MatchError if no case matches.

        Args:
            cases: The list of cases.

        Returns:
            The result (V) of the first matching case.

        Raises:
            MatchError: If no case matches the stored value.
        """
        return self.opt_list(cases).or_else_raise_from(
            lambda: ValueError(
                f"No case matched value: {self.__value}. Match was not exhaustive."
            )
        )


# --- Factory Functions ---


def case(
    matching: Union[T, Callable[[T], bool]],
    resulting: Union[V, Callable[[], V]],
) -> Case[T, V]:
    """
    Factory function to create a Case instance.

    Syntactic sugar for `Case(matching, resulting)`.

    Args:
        matching: The value, predicate function, or Predicate object to match against.
        resulting: The result value or a supplier function to generate the result.

    Returns:
        A new Case[T, V] instance.
    """
    return Case(matching, resulting)


def match(value: T) -> Match[T]:
    """
    Factory function to start a match expression for a non-optional value.

    Syntactic sugar for `Match(value)`.

    Example:
        result = match(5).of(
            case(1, "one"),
            case(5, "five"),
            default_case("other")
        ) # result will be "five"

    Args:
        value: The value to match against cases.

    Returns:
        A new Match[T] instance, ready to call `.of(...)` on.
    """
    return Match(value)


def match_opt(value: Optional[T]) -> Match[Optional[T]]:
    """
    Factory function to start a match expression specifically for an Optional value.

    This allows using predicates that work on Optional types, like `is_none`
    or `is_not_none`, directly in the cases.

    Syntactic sugar for `Match(value)` where value is Optional[T].

    Example:
        from jstreams.predicate import is_none, is_not_none

        opt_val: Optional[int] = None
        result = match_opt(opt_val).of(
            case(is_none, "It was None"),
            case(is_not_none, "It had a value")
        ) # result will be "It was None"

    Args:
        value: The Optional value to match against cases.

    Returns:
        A new Match[Optional[T]] instance, ready to call `.of(...)` on.
    """
    return Match(value)


def DefaultCase(resulting: Union[V, Callable[[], V]]) -> Case[T, V]:
    """
    Factory function to create a DefaultCase instance.

    This case will match any value if reached (i.e., if no preceding cases matched).
    It should typically be the last case provided to `.of()`.

    Args:
        resulting: The result value or a supplier function for the default case.

    Returns:
        A new DefaultCase[T, V] instance (returned as Case[T, V] for compatibility).
    """
    # Cast is safe here because DefaultCase is a subtype of Case[T, V] for any T
    return Case(lambda _: True, resulting)


def default_case(resulting: Union[V, Callable[[], V]]) -> Case[T, V]:
    """
    Factory function to create a DefaultCase instance.

    This case will match any value if reached (i.e., if no preceding cases matched).
    It should typically be the last case provided to `.of()`.

    Syntactic sugar for `DefaultCase(resulting)`.

    Args:
        resulting: The result value or a supplier function for the default case.

    Returns:
        A new DefaultCase[T, V] instance (returned as Case[T, V] for compatibility).
    """
    # Cast is safe here because DefaultCase is a subtype of Case[T, V] for any T
    return DefaultCase(resulting)
