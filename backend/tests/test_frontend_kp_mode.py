from pathlib import Path


INDEX_HTML = Path(__file__).parents[1] / "app" / "static" / "index.html"


def source() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


def test_kp_has_separate_persistent_markup_state() -> None:
    html = source()
    assert "telcord-kp-markup" in html
    assert "let kpMode=false" in html
    assert "function calculateClientCents" in html
    assert "baseCents*(100+percent)/100" in html


def test_specification_snapshot_keeps_kp_prices() -> None:
    html = source()
    assert "pricingMode:kpMode?'kp':'base'" in html
    assert "basePrice:" in html
    assert "markupPercent:" in html
    assert "clientPrice:" in html
    assert "function specificationItemUnitPrice" in html


def test_old_specification_items_are_migrated() -> None:
    html = source()
    assert "function migrateSpecificationItem" in html
    assert "item.basePrice??item.price" in html
    assert "pricingMode:item.pricingMode==='kp'?'kp':'base'" in html


def test_kp_duplicates_include_frozen_pricing() -> None:
    html = source()
    assert "function specificationDuplicateKey" in html
    assert "specificationDuplicateKey(item)===newItemKey" in html


def test_email_copy_has_html_and_plain_clipboard_formats() -> None:
    html = source()
    assert "Скопировать для письма" in html
    assert "function specificationEmailHtml" in html
    assert "function specificationEmailText" in html
    assert "new ClipboardItem" in html
    assert "'text/html'" in html
    assert "'text/plain'" in html


def test_client_email_builder_uses_effective_price_only() -> None:
    html = source()
    email_builder = html[html.index("function specificationEmailHtml") : html.index("async function copySpecificationForEmail")]
    assert "specificationItemUnitPrice" in email_builder
    assert "basePrice" not in email_builder
    assert "markupPercent" not in email_builder


def test_client_email_uses_full_telcord_article_and_product_name() -> None:
    html = source()
    assert "function specificationFullProductName" in html
    email_builder = html[html.index("function specificationEmailHtml") : html.index("async function copySpecificationForEmail")]
    assert "specificationFullProductName(item)" in email_builder


def test_switching_price_mode_requires_clear_confirmation() -> None:
    html = source()
    assert "Переключить режим?" in html
    assert "Текущая конфигурация и спецификация будут очищены" in html
    assert "Переключить и очистить" in html
    assert "function confirmKpModeSwitch" in html
    assert "function cancelKpModeSwitch" in html
    assert "specificationItems=[];saveSpecificationItems()" in html


def test_mixed_legacy_specification_is_cleared_safely() -> None:
    html = source()
    assert "new Set(items.map(item=>item.pricingMode))" in html
    assert "localStorage.removeItem(SPECIFICATION_STORAGE_KEY)" in html
    assert "pricingModes.size>1" in html


def test_specification_heading_follows_price_mode() -> None:
    html = source()
    assert "СПЕЦИФИКАЦИЯ · КП ДЛЯ КЛИЕНТА" in html
    assert "В копирование для письма попадут клиентские цены" in html


def test_every_price_mode_change_resets_current_calculation_and_specification() -> None:
    html = source()
    switch = html[html.index("function switchPriceMode") : html.index("function toggleKpMode")]
    assert "specificationItems=[]" in switch
    assert "saveSpecificationItems()" in switch
    assert "config={...EMPTY_CONFIG}" in switch
    assert "lastResult=null" in switch
    assert "emptyMode=true" in switch
    assert "markupPercent" not in switch


def test_kp_mode_has_explicit_client_visual_markers() -> None:
    html = source()
    assert "Ваша конфигурация · КП" in html
    assert "Режим КП для клиента" in html
    assert "КЛИЕНТСКАЯ ЦЕНА" in html
    assert "kp-mode" in html
    assert "КП скопировано · клиентские цены" in html


def test_manual_production_term_is_persisted_with_timestamp() -> None:
    html = source()
    assert "telcord-production-term" in html
    assert "telcord-production-term-updated-at" in html
    assert "let productionTerm=" in html
    assert "let productionTermUpdatedAt=" in html
    assert "function updateProductionTerm" in html
    assert "localStorage.setItem(PRODUCTION_TERM_STORAGE_KEY" in html
    assert "localStorage.setItem(PRODUCTION_TERM_UPDATED_AT_STORAGE_KEY" in html


def test_production_term_editor_lives_in_header_readiness_popover() -> None:
    html = source()
    assert "productionPopover.insertAdjacentHTML" in html
    assert "resultCard.insertBefore(productionTermEditor" not in html
    assert "event.target.closest('.production-popover')" in html


def test_price_mode_header_keeps_stable_geometry() -> None:
    html = source()
    assert "scrollbar-gutter:stable" in html
    assert ".result-header{min-height:" in html
    assert ".result-card.kp-mode:before" in html


def test_production_term_freshness_has_required_age_bands() -> None:
    html = source()
    assert "function productionTermFreshness" in html
    assert "Обновлено сегодня в" in html
    assert "Обновлено вчера" in html
    assert "дня назад" in html
    assert "Срок требует проверки" in html
    assert "freshness-warning" in html
    assert "freshness-caution" in html


def test_client_copy_excludes_production_timestamp_but_internal_copy_includes_freshness() -> None:
    html = source()
    email_builder = html[html.index("function specificationEmailHtml") : html.index("async function copySpecificationForEmail")]
    assert "productionLeadTime()" in email_builder
    assert "productionTermUpdatedAt" not in email_builder
    assert "productionTermFreshness" not in email_builder
    internal_builder = html[html.index("function specificationCopyText") : html.index("function configurationCopyText")]
    assert "productionTermFreshness" in internal_builder
