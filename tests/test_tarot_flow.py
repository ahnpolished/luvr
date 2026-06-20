from src.tarot import THREE_CARD_TAROT_FLOW


def test_three_card_tarot_flow_has_deterministic_slots() -> None:
    assert THREE_CARD_TAROT_FLOW.key == "three_card_relationship"
    assert [slot.key for slot in THREE_CARD_TAROT_FLOW.slots] == [
        "situation",
        "tension",
        "next_move",
    ]
    assert [slot.title for slot in THREE_CARD_TAROT_FLOW.slots] == [
        "Situation",
        "Tension",
        "Next move",
    ]


def test_three_card_tarot_flow_stays_grounded_and_v0_1_sized() -> None:
    assert len(THREE_CARD_TAROT_FLOW.slots) == 3
    assert "fate" in THREE_CARD_TAROT_FLOW.completion_cta
    assert "next step" in THREE_CARD_TAROT_FLOW.completion_cta
    assert "situation" in THREE_CARD_TAROT_FLOW.intro
    assert "tension" in THREE_CARD_TAROT_FLOW.intro
    assert "next move" in THREE_CARD_TAROT_FLOW.intro
