from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import textwrap
import unicodedata


TRANSCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_DIR = TRANSCRIPT_DIR / "texsrc"
AUTHOR = "Olasunkanmi Arowolo"
DEFAULT_DATE = "2026"
LECTURE_TRANSCRIPT = "Lecture Transcript"
PODCAST_SCRIPT = "Podcast Script"


@dataclass(frozen=True)
class FileSpec:
    source_name: str
    output_name: str
    title: str
    document_kind: str
    check_in_url: str = ""
    check_out_url: str = ""


FILE_SPECS = {
    spec.source_name: spec
    for spec in (
        FileSpec(
            source_name="Introduction to Editing and Graphics in Journalism - MCM 202 Lecture 1.txt",
            output_name="L1_Introduction_to_Editing_and_Graphics_in_Journalism.tex",
            title="MCM 202 - Lecture 1: Introduction to Editing and Graphics in Journalism",
            document_kind=LECTURE_TRANSCRIPT,
            check_in_url="https://forms.gle/cqQTx8whi6vPu1SK7",
            check_out_url="https://forms.gle/tgfQykahdnR4x21y8",
        ),
        FileSpec(
            source_name="How News Becomes News- Workflow & Editing Explained - MCM 202 - Lecture 2.txt",
            output_name="L2_How_News_Becomes_News_Workflow_and_Editing_Explained.tex",
            title="MCM 202 - Lecture 2: How News Becomes News - Workflow and Editing Explained",
            document_kind=LECTURE_TRANSCRIPT,
        ),
        FileSpec(
            source_name="𝐐&𝐀 - LIVE SESSION - How News is Edited Before You See It-MCM 202 Lecture 3.txt",
            output_name="L3_QA_How_News_is_Edited_Before_You_See_It.tex",
            title="MCM 202 - Lecture 3 Q&A: How News Is Edited Before You See It",
            document_kind="Live Session Q&A Transcript",
        ),
        FileSpec(
            source_name="Fact-Checking in Journalism- Why Editors Must Verify Everything- MCM 202 Lecture 4.txt",
            output_name="L4_Fact_Checking_in_Journalism_Why_Editors_Must_Verify_Everything.tex",
            title="MCM 202 - Lecture 4: Fact-Checking in Journalism - Why Editors Must Verify Everything",
            document_kind=LECTURE_TRANSCRIPT,
        ),
        FileSpec(
            source_name="LIVE SESSION - Foundations of Editing and Graphics.txt",
            output_name="Live_Session_Foundations_of_Editing_and_Graphics.tex",
            title="MCM 202 - Live Session: Foundations of Editing and Graphics",
            document_kind="Live Session Transcript",
        ),
        FileSpec(
            source_name="MCM202_Podcast_E01_Script_v1.txt",
            output_name="MCM202_Podcast_E01_Script_v1.tex",
            title="MCM 202 Audio Series - Episode 1 Script",
            document_kind=PODCAST_SCRIPT,
        ),
        FileSpec(
            source_name="MCM202_Podcast_E02_Script_v1.txt",
            output_name="MCM202_Podcast_E02_Script_v1.tex",
            title="MCM 202 Audio Series - Episode 2 Script",
            document_kind=PODCAST_SCRIPT,
        ),
        FileSpec(
            source_name="MCM202_Podcast_E04_Script_v1.txt",
            output_name="MCM202_Podcast_E04_Script_v1.tex",
            title="MCM 202 Audio Series - Episode 4 Script",
            document_kind=PODCAST_SCRIPT,
        ),
        FileSpec(
            source_name="Podcast_Repurpose_Plan_MCM_202.txt",
            output_name="Podcast_Repurpose_Plan_MCM_202.tex",
            title="MCM 202 Transcript Repurposing Plan",
            document_kind="Planning Document",
        ),
    )
}


UNICODE_REPLACEMENTS = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "--",
    "\u2014": "---",
    "\u2026": "...",
    "\u00a0": " ",
}


def normalize_text(text: str) -> str:
    for old, new in UNICODE_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def escape_tex(text: str) -> str:
    text = normalize_text(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def slugify(text: str) -> str:
    text = normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "content"


def parse_video_url(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("http://") or stripped.startswith("https://"):
            return stripped
        return ""
    return ""


def parse_display_title(spec: FileSpec, lines: list[str]) -> str:
    for line in lines[:10]:
        stripped = line.strip()
        if stripped.startswith("Title:"):
            return stripped.split(":", 1)[1].strip() or spec.title
    first_nonempty = next((line.strip() for line in lines if line.strip()), "")
    if first_nonempty and not first_nonempty.startswith("http") and first_nonempty != "Transcript:":
        return first_nonempty
    return spec.title


def extract_document_body(raw_text: str) -> tuple[str, str]:
    transcript_marker = "\nTranscript:\n"
    if transcript_marker in raw_text:
        _, body = raw_text.split(transcript_marker, 1)
        return "Transcript Text", body.strip()
    return "Document Text", raw_text.strip()


def wrap_verbatim_text(text: str, width: int = 100) -> str:
    wrapped_lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(
            textwrap.wrap(
                line,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return "\n".join(wrapped_lines)


def build_content_tex(spec: FileSpec, source_path: Path, raw_text: str, display_title: str, video_url: str) -> str:
    content_label, body_text = extract_document_body(raw_text)
    normalized_body = normalize_text(body_text)
    wrapped_body = wrap_verbatim_text(normalized_body)
    metadata_lines = [
        r"\subsection*{Source Metadata}",
        rf"\noindent\textbf{{Source File:}} \path{{{normalize_text(source_path.name)}}}\par",
        rf"\noindent\textbf{{Document Type:}} {escape_tex(spec.document_kind)}\par",
        rf"\noindent\textbf{{Display Title:}} {escape_tex(display_title)}\par",
    ]
    if video_url:
        metadata_lines.append(rf"\noindent\textbf{{Source URL:}} \url{{{video_url}}}\par")
    else:
        metadata_lines.append(r"\noindent\textbf{Source URL:} Not provided\par")

    metadata_lines.extend(
        [
            "",
            rf"\subsection*{{{content_label}}}",
            r"{\small",
            r"\begin{Verbatim}",
            wrapped_body,
            r"\end{Verbatim}",
            r"}",
            "",
        ]
    )
    return "\n".join(metadata_lines)


def build_wrapper_tex(spec: FileSpec, display_title: str, video_url: str, content_rel_path: str) -> str:
    safe_title = escape_tex(display_title)
    safe_author = escape_tex(AUTHOR)
    safe_date = escape_tex(DEFAULT_DATE)
    content_path = content_rel_path.replace("\\", "/")
    return "\n".join(
        [
            "% Auto-generated wrapper. Edit the source .txt file or generator instead of this file.",
            rf"\newcommand{{\LessonTitle}}{{{safe_title}}}",
            rf"\newcommand{{\LessonAuthor}}{{{safe_author}}}",
            rf"\newcommand{{\LessonDate}}{{{safe_date}}}",
            rf"\newcommand{{\LessonVideoURL}}{{{video_url}}}",
            rf"\newcommand{{\CheckInURL}}{{{spec.check_in_url}}}",
            rf"\newcommand{{\CheckOutURL}}{{{spec.check_out_url}}}",
            rf"\newcommand{{\TranscriptFile}}{{{content_path}}}",
            r"\input{transcript_template.tex}",
            "",
        ]
    )


def generate_file(spec: FileSpec) -> None:
    source_path = TRANSCRIPT_DIR / spec.source_name
    raw_text = source_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()
    video_url = parse_video_url(lines)
    display_title = parse_display_title(spec, lines)
    content_slug = slugify(spec.output_name.replace(".tex", ""))
    content_name = f"{content_slug}-content.tex"
    content_path = CONTENT_DIR / content_name
    wrapper_path = TRANSCRIPT_DIR / spec.output_name

    content_text = build_content_tex(spec, source_path, raw_text, display_title, video_url)
    wrapper_text = build_wrapper_tex(spec, display_title, video_url, f"texsrc/{content_name}")

    content_path.write_text(content_text, encoding="utf-8")
    wrapper_path.write_text(wrapper_text, encoding="utf-8")


def main() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in FILE_SPECS.values():
        generate_file(spec)
    print(f"Generated {len(FILE_SPECS)} wrapper files and matching content files in {TRANSCRIPT_DIR}")


if __name__ == "__main__":
    main()