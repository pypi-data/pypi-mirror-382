"""Hidden Library room: secret archive rewarding residential discovery."""

from ...engine.Room import Room
from ..characters.SpectralLibrarian import SpectralLibrarian
from ..items.AncientChronicle import AncientChronicle
from ..items.ProtectiveEnchantments import ProtectiveEnchantments

class HiddenLibrary(Room):
    """Secret subterranean archive providing lore and defensive preparation.

    Narrative Role:
        Revealed only after searching the residential quarter; delivers mid‑act
        exposition and grants defensive progression via protective enchantments.

    Key Mechanics:
        - Access gating performed externally; room remains statically defined.

    Story Flags:
        - Reads none directly; availability implies discovery flag set earlier.

    Contents:
        - Items: ``AncientChronicle``, ``ProtectiveEnchantments``.
        - NPC: ``SpectralLibrarian`` (future spell pedagogy hook).

    Design Notes:
        Minimal surface keeps spotlight on discovery moment; expandable with
        research or conditional dialogue systems later.
    """

    def __init__(self) -> None:
        """Initialize hidden library with lore items and secret passage exit."""
        super().__init__(
            name="Hidden Library",
            description=(
                "Discovered beneath Greendale through a secret passage, this ancient library holds "
                "countless volumes of magical lore. Glowing crystals provide soft illumination and "
                "the air hums with residual energy. Protective enchantments shimmer around the "
                "most valuable texts. This repository of knowledge may unlock mysteries of your "
                "destiny."
            ),
            items=[AncientChronicle(), ProtectiveEnchantments()],
            characters=[SpectralLibrarian()],
            exits={"secret_passage": "ResidentialQuarter"}
        )
