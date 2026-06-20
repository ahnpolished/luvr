import pytest

from src.web.instagram import InstagramPublicContext, normalize_instagram_handle


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("@Tae.Ahn", "tae.ahn"),
        (" tae_ahn ", "tae_ahn"),
        ("https://www.instagram.com/taeahn/", "taeahn"),
        ("https://instagram.com/taeahn?igsh=abc", "taeahn"),
    ],
)
def test_normalize_instagram_handle_accepts_handles_and_profile_urls(
    value: str,
    expected: str,
) -> None:
    assert normalize_instagram_handle(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not a handle",
        "https://example.com/taeahn",
        "https://instagram.com/p/abc123",
        "https://instagram.com/reel/abc123",
    ],
)
def test_normalize_instagram_handle_rejects_invalid_or_non_profile_inputs(value: str) -> None:
    with pytest.raises(ValueError):
        normalize_instagram_handle(value)


def test_public_context_is_bounded_and_onboarding_safe() -> None:
    context = InstagramPublicContext(
        handle="@TaeAhn",
        bio="x" * 400,
        recent_public_hint="y" * 400,
    ).to_onboarding_context()

    assert context["instagram_handle"] == "taeahn"
    assert len(context["instagram_bio"]) == 280
    assert len(context["instagram_recent_public_hint"]) == 280
