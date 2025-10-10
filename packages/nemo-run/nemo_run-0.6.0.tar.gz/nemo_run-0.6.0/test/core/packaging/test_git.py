# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import filecmp
import os
import shlex
import subprocess
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import invoke
import pytest

from nemo_run.core.packaging.git import GitArchivePackager
from test.conftest import MockContext


def mock_check_call(cmd, *args, **kwargs):
    cmd = " ".join(cmd)
    if "git archive" in cmd:
        return
    elif "pip install" in cmd:
        return
    else:
        raise subprocess.CalledProcessError(1, cmd)


@pytest.fixture
def temp_repo(tmpdir):
    repo_path = tmpdir.mkdir("repo")
    os.chdir(str(repo_path))
    subprocess.check_call(["git", "init", "--initial-branch=main"])
    # Create some files
    open("file1.txt", "w").write("Hello")
    open("file2.txt", "w").write("World")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Initial commit"])
    return repo_path


@pytest.fixture
def packager(temp_repo):
    return GitArchivePackager(basepath=str(temp_repo), subpath="", ref="HEAD")


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package(packager, temp_repo):
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(temp_repo, os.path.join(job_dir, "extracted_output"))
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_subpath(packager, temp_repo):
    temp_repo = Path(temp_repo)
    (temp_repo / "subdir").mkdir()
    open(temp_repo / "subdir" / "file3.txt", "w").write("Subdir file")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Add subdir"])

    packager = GitArchivePackager(basepath=str(temp_repo), subpath="subdir", ref="HEAD")
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "subdir"), os.path.join(job_dir, "extracted_output")
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_subpath_with_basepath(packager, temp_repo):
    temp_repo = Path(temp_repo)
    (temp_repo / "subdir").mkdir()
    (temp_repo / "subdir" / "subdir2").mkdir()
    open(temp_repo / "subdir" / "subdir2" / "file3.txt", "w").write("Subdir file")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Add subdir"])

    packager = GitArchivePackager(
        basepath=os.path.join(temp_repo, "subdir"), subpath="subdir/subdir2", ref="HEAD"
    )
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "subdir", "subdir2"),
            os.path.join(job_dir, "extracted_output"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_invalid_ref(packager, temp_repo):
    packager.ref = "invalid_ref"
    with pytest.raises(invoke.exceptions.UnexpectedExit):
        with tempfile.TemporaryDirectory() as job_dir:
            packager.package(Path(temp_repo), job_dir, "test_package")


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_nonexistent_basepath(packager, temp_repo):
    packager.basepath = str(Path(temp_repo) / "nonexistent_path")
    with pytest.raises(subprocess.CalledProcessError):
        with tempfile.TemporaryDirectory() as job_dir:
            packager.package(Path(temp_repo), job_dir, "test_package")


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_include_pattern(packager, temp_repo):
    temp_repo = Path(temp_repo)
    # Create extra files
    (temp_repo / "extra").mkdir()
    with open(temp_repo / "extra" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(temp_repo / "extra" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    packager = GitArchivePackager(ref="HEAD", include_pattern="extra")
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "extra"),
            os.path.join(job_dir, "extracted_output", "extra"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_include_pattern_and_subpath(packager, temp_repo):
    temp_repo = Path(temp_repo)
    # Create extra files
    (temp_repo / "extra").mkdir()
    with open(temp_repo / "extra" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(temp_repo / "extra" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    # Create extra files
    (temp_repo / "extra2").mkdir()
    with open(temp_repo / "extra2" / "extra2_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(temp_repo / "extra2" / "extra2_file2.txt", "w") as f:
        f.write("Extra file 2")
    subprocess.check_call(
        [f"cd {temp_repo} && git add extra2 && git commit -m 'Extra2 commit'"], shell=True
    )

    packager = GitArchivePackager(ref="HEAD", include_pattern="extra", subpath="extra2")
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "extra"),
            os.path.join(job_dir, "extracted_output", "extra"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files

        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "extra2"),
            os.path.join(job_dir, "extracted_output"),
            ignore=["extra"],
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_include_pattern_multiple_directories(packager, temp_repo):
    temp_repo = Path(temp_repo)
    # Create extra files
    (temp_repo / "extra").mkdir()
    with open(temp_repo / "extra" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(temp_repo / "extra" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    (temp_repo / "extra_1").mkdir()
    with open(temp_repo / "extra_1" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(temp_repo / "extra_1" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    packager = GitArchivePackager(ref="HEAD", include_pattern="extra extra_1")
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "extra"),
            os.path.join(job_dir, "extracted_output", "extra"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files

        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "extra_1"),
            os.path.join(job_dir, "extracted_output", "extra_1"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_include_pattern_rel_path(packager, temp_repo, tmpdir):
    temp_repo = Path(temp_repo)
    # Create extra files in a separate directory
    (tmpdir / "extra").mkdir()
    with open(tmpdir / "extra" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(tmpdir / "extra" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    packager = GitArchivePackager(
        include_pattern=str(tmpdir / "extra/*"), include_pattern_relative_path=str(tmpdir)
    )
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(tmpdir, "extra"),
            os.path.join(job_dir, "extracted_output", "extra"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_multi_include_pattern_rel_path(packager, temp_repo, tmpdir):
    temp_repo = Path(temp_repo)
    # Create extra files in a separate directory
    (tmpdir / "extra").mkdir()
    with open(tmpdir / "extra" / "extra_file1.txt", "w") as f:
        f.write("Extra file 1")
    with open(tmpdir / "extra" / "extra_file2.txt", "w") as f:
        f.write("Extra file 2")

    include_pattern = [str(tmpdir / "extra/extra_file1.txt"), str(tmpdir / "extra/extra_file2.txt")]
    relative_path = [str(tmpdir), str(tmpdir)]

    packager = GitArchivePackager(
        include_pattern=include_pattern, include_pattern_relative_path=relative_path
    )
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        cmp = filecmp.dircmp(
            os.path.join(tmpdir, "extra"),
            os.path.join(job_dir, "extracted_output", "extra"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_check_uncommitted_changes(packager, temp_repo):
    temp_repo = Path(temp_repo)
    open(temp_repo / "file1.txt", "w").write("Hello World")

    packager = GitArchivePackager(ref="HEAD", check_uncommitted_changes=True)
    with pytest.raises(RuntimeError, match="Your repo has uncommitted changes"):
        packager.package(temp_repo, str(temp_repo), "test_package")


def test_untracked_files_raises_exception(temp_repo):
    packager = GitArchivePackager(check_untracked_files=True)
    Path(temp_repo / "untracked.txt").touch()
    with open(temp_repo / "untracked.txt", "w") as f:
        f.write("Untracked file")
    with pytest.raises(AssertionError, match="Your repo has untracked files"):
        packager.package(temp_repo, str(temp_repo), "test")


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_with_include_submodules(packager, temp_repo):
    temp_repo = Path(temp_repo)
    # Create first submodule
    submodule_path = temp_repo / "submodule"
    submodule_path.mkdir()
    os.chdir(str(submodule_path))
    subprocess.check_call(["git", "init", "--initial-branch=main"])
    open("submodule_file.txt", "w").write("Submodule file")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Initial submodule commit"])

    # Create second submodule
    submodule2_path = temp_repo / "submodule2"
    submodule2_path.mkdir()
    os.chdir(str(submodule2_path))
    subprocess.check_call(["git", "init", "--initial-branch=main"])
    open("submodule2_file.txt", "w").write("Second submodule file")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Initial submodule2 commit"])

    os.chdir(str(temp_repo))
    subprocess.check_call(["git", "submodule", "add", str(submodule_path)])
    subprocess.check_call(["git", "submodule", "add", str(submodule2_path)])
    subprocess.check_call(["git", "commit", "-m", "Add submodules"])

    packager = GitArchivePackager(ref="HEAD", include_submodules=True)
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        # Check first submodule
        cmp = filecmp.dircmp(
            os.path.join(temp_repo, "submodule"),
            os.path.join(job_dir, "extracted_output", "submodule"),
        )
        assert cmp.left_list == cmp.right_list
        assert not cmp.diff_files

        # Check second submodule
        cmp2 = filecmp.dircmp(
            os.path.join(temp_repo, "submodule2"),
            os.path.join(job_dir, "extracted_output", "submodule2"),
        )
        assert cmp2.left_list == cmp2.right_list
        assert not cmp2.diff_files


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_package_without_include_submodules(packager, temp_repo):
    temp_repo = Path(temp_repo)
    # Create a submodule
    submodule_path = temp_repo / "submodule"
    submodule_path.mkdir()
    os.chdir(str(submodule_path))
    subprocess.check_call(["git", "init", "--initial-branch=main"])
    open("submodule_file.txt", "w").write("Submodule file")
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Initial submodule commit"])
    os.chdir(str(temp_repo))
    subprocess.check_call(["git", "submodule", "add", str(submodule_path)])
    subprocess.check_call(["git", "commit", "-m", "Add submodule"])

    packager = GitArchivePackager(ref="HEAD", include_submodules=False)
    with tempfile.TemporaryDirectory() as job_dir:
        output_file = packager.package(Path(temp_repo), job_dir, "test_package")
        assert os.path.exists(output_file)
        subprocess.check_call(shlex.split(f"mkdir -p {os.path.join(job_dir, 'extracted_output')}"))
        subprocess.check_call(
            shlex.split(
                f"tar -xvzf {output_file} -C {os.path.join(job_dir, 'extracted_output')} --ignore-zeros"
            ),
        )
        assert len(os.listdir(os.path.join(job_dir, "extracted_output", "submodule"))) == 0


def _make_uncompressed_tar_from_dir(src_dir: Path, tar_path: Path):
    # Create an uncompressed tar at tar_path from the contents of src_dir
    # with files at the root of the archive
    with tarfile.open(tar_path, mode="w") as tf:
        for entry in sorted(src_dir.iterdir()):
            tf.add(entry, arcname=entry.name)


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_concatenate_tar_files_non_linux_integration(tmp_path, monkeypatch):
    # Force non-Linux path (extract+repack)
    monkeypatch.setattr(os, "uname", lambda: SimpleNamespace(sysname="Darwin"))

    # Prepare two small tar fragments
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "fileA.txt").write_text("A")
    (dir_b / "fileB.txt").write_text("B")

    tar_a = tmp_path / "a.tar"
    tar_b = tmp_path / "b.tar"
    _make_uncompressed_tar_from_dir(dir_a, tar_a)
    _make_uncompressed_tar_from_dir(dir_b, tar_b)

    out_tar = tmp_path / "out.tar"
    packager = GitArchivePackager()
    ctx = MockContext()
    packager._concatenate_tar_files(ctx, str(out_tar), [str(tar_a), str(tar_b)])

    # Inputs removed
    assert not tar_a.exists() and not tar_b.exists()

    # Output contains both files at root
    assert out_tar.exists()
    with tarfile.open(out_tar, mode="r") as tf:
        names = sorted(m.name for m in tf.getmembers() if m.isfile())
    assert names == ["./fileA.txt", "./fileB.txt"]


def test_concatenate_tar_files_linux_emits_expected_commands(monkeypatch, tmp_path):
    # Simulate Linux branch; use a dummy Context that records commands instead of executing
    monkeypatch.setattr(os, "uname", lambda: SimpleNamespace(sysname="Linux"))

    class DummyContext:
        def __init__(self):
            self.commands: list[str] = []

        def run(self, cmd: str, **_kwargs):
            self.commands.append(cmd)

        # Support ctx.cd(...) context manager API
        def cd(self, _path: Path):
            class _CD:
                def __enter__(self_nonlocal):
                    return self

                def __exit__(self_nonlocal, exc_type, exc, tb):
                    return False

            return _CD()

    # Fake inputs (do not need to exist since we don't execute)
    tar1 = str(tmp_path / "one.tar")
    tar2 = str(tmp_path / "two.tar")
    tar3 = str(tmp_path / "three.tar")
    out_tar = str(tmp_path / "out.tar")

    ctx = DummyContext()
    packager = GitArchivePackager()
    packager._concatenate_tar_files(ctx, out_tar, [tar1, tar2, tar3])

    # Expected sequence: cp first -> tar Af rest -> rm all inputs
    assert len(ctx.commands) == 3
    assert ctx.commands[0] == f"cp {shlex.quote(tar1)} {shlex.quote(out_tar)}"
    assert (
        ctx.commands[1] == f"tar Af {shlex.quote(out_tar)} {shlex.quote(tar2)} {shlex.quote(tar3)}"
    )
    assert ctx.commands[2] == f"rm {shlex.quote(tar1)} {shlex.quote(tar2)} {shlex.quote(tar3)}"


@patch("nemo_run.core.packaging.git.Context", MockContext)
def test_include_pattern_length_mismatch_raises(packager, temp_repo):
    # Mismatch between include_pattern and include_pattern_relative_path should raise
    packager.include_pattern = ["extra"]
    packager.include_pattern_relative_path = ["/tmp", "/also/tmp"]
    with tempfile.TemporaryDirectory() as job_dir:
        with pytest.raises(ValueError, match="same length"):
            packager.package(Path(temp_repo), job_dir, "mismatch")
