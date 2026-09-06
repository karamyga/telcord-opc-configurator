from pathlib import Path


INDEX_HTML = Path(__file__).parents[1] / "app" / "static" / "index.html"


def test_frontend_has_one_empty_initial_configuration() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert "const EMPTY_CONFIG=Object.freeze(" in source
    assert "let config={...EMPTY_CONFIG}" in source
    assert "corrugation:null,lead_a:null,lead_b:null,execution:'standard'" in source
    assert "fiber_type:'OM3'" not in source
    assert "Object.assign(initial" not in source


def test_frontend_does_not_start_competing_options_request() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert "loadProductionSettings();refreshOptions();" not in source
    assert source.rstrip().endswith("refreshOptions(false);\n</script></body></html>")


def test_reset_uses_the_same_empty_configuration() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert "resetAll=function(){emptyMode=true;config={...EMPTY_CONFIG}" in source


def test_dependent_options_are_hidden_until_fiber_is_selected() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert "if(config.fiber_type===null)return dependentPlaceholderGroup" in source
    assert "dependentPlaceholderGroup('ОБОЛОЧКА','—')" in source
    assert "dependentPlaceholderGroup('ЦВЕТ','—')" in source
    assert ".dependent-option-placeholder" in source


def test_holder_is_hidden_and_reset_for_simplex() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert "function constructionIsDuplex()" in source
    assert "holderAllowed=constructionIsDuplex()&&['LC','SC'].includes(connector)" in source
    assert "if(!constructionIsDuplex()){config.holder_a=false;config.holder_b=false}" in source
