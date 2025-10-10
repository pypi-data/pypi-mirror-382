from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from httpx import Client

from bump_deps_index import Options, main, run
from bump_deps_index._loaders import get_loaders
from bump_deps_index._spec import PkgType

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def test_run_args(capsys: pytest.CaptureFixture[str], mocker: MockerFixture) -> None:
    mapping = {"A": "A>=1", "B": "B"}
    update_spec = mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )

    run(
        Options(
            index_url="https://pypi.org/simple",
            npm_registry="N",
            pkgs=[" A ", "B", "C"],
            filenames=None,
            pre_release="no",
        ),
    )

    out, err = capsys.readouterr()
    assert err == "failed C with KeyError('C')\n"
    assert set(out.splitlines()) == {"A -> A>=1", "B"}

    found: set[tuple[str, PkgType]] = set()
    for called in update_spec.call_args_list:
        assert len(called.args) == 6
        assert isinstance(called.args[0], Client)
        assert called.args[1] == "https://pypi.org/simple"
        assert called.args[2] == "N"
        found.add((called.args[3], called.args[4]))
        assert called.args[5] is False
        assert not called.kwargs
    assert found == {("C", PkgType.PYTHON), ("B", PkgType.PYTHON), ("A", PkgType.PYTHON)}


def test_run_pyproject_toml(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {"A": "A>=1", "B==2": "B==1", "C": "C>=1", "E": "E>=3", "F": "F>=4"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / "pyproject.toml"
    toml = """
    [build-system]
    requires = ["A"]
    [project]
    dependencies = [ "B==2"]
    optional-dependencies.test = [ "C" ]
    optional-dependencies.docs = [ "D"]
    [dependency-groups]
    first = ["E"]
    second = ["F", {include-group = "first"}]
    """
    dest.write_text(dedent(toml).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert err == "failed D with KeyError('D')\n"
    assert set(out.splitlines()) == {"C -> C>=1", "F -> F>=4", "A -> A>=1", "E -> E>=3", "B==2 -> B==1"}

    toml = """
    [build-system]
    requires = ["A>=1"]
    [project]
    dependencies = [ "B==1"]
    optional-dependencies.test = [ "C>=1" ]
    optional-dependencies.docs = [ "D"]
    [dependency-groups]
    first = ["E>=3"]
    second = ["F>=4", {include-group = "first"}]
    """
    assert dest.read_text() == dedent(toml).lstrip()


def test_tox_toml(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {"A": "A>=1"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / "tox.toml"
    toml = """
    requires = ["A"]
    """
    dest.write_text(dedent(toml).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {"A -> A>=1"}

    toml = """
    requires = ["A>=1"]
    """
    assert dest.read_text() == dedent(toml).lstrip()


def test_run_pyproject_toml_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    dest = tmp_path / "tox.ini"
    dest.write_text("")
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert not set(out.splitlines())
    assert not dest.read_text()


def test_run_tox_ini(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {"A": "A>=1", "B==2": "B==1", "C": "C>=3"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / "tox.ini"
    tox_ini = """
    [tox]
    requires =
        C
    [testenv]
    deps =
        A
    [testenv:ok]
    deps =
        B==2
    [magic]
    deps = NO
    """
    dest.write_text(dedent(tox_ini).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {"A -> A>=1", "B==2 -> B==1", "C -> C>=3"}

    tox_ini = """
    [tox]
    requires =
        C>=3
    [testenv]
    deps =
        A>=1
    [testenv:ok]
    deps =
        B==1
    [magic]
    deps = NO
    """
    assert dest.read_text() == dedent(tox_ini).lstrip()


def test_tox_ini_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    dest = tmp_path / "tox.ini"
    dest.write_text("")
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert not set(out.splitlines())
    assert not dest.read_text()


def test_run_setup_cfg(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {"A": "A>=1", "B": "B==1", "C": "C>=3"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / "setup.cfg"
    setup_cfg = """
    [options]
    install_requires =
        A
    [options.extras_require]
    testing =
        B
    type =
        C
    """
    dest.write_text(dedent(setup_cfg).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {"B -> B==1", "A -> A>=1", "C -> C>=3"}

    setup_cfg = """
    [options]
    install_requires =
        A>=1
    [options.extras_require]
    testing =
        B==1
    type =
        C>=3
    """
    assert dest.read_text() == dedent(setup_cfg).lstrip()


def test_run_setup_cfg_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    dest = tmp_path / "setup.cfg"
    dest.write_text("")
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert not set(out.splitlines())
    assert not dest.read_text()


def test_run_pre_commit(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {
        "flake8-bugbear==22.7.1": "flake8-bugbear==22.7.2",
        "black==22.6.0": "black==22.6",
        "prettier@2.7.0": "prettier@2.8",
    }
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / ".pre-commit-config.yaml"
    setup_cfg = """
    repos:
      - repo: https://github.com/asottile/blacken-docs
        hooks:
          - id: blacken-docs
            additional_dependencies:
            - black==22.6.0
            - prettier@2.7.0
      - repo: https://github.com/PyCQA/flake8
        hooks:
          - id: flake8
            additional_dependencies:
            - flake8-bugbear==22.7.1
    """
    dest.write_text(dedent(setup_cfg).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {
        "black==22.6.0 -> black==22.6",
        "flake8-bugbear==22.7.1 -> flake8-bugbear==22.7.2",
        "prettier@2.7.0 -> prettier@2.8",
    }

    setup_cfg = """
    repos:
      - repo: https://github.com/asottile/blacken-docs
        hooks:
          - id: blacken-docs
            additional_dependencies:
            - black==22.6
            - prettier@2.8
      - repo: https://github.com/PyCQA/flake8
        hooks:
          - id: flake8
            additional_dependencies:
            - flake8-bugbear==22.7.2
    """
    assert dest.read_text() == dedent(setup_cfg).lstrip()


def test_run_pre_commit_empty(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    dest = tmp_path / ".pre-commit-config.yaml"
    dest.write_text("")
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert not set(out.splitlines())
    assert not dest.read_text()


def test_run_args_empty(capsys: pytest.CaptureFixture[str], mocker: MockerFixture) -> None:
    mocker.patch("bump_deps_index._run.update_spec", side_effect=ValueError)
    run(Options(index_url="https://pypi.org/simple", pkgs=[], filenames=[], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert not out


def test_run_requirements_txt(capsys: pytest.CaptureFixture[str], mocker: MockerFixture, tmp_path: Path) -> None:
    mapping = {"A": "A>=1", "B==1": "B==2"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    dest = tmp_path / "requirements.txt"
    req_txt = """
    A
    B==1
    """
    dest.write_text(dedent(req_txt).lstrip())
    run(Options(index_url="https://pypi.org/simple", npm_registry="", pkgs=[], filenames=[dest], pre_release="no"))

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {"B==1 -> B==2", "A -> A>=1"}

    req_txt = """
    A>=1
    B==2
    """
    assert dest.read_text() == dedent(req_txt).lstrip()


@pytest.mark.parametrize(
    "filename",
    [
        "requirements",
        "requirements.test",
        "requirements-test",
    ],
)
def test_run_requirements_txt_in(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
) -> None:
    get_loaders.cache_clear()

    mapping = {"A": "A>=1", "B==1": "B==2"}
    mocker.patch(
        "bump_deps_index._run.update_spec",
        side_effect=lambda _, __, ___, spec, ____, _____: mapping[spec],
    )
    (tmp_path / f"{filename}.txt").write_text("C")
    dest = tmp_path / f"{filename}.in"
    req_txt = """
    A
    B==1

    # bad
    """
    dest.write_text(dedent(req_txt).lstrip())
    monkeypatch.chdir(tmp_path)

    main(["--index-url", "https://pypi.org/simple", "--pre-release", "no"])

    out, err = capsys.readouterr()
    assert not err
    assert set(out.splitlines()) == {"B==1 -> B==2", "A -> A>=1"}

    req_txt = """
    A>=1
    B==2

    # bad
    """
    assert dest.read_text() == dedent(req_txt).lstrip()
