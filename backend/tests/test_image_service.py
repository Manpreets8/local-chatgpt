from app.services.image_service import ImageService


def test_build_prompt_leaves_plain_prompts_unchanged():
    service = ImageService()
    prompt = "a photo of a mountain lake at sunset"

    assert service._build_prompt(prompt) == prompt


def test_build_prompt_adds_style_boost_for_3d_keyword():
    service = ImageService()
    result = service._build_prompt("a 3D render of a robot")

    assert result.startswith("a 3D render of a robot")
    assert "CGI" in result
    assert "not photorealistic" in result


def test_build_prompt_adds_style_boost_for_pixar_keyword():
    service = ImageService()
    result = service._build_prompt("pixar style dragon")

    assert "glossy toy-like materials" in result


def test_build_prompt_adds_style_boost_for_cartoon_keyword():
    service = ImageService()
    result = service._build_prompt("a cartoon cat")

    assert "octane render" in result


def test_build_prompt_is_case_insensitive():
    service = ImageService()
    result = service._build_prompt("A PIXAR movie character")

    assert "studio lighting" in result
