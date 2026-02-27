#!/usr/bin/env python3
"""Generate resume2.tex from resume.yaml."""

import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
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
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def tex_url_display(url: str) -> str:
    """Return a short display version of a URL (strip https://www.)."""
    display = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return display.rstrip("/")


def build_header(data: dict) -> str:
    parts = []
    parts.append(r"\begin{center}")
    parts.append(
        rf"  {{\Huge\scshape\color{{darktext}} {escape_latex(data['name'])}}} \\[6pt]"
    )
    parts.append(r"  \small")

    contact_items = []
    if data.get("phone"):
        phone = str(data["phone"])
        # Format as +XX XXX XXXX XXXX if it starts with country code
        formatted = f"+{phone}" if not phone.startswith("+") else phone
        contact_items.append(rf"\faIcon{{phone}} \, {formatted}")
    if data.get("email"):
        email = data["email"]
        contact_items.append(
            rf"\faIcon{{envelope}} \, \href{{mailto:{email}}}{{{escape_latex(email)}}}"
        )
    if data.get("linkedin"):
        url = data["linkedin"]
        display = tex_url_display(url)
        contact_items.append(
            rf"\faIcon{{linkedin}} \, \href{{{url}}}{{{escape_latex(display)}}}"
        )
    if data.get("github"):
        url = data["github"]
        display = tex_url_display(url)
        contact_items.append(
            rf"\faIcon{{github}} \, \href{{{url}}}{{{escape_latex(display)}}}"
        )
    if data.get("location"):
        contact_items.append(
            rf"\faIcon{{map-marker-alt}} \, {escape_latex(data['location'])}"
        )

    parts.append("  " + r" \quad".join(contact_items))
    parts.append(r"\end{center}")
    return "\n".join(parts)


def build_summary(data: dict) -> str:
    if not data.get("summary"):
        return ""
    lines = [
        r"\section{Summary}",
        r"  \small\color{darktext}{",
        f"    {escape_latex(data['summary'])}",
        r"  }",
    ]
    return "\n".join(lines)


def build_experience(data: dict) -> str:
    jobs = data.get("employment", [])
    if not jobs:
        return ""

    lines = [r"\section{Experience}", r"  \resumeSubHeadingListStart", ""]

    for job in jobs:
        title = escape_latex(job["title"])
        company = escape_latex(job["name"])
        start = str(job["start"])
        end = str(job["end"]).capitalize()
        location = escape_latex(job.get("location", ""))
        lines.append(rf"    \resumeSubheading")
        lines.append(rf"      {{{title}}}{{{start} -- {end}}}")
        lines.append(rf"      {{{company}}}{{{location}}}")

        bullets = job.get("job_description", [])
        if bullets:
            lines.append(r"      \resumeItemListStart")
            for bullet in bullets:
                lines.append(rf"        \resumeItem{{{escape_latex(bullet)}}}")
            lines.append(r"      \resumeItemListEnd")
        lines.append("")

    lines.append(r"  \resumeSubHeadingListEnd")
    return "\n".join(lines)


def build_education(data: dict) -> str:
    schools = data.get("education", [])
    if not schools:
        return ""

    lines = [r"\section{Education}", r"  \resumeSubHeadingListStart", ""]

    for school in schools:
        degree = escape_latex(school["degree"])
        faculty = school.get("faculty", "")
        if faculty:
            degree = f"{degree} in {escape_latex(faculty)}"
        name = escape_latex(school["name"])
        start = str(school["start"])
        end = str(school["end"])
        location = escape_latex(school.get("location", ""))
        lines.append(r"    \resumeEduSubheading")
        lines.append(rf"      {{{degree}}}{{{start} -- {end}}}")
        lines.append(rf"      {{{name}}}{{{location}}}")

        # Thesis info
        thesis = school.get("thesis")
        if thesis:
            lines.append(r"      \resumeItemListStart")
            thesis_line = f"Thesis: \\emph{{{escape_latex(thesis['title'])}}}"
            if thesis.get("advisor"):
                thesis_line += f" — Advisor: {escape_latex(thesis['advisor'])}"
            lines.append(rf"        \resumeItem{{{thesis_line}}}")
            lines.append(r"      \resumeItemListEnd")
        lines.append("")

    lines.append(r"  \resumeSubHeadingListEnd")
    return "\n".join(lines)


def build_projects(data: dict) -> str:
    projects = data.get("projects", [])
    if not projects:
        return ""

    lines = [r"\section{Projects}", r"  \resumeSubHeadingListStart", ""]

    for proj in projects:
        name = escape_latex(proj["name"])
        lines.append(r"    \resumeProjectHeading")
        lines.append(rf"      {{\textbf{{{name}}}}}{{}}")

        has_details = proj.get("description") or proj.get("supervisors")
        if has_details:
            lines.append(r"      \resumeItemListStart")
            if proj.get("description"):
                lines.append(
                    rf"        \resumeItem{{{escape_latex(proj['description'])}}}"
                )
            if proj.get("supervisors"):
                lines.append(
                    rf"        \resumeItem{{Supervisors: {escape_latex(proj['supervisors'])}}}"
                )
            lines.append(r"      \resumeItemListEnd")
        lines.append("")

    lines.append(r"  \resumeSubHeadingListEnd")
    return "\n".join(lines)


def build_publications(data: dict) -> str:
    pubs = data.get("publications", [])
    if not pubs:
        return ""

    lines = [r"\section{Publications}", r"  \begin{itemize}[leftmargin=0.2in]", ""]

    for pub in pubs:
        title = escape_latex(pub["title"])
        authors = escape_latex(pub.get("authors", ""))
        journal = escape_latex(pub.get("journal", ""))
        year = str(pub.get("year", ""))
        url = pub.get("url", "")
        # All on one line: authors. "Title", Conference, Year
        if url:
            title_part = f"\\href{{{url}}}{{\\textbf{{{title}}}}}"
        else:
            title_part = f"\\textbf{{{title}}}"
        pub_line = f"{authors}. {title_part}"
        if journal:
            pub_line += f", \\emph{{{journal}}}"
        if year:
            pub_line += f", {year}"
        lines.append(rf"    \resumePubItem{{{pub_line}}}")
        lines.append("")

    lines.append(r"  \end{itemize}")
    return "\n".join(lines)


def build_skills(data: dict) -> str:
    tags = data.get("tags", [])
    if not tags:
        return ""

    # Group tags by category
    categories = {
        "Languages": [],
        "ML \\& AI": [],
        "Data \\& Databases": [],
        "Tools \\& Platforms": [],
    }

    lang_keywords = {"python", "c++", "c#", "sql", "bash"}
    ml_keywords = {"tensorflow", "pytorch", "opencv", "diffusion", "genai", "scipy", "numpy", "pandas", "mlflow"}
    data_keywords = {"postgresql"}
    tool_keywords = {"git", "docker", "slurm", "linux", "latex"}

    for tag in tags:
        low = tag.lower()
        if low in lang_keywords:
            categories["Languages"].append(tag)
        elif low in ml_keywords:
            categories["ML \\& AI"].append(tag)
        elif low in data_keywords:
            categories["Data \\& Databases"].append(tag)
        elif low in tool_keywords:
            categories["Tools \\& Platforms"].append(tag)
        else:
            # Default to tools
            categories["Tools \\& Platforms"].append(tag)

    lines = [
        r"\section{Technical Skills}",
        r"  \begin{itemize}[leftmargin=0.15in, label={}]",
        r"    \small{\item{",
    ]

    skill_lines = []
    for category, items in categories.items():
        if items:
            joined = ", ".join(escape_latex(t) for t in items)
            skill_lines.append(rf"      \textbf{{{category}:}}{{ {joined}}}")

    lines.append(" \\\\\n".join(skill_lines))
    lines.append(r"    }}")
    lines.append(r"  \end{itemize}")
    return "\n".join(lines)


PREAMBLE = r"""%-------------------------
% Resume in LaTeX — auto-generated from resume.yaml
%-------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{xcolor}

% ---------- PAGE STYLE ----------
\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% ---------- MARGINS ----------
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-0.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% ---------- COLORS ----------
\definecolor{accent}{HTML}{2b6cb0}
\definecolor{darktext}{HTML}{1a1a1a}
\definecolor{lighttext}{HTML}{4a4a4a}

% ---------- SECTION FORMATTING ----------
\titleformat{\section}{
  \vspace{-6pt}\scshape\raggedright\large\bfseries\color{accent}
}{}{0em}{}[\color{accent}\titlerule\vspace{-5pt}]

% ---------- CUSTOM COMMANDS ----------
\newcommand{\resumeItem}[1]{
  \item\small\color{darktext}{#1\vspace{-2pt}}
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\color{darktext}#1} & \small\color{lighttext}#2 \\
      \textit{\small\color{lighttext}#3} & \textit{\small\color{lighttext}#4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small\textbf{\color{darktext}#1} & \small\color{lighttext}#2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.2in]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\newcommand{\resumePubItem}[1]{
  \vspace{-2pt}\item\small\color{darktext}{#1\vspace{-2pt}}
}

\newcommand{\resumeEduSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\color{darktext}#1} & \small\color{lighttext}#2 \\
      \textit{\small\color{lighttext}#3} & \textit{\small\color{lighttext}#4} \\
    \end{tabular*}\vspace{-2pt}
}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
"""


## ---------------------------------------------------------------------------
## Markdown generation
## ---------------------------------------------------------------------------


def md_header(data: dict) -> str:
    lines = [f"# {data['name']}", ""]
    contact = []
    if data.get("email"):
        contact.append(f"[{data['email']}](mailto:{data['email']})")
    if data.get("phone"):
        phone = str(data["phone"])
        formatted = f"+{phone}" if not phone.startswith("+") else phone
        contact.append(formatted)
    if data.get("linkedin"):
        display = data["linkedin"].replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        contact.append(f"[{display}]({data['linkedin']})")
    if data.get("github"):
        display = data["github"].replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        contact.append(f"[{display}]({data['github']})")
    if data.get("location"):
        contact.append(data["location"])
    if contact:
        lines.append(" | ".join(contact))
        lines.append("")
    return "\n".join(lines)


def md_summary(data: dict) -> str:
    if not data.get("summary"):
        return ""
    return f"## Summary\n\n{data['summary']}\n"


def md_experience(data: dict) -> str:
    jobs = data.get("employment", [])
    if not jobs:
        return ""
    lines = ["## Experience", ""]
    for job in jobs:
        start = str(job["start"])
        end = str(job["end"]).capitalize()
        lines.append(f"### {job['title']} — {job['name']} ({start} – {end})")
        lines.append("")
        for bullet in job.get("job_description", []):
            lines.append(f"- {bullet}")
        lines.append("")
    return "\n".join(lines)


def md_education(data: dict) -> str:
    schools = data.get("education", [])
    if not schools:
        return ""
    lines = ["## Education", ""]
    for school in schools:
        degree = school["degree"]
        faculty = school.get("faculty", "")
        if faculty:
            degree = f"{degree} in {faculty}"
        start = str(school["start"])
        end = str(school["end"])
        lines.append(f"### {degree} — {school['name']} ({start} – {end})")
        thesis = school.get("thesis")
        if thesis:
            lines.append("")
            thesis_line = f"Thesis: *{thesis['title']}*"
            if thesis.get("advisor"):
                thesis_line += f" — Advisor: {thesis['advisor']}"
            lines.append(thesis_line)
        lines.append("")
    return "\n".join(lines)


def md_publications(data: dict) -> str:
    pubs = data.get("publications", [])
    if not pubs:
        return ""
    lines = ["## Publications", ""]
    for pub in pubs:
        title = pub["title"]
        authors = pub.get("authors", "")
        journal = pub.get("journal", "")
        year = str(pub.get("year", ""))
        url = pub.get("url", "")
        if url:
            title_part = f"[**{title}**]({url})"
        else:
            title_part = f"**{title}**"
        entry = f"- {authors}. {title_part}"
        if journal:
            entry += f", *{journal}*"
        if year:
            entry += f", {year}"
        lines.append(entry)
    lines.append("")
    return "\n".join(lines)


def md_projects(data: dict) -> str:
    projects = data.get("projects", [])
    if not projects:
        return ""
    lines = ["## Projects", ""]
    for proj in projects:
        lines.append(f"### {proj['name']}")
        lines.append("")
        if proj.get("description"):
            lines.append(proj["description"])
            lines.append("")
        if proj.get("supervisors"):
            lines.append(f"*Supervisors: {proj['supervisors']}*")
            lines.append("")
    return "\n".join(lines)


def md_skills(data: dict) -> str:
    tags = data.get("tags", [])
    if not tags:
        return ""
    return f"## Technical Skills\n\n{', '.join(tags)}\n"


def generate_markdown(data: dict) -> str:
    """Generate a complete Markdown resume from the YAML data."""
    sections = [
        md_header(data),
        md_summary(data),
        md_experience(data),
        md_education(data),
        md_publications(data),
        md_projects(data),
        md_skills(data),
    ]
    return "\n---\n\n".join(s for s in sections if s)


## ---------------------------------------------------------------------------
## Main
## ---------------------------------------------------------------------------


def main():
    yaml_path = SCRIPT_DIR / "resume.yaml"
    tex_path = SCRIPT_DIR / "resume.tex"
    md_path = SCRIPT_DIR / "README.md"

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # --- LaTeX output ---
    sections = [
        PREAMBLE,
        r"\begin{document}",
        "",
        "% ---------- HEADER ----------",
        build_header(data),
        "",
        "% ---------- SUMMARY ----------",
        build_summary(data),
        "",
        "% ---------- EXPERIENCE ----------",
        build_experience(data),
        "",
        "% ---------- EDUCATION ----------",
        build_education(data),
        "",
        "% ---------- PUBLICATIONS ----------",
        build_publications(data),
        "",
        "% ---------- PROJECTS ----------",
        build_projects(data),
        "",
        "% ---------- SKILLS ----------",
        build_skills(data),
        "",
        "",
        r"\end{document}",
        "",
    ]

    tex_content = "\n".join(sections)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"Generated {tex_path}")

    # --- Markdown / README output ---
    md_content = generate_markdown(data)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Generated {md_path}")


if __name__ == "__main__":
    main()
