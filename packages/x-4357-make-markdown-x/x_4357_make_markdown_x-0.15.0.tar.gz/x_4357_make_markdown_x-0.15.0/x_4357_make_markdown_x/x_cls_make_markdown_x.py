"""Markdown document builder with optional PDF generation.

Features (redrabbit):
- Headers with hierarchical numbering and TOC entries
- Paragraphs, tables, images, lists
- Optional PDF export using wkhtmltopdf via pdfkit
"""

from __future__ import annotations

import importlib
from typing import Any, cast
import os as _os
import logging as _logging
import sys as _sys

_LOGGER = _logging.getLogger("x_make")


class BaseMake:
    @classmethod
    def get_env(cls, name: str, default: Any = None) -> Any:
        return _os.environ.get(name, default)

    @classmethod
    def get_env_bool(cls, name: str, default: bool = False) -> bool:
        v = _os.environ.get(name)
        if v is None:
            return default
        return str(v).lower() in ("1", "true", "yes")


def _info(*args: object) -> None:
    msg = " ".join(str(a) for a in args)
    try:
        _LOGGER.info("%s", msg)
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        try:
            _sys.stdout.write(msg + "\n")
        except Exception:
            pass


# red rabbit 2025_0902_0944


class x_cls_make_markdown_x(BaseMake):
    """A simple markdown builder with an optional PDF export step."""

    # Environment variable to override wkhtmltopdf path
    WKHTMLTOPDF_ENV_VAR: str = "X_WKHTMLTOPDF_PATH"
    # Default Windows install path (used if present and env var not set)
    DEFAULT_WKHTMLTOPDF_PATH: str = (
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    def __init__(
        self, wkhtmltopdf_path: str | None = None, ctx: object | None = None
    ) -> None:
        """Accept optional ctx for future orchestrator integration.

        Backwards compatible: callers that don't pass ctx behave as before.
        If ctx has a truthy `verbose` attribute this class will emit small
        informational messages to stdout to help debugging in orchestrated runs.
        """
        self._ctx = ctx
        self.elements: list[str] = []
        self.toc: list[str] = []
        self.section_counter: list[int] = []
        if wkhtmltopdf_path is None:
            env_path = self.get_env(self.WKHTMLTOPDF_ENV_VAR, None)
            wkhtmltopdf_path = env_path or (
                self.DEFAULT_WKHTMLTOPDF_PATH
                if _os.path.isfile(self.DEFAULT_WKHTMLTOPDF_PATH)
                else None
            )
        self.wkhtmltopdf_path: str | None = wkhtmltopdf_path

    def add_header(self, text: str, level: int = 1) -> None:
        """Add a header with hierarchical numbering and TOC update."""
        if level > 6:
            raise ValueError("Header level cannot exceed 6.")

        # Update section counter
        while len(self.section_counter) < level:
            self.section_counter.append(0)
        self.section_counter = self.section_counter[:level]
        self.section_counter[-1] += 1

        # Generate section index
        section_index = ".".join(map(str, self.section_counter))
        header_text = f"{section_index} {text}"

        # Add header to elements and TOC
        self.elements.append(f"{'#' * level} {header_text}\n")
        self.toc.append(
            f"{'  ' * (level - 1)}- [{header_text}]"
            f"(#{header_text.lower().replace(' ', '-').replace('.', '')})"
        )

    def add_paragraph(self, text: str) -> None:
        """Add a paragraph to the markdown document."""
        self.elements.append(f"{text}\n\n")

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Add a table to the markdown document."""
        header_row = " | ".join(headers)
        separator_row = " | ".join(["---"] * len(headers))
        data_rows = "\n".join([" | ".join(row) for row in rows])
        self.elements.append(f"{header_row}\n{separator_row}\n{data_rows}\n\n")

    def add_image(self, alt_text: str, url: str) -> None:
        """Add an image to the markdown document."""
        self.elements.append(f"![{alt_text}]({url})\n\n")

    def add_list(self, items: list[str], ordered: bool = False) -> None:
        """Add a list to the markdown document."""
        if ordered:
            self.elements.extend(
                [f"{i + 1}. {item}" for i, item in enumerate(items)]
            )
        else:
            self.elements.extend([f"- {item}" for item in items])
        self.elements.append("\n")

    def add_toc(self) -> None:
        """Add a table of contents (TOC) to the top of the document."""
        self.elements = ["\n".join(self.toc) + "\n\n", *self.elements]

    def to_html(self, text: str) -> str:
        """Convert markdown text to HTML using python-markdown; minimal fallback on failure."""
        try:
            _markdown: Any = importlib.import_module("markdown")
            val = _markdown.markdown(text or "")
            return cast(str, val)
        except Exception:
            # Minimal fallback: return plain text wrapped in <pre> to preserve content
            return f"<pre>{(text or '').replace('<','&lt;').replace('>','&gt;')}</pre>"

    def to_pdf(self, html_str: str, out_path: str) -> None:
        """Render HTML to PDF using pdfkit + wkhtmltopdf; fail fast if unavailable."""
        if not self.wkhtmltopdf_path or not _os.path.isfile(
            self.wkhtmltopdf_path
        ):
            raise RuntimeError(
                f"wkhtmltopdf not found (set {self.WKHTMLTOPDF_ENV_VAR} or install at default path)"
            )
        try:
            _pdfkit: Any = importlib.import_module("pdfkit")
        except Exception as e:
            raise RuntimeError("pdfkit is required for PDF export") from e
        _os.makedirs(
            _os.path.dirname(_os.path.abspath(out_path)) or ".", exist_ok=True
        )
        cfg = _pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        _pdfkit.from_string(html_str, out_path, configuration=cfg)

    def generate(self, output_file: str = "example.md") -> str:
        """Generate markdown and save it to a file; optionally render a PDF."""
        markdown_content = "".join(self.elements)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        if getattr(self._ctx, "verbose", False):
            _info(f"[markdown] wrote markdown to {output_file}")

        # Convert to PDF if wkhtmltopdf_path is configured
        if self.wkhtmltopdf_path:
            html_content = self.to_html(markdown_content)
            pdf_file = output_file.replace(".md", ".pdf")
            self.to_pdf(html_content, pdf_file)

        return markdown_content


if __name__ == "__main__":
    # Rich example: Alice in Wonderland sampler -> Markdown + PDF beside this file
    base_dir = _os.path.dirname(_os.path.abspath(__file__))
    out_dir = _os.path.join(base_dir, "out_docs")
    _os.makedirs(out_dir, exist_ok=True)

    class _Ctx:
        verbose = True

    maker = x_cls_make_markdown_x(ctx=_Ctx())

    maker.add_header("Alice's Adventures in Wonderland", 1)
    maker.add_paragraph(
        "Public-domain sampler inspired by Lewis Carroll (1865)."
    )

    maker.add_header("Down the Rabbit-Hole", 2)
    maker.add_paragraph(
        "Alice was beginning to get very tired of sitting by her sister on the bank, "
        "and of having nothing to do: once or twice she had peeped into the book her "
        "sister was reading, but it had no pictures or conversations in it..."
    )

    maker.add_list(
        [
            "Sees a White Rabbit with a pocket watch",
            "Follows it down the rabbit-hole",
            "Finds a hall with many locked doors",
        ],
        ordered=True,
    )

    maker.add_header("A Curious Bottle", 2)
    maker.add_paragraph(
        'On a little table she found a bottle, on it was a paper label, with the words "DRINK ME" beautifully printed on it.'
    )

    maker.add_table(
        ["Item", "Effect"],
        [
            ["Cake (EAT ME)", "Grows tall"],
            ["Fan", "Shrinks"],
            ["Key", "Opens small door"],
        ],
    )

    maker.add_image(
        "Alice meets the White Rabbit (Tenniel, public domain)",
        "https://upload.wikimedia.org/wikipedia/commons/6/6f/Alice_par_John_Tenniel_02.png",
    )

    maker.add_header("Conclusion", 2)
    maker.add_paragraph(
        "This document demonstrates headers with numbering and TOC, lists, tables, and images."
    )

    # Insert TOC at the top after all headers were added
    maker.add_toc()

    output_md = _os.path.join(out_dir, "alice_in_wonderland.md")
    maker.generate(output_file=output_md)

    if not maker.wkhtmltopdf_path:
        _info(
            f"[markdown] PDF not generated: set {x_cls_make_markdown_x.WKHTMLTOPDF_ENV_VAR} to wkhtmltopdf.exe"
        )
