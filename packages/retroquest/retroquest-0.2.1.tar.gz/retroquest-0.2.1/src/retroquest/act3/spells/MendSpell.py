"""Mend spell for Act 3: finalizes mirror repairs when used on MirrorMounts."""
from ...engine.Spell import Spell
from ...engine.GameState import GameState


class MendSpell(Spell):
    """Mend spell used to finish repairs on Mirror Mounts in Act 3.

    Casting this spell on a MirrorMount will call its `mend` method so the
    mount can finalize and set the quest completion flag.
    """

    def __init__(self) -> None:
        """Initialize the Mend spell."""
        super().__init__(
            name="mend",
            description=(
                "A focused repair charm used to bind and finish delicate work; in "
                "Mount Ember it is used to set the final mirrors into resonance."
            ),
        )

    def cast_spell(self, _game_state: GameState) -> str:
        """Cast the mend spell without a specific target."""
        name = self.get_name()
        return (
            f"[success]You cast [spell_name]{name}[/spell_name] into the air. The "
            "magic shivers but finds nothing to mend nearby.[/success]"
        )

    def cast_on_item(self, game_state: GameState, target_item) -> str:
        """If target_item is a MirrorMount call its mend method, otherwise fall back.

        We import locally to avoid circular imports.
        """
        from ..items.MirrorMount import MirrorMount

        if isinstance(target_item, MirrorMount):
            # Delegate to the mount's mend method which sets story flags when ready
            return target_item.mend(game_state)

        # Fallback behavior: mimic the generic mend response
        name = self.get_name()
        iname = target_item.get_name()
        return (
            f"[info]You cast [spell_name]{name}[/spell_name] on "
            f"[item_name]{iname}[/item_name], but it doesn't appear to need mending.[/info]"
        )
