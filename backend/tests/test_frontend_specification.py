from pathlib import Path


HTML = Path(__file__).parents[1] / "app" / "static" / "index.html"


def source() -> str:
    return HTML.read_text(encoding="utf-8")


def test_specification_uses_dedicated_persistent_state() -> None:
    html = source()
    assert "const SPECIFICATION_STORAGE_KEY='telcord-specification'" in html
    assert "localStorage.setItem(SPECIFICATION_STORAGE_KEY" in html
    assert "configuration:JSON.parse(JSON.stringify(config))" in html


def test_reset_does_not_clear_specification() -> None:
    html = source()
    reset = html[html.index("resetAll=function()") : html.index("const SPECIFICATION_STORAGE_KEY")]
    assert "specificationItems" not in reset
    assert "localStorage" not in reset


def test_duplicate_article_increases_quantity() -> None:
    html = source()
    assert "specificationDuplicateKey(item)===newItemKey" in html
    assert "duplicate.quantity+=1" in html


def test_specification_has_quantity_remove_copy_and_total() -> None:
    html = source()
    assert "changeSpecificationQuantity" in html
    assert "removeSpecificationItem" in html
    assert "copySpecification" in html
    assert "specificationTotalCents" in html
    assert ">Добавить в спецификацию</button>" in html


def test_quantity_supports_keyboard_editing_and_normalization() -> None:
    html = source()
    assert 'class="quantity-input" type="number" min="1" step="1"' in html
    assert "event.key==='Enter'" in html
    assert "commitSpecificationQuantity" in html
    assert "Math.trunc(Number(value))" in html
    assert "saveSpecificationItems();renderSpecification()" in html


def test_clipboard_has_http_fallback() -> None:
    html = source()
    assert "navigator.clipboard" in html
    assert "document.execCommand('copy')" in html
    assert "Не удалось скопировать" in html


def test_article_display_omits_brand_but_copy_keeps_brand() -> None:
    html = source()
    assert "function displayArticle(article)" in html
    assert ".replace(/^TELCORD\\s+/i,'')" in html
    assert "TELCORD ${displayArticle(lastResult.sku)} ${lastResult.name}" in html


def test_last_specification_item_can_be_repeated() -> None:
    html = source()
    assert "Повторить последний вариант" in html
    assert "function repeatLastSpecificationItem()" in html
    assert "last.configuration" in html
    assert "refreshOptions(true)" in html
