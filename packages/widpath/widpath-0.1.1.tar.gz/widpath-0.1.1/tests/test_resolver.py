import pytest
from pathlib import Path
from widpath import WidPathResolver

@pytest.fixture
def resolver():
    return WidPathResolver(size=2)

@pytest.fixture
def sample_wid():
    return "dc10ce02019b8ed9787869d0103e9c4b"  # 32 chars

def test_max_level(resolver, sample_wid):
    max_level = resolver.get_max_level(sample_wid)
    assert max_level == len(sample_wid)//2 - 1
    assert max_level == 15  # 32/2 = 16 parts, max_level = 15

def test_hierarchical_json_levels(resolver, sample_wid):
    # Level 0: dc.json
    p0 = resolver.get_hierarchical_json(sample_wid, 0)
    assert str(p0) == "dc.json"

    # Level 1: dc/10.json
    p1 = resolver.get_hierarchical_json(sample_wid, 1)
    assert str(p1) == "dc/10.json"

    # Level 2: dc/10/ce.json
    p2 = resolver.get_hierarchical_json(sample_wid, 2)
    assert str(p2) == "dc/10/ce.json"

    # Max level: full split + .json
    pmax = resolver.get_hierarchical_json(sample_wid, 100)  # 超过 max_level 会被限制
    assert str(pmax).endswith("4b.json")
    assert str(pmax).count("/") == resolver.get_max_level(sample_wid)

def test_file_path_returns_path(resolver, sample_wid, tmp_path):
    # 创建一个模拟的文件结构
    target = tmp_path / "dc" / "10" / "ce.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}")

    # 切换到临时目录运行测试
    cwd = Path.cwd()
    try:
        # 临时目录作为工作目录
        import os
        os.chdir(tmp_path)

        result = resolver.get_file_path(sample_wid)
        assert result.exists()
        assert result == Path("dc/10/ce.json")
    finally:
        os.chdir(cwd)
