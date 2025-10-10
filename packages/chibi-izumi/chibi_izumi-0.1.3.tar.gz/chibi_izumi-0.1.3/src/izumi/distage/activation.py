"""
Activation system for choosing between alternative bindings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class AxisChoiceDef:
    """Base class for axis choices."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self) -> int:
        return hash((self.__class__, self.name))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name


class Axis(ABC):
    """Base class for defining activation axes."""

    @abstractmethod
    def __repr__(self) -> str:
        """Abstract method to ensure subclasses define representation."""
        pass


# Standard axes following distage convention
class StandardAxis:
    """Standard activation axes provided by distage."""

    class Mode(Axis):
        class Prod(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Prod")

        class Test(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Test")

        # These are instances, not class assignments
        _prod_instance = Prod()
        _test_instance = Test()

        # Class attributes for access
        Prod = _prod_instance  # type: ignore[misc,assignment]
        Test = _test_instance  # type: ignore[misc,assignment]

    class Repo(Axis):
        class Prod(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Prod")

        class Dummy(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Dummy")

        # These are instances, not class assignments
        _prod_instance = Prod()
        _dummy_instance = Dummy()

        # Class attributes for access
        Prod = _prod_instance  # type: ignore[misc,assignment]
        Dummy = _dummy_instance  # type: ignore[misc,assignment]

    class World(Axis):
        class Real(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Real")

        class Mock(AxisChoiceDef):
            def __init__(self) -> None:
                super().__init__("Mock")

        # These are instances, not class assignments
        _real_instance = Real()
        _mock_instance = Mock()

        # Class attributes for access
        Real = _real_instance  # type: ignore[misc,assignment]
        Mock = _mock_instance  # type: ignore[misc,assignment]


@dataclass(frozen=True)
class Activation:
    """An activation specifies choices for various axes."""

    choices: dict[type[Axis], AxisChoiceDef]

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        *args: tuple[type[Axis], AxisChoiceDef] | dict[type[Axis], AxisChoiceDef],
        **kwargs: AxisChoiceDef,
    ) -> None:
        if len(args) == 1 and isinstance(args[0], dict):
            # Support Activation(dict) constructor
            choices = args[0]
        else:
            # Support Activation(axis1=choice1, axis2=choice2)
            choices = {}
            # Handle positional args as tuples
            for arg in args:
                if isinstance(arg, tuple) and len(arg) == 2:
                    axis_type, choice = arg
                    choices[axis_type] = choice
            # Handle keyword args
            for key, value in kwargs.items():
                if hasattr(StandardAxis, key):
                    axis_type = getattr(StandardAxis, key)
                    choices[axis_type] = value

        # Use object.__setattr__ because this is a frozen dataclass
        object.__setattr__(self, "choices", choices)

    def get_choice(self, axis_type: type[Axis]) -> AxisChoiceDef | None:
        """Get the choice for a specific axis."""
        return self.choices.get(axis_type)

    def has_choice_for(self, axis_type: type[Axis]) -> bool:
        """Check if this activation has a choice for the given axis."""
        return axis_type in self.choices

    def is_compatible_with_tags(self, tags: set[AxisChoiceDef]) -> bool:
        """Check if this activation is compatible with the given tags."""
        if not tags:
            return True

        # For each tag in the binding, check if the activation matches
        for tag in tags:
            # Find if this tag matches any choice in the activation
            tag_matches = False
            for _axis_type, choice in self.choices.items():
                if choice == tag or str(choice) == str(tag):
                    tag_matches = True
                    break

            # If no matching choice found, the binding doesn't match this activation
            if not tag_matches:
                return False

        return True

    def _tag_belongs_to_axis(self, tag: AxisChoiceDef, axis_type: type[Axis]) -> bool:
        """Check if a tag belongs to the given axis type."""
        # This is a simplified check - in a real implementation, you'd have
        # a more sophisticated way to determine axis membership
        axis_name = axis_type.__name__
        return hasattr(StandardAxis, axis_name) and hasattr(
            getattr(StandardAxis, axis_name), tag.name
        )

    @staticmethod
    def empty() -> Activation:
        """Create an empty activation with no choices."""
        return Activation({})

    def __str__(self) -> str:
        if not self.choices:
            return "Activation()"

        choices_str = ", ".join(
            f"{axis.__name__}.{choice.name}" for axis, choice in self.choices.items()
        )
        return f"Activation({choices_str})"
