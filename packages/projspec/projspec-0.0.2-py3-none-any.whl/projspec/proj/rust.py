from projspec.proj import ProjectSpec, PythonLibrary


class Rust(ProjectSpec):
    """A directory, which can build a binary executable or library with Cargo."""

    spec_doc = "https://doc.rust-lang.org/cargo/reference/manifest.html"

    def match(self) -> bool:
        return "Cargo.toml" in self.proj.basenames

    # this builds a (static) library or an executable, or both.
    def parse(self):
        pass


class RustPython(Rust, PythonLibrary):
    """A rust project designed for importing with python, perhaps with mixed rust/python code trees.

    This version assumes the build tool is ``maturin``, which may not be the only possibility.
    """

    spec_doc = "https://www.maturin.rs/config.html"

    def match(self) -> bool:
        # The second condition here is not necessarily required, it is enough to
        # have a python package directory with the same name as the rust library.
        return (
            Rust.match(self)
            and "maturin" in self.proj.pyproject.get("tool", {})
            and self.proj.pyproject.get("build-backend", "") == "maturin"
        )

    # this builds a python-installable wheel in addition to rust artifacts.
