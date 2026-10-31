from app.app import build_year_range, get_comparison_title


def test_build_year_range_keeps_end_after_start():
    assert build_year_range("2020", "2024") == (2020, 2024)
    assert build_year_range("2024", "2020") == (2020, 2024)
    assert build_year_range("Todos", "2026") == (None, 2026)


def test_get_comparison_title_when_municipio_is_selected():
    assert get_comparison_title("Campo Grande") == "Taxa de aprovação em Campo Grande"
    assert get_comparison_title("Todos") == "Comparação entre municípios"
