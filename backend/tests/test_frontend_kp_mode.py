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
    email_builder = html[html.index("function specificationEmailHtml") : html.index("async function copySpecificationForEmail")]
    assert "specificationArticle(item)" in email_builder
    assert "item.productName" in email_builder


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


def test_kp_header_reserves_badge_space_and_has_fixed_height() -> None:
    html = source()
    assert "resultModeBadge.classList.toggle('is-visible',kpMode)" in html
    assert ".kp-mode-badge{visibility:hidden" in html
    assert ".kp-mode-badge.is-visible{visibility:visible}" in html
    assert ".result-header{height:86px;min-height:86px" in html
    assert "background:linear-gradient(to bottom,#fff6f5 0 86px,#fff 86px)" in html


def test_specification_header_keeps_kp_details_space_in_both_modes() -> None:
    html = source()
    assert 'class="specification-kp-details ${kpMode?\'is-visible\':\'\'}"' in html
    assert "В копирование для письма попадут клиентские цены" in html
    assert "Срок изготовления:" in html
    assert ".specification-head{height:96px;min-height:96px" in html
    assert ".specification-kp-details{display:grid;gap:1px;visibility:hidden" in html
    assert ".specification-kp-details.is-visible{visibility:visible}" in html


def test_card_header_dividers_are_full_width_without_moving_content() -> None:
    html = source()
    assert ".page-header{margin-left:-24px;margin-right:-24px;padding-left:24px;padding-right:24px;border-bottom:1px solid #e7ebee}" in html
    assert ".result-card{background:linear-gradient(to bottom,#fff 0 85px,#e7ebee 85px 86px,#fff 86px)}" in html
    assert ".result-card.kp-mode{background:linear-gradient(to bottom,#fff6f5 0 85px,#f1d9d7 85px 86px,#fff 86px)}" in html
    assert ".page-header{margin-left:-18px;margin-right:-18px;padding-left:18px;padding-right:18px}" in html


def test_workspace_columns_are_content_independent() -> None:
    html = source()
    assert ".workspace{grid-template-columns:minmax(0,2.2fr) minmax(340px,1fr);" in html
    assert ".workspace>.configurator,.workspace>.result-card,.workspace>.specification-card{min-width:0;width:100%}" in html
    assert "column-gap:24px" in html


def test_page_scrollbar_does_not_shift_centered_workspace() -> None:
    html = source()
    assert "html{overflow-y:scroll;scrollbar-gutter:stable}" in html


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
    assert "emailProductionLeadTime()" in email_builder
    assert "productionTermUpdatedAt" not in email_builder
    assert "productionTermFreshness" not in email_builder
    internal_builder = html[html.index("function specificationCopyText") : html.index("function configurationCopyText")]
    assert "productionTermFreshness" in internal_builder


def test_exchange_rate_control_uses_existing_backend_reference() -> None:
    html = source()
    assert html.index('id="exchangeRateButton"') < html.index('id="productionLoad"')
    assert "1$ = — руб." in html
    assert "data.exchange_rate_usd_rub" in html
    assert "fetch('/api/settings/exchange-rate',{method:'PUT'" in html
    assert "localStorage" not in html[html.index("function renderExchangeRate") : html.index("function toggleExchangeRatePopover")]


def test_exchange_rate_control_accepts_decimal_comma_and_formats_rubles() -> None:
    html = source()
    assert "replace(',','.')" in html
    assert "minimumFractionDigits:2,maximumFractionDigits:2" in html
    assert "1$ = ${formatted} руб." in html


def test_kp_email_copy_is_compact_and_separates_article_from_description() -> None:
    html = source()
    email_builder = html[html.index("function specificationEmailHtml") : html.index("function specificationEmailText")]
    assert "Коммерческое предложение" not in email_builder
    assert "display:inline-table" in email_builder
    assert "width:100%" not in email_builder
    assert "font-weight:600" in email_builder
    assert "specificationArticle(item)" in email_builder
    assert "item.productName" in email_builder
    assert '</span><br><span style="font-weight:400;line-height:1.35">' in email_builder
    assert '<div style="font-weight:600;line-height:1.35">' not in email_builder
    assert "${index+1}. ${esc(specificationArticle(item))}" not in email_builder


def test_kp_email_production_term_adds_two_calendar_days() -> None:
    html = source()
    assert "function emailProductionLeadTime" in html
    assert "value*7+2" in html
    assert "value+2" in html
    assert "pluralizeDays" in html
    email_builder = html[html.index("function specificationEmailHtml") : html.index("async function copySpecificationForEmail")]
    assert "emailProductionLeadTime()" in email_builder
