
"""Chicken item representing a restless chicken in the environment."""
from ...engine.Item import Item

class Chicken(Item):
    """
    Chicken item representing a restless chicken in the environment.
    """

    def __init__(self) -> None:
        """Initialize the Chicken item with name and description."""
        super().__init__(
            name="chicken",
            description="A live, clucking chicken. It seems restless and"
            + " might peck if you're not careful."
        )
