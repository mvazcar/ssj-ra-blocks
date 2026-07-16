import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_repository_is_runnable_but_not_packaged_as_an_api():
    configuration = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    namespace = (ROOT / "src" / "rbc_rank_blocks" / "__init__.py").read_text(
        encoding="utf-8"
    )
    block_namespace = (
        ROOT / "src" / "rbc_rank_blocks" / "blocks" / "__init__.py"
    ).read_text(encoding="utf-8")

    assert (ROOT / "run_models.py").is_file()
    assert (ROOT / "requirements.txt").is_file()
    assert (ROOT / "requirements-dev.txt").is_file()
    assert "public domain" in (ROOT / "UNLICENSE").read_text(encoding="utf-8")
    assert not (ROOT / "pyproject.toml").exists()
    assert "[pytest]" in configuration and "pythonpath = src" in configuration
    assert "pip install -e" not in readme
    assert "python -m rbc_rank_blocks" not in readme
    assert "from .models import" not in namespace
    assert "__all__" not in namespace and "__all__" not in block_namespace
    assert not (ROOT / "src" / "rbc_rank_blocks" / "__main__.py").exists()


def test_generated_figure_tree_contains_only_the_published_artifacts():
    irf_names = {path.name for path in (ROOT / "figures" / "irfs").iterdir()}
    assert irf_names == {
        "README.md",
        "rbc.csv",
        "rbc_output_response.svg",
        "rank_calvo_sticky_prices.csv",
        "rank_rotemberg_sticky_prices.csv",
        "rank_price_output_comparison.svg",
        "rank_union_sticky_wages.csv",
        "rank_firm_sticky_wages.csv",
        "rank_wage_output_comparison.svg",
    }
    assert not list((ROOT / "figures").glob("*.png"))


def test_all_local_markdown_links_resolve():
    markdown_files = [
        ROOT / "README.md",
        ROOT / "SOURCES.md",
        *(ROOT / "docs").glob("*.md"),
        ROOT / "figures" / "dags" / "README.md",
        ROOT / "figures" / "irfs" / "README.md",
    ]
    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        link_pattern = r"(?<!\\)!?\[[^\]\\\r\n]*\]\(([^)\r\n]+)\)"
        for target in re.findall(link_pattern, text):
            if target.startswith(("http://", "https://", "#")):
                continue
            relative = target.split("#", 1)[0]
            assert (markdown.parent / relative).resolve().exists(), (
                f"Broken local link in {markdown.relative_to(ROOT)}: {target}"
            )
