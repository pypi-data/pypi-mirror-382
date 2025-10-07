# mkdocs_vwidref/plugin.py
from __future__ import annotations
import re
import logging
from typing import Dict, Optional, Any, Tuple
from urllib.parse import quote

import yaml
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files, File
from mkdocs.structure.nav import Navigation

log = logging.getLogger("mkdocs.plugins.vwidref")

# Supported syntaxes (flags order flexible):
#   [[id:tm-gp]]
#   [[id:s:tm-gp]]
#   [[id:p:tm-gp]]
#   [[id:t:tm-gp]]
#   [[id:s:t:tm-gp]]
#   [[id:p:t:tm-gp]]
#   [[id:s:p:t:tm-gp]]
#   [[id:s:p:tm-gp]]
#   [[id:t:test-id#section-id]]          # NEW: explicit section fragment
# Optional custom label: [[id:s:t:tm-gp|Custom]]  (label only used when :t)
IDREF_PATTERN = re.compile(
    r"""\[\[
        id:
        (?:(?P<flags>(?:[spt]:)+))?         # zero or more flags 's:' 'p:' 't:'
        (?P<idfrag>[^|\]]+)                 # id or id#fragment (no '|' or ']]')
        (?:\|(?P<label>[^\]]+))?            # optional |label (used only if :t)
    \]\]""",
    re.VERBOSE,
)

# Skip fenced code blocks when rewriting
FENCE_PATTERN = re.compile(r"(^|\n)(?P<fence>```|~~~)[^\n]*\n.*?(\n\2\s*$)", re.DOTALL)

def _read_front_matter(abs_path: str) -> Optional[dict]:
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.startswith("---\n"):
            return None
        end = text.find("\n---", 4)
        if end == -1:
            return None
        block = text[4:end]
        data = yaml.safe_load(block) or {}
        return data if isinstance(data, dict) else None
    except Exception as e:
        log.debug("[vwidref] front-matter read failed for %s: %s", abs_path, e)
        return None

def _ensure_pretty_url(url: str) -> str:
    if url.endswith(".html"):
        url = url[:-5]
    if not url.endswith("/"):
        url += "/"
    return url

def _round_progress(value: Any) -> Optional[int]:
    try:
        v = float(str(value).strip())
    except Exception:
        return None
    v = max(0.0, min(100.0, v))
    choices = [0, 20, 40, 60, 80, 100]
    return min(choices, key=lambda c: abs(c - v))

# Progress bars WITHOUT angle brackets (angle brackets added only when multiple components shown)
PROGRESS_BARS = {
    0:   ":board-progtodo:",
    20:  ":board-prog20:",
    40:  ":board-prog70:",
    60:  ":board-prog60:",
    80:  ":board-prog80:",
    100: ":board-progdone:",
}

STATUS_ICONS = {
    "todo": ":board-statustodo:",
    "inprogress": ":board-statusinprogress:",
    "done": ":board-statusdone:",
}

class IdRefPlugin(BasePlugin):
    """
    [[id:foo]] -> link to the page whose front-matter has id: foo
    [[id:foo#frag]] -> same page, but anchor to #frag (explicit section)

    Link text rules (title appears ONLY when :t is present):
      No flags        -> id string
      s               -> status only (no parentheses)
      p               -> progress only (no angle brackets)
      t               -> title only
      s:t             -> (status) Title
      p:t             -> <progress> Title
      s:p:t           -> (status) <progress> Title
      s:p             -> (status) <progress>        # no title without :t
    """

    config_scheme = (
        ("id_field",       config_options.Type(str, default="id")),
        ("title_field",    config_options.Type(str, default="title")),
        ("status_field",   config_options.Type(str, default="status")),
        ("progress_field", config_options.Type(str, default="progress")),
        ("append_hash",    config_options.Type(bool, default=True)),
        ("lowercase_ids",  config_options.Type(bool, default=False)),
        ("debug",          config_options.Type(bool, default=False)),
    )

    def __init__(self):
        super().__init__()
        self._id_index: Dict[str, Dict[str, str]] = {}

    # ---------- Index build ----------

    def on_files(self, files: Files, config: MkDocsConfig, **kwargs):
        id_key = self.config["id_field"]
        title_key = self.config["title_field"]
        status_key = self.config["status_field"]
        progress_key = self.config["progress_field"]
        lower = self.config["lowercase_ids"]

        count = 0
        for f in files:
            if isinstance(f, File) and f.src_path.endswith((".md", ".markdown")):
                meta = _read_front_matter(f.abs_src_path)
                if not meta or id_key not in (meta or {}):
                    continue

                raw_id = str(meta.get(id_key) or "").strip()
                if not raw_id:
                    continue
                idx = raw_id.lower() if lower else raw_id

                title = str(meta.get(title_key) or "").strip()
                status = str(meta.get(status_key) or "").strip().lower() if status_key in meta else ""
                progress_val = meta.get(progress_key) if progress_key in meta else None
                progress_round = _round_progress(progress_val) if progress_val is not None else None

                self._id_index[idx] = {
                    "src_path": f.src_path,
                    "url": "",  # filled in on_nav
                    "title": title,
                    "status": status,
                    "progress_round": str(progress_round) if progress_round is not None else "",
                    "id": raw_id,  # original case preserved
                }
                count += 1

        log.info("[vwidref] collected %d ids from front-matter", count)
        return files

    def on_nav(self, nav: Navigation, config: MkDocsConfig, files: Files, **kwargs):
        by_src = {p.file.src_path: p for p in nav.pages}
        updated = 0
        for idx, rec in self._id_index.items():
            p = by_src.get(rec["src_path"])
            if not p:
                continue
            url = _ensure_pretty_url(p.url or "")
            url = "/" + url.lstrip("/")   # root-relative
            rec["url"] = url
            if not rec["title"]:
                rec["title"] = getattr(p, "title", "") or idx
            updated += 1
        log.info("[vwidref] attached URLs for %d ids", updated)
        return nav

    # ---------- Helpers ----------

    def _resolve(self, token_id: str) -> Optional[Dict[str, str]]:
        key = token_id.lower() if self.config["lowercase_ids"] else token_id
        return self._id_index.get(key)

    def _parse_flags(self, flags_text: Optional[str]) -> Tuple[bool, bool, bool, bool]:
        if not flags_text:
            return (False, False, False, False)
        tokens = [t for t in flags_text.split(":") if t]
        want_s = "s" in tokens
        want_p = "p" in tokens
        want_t = "t" in tokens
        return (True, want_s, want_p, want_t)

    def _split_id_and_fragment(self, idfrag: str) -> Tuple[str, Optional[str]]:
        # Accept 'base#fragment' (fragment may contain URL-safe chars; we'll encode)
        if "#" in idfrag:
            base, frag = idfrag.split("#", 1)
            base = base.strip()
            frag = frag.strip()
            return base, frag or None
        return idfrag.strip(), None

    # ---------- Rewriter ----------

    def _rewrite_block(self, text: str) -> str:
        def repl(m: re.Match) -> str:
            flags_text = m.group("flags")
            idfrag = m.group("idfrag")
            override_label = m.group("label")

            base_id, explicit_frag = self._split_id_and_fragment(idfrag)

            rec = self._resolve(base_id)
            if not rec or not rec.get("url"):
                log.warning("[vwidref] unresolved id '%s' in %r", base_id, m.group(0))
                return m.group(0)

            has_flags, want_s, want_p, want_t = self._parse_flags(flags_text)

            # Determine inclusion strictly by flags
            include_status = bool(want_s and STATUS_ICONS.get(rec.get("status", "").lower()))
            include_progress = bool(want_p and rec.get("progress_round"))
            include_title = bool(want_t)

            # Build title text (custom label used ONLY if include_title)
            title_text = ""
            if include_title:
                title_text = (override_label.strip() if override_label else (rec.get("title") or base_id)).strip()

            # Count components to decide wrappers
            components_count = (1 if include_status else 0) + (1 if include_progress else 0) + (1 if include_title else 0)

            # Status text: add parentheses only if multiple components shown
            status_text = ""
            if include_status:
                icon = STATUS_ICONS.get(rec.get("status", "").lower())
                if icon:
                    status_text = f"({icon})" if components_count > 1 else icon

            # Progress text: add angle brackets only if multiple components shown
            progress_text = ""
            if include_progress:
                try:
                    pr = int(rec.get("progress_round"))
                    bar = PROGRESS_BARS.get(pr, "")
                except (TypeError, ValueError):
                    bar = ""
                if bar:
                    progress_text = f"<{bar}>" if components_count > 1 else bar

            # If no flags at all -> plain id
            if not has_flags:
                link_text = rec.get("id") or base_id
            else:
                parts = [p for p in [status_text, progress_text, title_text] if p]
                if not parts:
                    parts = [rec.get("id") or base_id]
                link_text = " ".join(parts)

            url = rec["url"]
            if self.config["append_hash"]:
                if explicit_frag:
                    # Encode fragment but keep common anchor-safe characters
                    url = f"{url}#{quote(explicit_frag, safe='-._~!$&\\'()*+,;=:@/')}"
                else:
                    url = f"{url}#{quote(rec.get('id', base_id), safe='-._~')}"

            return f"[{link_text}]({url})"

        return IDREF_PATTERN.sub(repl, text)

    def on_page_markdown(self, markdown: str, page, config: MkDocsConfig, files: Files, **kwargs):
        if "[[id:" not in markdown:
            return markdown

        parts = []
        last = 0
        for m in FENCE_PATTERN.finditer(markdown):
            start, end = m.start(), m.end()
            parts.append(self._rewrite_block(markdown[last:start]))  # non-code
            parts.append(markdown[start:end])                        # keep code intact
            last = end
        parts.append(self._rewrite_block(markdown[last:]))

        new_md = "".join(parts)
        if self.config["debug"] and new_md != markdown:
            log.debug("[vwidref] rewrote links on page %s", getattr(page.file, "src_path", "?"))
        return new_md
