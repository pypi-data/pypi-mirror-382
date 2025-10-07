from prompt_toolkit import HTML
from scipy import io
import os, zipfile, time, uuid, werkzeug, queue, html, ast, re, threading, textwrap, json, pandas as pd
from PyPDF2.errors import EmptyFileError
import io
from io import BytesIO
from PyPDF2 import PdfReader
from markupsafe  import Markup
from urllib.parse import quote 
from .auth import register_user, authenticate, login_required, admin_required, superadmin_required           
from flask import Blueprint, Response, request, send_file, session, render_template, render_template_string, redirect, url_for, flash, jsonify, send_from_directory, get_flashed_messages, stream_with_context

from syntaxmatrix.themes import DEFAULT_THEMES
from syntaxmatrix import db
from syntaxmatrix.utils import * 
from syntaxmatrix.vector_db import add_pdf_chunk
from syntaxmatrix.file_processor import *  
from syntaxmatrix.vectorizer import embed_text
from syntaxmatrix import llm_store as _llms   
from syntaxmatrix.plottings import datatable_box
from syntaxmatrix.history_store import SQLHistoryStore, PersistentHistoryStore
from syntaxmatrix.kernel_manager import SyntaxMatrixKernelManager, execute_code_in_kernel
from syntaxmatrix.vector_db import * 
from syntaxmatrix.settings.string_navbar import string_navbar_items
from syntaxmatrix.settings.model_map import PROVIDERS_MODELS, MODEL_DESCRIPTIONS, PURPOSE_TAGS, EMBEDDING_MODELS
from .project_root import detect_project_root
from . import profiles as _prof
from . import generate_page as _genpage
from . import profiles as _prof
from . import auth as _auth
from syntaxmatrix import profiles as _prof
from syntaxmatrix.gpt_models_latest import set_args, extract_output_text as _out
from datetime import datetime
import contextlib

try:
    from pygments import highlight as _hl
    from pygments.lexers import PythonLexer as _PyLexer
    from pygments.formatters import HtmlFormatter as _HtmlFmt
    _HAVE_PYGMENTS = True
except Exception:
    _HAVE_PYGMENTS = False

from flask_login import current_user
from flask import g

# app = Flask(__name__)

_CLIENT_DIR = detect_project_root()
_stream_q = queue.Queue() 
_stream_cancelled = {}
_last_result_html = {}  # { session_id: html_doc }

# single, reused formatter: inline styles, padding, rounded corners, scroll
_FMT = _HtmlFmt(
    noclasses=True,
    style="monokai",
    linenos=False,
    wrapcode=True,                                # <pre><code>…</code></pre>
    cssstyles="margin:0;",                        # wrapper <div> style
    prestyles=(
        "background:#1e1e1e;"
        "color:#ddd;"                             # base; tokens still colourize
        "padding:14px 16px;"
        "border-radius:8px;"
        "overflow:auto;"                          # scroll if too wide
        "max-width:100%;"
        "box-sizing:border-box;"
        "font-size:13.5px; line-height:1.45;"
    ),
)

def _pygmentize(code: str) -> str:
    if not _HAVE_PYGMENTS:
        import html as _html
        esc = _html.escape(code or "").replace("</", "<\\/")
        return f"<pre style='background:#1e1e1e;color:#ddd;padding:14px 16px;border-radius:8px;overflow:auto;max-width:100%;box-sizing:border-box;'>{esc}</pre>"
    return _hl(code or "", _PyLexer(), _FMT)

def _render_code_block(title: str, code: str) -> str:
    return (
        f"<h2 style='margin-top:24px;'>{title}</h2>"
        "<details open style='margin:8px 0;'>"
        "<summary style='cursor:pointer;'>Show/Hide code</summary>"
        f"{_pygmentize(code)}"
        "</details>"
    )

def get_contrast_color(hex_color: str) -> str:
    """
    Returns a contrasting color (#000000 or #ffffff) based on the brightness of hex_color.
    """
    hex_color = hex_color.strip().lstrip('#')
    if len(hex_color) == 3:
        r = int(hex_color[0]*2, 16)
        g = int(hex_color[1]*2, 16)
        b = int(hex_color[2]*2, 16)
    elif len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    else:
        return '#000000'
    brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return '#ffffff' if brightness < 0.5 else '#000000'

def render_chat_history(smx):
    plottings_html = smx.get_plottings()
    messages = session.get("chat_history", [])
    chat_html = ""
    if not messages and not plottings_html:
        chat_html += f"""
        <div id="deepseek-header" style="text-align:center; margin-top:10px; margin-bottom:5px;">
          <h2>{smx.bot_icon}{smx.project_name}</h2>
        </div>
        """
    elif plottings_html:
        {f'''
            <div id="system-output-container">       
                {plottings_html}
            </div>           
        ''' if plottings_html.strip() else ""}
            
    for role, message in messages:
        is_user = (str(role).lower() == "user")
        klass = "user" if is_user else "bot"
        timestamp = ""
        if smx.ui_mode == "card":
            timestamp = f"""<span style="float: right; font-size: 0.8em; color: {smx.theme['text_color']};">{time.strftime('%H:%M')}</span>"""
        chat_icon = smx.user_icon if is_user else smx.bot_icon
        if role.lower() == "user":
          chat_html += f"""
            <div class='chat-message {klass}' style='display: flex; flex-direction: column; align-items: flex-start;'>
              <span style='align-self: flex-end;'>{chat_icon}{timestamp}</span>
              <p>{message}</p>
            </div>
          """
        else:   
          chat_html += f"""
            <div class='chat-message {klass}'>
              <span>{chat_icon}{timestamp}</span>
              <p>{message}</p>
            </div>
          """
    return chat_html

# def _favicon_link_tag():
#     """
#     Returns a robust <link rel="icon"> for the current smx.favicon setting.
#     Accepts:
#       - a full <link ...> tag (returned as-is),
#       - an <img ... src="..."> tag (converts to <link>),
#       - a URL or /path (uses directly),
#       - an emoji or anything else (falls back to /favicon.ico).
#     """
    # icon = smx.get_favicon() or "/static/icons/favicon.ico"
    # s = str(icon).strip()

    # # If developer supplied a full <link>, use it unchanged.
    # if s.lower().startswith("<link"):
    #     return s

    # # If they supplied an <img>, extract src and convert to <link>.
    # if s.lower().startswith("<img"):
    #     m = re.search(r'src=[\'"]([^\'"]+)[\'"]', s, re.I)
    #     href = m.group(1) if m else "/favicon.ico"
    #     if not (href.startswith(("http://", "https://", "/"))):
    #         href = "/favicon.ico"
    #     return f'<link rel="icon" href="{href}">'

    # # If it looks like a URL or absolute path, use it. Otherwise, fall back.
    # href = s if s.startswith(("http://", "https://", "/")) else "/favicon.ico"
    # return f'<link rel="icon" href="{href}">'

def setup_routes(smx):
    # Prevent duplicate route registration.
    if "home" in smx.app.view_functions:
        return
    
    from syntaxmatrix.session import ensure_session_cookie
    smx.app.before_request(ensure_session_cookie)

    DATA_FOLDER = os.path.join(_CLIENT_DIR, "uploads", "data")
    os.makedirs(DATA_FOLDER, exist_ok=True)

    MEDIA_FOLDER = os.path.join(_CLIENT_DIR, "uploads", "media")
    if not os.path.exists(MEDIA_FOLDER):
      os.makedirs(MEDIA_FOLDER)

    def _evict_profile_caches_by_name(prof_name: str) -> None:
            """
            Clear any in-memory profile cache on `smx` that points to the deleted profile.
            Future-proof: it scans all attributes and clears any dict whose 'name' matches.
            """
            if not prof_name:
                return
            try:
                for attr in dir(smx):
                    # be generous: match anything that mentions 'profile' in its name
                    if "profile" not in attr.lower():
                        continue
                    val = getattr(smx, attr, None)
                    if isinstance(val, dict) and val.get("name") == prof_name:
                        setattr(smx, attr, {})  # drop just this one; others untouched
            except Exception:
                # never let cache eviction break the request path
                pass
            
    @smx.app.after_request
    def _set_session_cookie(resp):
        new_sid = getattr(g, "_smx_new_sid", None)
        if new_sid:                   # created in ensure_session_cookie()
            resp.set_cookie(
                "smx_session",
                new_sid,
                max_age=60 * 60 * 24, # 24 h
                secure=True,          # served via HTTPS on Cloud Run
                httponly=True,
                samesite="Lax",
            )
        return resp
    

    def head_html():
        # Determine a contrasting mobile text color based on the sidebar background.
        mobile_text_color = smx.theme["nav_text"]
        if smx.theme.get("sidebar_background", "").lower() in ["#eeeeee", "#ffffff"]:
            mobile_text_color = smx.theme.get("text_color", "#333")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

          {smx.favicon}
          <title>{smx.page}</title>
          <style>
            body {{
              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
              margin: 0 20px;
              padding: 0;
              background: {smx.theme["background"]};
              color: {smx.theme["text_color"]};
            }}
            /* Responsive typography using clamp */
            html {{
              font-size: clamp(12px, 1.7vw, 18px);
            }}
            /* Desktop Navbar */
            nav {{
              display: flex;
              justify-content: space-between;
              align-items: center;
              background: {smx.theme["nav_background"]};
              padding: 10px 20px;
              position: fixed;
              top: 0;
              left: 0;
              right: 0;
              z-index: 1000;
            }}
            .nav-left {{
              display: flex;
              align-items: center;
            }}
            .nav-left .logo {{
              font-size: clamp(1.3rem, 2vw, 1.5rem);
              font-weight: bold;
              color: {smx.theme["nav_text"]};
              margin-right: 20px;
            }}
            .nav-left .nav-links a {{
              font-size: clamp(1rem, 1.2vw, 1.2rem);
              color: {smx.theme["nav_text"]};
              text-decoration: none;
              margin-right: 15px;
            }}
            .nav-right a {{
              font-size: clamp(1rem, 1.2vw, 1.2rem);
              color: {smx.theme["nav_text"]};
              text-decoration: none;
            }}
            /* Hamburger button (hidden on desktop) */
            #hamburger-btn {{
              display: none;
              width: clamp(140px, 20vw, 240px);
              font-size: 2rem;
              background: none;
              border: none;
              color: {smx.theme["nav_text"]};
              cursor: pointer;
            }}
            /* Mobile nav menu */
            #mobile-nav {{
              position: fixed;
              top: 50px; 
              right: -260px; 
              width: 18vw;
              font-size: .8rem;
              height: calc(100% - 60px);
              background: {smx.theme["sidebar_background"]};
              box-shadow: -2px 0 5px rgba(0,0,0,0.3);
              transition: right 0.3s ease;
              padding: 20px 5px 10px; 15px;
              display: flex;
              flex-direction: column;
              gap: 10px;
              z-index: 900;
              color: {mobile_text_color};
            }}
            #mobile-nav a {{
              font-size: inherit;
              color: {mobile_text_color};
              text-decoration: none;
              margin-left:4px;
            }}
            #mobile-nav.active {{
              right: 0;
            }}
            #mobile-nav a:hover {{
              background-color: rgba(0, 0, 0, 0.05);
              transform: scale(1.2);
            }}
            /* Responsive adjustments for mobile */
            @media (max-width: 768px) {{
              .nav-left .nav-links, .nav-right {{
                display: none;
              }}
              #hamburger-btn {{
                display: block;
              }}
             
            }}
            /* Sidebar styles */
            #sidebar {{
              position: fixed;
              top: 40px;
              left: -240px;
              width: var(--sidebar-w);
              height: calc(100% - 10px);
              background: {smx.theme["sidebar_background"]};
              overflow-y: auto;
              padding: 10px; 5px;
              font-size: 1.2rem;
              gap: 10px;
              box-shadow: 2px 0 5px rgba(0,0,0,0.3);
              transition: left 0.3s ease;
              z-index: 999;
              color: {get_contrast_color(smx.theme["sidebar_background"])};
            }}
            #sidebar a {{
              color: {get_contrast_color(smx.theme["sidebar_background"])};
              margin:3px;
              text-decoration: none;
            }}
            #sidebar.open {{
                left: 0;
            }}
            #sidebar-toggle-btn {{
              position: fixed;
              top: 52px;
              left: 0;
              width: 2rem;
              height: 2rem;
              padding: 1px;
              cursor: pointer;
              border: 1px solid {get_contrast_color(smx.theme["sidebar_background"])};
              border-radius: 8px;
              z-index: 1000;
              background: {smx.theme["nav_text"]};
              color: {smx.theme["nav_text"]};
              transition: background-color 0.2s ease, transform 0.2s ease;
            }}
            #sidebar-toggle-btn:hover {{
              background-color: rgba(0, 0, 0, 0.05);
              transform: scale(1.2);
            }}
            #chat-history {{
              width: 100%;
              max-width: 980px;
              margin: 50px auto 10px auto;
              padding: 10px 5px;
              background: {smx.theme["chat_background"]};
              border-radius: 20px;
              overflow-y: auto;
              min-height: 360px;
            }}
             #chat-history-default {{
              width: 100%;
              margin: 45px auto 10px auto;
              padding: 10px 5px;
              background: {smx.theme["chat_background"]};
              border-radius: 10px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.5);
              overflow-y: auto;
              min-height: 350px;
            }}
            #nc:hover {{
                background-color:#d6dbdf;
                transform:scale(1.2);
                transition: all 0.3s ease;
            }}
            #widget-container {{
              max-width: 850px;
              margin: 0 auto 40px auto;
            }}

            { _chat_css() }

            .closeable-div {{
              position: relative;
              padding: 20px;
              border: 1px solid #ccc;
              max-width: 70%;
              background-color: #fff;
            }}
            .close-btn {{
              position: absolute;
              top: 5px;
              right: 5px;
              cursor: pointer;
              font-size: 16px;
              padding: 2px 6px;
              color: #000;
            }}
            .close-btn:hover {{
              color: #ff0000;
            }}
          </style>
          <style>
            @keyframes spin {{
              0% {{ transform: rotate(0deg); }}
              100% {{ transform: rotate(360deg); }}
            }}
            
          </style>
          <style>
            .dropdown:hover .dropdown-content {{
                display: block;
            }}
          </style>
          <style>
            /* Keep the shift amount equal to the actual sidebar width */
             :root {{ --sidebar-w: 16vw; --nav-bg: {{smx.theme["nav_background"]}}; }}
          
            /* Messages slide; composer doesn't stay shifted */
            #chat-history,
            #widget-container {{ transition: transform .45s ease; }}

            /* Messages move fully clear of the sidebar */
            body.sidebar-open #chat-history {{ transform: translateX(calc(var(--sidebar-w) * 0.30)); }}

            /* Composer peeks right then returns to overlay the sidebar */
            @keyframes composer-peek {{
              0%   {{ transform: translateX(0); }}
              60%  {{ transform: translateX(var(--sidebar-w)); }}
              100% {{ transform: translateX(0); }}
            }}

            body.sidebar-open #widget-container {{ animation: composer-peek .45s ease; }}

            /* Composer should sit above the sidebar when it returns */
            #widget-container, #smx-widgets {{
              position: sticky;
              bottom: 0;
              z-index: 1100;          /* > sidebar (999) */
              background: inherit;
            }}
            #chat-history{{
              padding-bottom: calc(var(--composer-h, 104px) + 78);
            }}
            #chat-history .chat-message {{
              scroll-margin-bottom: calc(var(--composer-h, 104px) + 78);
            }}
            /* Stop browser scroll-anchoring from fighting our autoscroll */
            #chat-history,
            #widget-container {{
              overflow-anchor: none;
            }}

            /* Reduce visual “jump” when the scrollbar appears/disappears */
            html {{
              scrollbar-gutter: stable both-edges;
            }}

            /* Avoid unexpected smooth scrolling that can look like a jerk */
            html, body {{
              scroll-behavior: auto;
            }}
    
            /* Textarea bounds */
            .chat-composer {{ min-width:0; max-height:12vh; }}
            @media (max-width:900px){{
              .chat-composer {{ 
                min-height:56px; 
                line-height:1.4; 
                white-space: pre-wrap;
                padding: 10px 10px 16px 24px;
                font-size: 16px;       /* prevents iOS zoom + improves legibility */
                overflow-y: auto;      /* scroll after cap */
                box-sizing: border-box;
              }}
            }}
            
           .nav-left .nav-links a.active,
            .nav-left .nav-links a.active:hover,
            #mobile-nav a.active,
            #mobile-nav a.active:hover {{
              background-color: var(--nav-bg) !important;   /* keep the same base */
              box-shadow: inset 0 0 0 9999px rgba(0,0,0,.52); /* darken ~52% */
              border-radius: 6px;
              padding: 2px 8px;
              color:cyan;
            }}

          </style>
         
          <!-- Add MathJax -->
          <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
          <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
          <script>
          // Toggle mobile nav menu on hamburger click
            document.addEventListener("DOMContentLoaded", function() {{
            var hamburger = document.getElementById("hamburger-btn");
            var mobileNav = document.getElementById("mobile-nav");
            hamburger.addEventListener("click", function() {{
              mobileNav.classList.toggle("active");
            }});
          }});
          </script>
          <script>
            /** Turn the latest bot <p> into fade-in “lines” and reveal them sequentially */
            function splitToLines(node){{
              // If there are list items, animate them item-by-item.
              const lis = node.querySelectorAll('li');
              if (lis.length){{
                lis.forEach(li => li.classList.add('fade-line'));
                return Array.from(lis);
              }}

              // Normalise <br> and \n cases
              let html = node.innerHTML;

              // If there are explicit <br>, split on those
              if (/<br\s*\/?>/i.test(html)){{
                const parts = html.split(/<br\s*\/?>/i).map(s => s.trim()).filter(Boolean);
                node.innerHTML = parts.map(s => `<span class="fade-line">${{s}}</span>`).join('<br>');
                return Array.from(node.querySelectorAll('.fade-line'));
              }}

              // If there are plain newlines in the HTML, split on those
              if (/\n/.test(html)){{
                const parts = html.split(/\n+/).map(s => s.trim()).filter(Boolean);
                node.innerHTML = parts.map(s => `<span class="fade-line">${{s}}</span>`).join('<br>');
                return Array.from(node.querySelectorAll('.fade-line'));
              }}

              // As a fallback, split into sentences (keeps inline markup intact)
              // If content is code/pre, bail out to avoid mangling
              if (node.querySelector('code, pre') || html.includes('```')){{
                return []; // let the whole bubble’s default fade handle it
              }}

              const SENTENCES = html
                .split(/(?<=[.!?])\s+(?=[A-Z(“"'])/)   // split on sentence boundaries
                .map(s => s.trim())
                .filter(Boolean);

              if (SENTENCES.length <= 1){{
                node.innerHTML = `<span class="fade-line">${{html}}</span>`;
              }} else {{
                node.innerHTML = SENTENCES.map(s => `<span class="fade-line">${{s}}</span>`).join(' ');
              }}
              return Array.from(node.querySelectorAll('.fade-line'));
            }}

            function fadeInSequential(elems, baseDelay=90){{
              elems.forEach((el, i) => {{
                setTimeout(() => el.classList.add('show'), i * baseDelay);
              }});
            }}

            /** Animate only the newest bot message; no effect on older bubbles */
            function animateLastBotMessageLines(){{
              const bubbles = document.querySelectorAll(
                '#chat-history .chat-message.bot p, #chat-history .chat-message.assistant p'
              );
              if (!bubbles.length) return;
              const target = bubbles[bubbles.length - 1];
              if (target.dataset.animated === '1') return;

              const lines = splitToLines(target);
              if (lines.length){{
                target.dataset.animated = '1';
                fadeInSequential(lines);
              }}
            }}
            </script>
        
        </head>       
        """
   
    def _generate_nav():

        def _is_active(href: str) -> bool:
            cur = (request.path or "/").rstrip("/") or "/"
            dst = (href or "/").rstrip("/") or "/"
            return cur == dst or cur.startswith(dst + "/")

        # Build nav links with active class
        nav_items = []
        for page in smx.pages:
            href = f"/page/{page}"
            active = " active" if _is_active(href) else ""
            aria = ' aria-current="page"' if active else ""
            nav_items.append(f'<a href="{href}" class="{active.strip()}"{aria}>{page.capitalize()}</a>')

        for st in string_navbar_items:
            slug = st.lower().replace(" ", "_")
            href = f"/{slug}"
            active = " active" if _is_active(href) else ""
            aria = ' aria-current="page"' if active else ""
            if st == "Dashboard":
                st = "MLearning"

            # Only show Admin link to admins/superadmins
            if slug in ("admin", "admin_panel", "adminpanel"):
                role = session.get("role")
                if role not in ("admin", "superadmin"):
                    continue
            nav_items.append(f'<a href="{href}" class="{active.strip()}"{aria}>{st}</a>')

        nav_links = "".join(nav_items)

        theme_link = ''
        if smx.theme_toggle_enabled:
            theme_link = '<a href="/toggle_theme">Theme</a>'

        # Authentication links
        if session.get("user_id"):
            auth_links = (
                f'<span class="nav-auth" style="color:#ccc;">Hi {session.get("username")}</span> '
                f'<form action="{url_for("logout")}" method="post" style="display:inline;margin-left:0.5rem;">'
                '<button type="submit" class="nav-link" style="cursor:pointer;">Logout</button>'
                '</form>'
            )
        else:
            auth_links = (
                f'<a href="{url_for("login")}" class="nav-link">Login</a>'
                '|'
                f'<a href="{url_for("register")}" class="nav-link">Register</a>'
            )

        desktop_nav = f"""
          <div class="nav-left">
            <a class="logo" href="/" style="margin:0; padding:0;">{smx.site_logo}</a>
            <a class="logo" href="/" style="text-decoration:none; vertical-align="middle; margin:0 24px 0 0; padding:0px;">{smx.site_title}</a>
            <div class="nav-links" style="margin-left:24px;">
              {nav_links}
            </div>
          </div>
          <div class="nav-right">
            {theme_link}
          </div>
          <div class="nav-right">
            {auth_links}
          </div>
        """
        hamburger_btn = '<button id="hamburger-btn">&#9776;</button>'
        mobile_nav = f"""
          <div id="mobile-nav">
            {nav_links}
            {theme_link}
            {auth_links}
          </div>
          """
        return f"""
          <nav>
            {desktop_nav}
            {hamburger_btn}
          </nav>
          {mobile_nav}
          {hamburger_btn}
        """

    def footer_html():
        # Returns a simple footer styled with theme variables.
        return f"""
        <footer style="width:100%; padding:0; background:{smx.theme['nav_background']}; color:{smx.theme['nav_text']}; text-align:center; padding:4px;">
          <p style="margin:0; font_size:4px;">
            <em> 
              <span>&copy; {time.strftime('%Y')}</span>
              <span>|</span>
              <span style=color:cyan; font-size:0.7vw; margin-right:7px;>{smx.site_title}</span>
              <span>|</span>
              <span>All rights reserved.</span>
            </em>
          </p>
        </footer>
        """

    def _chat_css():
        fade_in = f"""
          /* Progressive line reveal */
          .fade-line{{opacity:0; transform:translateY(4px); transition:opacity .14s ease, transform .14s ease; display:block;}}
          .fade-line.show{{opacity:1; transform:translateY(0);}}
          @media (prefers-reduced-motion: reduce){{
            .fade-line{{transition:none; transform:none;}}
          }}

        """
        if smx.ui_mode == "default":
          return f"""
          .chat-message {{
              position: relative;
              max-width: 70%;
              margin: 10px 0;
              padding: 18px;
              border-radius: 20px;
              animation: fadeIn 0.7s forwards;
              clear: both;
              font-size: 0.8em;
          }}
          .chat-message.user {{
              background: #e4e8ed;
              float: right;
              margin-right: 15px;
              border-top-right-radius: 2px;
          }}
          .chat-message.user::after {{
              content: '';
              position: absolute;
              top: 0;               
              right: -9px;          
              width: 0;
              height: 0;
              border: 10px solid transparent;
              border-left-color: #6d3f3f;  
              border-right: 0;
          }}
          .chat-message.bot {{
              background: #E4E8ED;
              float: left;
              margin-left: 20px;
              border-top-left-radius: 2px;
          }}
          .chat-message.bot::after {{
              content: '';
              position: absolute;
              top: 0;             /* flush to bottom edge */
              left: -9px;            /* flush to left edge */
              width: 0x;
              height: 0x;
              border: 10px solid transparent;
              border-right-color: #69c2ff; 
              border-left: 0; 

              /* rotate 90° clockwise, pivoting at the bottom-left corner 
              transform: rotate(-45deg);
              transform-origin: 0% 100%; */
          }}
          .chat-message p {{
            margin: 0;
            word-wrap: break-word;
            white-space: pre-wrap;
            font-size: 0.9rem;
          }}

          {fade_in}
          """
        elif smx.ui_mode == "bubble":
            return f"""
            .chat-message {{
              position: relative;
              max-width: 70%;
              margin: 10px 0;
              padding: 12px 18px;
              border-radius: 20px;
              animation: fadeIn 0.9s forwards;
              clear: both;
              font-size: 0.9em;
            }}
            .chat-message.user {{
              background: pink;
              float: right;
              margin-right: 15px;
              border-bottom-left-radius: 2px;
            }}
            .chat-message.user::before {{
              content: '';
              position: absolute;
              left: -8px;
              top: 12px;
              width: 0;
              height: 0;
              border: 8px solid transparent;
              border-right-color: pink;
              border-right: 0;
            }}
            .chat-message.bot {{
              background: #ffffff;
              float: left;
              margin-left: 15px;
              border-bottom-left-radius: 2px;
              border: 1px solid {smx.theme['chat_border']};
            }}
            .chat-message.bot::after {{
              content: '';
              position: absolute;
              right: -8px;
              top: 12px;
              width: 0;
              height: 0;
              border: 8px solid transparent;
              border-left-color: #ffffff;
              border-right: 0;
            }}
            .chat-message p {{
              margin: 0;
              padding: 0;
              word-wrap: break-word;
              white-space: pre-wrap; /* preserve \n so “line-by-line” exists */
            }}
            {fade_in}
            """
        
        elif smx.ui_mode == "card":
            return f"""
            .chat-message {{
              display: block;
              margin: 20px auto;
              padding: 20px 24px;
              border-radius: 16px;
              background: linear-gradient(135deg, #fff, #f7f7f7);
              box-shadow: 0 4px 12px rgba(0,0,0,0.15);
              max-width: 80%;
              animation: fadeIn 0.7s forwards;
              position: relative;
            }}
            .chat-message.user {{
              margin-left: auto;
              border: 2px solid {smx.theme['nav_background']};
            }}
            .chat-message.bot {{
              margin-right: auto;
              border: 2px solid {smx.theme['chat_border']};
            }}
            .chat-message p {{
              margin: 0;
              font-size: em;
              line-height: 1.2;
            }}
            .chat-message strong {{
              display: block;
              margin-bottom: 8px;
              color: {smx.theme['nav_background']};
              font-size: 0.9em;
            }}
            {fade_in}
            """
        
        elif smx.ui_mode == "smx":
            return f"""
            .chat-message {{
              display: block;
              margin: 15px auto;
              padding: 16px 22px;
              border-radius: 12px;
              animation: fadeIn 0.9s forwards;
              max-width: 85%;
              background: #ffffff;
              border: 2px solid {smx.theme['nav_background']};
              position: relative;
            }}
            .chat-message.user {{
              background: #f9f9f9;
              border-color: {smx.theme['chat_border']};
              text-align: left;
            }}
            .chat-message.bot {{
              background: #e9f7ff;
              border-color: {smx.theme['nav_background']};
              text-align: right;
            }}
            .chat-message p {{
              margin: 0;
              word-wrap: break-word;
              font-size: 0.5em;
            }}
            """
        
        else:
            return f"""
            .chat-message {{
              display: block;
              width: 90%;
              margin-bottom: 10px;
              padding: 12px 18px;
              border-radius: 8px;
              animation: fadeIn 0.9s forwards;
            }}
            .chat-message.user {{
              background: #e1f5fe;
              text-align: right;
              margin-left: auto;
              max-width: 50%;
            }}
            .chat-message.bot {{
              background: #ffffff;
              border: 1px solid {{smx.theme["chat_border"]}};
              text-align: left;
              max-width: 80%;
            }}
            {fade_in}
            """

    def _render_widgets():
        """
        Renders the default system widget (the user_query text area with inner icons)
        and then any additional developer-defined widgets.
        Developer file upload triggered by the paper clip now supports multiple files.
        """
        form_html = """
        <form id="chat-form"
              style="width:100%; max-width:800px; margin:16px auto 12px auto; padding:0 10px; box-sizing:border-box;">
          <input type="hidden" id="action-field" name="action" value="submit_query">
        """

        horizontal_buttons_html = ""

        for key, widget in smx.widgets.items():
            """<span class="icon-default" style="cursor:pointer; transition:transform 0.2s ease;" title="Attach"
                          onclick="document.getElementById('user-file-upload').click();">
                          ➕ 📎
                </span>
            """
            # For the 'user_query' text input with injected icons and submit button.            
            # if widget["type"] == "text_input" and widget["key"] == "user_query":
            #     form_html += f"""
            #     <div style="position: relative; margin-bottom:15px; padding:10px 5px; width:100%; box-sizing:border-box;">
            #       <textarea
            #         id="user_query" class="chat-composer"
            #         name="{key}"
            #         rows="2"
            #         placeholder="{widget.get('placeholder','')}"
            #         style="
            #           position: absolute;
            #           bottom:0; left:0;
            #           width:100%;
            #           padding:12px 15px 50px 15px;
            #           font-size:1em;
            #           border:1px solid #ccc;
            #           border-radius:24px;
            #           box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            #           overflow:hidden; resize:none; box-sizing:border-box;
            #         "
            #         oninput="this.style.height='auto'; this.style.height=(this.scrollHeight)+'px'; checkInput(this)"
            #         autofocus
            #       >{session.get(key, '')}</textarea>

            #       <!-- Inline icons -->
            #       <div style="position:absolute; bottom:15px; left:15px; display:flex; gap:20px;">
            #         <!-- “+” opens the hidden PDF-upload input -->
            #         <span class="icon-default"
            #               title="Upload PDF files for this chat"
            #               style="cursor:pointer; transition:transform 0.2s ease;"
            #               onclick="document.getElementById('user_files').click()">
            #           📎
            #         </span>
            #         <!--
            #         <span class="icon-default"
            #               title="Internet"
            #               style="cursor:pointer; transition:transform 0.2s ease;">
            #           🌐
            #         </span>
            #         <span class="icon-default"
            #               title="Search"
            #               style="cursor:pointer; transition:transform 0.2s ease;">
            #           🔍
            #         </span> 
            #         -->
            #       </div>

            #       <!-- Hidden file-upload input bound to smx.file_uploader('user_files',…) -->
            #       <input
            #         type="file"
            #         id="user_files"
            #         name="user_files"
            #         multiple
            #         style="display:none"
            #         onchange="uploadUserFileAndProcess(this, 'user_files')"
            #       />

            #       <!-- Send button -->
            #       <button
            #         class="icon-default"
            #         title="Submit query
            #         type="submit"
            #         id="submit-button"
            #         name="submit_query"
            #         value="clicked"
            #         onclick="document.getElementById('action-field').value='submit_query'"
            #         disabled
            #         style="
            #           text-align:center;
            #           position:absolute;
            #           bottom:15px; right:15px;
            #           width:2rem; height:2rem;
            #           border-radius:50%; border:none;
            #           opacity:0.5;
            #           background:{smx.theme['nav_background']};
            #           color:{smx.theme['nav_text']};
            #           cursor:pointer; 
            #           font-size:1.2rem;
            #           display:flex; 
            #           align-items:center; justify-content:center;
            #           transition:transform 0.2s ease;
            #         "
            #       >⇧</button>
            #     </div>
            #     """
            if widget["type"] == "text_input" and widget["key"] == "user_query":
                # build conditional bits once
                files_icon_html = (
                    """
                    <span class="icon-default"
                          title="Upload PDF files for this chat"
                          style="cursor:pointer; transition:transform 0.2s ease; width=12px;"
                          onclick="document.getElementById('user_files').click()">➕</span>
                    """ if getattr(smx, "user_files_enabled", False) else ""
                )
                files_input_html = (
                    """
                    <input type="file" id="user_files" name="user_files" multiple
                          style="display:none"
                          onchange="uploadUserFileAndProcess(this, 'user_files')" />
                    """ if getattr(smx, "user_files_enabled", False) else ""
                )

                form_html += f"""
                <div style="position: relative; margin-bottom:15px; padding:10px 5px; width:100%; box-sizing:border-box;">
                  <textarea
                    id="user_query" class="chat-composer"
                    name="{key}"
                    rows="2"
                    placeholder="{widget.get('placeholder','')}"
                    style="
                      position: absolute;
                      bottom:0; left:0;
                      width:100%;
                      padding:12px 15px 56px 15px;  
                      font-size:1em;
                      border:1px solid #ccc;
                      border-radius:24px;
                      box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                      overflow:hidden; resize:none; box-sizing:border-box;"
                    oninput="this.style.height='auto'; this.style.height=(this.scrollHeight)+'px'; checkInput(this)"
                    autofocus>{session.get(key, '')}</textarea>

                  <!-- Inline icons (conditional) -->
                  {f'<div style="position:absolute; bottom:15px; left:15px; display:flex; gap:20px;">{files_icon_html}</div>' if getattr(smx, "enable_user_files", False) else ''}

                  <!-- Hidden file-upload (conditional) -->
                  {files_input_html}

                  <!-- Send button -->
                  <button
                    class="icon-default"
                    title="Submit query"
                    type="submit"
                    id="submit-button"
                    name="submit_query"
                    value="clicked"
                    onclick="document.getElementById('action-field').value='submit_query'"
                    disabled
                    style="
                      text-align:center;
                      position:absolute;
                      bottom:15px; right:15px;
                      width:2rem; height:2rem;
                      border-radius:50%; border:none;
                      opacity:0.5;
                      background:{smx.theme['nav_background']};
                      color:{smx.theme['nav_text']};
                      cursor:pointer;
                      font-size:1.2rem;
                      display:flex; align-items:center; justify-content:center;
                      transition:transform 0.2s ease;">⇧</button>
                </div>
                """

            elif widget["type"] == "text_input":
                form_html += f"""
                <div style="margin-bottom:15px;">
                  <label for="{key}" style="display:block; margin-bottom:5px;">{widget['label']}</label>
                  <input type="text" id="{key}" name="{key}" placeholder="{widget.get('placeholder','')}"
                        value="{session.get(key, '')}"
                        style="width:calc(100% - 20px); padding:12px; font-size:1em; border:1px solid #ccc;
                        border-radius:8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); box-sizing:border-box;">
                </div>
                """
            
            elif widget["type"] == "button" and widget["key"] == "submit_query":
                continue # Handled inline in the user_query textarea above.
            elif widget["type"] == "file_upload" and widget["key"] == "user_files":
                continue # Handled inline in the user_query textarea above.
            
            elif widget["type"] == "button":
                horizontal_buttons_html += f"""
                <div style="width:850px;text-align:center;">
                <button
                    class="icon-default"
                    type="submit"
                    name="{key}"
                    value="clicked"
                    onclick="document.getElementById('action-field').value='{key}'"
                    style="
                        with:2rem;
                        font-size:0.8rem;
                        padding:5px 10px;
                        border:none;
                        border-radius:30px;
                        background:{smx.theme['nav_background']};
                        color:{smx.theme['nav_text']};
                        cursor:pointer;
                        /*transition: background 0.3s;*/
                        transition:transform 0.2s ease;"
                    "
                    onmouseover="this.style.backgroundColor='#e0e0e0';"
                    onmouseout="this.style.backgroundColor='{smx.theme['nav_background']}';"
                >
                    {widget['label']}
                </button>
                </div>
                """
            
            elif widget["type"] == "file_upload":
                uploaded = request.files.getlist(key)
                if uploaded:
                    sid = smx.get_session_id()
                    for f in uploaded:
                        raw = f.read()
                        reader = PdfReader(BytesIO(raw))
                        text = "".join(page.extract_text() or "" for page in reader.pages)
                        chunks = recursive_text_split(text)
                        smx.add_user_chunks(sid, chunks)
                    # invoke the one callback you registered
                    if widget.get("callback"):
                        widget["callback"]()
                    count = len([f for f in uploaded if getattr(f, "filename", "")])
                    if count:
                        smx.success(f"Uploaded {count} file{'s' if count != 1 else ''} and indexed them.")

            elif widget["type"] == "dropdown":
                options_html = "".join([
                    f"<option value='{opt}'{' selected' if opt == widget['value'] else ''}>{opt}</option>"
                    for opt in widget["options"]
                ])
         
                dropdown_html = f"""
                <div style="margin:10px 0;">
                    <label for="{key}" style="font-weight:bold;">{widget['label']}</label>
                    <select name="{key}" id="{key}" onchange="widget_event_dropdown('{key}')"
                        style="padding:4px 16px; border-radius:5px; font-size:1.06em; min-width:180px; margin-left:4px;">
                        {options_html}
                    </select>
                </div>
                """
                form_html += dropdown_html

        if horizontal_buttons_html:
            form_html += f"""
            <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-bottom:15px;">
                {horizontal_buttons_html}
            </div>
            """
        form_html += "</form>"
        
        form_html += """
        <script>
          function checkInput(textarea) {
            var submitBtn = document.getElementById("submit-button");
            if (!submitBtn) return;

            // If the button is currently acting as STOP for an active turn,
            // never disable it or fade it, even if the textbox is empty.
            if (submitBtn.classList.contains('stop')) {
              submitBtn.disabled = false;
              submitBtn.style.opacity = "1";
              return;
            }

            if ((textarea.value || "").trim() === "") {
              submitBtn.disabled = true;
              submitBtn.style.opacity = "0.5";
            } else {
              submitBtn.disabled = false;
              submitBtn.style.opacity = "1";
            }
          }
          // Animate icons on hover
          var icons = document.getElementsByClassName('icon-default');
          for (var i = 0; i < icons.length; i++) {
            icons[i].addEventListener('mouseover', function() {
              this.style.transform = "scale(1.2)";
            });
            icons[i].addEventListener('mouseout', function() {
              this.style.transform = "scale(1)";
            });
          }
          
          // AJAX function to upload multiple user files
          function uploadUserFile(inputElement) {
            if (inputElement.files.length > 0) {
              var formData = new FormData();
              for (var i = 0; i < inputElement.files.length; i++) {
                  formData.append("user_files", inputElement.files[i]);
              }
              fetch('/upload_user_file', {
                  method: "POST",
                  body: formData
              })
              .then(response => response.json())
              .then(data => {
                  if(data.error) {
                      alert("Error: " + data.error);
                  } else {
                      alert("Uploaded files: " + data.uploaded_files.join(", "));
                      // Optionally, store or display file paths returned by the server.
                  }
              })
              .catch(err => {
                  console.error(err);
                  alert("Upload failed.");
              });
            }
          }
        </script>
        <script>
          // When picking files, the action is stashed to the widget key
          // then fire submitChat with submitter.id = that key.
          
          // Upload PDFs and process via the non-stream route only
          async function uploadUserFileAndProcess(inputEl, actionKey) {
            if (!inputEl.files.length) return;

            const spinner = document.getElementById('loading-spinner');
            if (spinner) spinner.style.display = 'block';

            const form = document.getElementById('chat-form');
            const actionField = document.getElementById('action-field');

            // Tell the server which widget to execute
            actionField.value = actionKey;

            // Build payload from the *form* so the files are included
            const fd = new FormData(form);
            if (!fd.has(actionKey)) fd.append(actionKey, 'clicked');

            try {
              const res = await fetch('/process_chat', { method: 'POST', body: fd });
              const data = await res.json();

              // Update chat pane
              document.getElementById('chat-history').innerHTML = data.chat_html;

              // Update (or remove) the system output panel exactly like submitChat
              let outputContainer = document.getElementById('system-output-container');
              if (outputContainer) {
                if ((data.system_output_html || '').trim() === '') {
                  outputContainer.remove();
                } else {
                  outputContainer.innerHTML = data.system_output_html;
                  const scripts = outputContainer.querySelectorAll('script');
                  scripts.forEach(oldScript => {
                    const s = document.createElement('script');
                    if (oldScript.src) s.src = oldScript.src; else s.textContent = oldScript.textContent;
                    oldScript.parentNode.replaceChild(s, oldScript);
                  });
                }
              } else if ((data.system_output_html || '').trim() !== '') {
                outputContainer = document.createElement('div');
                outputContainer.id = 'system-output-container';
                outputContainer.style = "max-width:850px; margin:20px auto; padding:10px; background:#fff; border:1px solid #ccc; border-radius:8px; margin-top:150px;";
                outputContainer.innerHTML = data.system_output_html;
                const scripts = outputContainer.querySelectorAll('script');
                scripts.forEach(oldScript => {
                  const s = document.createElement('script');
                  if (oldScript.src) s.src = oldScript.src; else s.textContent = oldScript.textContent;
                  oldScript.parentNode.replaceChild(s, oldScript);
                });
                document.body.prepend(outputContainer);
              }

              // Scroll to bottom
              const chatHistory = document.getElementById('chat-history');
              window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' });
            } catch (err) {
              console.error(err);
              alert('Upload failed.');
            } finally {
              if (spinner) spinner.style.display = 'none';
              // Reset UI state
              actionField.value = 'submit_query';
              inputEl.value = '';
              const dot = document.getElementById('thinking-dots');
              if (dot) dot.remove(); // in case any nudge slipped in
              const btn = document.getElementById('submit-button');
              if (btn) {
                btn.disabled = true;
                btn.innerText = '⇧';
                btn.style.opacity = '0.5';
              }
            }
          }
        </script>
        <script>
          function widget_event_dropdown(key) {
              var value = document.getElementById(key).value;
              fetch('/widget_event', {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({widget_key: key, widget_value: value})
              })
              .then(response => response.json())
              .then(data => {
                  let outputContainer = document.getElementById('system-output-container');
                  if (outputContainer) {
                      if (data.system_output_html.trim() === "") {
                          outputContainer.remove();
                      } else {
                          outputContainer.innerHTML = data.system_output_html;
                      }
                  } else if (data.system_output_html.trim() !== "") {
                      outputContainer = document.createElement('div');
                      outputContainer.id = 'system-output-container';
                      outputContainer.innerHTML = data.system_output_html;

                      const scripts = outputContainer.querySelectorAll('script');
                      scripts.forEach(oldScript => {
                        const newScript = document.createElement('script');
                        if (oldScript.src) {
                          newScript.src = oldScript.src;
                        } else {
                          newScript.textContent = oldScript.textContent;
                        }
                        oldScript.parentNode.replaceChild(newScript, oldScript);
                      });

                      document.body.prepend(outputContainer);
                  }
                  // Update widgets if changed
                  if (data.widgets_html) {
                      document.getElementById('widget-container').innerHTML = data.widgets_html;
                  }
              });
          }
          </script>
        """      
        return form_html
      
    def _render_session_sidebar():
        current = session.get("current_session", {"title": "Current"})
        current_display = current.get("title", "Current")
        past_sessions = session.get("past_sessions", [])
        sidebar_html = '<div id="sidebar">'
        sidebar_html += (
            '<div style="margin:8px auto; text-align:right;">'
            '<button id="nc" type="button" onclick="createNewChat()" title="New Chat" style="width:4rem; height:2rem; font-size:1rem; border:none; border-radius:4px; cursor:pointer;">..𓂃🖊</button>'
            '</div>'
        )
        if current_display == "Current":
            try:
              sidebar_html += f'''
                  <div class="session-item active" style="margin-bottom: 15px; color: {smx.theme["nav_text"]};">
                    <span class="session-title" style="font-size:0.8rem;cursor:default;">{current_display}</span>
                  </div>
              '''
            except: return 
        if past_sessions:
            sidebar_html += f'''
                <hr style="margin:10px 0;">
                <div style="color: {smx.theme["nav_background"]};font-size:0.7rem;"><strong>Chats</strong></div>
                <ul style="list-style-type:none; padding:0; margin:0;">
            '''
            for s in past_sessions:
      
                safe_title_raw  = s["title"]
                # Tooltip – needs HTML-escaping
                
                try: 
                  safe_title_html = html.escape(safe_title_raw) 
                except: return

                # Data for JS call – encode once, decode on click
                encoded_title   = quote(safe_title_raw, safe='')

                display_title = (
                    safe_title_raw if len(safe_title_raw) <= 15 else safe_title_raw[:15] + "…"
                )
                active_class  = (
                    " active" if s["id"] == current.get("id") and current_display != "Current"
                    else ""
                )
                sidebar_html += f"""
                <li class="session-item{active_class}" data-session-id="{s['id']}" 
                    style="margin-top:4px; padding:0;">
                    <span class="session-title" title="{safe_title_html}"
                          style="float:left;"
                          onclick="setSession('{s['id']}', this)">{display_title} 
                    </span>
                    <span class="icon-default session-ellipsis" title="Options"
                          style="margin-left:auto;font-size:18px;cursor:pointer;transition:transform 0.2s ease; border:1px solid purple;border-radius:4px;"
                          onclick="event.stopPropagation(); toggleSessionMenu('{s['id']}')">
                          &vellip;&vellip;
                    </span>
                    <div class="session-menu" id="menu-{s['id']}" style="text-align:right;">
                        <div class="menu-item" title="Rename chat"
                            onclick="openRenameModal('{s['id']}', decodeURIComponent('{encoded_title}'))">
                            ✏️Rename
                        </div>
                        <div class="menu-item" title="Delete chat"
                            onclick="openDeleteModal('{s['id']}')">
                            🗑️Delete
                        </div>
                    </div>
                </li>
                """
            sidebar_html += '</ul>'
        sidebar_html += '</div>'
        misc_sidebar_css = f"""
        <style>
          .session-item {{
              font-size: 0.7rem;
              margin: 5px 0;
              position: relative;
              padding: 5px 10px;
              border-radius: 4px;
              cursor: pointer;
              display: flex;
              justify-content: space-between;
              align-items: center;
              transition: background 0.3s;
          }}
          .session-item:hover {{
              background-color: {smx.theme.get('sidebar_hover', '#cccccc')};
          }}
          .session-item.active {{
              background-color: {smx.theme.get('sidebar_active', '#aaaaaa')};
          }}
          .session-title {{
              flex-grow: 1;
          }}
          .session-ellipsis {{
              display: none;
              margin-left: 5px;
          }}
          .session-item:hover .session-ellipsis {{
              display: inline-block;
          }}
          .session-menu {{
              display: none;
              position: absolute;
              right: 0;
              top: 50%;
              transform: translateY(-50%);
              background: #fff;
              border: 1px solid #ccc;
              min-width: 100px;
              z-index: 10;
              padding: 5px;
          }}
          .menu-item {{
              padding: 3px 5px;
              cursor: pointer;
          }}
          .menu-item:hover {{
              background: #eee;
          }}
        </style>
        """
        return sidebar_html + misc_sidebar_css

    
     # ──────────────────────────────────────────────────────────────────────────────────────── 
    
    @smx.app.route("/toggle_theme", methods=["GET"])
    def toggle_theme():
        # Use an explicit order if you have one; otherwise dict insertion order.
        names = getattr(smx, "theme_order", None) or list(DEFAULT_THEMES.keys())
        if not names:
            return redirect(request.referrer or url_for("home"))

        # Figure out current theme name (from session, or by matching smx.theme)
        cur = (session.get("theme_name") or "").lower()
        if cur not in [n.lower() for n in names]:
            # try to infer from the current smx.theme dict
            for n in names:
                if DEFAULT_THEMES[n] == smx.theme:
                    cur = n.lower()
                    break
            else:
                cur = names[0].lower()

        # Next theme (wrap around)
        i = next((idx for idx, n in enumerate(names) if n.lower() == cur), 0)
        next_name = names[(i + 1) % len(names)]

        # Apply & persist
        smx.theme = DEFAULT_THEMES[next_name]
        session["theme_name"] = next_name
        session.modified = True
        return redirect(request.referrer or url_for("home"))

    # ──────────────────────────────────────────────────────────────────────────────────────── 
    # ── HOME VIEW DETAILS -----------------------------
    @smx.app.route("/", methods=["GET", "POST"])
    def home():
        smx.page = ""
        if not session.get("current_session"):
            session["current_session"] = {"id": str(uuid.uuid4()), "title": "Current", "history": []}
            session.setdefault("past_sessions", [])
            session.setdefault("chat_history", [])
            session["active_chat_id"] = session["current_session"]["id"]

        if session.pop("needs_end_chat", False):
            current_history = session.get("chat_history", [])
            current_session = session.get("current_session", {"id": str(uuid.uuid4()), "title": "Current", "history": []})
            past_sessions = session.get("past_sessions", [])
            
            if current_history:
                exists = any(s["id"] == current_session["id"] for s in past_sessions)
                if not exists:
                    if _prof.get_profile("labeller"):
                        generated_title = smx.generate_contextual_title(current_history)
                    else:
                        generated_title = "Conversation"
                    current_session["title"] = generated_title
                    current_session["history"] = current_history.copy()
                    past_sessions.insert(0, current_session)
                else:
                    for s in past_sessions:
                        if s["id"] == current_session["id"]:
                            s["history"] = current_history.copy()
                            break
                        
                session["past_sessions"] = past_sessions
            session["current_session"] = {"id": str(uuid.uuid4()), "title": "Current", "history": []}
            session["active_chat_id"] = session["current_session"]["id"]
            session["chat_history"] = []
            session["user_query"] = ""
            session["app_token"] = smx.app_token

            cur = session.get("current_session")
            if cur and cur.get("id") and session.get("active_chat_id") != cur["id"]:
                session["active_chat_id"] = cur["id"]
        
        if request.method == "POST":
            action = request.form.get("action")

            if action == "clear_chat":
                session["chat_history"] = []

            elif action == "new_session":
                current_history = session.get("chat_history", [])
                current_session = session.get("current_session", {"id": str(uuid.uuid4()), "title": "Current", "history": []})
                past_sessions = session.get("past_sessions", [])
                exists = any(s["id"] == current_session["id"] for s in past_sessions)
                if current_history:
                    if not exists:
                        generated_title = smx.generate_contextual_title(current_history)
                        current_session["title"] = generated_title
                        current_session["history"] = current_history.copy()
                        past_sessions.insert(0, current_session)
                    else:
                        for s in past_sessions:
                            if s["id"] == current_session["id"]:
                                s["history"] = current_history.copy()
                                break
                    session["past_sessions"] = past_sessions
                    # — Persist the just‐ended “Current” chat into chats.db for logged-in users —
                    if session.get("user_id"):
                        user_id = session["user_id"]
                        cid     = current_session["id"]
                        title   = current_session["title"]
                        SQLHistoryStore.save(user_id, cid, current_history, title)

                session["current_session"] = {"id": str(uuid.uuid4()), "title": "Current", "history": []}
                session["active_chat_id"] = session["current_session"]["id"]
                session["chat_history"] = []
                session["user_query"] = ""             
                session.modified = True
            session["app_token"] = smx.app_token
        nav_html = _generate_nav()
        chat_html = render_chat_history(smx)
        widget_html = _render_widgets()
        sidebar_html = _render_session_sidebar()

        new_chat_js = """
        <script>
          function createNewChat() {
            var form = document.createElement("form");
            form.method = "POST";
            form.action = "/";
            var input = document.createElement("input");
            input.type = "hidden";
            input.name = "action";
            input.value = "new_session";
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
          }
        </script>
        """

        scroll_and_toggle_js = f"""
          <script>

            if (!window.__smxListenersBound) {{
              window.__smxListenersBound = true;

              document.addEventListener('submit', function(ev){{
                if (ev.target && ev.target.id === 'chat-form') {{
                  ev.preventDefault();
                  const af = document.getElementById('action-field');
                  const actionVal = af ? af.value : 'submit_query';
                  const submitter = (ev && ev.submitter) || document.activeElement;
                  const isClear = (actionVal === 'clear' || actionVal === 'clear_chat' ||
                                  (submitter && (submitter.name === 'clear' || submitter.id === 'clear')));
                }}
              }});

              document.addEventListener('keydown', function(ev) {{
                if (ev.key === 'Enter' && !ev.shiftKey &&
                    ev.target && ev.target.matches('#chat-form textarea[name="user_query"]')) {{
                  ev.preventDefault();
                  const af = document.getElementById('action-field');
                  if (af) af.value = 'submit_query';
                  const form = document.getElementById('chat-form');
                  if (form) form.requestSubmit();
                }}
              }});

              document.addEventListener('keydown', function (ev) {{
                if (ev.key !== 'Escape') return;

                // If a modal is open (admin pages), don't hijack Esc
                const modal = document.getElementById('delBackdrop');
                if (modal && modal.style.display === 'flex') return;

                // Only act if a turn is in progress or the Stop UI is active
                const stopBtn = document.getElementById('submit-button');
                const stopActive =
                  !!window.__smxBusy ||
                  !!window.__smxEvt ||
                  !!window.__smxPostAbort ||
                  (stopBtn && stopBtn.classList.contains('stop'));

                if (!stopActive) return;

                ev.preventDefault();
                ev.stopPropagation();
                // Same handler your Stop button uses
                if (typeof smxAbortActiveTurn === 'function') smxAbortActiveTurn();
              }});
            }}

            // --- Make icons from Python available to JavaScript ---
            window.SMX_USER_ICON = `{smx.user_icon}`;
            window.SMX_BOT_ICON = `{smx.bot_icon}`;
            window.SMX_IS_STREAM = { 'true' if smx.stream() else 'false' };
            window.__smxEvt = window.__smxEvt || null;             // active EventSource (SSE)
            window.__smxPostAbort = window.__smxPostAbort || null; // AbortController for POST
            // ----------------------------------------------------------------
            // Global busy flag to prevent concurrent submits
            window.__smxBusy = window.__smxBusy || false;

            function smxRemoveProvisionalBubbles() {{
              try {{
                const ch = document.getElementById('chat-history');
                if (!ch) return;
                // Remove the last provisional user bubble (if any)
                const userProvs = ch.querySelectorAll('.chat-message.user.provisional');
                if (userProvs.length) userProvs[userProvs.length - 1].remove();
                // Remove any streaming bot bubbles (thinking + typing shell)
                ch.querySelectorAll('.chat-message.bot.streaming').forEach(n => n.remove());
              }} catch (_) {{}}
            }}

            async function smxAbortActiveTurn() {{
              // 1) Close SSE (if open)
              try {{ if (window.__smxEvt) window.__smxEvt.close(); }} catch(_) {{}}
              window.__smxEvt = null;

              // 2) Abort in-flight POST (non-stream path)
              try {{ if (window.__smxPostAbort) window.__smxPostAbort.abort(); }} catch(_) {{}}
              window.__smxPostAbort = null;

              // 3) Tell server to discard partial stream + roll back any slip-in bot text
              //    (your /cancel_stream already pops a trailing Bot turn and mirrors session) :contentReference[oaicite:0]{{index=0}}
              try {{ await fetch('/cancel_stream', {{ method:'POST', credentials:'same-origin' }}); }} catch(_) {{}}

              // 4) Undo UI renderings
              smxRemoveProvisionalBubbles();
              smxThinkingOff?.();

              // 5) Re-sync panes from canonical server state (just like after a normal stream) :contentReference[oaicite:1]{{index=1}}
              try {{
                 const r = await fetch('/sync_after_stream', {{ 
                  method:'POST', 
                  credentials:'same-origin',
                  headers: {{ 'Content-Type':'application/json' }},
                  body: JSON.stringify({{ sidebar_state: (localStorage.getItem('sidebarState') || 'closed') }})
                }});
                const {{ chat_html, sidebar_html, sidebar_state }} = await r.json();

                const ch = document.getElementById('chat-history');
                if (ch && chat_html) ch.innerHTML = chat_html;
                const sb = document.getElementById('sidebar-container');
                if (sb && sidebar_html) sb.innerHTML = sidebar_html;
                
                try {{ window.dispatchEvent(new Event('sidebar:redraw')); }} catch (e) {{}}

                (function restoreSidebarState() {{
                  // Prefer localStorage; fall back to server echo if needed
                  const state = localStorage.getItem('sidebarState') || sidebar_state || 'closed';
                  const isOpen = state === 'open';
                  const sidebar = document.getElementById('sidebar');
                  const body = document.body;
                  if (sidebar) sidebar.classList.toggle('open', isOpen);
                  body.classList.toggle('sidebar-open', isOpen);
                  const toggle = document.getElementById('sidebar-toggle');
                  if (toggle) toggle.setAttribute('aria-pressed', String(isOpen));
                  // Keep both sides consistent
                  localStorage.setItem('sidebarState', state);
                }})();
              }} catch(_) {{}}

              // 6) Reset controls
              const big = document.getElementById('loading-spinner');
              if (big) big.style.display = 'none';
              smxRestoreSubmitArrow?.();
              window.__smxBusy = false;
            }}

            // Fade in the last assistant/bot message, line by line.
            function fadeInLastAssistant() {{
              const chatHistory = document.getElementById('chat-history');
              if (!chatHistory) return;

              const messages = chatHistory.querySelectorAll('.chat-message');
              if (!messages || !messages.length) return;

              // Find last NON-user message
              let last = null;
              for (let i = messages.length - 1; i >= 0; i--) {{
                if (!messages[i].classList.contains('user')) {{ last = messages[i]; break; }}
              }}
              if (!last) return;

              const p = last.querySelector('p');
              if (!p) return;
              if (p.dataset.animated === '1') return; // idempotent
              p.dataset.animated = '1';

              // Normalise line breaks and collapse 3+ blank lines to a single blank line
              const raw = (p.textContent || '').replace(/\\r\\n/g, '\\n').replace(/\\n{{3,}}/g, '\\n\\n');
              const lines = raw.split('\\n');

              // One-liners: simple fade
              if (lines.length <= 1) {{
                p.style.opacity = '0';
                p.style.transition = 'opacity 320ms ease';
                requestAnimationFrame(() => {{ p.style.opacity = '1'; }});
                return;
              }}

              // Build line-by-line spans
              // Build line-by-line spans, adding a small gap after each fade
              p.innerHTML = '';
              const FADE_MS = 180;     // how long each line fades
              const GAP_MS = 70;     // extra pause before the next line starts
              const STEP_MS = FADE_MS + GAP_MS; // total time between line starts

              lines.forEach((line, idx) => {{
                const span = document.createElement('span');
                span.style.opacity = '0';
                span.style.display = 'block';
                span.style.margin = '0';
                span.style.padding = '0';
                span.style.lineHeight = '1.35';
                span.textContent = line;
                p.appendChild(span);

                setTimeout(() => {{
                  span.style.transition = `opacity ${{FADE_MS}}ms ease`;
                  span.style.opacity = '1';
                  if (idx === lines.length - 1) {{
                    last.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                  }}
                }}, STEP_MS * idx);
              }});
            }}

            function smxSetSubmitAsStop() {{
              const btn = document.getElementById('submit-button');
              if (!btn) return;
              btn.dataset.prevType = btn.getAttribute('type') || 'submit';
              btn.dataset.prevHtml = btn.innerHTML || '⇧';
              btn.classList.add('stop');
              btn.setAttribute('type', 'button'); // avoid accidental resubmits while busy
              btn.disabled = false;
              btn.style.opacity = '1';
              btn.title = 'Stop';

              // Spinner ring circumscribing the stop icon
              btn.innerHTML = `
                <span class="btn-spinner-wrap" aria-hidden="true">
                  <span class="btn-spinner-ring"></span>
                  <span class="btn-stop" role="img" aria-label="Stop">■</span>
                </span>
              `;
               btn.onclick = smxAbortActiveTurn;
            }}

            function smxRestoreSubmitArrow() {{
              const btn = document.getElementById('submit-button');
              if (!btn) return;
              btn.classList.remove('stop');
              btn.setAttribute('type', btn.dataset.prevType || 'submit');
              btn.innerHTML = (btn.dataset.prevHtml || '⇧');
              // Keep enabled/disabled consistent with textbox content
              try {{
                const ta = document.querySelector('#chat-form textarea[name="user_query"]');
                const hasText = !!(ta && (ta.value || '').trim());
                btn.disabled = !hasText;
                btn.style.opacity = hasText ? '1' : '0.5';
              }} catch (_) {{}}
              btn.title = 'Submit query';
              btn.onclick = null; // remove Stop handler
            }}

            function smxThinkingOn() {{
              const think = document.getElementById('bot-thinking');
              if (think) think.style.display = 'inline-flex';
              const typer = document.getElementById('typewriter-icon');
              if (typer) typer.style.display = 'inline-flex';
            }}

            function smxThinkingOff() {{
              const think = document.getElementById('bot-thinking');
              if (think) think.style.display = 'none';
              const typer = document.getElementById('typewriter-icon');
              if (typer) typer.style.display = 'none';
            }}

            // Submit handler (fetches /process_chat)
            async function submitChat(e) {{
              // Always prevent native submission
              if (e && typeof e.preventDefault === 'function') e.preventDefault();
              if (window.__smxBusy) return false;
              window.__smxBusy = true;

              smxSetSubmitAsStop();

              // Decide stream mode immediately
              const isStreaming = !!(typeof window !== 'undefined' &&
                       (window.SMX_IS_STREAM === true || window.SMX_IS_STREAM === 'true'));
              
              let startedStream = false;

              // Big page spinner only for NON-stream now
              const big = document.getElementById('loading-spinner');
              if (isStreaming) {{
                if (big) big.style.display = 'none';
                // Show thinking + typewriter immediately in stream mode
                smxThinkingOn();
              }} else {{
                if (big) big.style.display = 'block';
              }}

              // Default action: submit_query
              const af = document.getElementById('action-field');
              // Only set a default if nothing has already set the action (e.g., the file uploader)
              if (af && !af.value) af.value = "submit_query";

              try {{
                const form = document.getElementById('chat-form');
                const formData = new FormData(form);
                const action = document.getElementById('action-field').value;
                if (!formData.has(action)) formData.append(action, 'clicked');

                var ta = document.querySelector('#chat-form textarea[name="user_query"]');
                  var userText = ta ? ta.value : '';
                  if (userText && userText.trim() !== '') {{
                    smxShowProvisionalUserBubble(userText);
                }}

                // Create a provisional bot bubble right now so dots/caret show instantly
                if (isStreaming && !window.__smxPreBubble && typeof smxMakeStreamBubble === 'function') {{
                  window.__smxPreBubble = smxMakeStreamBubble();
                }}

                // Wire an AbortController so Stop can cancel a non-stream POST
                const ctrl = new AbortController();
                window.__smxPostAbort = ctrl;

                const response = await fetch('/process_chat', {{
                  method: 'POST',
                  body: formData,
                  credentials: 'same-origin',
                  signal: ctrl.signal
                }});
                
                // If this was a file-upload action, clear the chooser and restore default action
                if (action === 'user_files') {{
                  const f = document.getElementById('user_files');
                  if (f) f.value = '';
                  const af = document.getElementById('action-field');
                  if (af) af.value = 'submit_query';
                }}

                const data = await response.json();

                // Decide stream vs non-stream based on what the server returned
                try {{
                  const af = document.getElementById('action-field');
                  const isSubmit = (af && af.value === 'submit_query');

                  const ch = document.getElementById('chat-history');
                  const serverHtml = (data && data.chat_html) ? String(data.chat_html) : '';

                  // Detect if the LAST bubble in the returned HTML is a bot message.
                  // If true → server has already produced the final bot reply (NON-STREAM).
                  // If false → open SSE (STREAM).
                  let lastIsBot = false;
                  if (serverHtml) {{
                    const idxBotSingle  = serverHtml.lastIndexOf("class='chat-message bot'");
                    const idxUserSingle = serverHtml.lastIndexOf("class='chat-message user'");
                    const idxBotDouble  = serverHtml.lastIndexOf('class="chat-message bot"');
                    const idxUserDouble = serverHtml.lastIndexOf('class="chat-message user"');

                    const idxBot  = Math.max(idxBotSingle,  idxBotDouble);
                    const idxUser = Math.max(idxUserSingle, idxUserDouble);
                    lastIsBot = (idxBot > -1 && idxBot > idxUser);
                  }}

                  if (isSubmit && lastIsBot) {{
                    // NON-STREAM: render the final HTML and DO NOT start streaming
                    if (ch) ch.innerHTML = serverHtml;
                    // Drop the provisional stream bubble if we created one
                    if (window.__smxPreBubble && window.__smxPreBubble.bubble) {{
                      try {{ window.__smxPreBubble.bubble.remove(); }} catch(_) {{}}
                      window.__smxPreBubble = null;
                    }}
                  }} else if (isSubmit) {{
                    // STREAM: keep the DOM as-is (your provisional user bubble stays) and start SSE
                    startedStream = true;
                    startStream();
                  }} else {{
                    // Not a submit (uploads/buttons/etc.): normal refresh
                    if (ch) ch.innerHTML = serverHtml;
                  }}
                }} catch (e) {{
                  console.error('stream/non-stream decision failed', e);
                }}

                // Update or create the system output panel
                let outputContainer = document.getElementById('system-output-container');
                if (outputContainer) {{
                  outputContainer.innerHTML = data.system_output_html;
                }} else if (data.system_output_html && data.system_output_html.trim() !== "") {{
                  outputContainer = document.createElement('div');
                  outputContainer.id = 'system-output-container';
                  outputContainer.style = "max-width:850px; margin: 0 auto; padding:16px; background:#fff; border:1px solid #ccc; border-radius:8px; margin-top:150px;";
                  outputContainer.innerHTML = data.system_output_html;

                  // Re-execute any scripts inside the injected HTML
                  const scripts = outputContainer.querySelectorAll('script');
                  scripts.forEach(oldScript => {{
                    const newScript = document.createElement('script');
                    if (oldScript.src) newScript.src = oldScript.src;
                    else newScript.textContent = oldScript.textContent;
                    oldScript.parentNode.replaceChild(newScript, oldScript);
                  }});

                  document.body.prepend(outputContainer);
                }}

                // If widgets changed server-side, swap them in
                if (data.widgets_html) {{
                  const wc = document.getElementById('widget-container');
                  if (wc) wc.innerHTML = data.widgets_html;
                }}

                // Clear composer for real submits
                if (af && af.value === 'submit_query') {{
                  const userQuery = document.querySelector('#chat-form textarea[name="user_query"]');
                  if (userQuery) {{
                    userQuery.value = "";
                    if (typeof window.checkInput !== 'function') {{
                      window.checkInput = function(textarea) {{
                        var submitBtn = document.getElementById("submit-button");
                        if (!submitBtn) return;
                        if ((textarea.value || "").trim() === "") {{
                          submitBtn.disabled = true; submitBtn.style.opacity = "0.5";
                        }} else {{
                          submitBtn.disabled = false; submitBtn.style.opacity = "1";
                        }}
                      }};
                    }}
                    const btn = document.getElementById('submit-button');
                    if (!(btn && btn.classList.contains('stop'))) {{
                      window.checkInput(userQuery);
                    }}
                  }}
                }}

                // Animate non-streamed reply
                fadeInLastAssistant();

                // Scroll to newest message
                const chatHistory = document.getElementById("chat-history");
                const lastMsg = chatHistory ? chatHistory.lastElementChild : null;
                if (lastMsg) lastMsg.scrollIntoView({{ behavior: 'smooth', block: 'end' }});

              }} catch (error) {{
                if (error && error.name === 'AbortError') {{
                  // User clicked Stop during the POST — cleanup already handled in smxAbortActiveTurn
                  return false;
                }}
                console.error("Error processing chat:", error);
              }} finally {{
                  const big = document.getElementById('loading-spinner');
                  if (big) big.style.display = 'none';

                  // If we’re streaming, DO NOT reset yet — the stream handlers will.
                 queueMicrotask(() => {{ if (!window.__smxEvt) {{ smxThinkingOff?.(); smxRestoreSubmitArrow?.(); 
                 window.__smxBusy = false; }} }});

                  window.__smxPostAbort = null;
                }}
              return false;
            }}

            // Delegated bindings that survive innerHTML swaps
            // 1) Intercept submits from #chat-form
            // 1) Intercept submits from #chat-form
            document.addEventListener('submit', function(ev){{
              if (ev.target && ev.target.id === 'chat-form') {{
                ev.preventDefault();

                const af = document.getElementById('action-field');
                const actionVal = af ? af.value : 'submit_query';
                const submitter = (ev && ev.submitter) || document.activeElement;
                const isClear = (actionVal === 'clear' || actionVal === 'clear_chat' ||
                                (submitter && (submitter.name === 'clear' || submitter.id === 'clear')));

                // ALWAYS use non-stream path for Clear actions
                // if (isClear) return submitChat(ev);

                // Otherwise: stream if enabled
                return submitChat(ev);
              }}
            }});
            
            // 2) Enter to send (Shift+Enter for newline) - route through a single submit path
            document.addEventListener('keydown', function(ev) {{
              if (ev.key === 'Enter' && !ev.shiftKey &&
                  ev.target && ev.target.matches('#chat-form textarea[name="user_query"]')) {{
                ev.preventDefault();
                const af = document.getElementById('action-field');
                if (af) af.value = 'submit_query';   // make intent explicit
                const form = document.getElementById('chat-form');
                if (form) form.requestSubmit();
              }}
            }});
            // 3) Ensure checkInput exists globally
            if (typeof window.checkInput !== 'function') {{
              window.checkInput = function(textarea) {{
                var submitBtn = document.getElementById("submit-button");
                if (!submitBtn) return;
                if ((textarea.value || "").trim() === "") {{
                  submitBtn.disabled = true; submitBtn.style.opacity = "0.5";
                }} else {{
                  submitBtn.disabled = false; submitBtn.style.opacity = "1";
                }}
              }};
            }}

            // ************** Assistant Placeholder For Stream *******************
            // NOTE: This function's logic was simple and has been merged directly into
            function smxCreateAssistantPlaceholder() {{}}
            // ********** Assistant Placeholder For Stream ***************

            function smxShowProvisionalUserBubble(text) {{
              try {{
                var ch = document.getElementById('chat-history');
                if (!ch) return;

                // Build a temporary user bubble that looks like your normal one
                var wrap = document.createElement('div');
                wrap.className = 'chat-message user provisional';
                
                // --- CHANGE 3: Add styles and icon to the user's provisional bubble ---
                wrap.style.display = 'flex';
                wrap.style.flexDirection = 'column';
                wrap.style.alignItems = 'flex-start';

                var iconSpan = document.createElement('span');
                iconSpan.style.alignSelf = 'flex-end';
                iconSpan.innerHTML = window.SMX_USER_ICON;
                wrap.appendChild(iconSpan);

                var p = document.createElement('p');
                p.textContent = text || '';
                wrap.appendChild(p);
                // ----------------------------------------------------------------------
                
                ch.appendChild(wrap);

                // Keep viewport pinned to the newest message
                wrap.scrollIntoView({{ behavior: 'smooth', block: 'end' }});
              }} catch (e) {{
                console.error('provisional bubble error', e);
              }}
            }}
          </script>
        """

        close_eda_btn_js = """
        <script>
          function closeEdaPanel() {
              fetch('/clear_eda_panel', { method: 'POST' })
                  .then(response => response.json())
                  .then(data => {
                      // Remove or empty the EDA panel from the DOM
                      const eda = document.getElementById('system-output-container');
                      if (eda) eda.remove();  // or: eda.innerHTML = '';
                  });
          }
        </script>
        """ 

        stream_js = """
          <script>
            // ----- bottom-lock helpers (cross-browser) -----
            const DOC = document.scrollingElement || document.documentElement;

            function isPinnedToBottom() {
              // Are we within 6px of the bottom?
              return (DOC.scrollHeight - (DOC.scrollTop + window.innerHeight)) <= 6;
            }

            let streaming = false;
            let lockScrollDuringStream = false;
            let rafScheduled = false;

            function lockToBottom() {
              if (!streaming || !lockScrollDuringStream) return;
              if (rafScheduled) return;
              rafScheduled = true;
              requestAnimationFrame(() => {
                // padding-bottom keeps content visible above the widget
                window.scrollTo({ top: DOC.scrollHeight, behavior: 'auto' });
                rafScheduled = false;
              });
            }

            // Update the lock if the user scrolls mid-stream
            window.addEventListener('scroll', () => {
              if (!streaming) return;
              // If the user scrolls up, release the lock; if they return to bottom, re-lock
              lockScrollDuringStream = isPinnedToBottom();
            }, { passive: true });

            (function smxInjectThinkingCss() {
              if (document.getElementById('smx-thinking-style')) return;
              const style = document.createElement('style'); style.id = 'smx-thinking-style';
              style.textContent = `
              .chat-message.bot.streaming .thinking-dots {
                display:inline-flex; gap:3px; margin-left:6px; vertical-align:middle;
              }
              .chat-message.bot.streaming .thinking-dots span {
                width:6px; height:6px; border-radius:50%;
                opacity:.25; background: currentColor;
                animation: smxDots 1s infinite ease-in-out;
              }
              .chat-message.bot.streaming .thinking-dots span:nth-child(2){ animation-delay:.2s }
              .chat-message.bot.streaming .thinking-dots span:nth-child(3){ animation-delay:.4s }
              @keyframes smxDots {
                0%,80%,100% { opacity:.25; transform:translateY(0) }
                40%        { opacity:1;   transform:translateY(-2px) }
              }`;
              document.head.appendChild(style);
            })();

            // Global handle so Clear/Stop can close it later
            window.__smxEvt = null;

            function smxMakeStreamBubble() {
              const host = document.getElementById('chat-history');
              if (!host) return { bubble: null, targetP: null, head: null, dots: null };

              const bubble = document.createElement('div');
              bubble.className = 'chat-message bot streaming';

              const head = document.createElement('span');
              head.className = 'bot-head';
              head.innerHTML = (window.SMX_BOT_ICON || '');

              const dots = document.createElement('span');
              dots.className = 'thinking-dots';
              dots.innerHTML = '<span></span><span></span><span></span>';

              head.appendChild(dots);
              bubble.appendChild(head);

              const targetP = document.createElement('p');
              targetP.className = 'stream-target';
              bubble.appendChild(targetP);

              host.appendChild(bubble);
              return { bubble, targetP, head, dots };
            }

            function startStream() {
              // Close any prior stream
              try { if (window.__smxEvt) window.__smxEvt.close(); } catch(_) {}
              window.__smxEvt = null;

              let bubble, targetP, head, dots;
              // Keep the live typing caret visible above the sticky widget
              function ensureLiveInView(targetNode) {
                // Prefer bottom-lock; only nudge when not pinned but dangerously low
                if (lockScrollDuringStream) {
                  lockToBottom();
                  return;
                }
                // Fallback: if the caret is about to be hidden under the widget, nudge once
                try {
                  const wc = document.getElementById('widget-container');
                  const wcH = wc ? wc.getBoundingClientRect().height : 0;
                  const node = targetNode || document.querySelector('#chat-history .chat-message:last-child');
                  if (!node) return;
                  const rect = node.getBoundingClientRect();
                  const usableBottom = window.innerHeight - wcH - 12; // breathing room
                  if (rect.bottom > usableBottom) {
                    // Single RAF-batched nudge, not per character
                    if (!rafScheduled) {
                      rafScheduled = true;
                      requestAnimationFrame(() => {
                        window.scrollTo({ top: DOC.scrollTop + (rect.bottom - usableBottom), behavior: 'auto' });
                        rafScheduled = false;
                      });
                    }
                  }
                } catch (_) {}
              }
              if (window.__smxPreBubble && window.__smxPreBubble.bubble) {
                ({ bubble, targetP, head, dots } = window.__smxPreBubble);
                window.__smxPreBubble = null;
              } else {
                ({ bubble, targetP, head, dots } = smxMakeStreamBubble());
              }
              if (!bubble || !targetP) return;

              // --- Typewriter state (per turn) ---
              let gotFirstChunk = false;
              const q = [];              // queue of chars to type
              let twRunning = false;
              const TYPE_DELAY_MS = 14;  // feel: 10-18ms is nice
              const CHARS_PER_TICK = 3;  // smoothness vs CPU

              function twKick() {
                if (twRunning) return;
                twRunning = true;
                function step() {
                  let n = 0;
                  while (n < CHARS_PER_TICK && q.length) {
                    targetP.textContent += q.shift();
                    n++;
                  }
                  ensureLiveInView();
                  if (q.length) {
                    setTimeout(step, TYPE_DELAY_MS);
                  } else {
                    twRunning = false;
                  }
                }
                setTimeout(step, TYPE_DELAY_MS);
              }
              // --- end typewriter ---

              // Open SSE
              const es = new EventSource('/process_chat?stream=1');
              // when stream begins:
              streaming = true;
              lockScrollDuringStream = isPinnedToBottom();
              lockToBottom();
              
              window.__smxEvt = es;

              es.onmessage = (e) => {
                let msg;
                try { msg = JSON.parse(e.data); } catch { msg = { event:'chunk', delta:String(e.data||'') }; }
                if (!msg || !msg.event) return;
                if (msg.event === 'started') return;

                if (msg.event === 'chunk') {
                  if (!gotFirstChunk) {
                    gotFirstChunk = true;
                    // Remove the thinking dots on first token
                    if (dots && dots.parentNode) dots.parentNode.removeChild(dots);
                    // after adding chars to targetP.textContent...
                    lockToBottom();
                    ensureLiveInView(targetP);
                  }
                  const delta = msg.delta || '';
                  for (let i = 0; i < delta.length; i++) q.push(delta[i]);
                  twKick();
                  return;
                }

                if (msg.event === 'done' || msg.event === 'error') {
                  // 1) Close the stream and mark it inactive
                  try { es.close(); } catch(_) {}
                  window.__smxEvt = null;

                  // 2a) IMMEDIATE UI RESET — do not wait on any network calls
                  queueMicrotask(() => {
                    const big = document.getElementById('loading-spinner');
                    if (big) big.style.display = 'none';
                    smxThinkingOff?.();
                    smxRestoreSubmitArrow?.();
                    window.__smxBusy = false;
                  });

                  // 2b) Close the sidebar if it’s open (mobile-first)
                  // Remove the body flag used by your CSS: body.sidebar-open …
                  if (document.body.classList.contains('sidebar-open')) {
                    // Optional: limit to small screens; remove the if() to always close
                    if (window.matchMedia('(max-width: 1024px)').matches) {
                      document.body.classList.remove('sidebar-open');
                    }
                  }
                  // Also clear a widget/side panel “open” class if present
                  const sbc = document.getElementById('sidebar-container');
                  if (sbc && sbc.classList) sbc.classList.remove('open');

                  // 3) Finish any residual typed chars
                  if (q.length) {
                    targetP.textContent += q.join('');
                    q.length = 0;
                  }

                  // 4) Replace the “typed” paragraph with structured HTML if we have any
                  const raw = (msg.raw_answer || msg.raw || msg.answer || '').trim();
                  const looksHtml = /<[^>]+>/.test(raw);
                  if (looksHtml) {
                    const structured = document.createElement('div');
                    structured.className = 'smx-structured';
                    structured.innerHTML = raw;
                    targetP.replaceWith(structured);
                  }

                  bubble.classList.remove('streaming');

                  // 5) Fire-and-forget sync so panes stay accurate (UI already reset above)
                  fetch('/sync_after_stream', { 
                    method:'POST', 
                    credentials:'same-origin',
                    headers: { 'Content-Type':'application/json' },
                    body: JSON.stringify({ sidebar_state: (localStorage.getItem('sidebarState') || 'closed') })
                  })
                  .then(r => r.json())
                  .then(({chat_html, sidebar_html, sidebar_state}) => { /* non-fatal; UI is already correct */ });

                  try {
                    lockToBottom();          // one last snap, in case of late reflow
                    ensureLiveInView();      // safety nudge
                  } catch(_) {}
                  return;
                }

              };
              es.onerror = () => {
                try { es.close(); } catch(_) {}
                window.__smxEvt = null;
                const big = document.getElementById('loading-spinner');
                if (big) big.style.display = 'none';
                smxThinkingOff?.();
                smxRestoreSubmitArrow?.();
                window.__smxBusy = false;
              };
            }
          </script>
        """

        home_page_html = f"""      
        {head_html()}
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <style>
            /* Match /dashboard font scale */
            :root{{
              --smx-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
                          Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
              --smx-font-size: 16px;   /* >=16px prevents iOS zoom */
              --smx-line: 1.55;
            }}
            html{{ -webkit-text-size-adjust: 100%; }}
            body{{ font-family: var(--smx-font); font-size: var(--smx-font-size); line-height: var(--smx-line); }}
          </style>
          <style>
            /* Container sizing & equal gutters */
            .chat-container{{
              max-width: 820px;
              margin-inline: auto;
              padding-inline: 12px;
              box-sizing: border-box;
            }}

            /* Bubbles never overflow the viewport width */
            .chat-messages{{
              overflow-wrap: anywhere;
              word-break: break-word;
              padding-bottom: 84px; /* room for sticky footer input */
            }}

            /* Sticky footer input area (safe on iOS address-bar) */
            .chat-footer{{
              position: sticky;
              bottom: 0;
              background: #fff;
              border-top: 1px solid #e5e7eb;
              padding: 10px 0;
            }}

            /* iOS zoom fix: input/textarea >= 16px, full-width */
            .chat-footer textarea,
            .chat-footer input[type="text"],
            .chat-footer input[type="search"]{{
              font-size: 16px !important;          /* critical: prevents iOS zoom */
              line-height: 1.35;
              width: 100%;
              min-height: 48px;
              padding: 10px 12px;
              border: 1px solid #d0d7de;
              border-radius: 10px;
              outline: none;
              box-sizing: border-box;
              -webkit-appearance: none;
            }}

            /* Send button: large enough for touch, matches /dashboard scale */
            .chat-footer .send-btn{{
              font-size: 16px;
              padding: 10px 14px;
              border-radius: 10px;
            }}

            /* Tighten tiny screens */
            @media (max-width: 480px){{
              .chat-container{{ padding-inline: 10px; }}
              .chat-footer .send-btn{{ width: 100%; margin-top: 8px; }}
            }}

            /* Optional: hide textarea resize grabber on mobile for clean UI */
            @supports (-webkit-touch-callout: none){{
              .chat-footer textarea{{ resize: none; }}
            }}
          </style>
          <style>
            /* Desktop: push chat-history a little more than the base shift */
            body.sidebar-open #chat-history{{
              transform: translateX(calc(var(--sidebar-shift, var(--sidebar-w)) - 90px));
            }}
            @media (min-width: 901px) and (max-width: 1200px) {{
              #chat-history {{
                max-width: 92vw;  
              }}
              body.sidebar-open #chat-history {{
               /* transform: translateX(4.5vw);  tweak 3-6vw to taste */
                transform: translateX(calc(var(--sidebar-shift, var(--sidebar-w)) - 4rem));
                max-width: 80vw;
              }}
            }}
            @media (max-width: 900px){{
              #chat-history {{
                width: 80vw;       
                max-width: 80vw;    /* overrides desktop width */
                margin-left: auto;  /* keep it centered */
                margin-right: auto;
                margin-top: 0;
              }}
              body.sidebar-open #chat-history{{
                transform: translateX(calc(var(--sidebar-shift, var(--sidebar-w)) - 30px));
              }}
            }}
            form#chat-form, div#widget-container {{
              background: none;
            }}
            /* Typewriter look during streaming only */
            .chat-message.bot.streaming .stream-target{{
              font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
              font-variant-ligatures: none;
              white-space: pre-wrap;      /* keep line breaks as they stream */
              letter-spacing: 0.01em;     /* subtle spacing for “typed” feel */
            }}

            /* Blinking caret visible only while streaming */
            .chat-message.bot.streaming .stream-target::after{{
              content: '▍';
              display: inline-block;
              margin-left: 2px;
              opacity: 0.8;
              animation: smx-caret 1s steps(1, end) infinite;
            }}

            /* Respect reduced-motion preferences */
            @media (prefers-reduced-motion: reduce){{
              .chat-message.bot.streaming .stream-target::after{{
                animation: none;
              }}
            }}

            @keyframes smx-caret{{
              0%, 100% {{ opacity: 0; }}
              50%      {{ opacity: 1; }}
            }}
          </style>
          <style id="smx-structured-style">
            /* Container for structured bot content */
            .chat-message.bot .smx-structured {{
              margin-top: 4px;
              line-height: 1.55;
            }}

            /* Headings */
            .chat-message.bot .smx-structured h1,
            .chat-message.bot .smx-structured h2,
            .chat-message.bot .smx-structured h3 {{
              margin: 8px 0 4px;
              font-weight: 700;
            }}
            .chat-message.bot .smx-structured h1 {{ font-size: 1.15rem; }}
            .chat-message.bot .smx-structured h2 {{ font-size: 1.06rem; }}
            .chat-message.bot .smx-structured h3 {{ font-size: 1.0rem; }}

            /* Paragraphs */
            .chat-message.bot .smx-structured p {{
              margin: 6px 0;
            }}

            /* Lists */
            .chat-message.bot .smx-structured ul,
            .chat-message.bot .smx-structured ol {{
              margin: 6px 0 6px 20px;
              padding: 0;
            }}
            .chat-message.bot .smx-structured li {{ margin: 3px 0; }}

            /* Code block */
            .chat-message.bot .smx-structured pre {{
              margin: 8px 0;
              padding: 8px 10px;
              border-radius: 8px;
              overflow: auto;
              font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
            }}

            /* While streaming we still use a live typing box */
            .chat-message.bot.streaming .stream-target {{
              white-space: pre-wrap;   /* so newlines render during typing */
            }}
          </style>
          <style>
            /* --- Stop-in-a-ring spinner --- */
            #submit-button.stop {{
              display: inline-flex;
              align-items: center;
              justify-content: center;
            }}

            .btn-spinner-wrap {{
              position: relative;
              display: inline-block;
              width: 1.25rem;   /* tweak if you want a bigger ring */
              height: 1.25rem;
              vertical-align: middle;
            }}

            .btn-spinner-ring {{
              position: absolute;
              inset: 0;
              border-radius: 50%;
              border: 2px solid currentColor;
              border-right-color: transparent;   /* creates the “gap” */
              border-bottom-color: transparent;  /* optional: makes it 2-quadrant spinner */
              animation: smxSpin 0.8s linear infinite;
              box-sizing: border-box;
            }}

            .btn-stop {{
              position: absolute;
              inset: 0;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 0.7rem; /* slightly smaller so the ring is visible */
              line-height: 1;
            }}

            @keyframes smxSpin {{
              to {{ transform: rotate(360deg); }}
            }}
          </style>
          <style>
            /* Force strict top→bottom stacking and align sides without floats */
            #chat-history{{
              display: flex;
              flex-direction: column;
              align-items: stretch;     /* base */
            }}
            #chat-history .chat-message {{
              float: none !important;   /* defeat old float rules */
              clear: none !important;
              align-self: flex-start;    /* bot/assistant */
              max-width: 70%;            /* keep your bubble width cap */
            }}
            #chat-history .chat-message.user {{
              align-self: flex-end;      /* user on the right */
            }}
          
            /* Hover tools for user bubbles */
            #chat-history .chat-message {{ position: relative; }}
            #chat-history .chat-message.user .bubble-tools{{
              position: absolute;
              right: 10px;
              bottom: 8px;
              display: none;
              gap: 6px;
              align-items: center;
              padding: 2px 4px;
              background: rgba(255,255,255,0.85);
              border: 1px solid #ddd;
              border-radius: 8px;
              box-shadow: 0 2px 6px rgba(0,0,0,.08);
            }}
            #chat-history .chat-message.user:hover .bubble-tools{{ display: inline-flex; }}

            /* Buttons */
            .bubble-tools button{{
              all: unset;
              cursor: pointer;
              line-height: 1;
              padding: 2px 4px;
              border-radius: 6px;
              font-size: 0.9rem;
            }}
            .bubble-tools button:hover{{
              background: rgba(0,0,0,.06);
            }}
            body {{
              padding-bottom:0;
            }}
          </style>

        <body>
          {nav_html}
         
          <button
            id="sidebar-toggle-btn"
            title="Open sidebar"
            data-icon-open="{url_for('static', filename='icons/svg_497526.svg')}"
            data-icon-close="{url_for('static', filename='icons/svg_497528.svg')}"
          >
            <img
              id="sidebar-toggle-icon"
              src="{url_for('static', filename='icons/svg_497526.svg')}"
              alt="Toggle Sidebar"  
              style="width:1.4rem; height:1.8rem;"
            />
          </button>

          <div id="sidebar-container">{sidebar_html}</div>         
          <div id="loading-spinner" style="display:none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000;">
              <div class="spinner" style="border: 8px solid #f3f3f3; border-top: 8px solid {smx.theme['nav_background']}; border-radius: 50%; width: 60px; height: 60px; animation: spin 1s linear infinite;">
              </div>
          </div>
          <div id="chat-history">{chat_html}</div>
          <div id="composer-spacer" style="height:0"></div>
          <div id="widget-container">{widget_html}</div>

          {scroll_and_toggle_js}
          {close_eda_btn_js}
          {new_chat_js}
          {stream_js}
          <script>
            // Force the stream-aware submitChat to be the one that runs.
            if (!window.__smxSubmitPinned) {{
              window.__smxSubmitPinned = true;
              window.submitChat = window.submitChat; // keeps name-based handlers working
              // If you prefer, you can also reassign window.submitChat = <the new impl>
              // but as long as the new one was defined last, this pin stops later overwrites.
            }}
          </script>
          <script src="{ url_for('static', filename='js/sidebar.js') }"></script>
          <script>
            (function(){{
                const ta = document.getElementById('user_query');
                if (!ta) return;

                const chatHistory = document.getElementById('chat-history');
                const sidebar     = document.getElementById('sidebar');

                const isPhone = () => window.matchMedia('(max-width:900px)').matches;
                const capPx   = () => Math.floor(window.innerHeight * (isPhone() ? 0.18 : 0.28));

                function fit(){{
                  ta.style.maxHeight = capPx() + 'px';     // keep CSS + JS in sync
                  ta.style.height = 'auto';
                  ta.style.height = Math.min(ta.scrollHeight, capPx()) + 'px';
                  const wc = document.getElementById('widget-container');
                  const ch = document.getElementById('chat-history');
                  if (wc) {{
                    const h = wc.offsetHeight || 0;
                    document.documentElement.style.setProperty('--composer-h', h + 'px');
                    if (ch) ch.style.paddingBottom = (h + 16) + 'px';   // belt & braces
                  }}
                }}

                // Input typing
                ta.addEventListener('input', fit);

                // True viewport changes
                window.addEventListener('resize', fit);
                window.addEventListener('orientationchange', fit);

                // Any size/layout changes to the textarea OR its containers
                // Any size/layout changes to the textarea OR its containers
                if ('ResizeObserver' in window) {{
                  const ro = new ResizeObserver(fit);
                  ro.observe(ta);
                  if (chatHistory) ro.observe(chatHistory);
                  // re-query here (wc was local inside fit())
                  const wcEl = document.getElementById('widget-container');
                  if (wcEl) ro.observe(wcEl); // watch the composer itself
                  ro.observe(document.documentElement);
                }}

                // Detect sidebar open/close (class change) and CSS transitions
                if ('MutationObserver' in window && sidebar) {{
                  new MutationObserver(fit).observe(sidebar, {{ attributes:true, attributeFilter:['class'] }});
                  sidebar.addEventListener('transitionend', fit, true);
                }}

                // First render
                fit();
              }})();
          </script>
          <script>
              // Add the “Copy / Edit” toolbar to user bubbles (idempotent)
              function smxDecorateUserBubbles(){{
                const host = document.getElementById('chat-history');
                if (!host) return;
                host.querySelectorAll('.chat-message.user').forEach(b => {{
                  if (b.dataset.tools === '1') return; // already decorated
                  b.dataset.tools = '1';

                  const tools = document.createElement('div');
                  tools.className = 'bubble-tools';
                  tools.innerHTML = `
                    <button class="bt-copy" title="Copy">📋</button>
                    <button class="bt-edit" title="Edit">✏️</button>
                  `;
                  b.appendChild(tools);
                }});
              }}

              // Handle copy / edit via event delegation (works across redraws)
              document.addEventListener('click', async (e) => {{
                const copyBtn = e.target.closest('.bubble-tools .bt-copy');
                if (copyBtn){{
                  const bubble = copyBtn.closest('.chat-message.user');
                  const p = bubble && bubble.querySelector('p');
                  const text = p ? p.innerText : '';
                  try {{
                    await navigator.clipboard.writeText(text);
                    copyBtn.title = 'Copied!';
                    setTimeout(() => copyBtn.title = 'Copy', 900);
                  }} catch (_) {{
                    // Fallback: select + alert
                    alert('Copied:\n\n' + text);
                  }}
                  return;
                }}

                const editBtn = e.target.closest('.bubble-tools .bt-edit');
                if (editBtn){{
                  const bubble = editBtn.closest('.chat-message.user');
                  const p = bubble && bubble.querySelector('p');
                  const text = p ? p.innerText : '';
                  const ta = document.getElementById('user_query');
                  if (ta){{
                    ta.value = text;
                    if (typeof window.checkInput === 'function') window.checkInput(ta);
                    ta.focus();
                    // place cursor at the end
                    ta.selectionStart = ta.selectionEnd = ta.value.length;
                    // scroll composer into view
                    document.getElementById('widget-container')?.scrollIntoView({{ behavior: 'smooth', block: 'end' }});
                  }}
                  return;
                }}
              }});

              // Run once on load…
              smxDecorateUserBubbles();

              // …and re-run automatically whenever chat history changes
              (function(){{
                const host = document.getElementById('chat-history');
                if (!host || !('MutationObserver' in window)) return;
                const mo = new MutationObserver(() => smxDecorateUserBubbles());
                mo.observe(host, {{ childList: true, subtree: true }});
              }})();
          </script>
        </body>
        </html>"""
        return render_template_string(home_page_html)

        # ---- Shared widget + action preprocessor (call from both routes) ------------
    

    @smx.app.route('/favicon.ico')
    def _serve_favicon():
        from flask import send_from_directory
        import os
        # If you set an absolute URL (https://...), let the <link> tags handle it.
        # This handler just covers the /favicon.ico direct request.
        icon = smx.favicon or "/static/icons/favicon.ico"
        if icon.startswith("/static/"):
            icons_dir = os.path.join(_CLIENT_DIR, "static", "icons")
            return send_from_directory(icons_dir, os.path.basename(icon))
        # Fall back to the packaged default
        icons_dir = os.path.join(_CLIENT_DIR, "static", "icons")
        return send_from_directory(icons_dir, "favicon.ico")


    @smx.app.route("/sync_after_stream", methods=["POST"])
    def sync_after_stream():
        """Synchronise sidebar snapshots after a streamed turn has finished."""
        
        # 0) Ensure we are pointing at the chat visible in the pane
        try:
            cur = session.get("current_session")
            if cur and cur.get("id"):
                if session.get("active_chat_id") != cur["id"]:
                    session["active_chat_id"] = cur["id"]
                    session.modified = True
        except Exception:
            pass

        # 1) Pull the canonical, up-to-date history saved by set_chat_history()
        hist = smx.get_chat_history() or []
        data = (request.get_json(silent=True) or {})
        state = data.get("sidebar_state")
        if state in ("open", "closed"):
            session["sidebar_state"] = state
        session["chat_history"] = hist

        if "current_session" in session:
            session["current_session"]["history"] = session["chat_history"]
            past = session.get("past_sessions", [])
            for s in past:
                if s.get("id") == session["current_session"]["id"]:
                    s["history"] = session["chat_history"]
                    break
            session["past_sessions"] = past

        session.modified = True

        # 3) Return updated panes so the UI can refresh safely
        chat_html = render_chat_history(smx)
        sidebar_html = _render_session_sidebar()
        return jsonify({
            "chat_html": chat_html,
            "sidebar_html": sidebar_html,
            "sidebar_state": session.get("sidebar_state", "closed")
        })


    @smx.app.route("/process_chat", methods=["GET","POST"])
    def process_chat():
        
        # --- Guard rail: keep active id in lockstep with the visible "Current" chat ---
        try:
            cur = session.get("current_session")
            if cur and cur.get("id"):
                if session.get("active_chat_id") != cur["id"]:
                    session["active_chat_id"] = cur["id"]
                    session.modified = True
        except Exception:
            pass

        # 0) Clear is handled here and returns immediately
        action = (request.form.get("action") or "").strip().lower()
        if action in ("clear", "clear_chat"):
            try:
                smx.clear_chat_history()
            except Exception:
                session["chat_history"] = []
            try:
                sid = smx.get_session_id()
                smx.clear_user_chunks(sid)
            except Exception:
                pass
            session.modified = True
            return jsonify({
                "chat_html": render_chat_history(smx),
                "system_output_buffer_html": (smx.system_output_buffer or "").strip(),
                "system_output_html": smx.get_plottings() if hasattr(smx, "get_plottings") else ""
            })

        # 1) Minimal widget preprocessing (seed values / files; DO NOT prepare stream args)
        for key, widget in smx.widgets.items():
            wtype = widget.get("type")
            if wtype == "text_input":
                session[key] = request.form.get(key, session.get(key, widget.get("placeholder","")))
            elif wtype == "file_upload":
                uploaded = request.files.getlist(key)
                if uploaded:
                    sid = smx.get_session_id()
                    total_chunks = 0
                    for f in uploaded:
                        try:
                            raw = f.read()
                            if not raw: continue
                            reader = PdfReader(BytesIO(raw))
                            text = "".join((page.extract_text() or "") for page in reader.pages)
                            chunks = recursive_text_split(text)
                            smx.add_user_chunks(sid, chunks)
                            total_chunks += len(chunks)
                        except EmptyFileError:
                            pass
                        except Exception as ex:
                            smx.error(f"Failed to process uploaded file '{getattr(f,'filename','')}': {ex}")
                    if action == key:
                        smx.success(f"Uploaded {len(uploaded)} file(s); indexed {total_chunks} chunks.") if total_chunks else smx.warning("No valid content found in uploaded file(s).")
            elif wtype == "button":
                if key in request.form and widget.get("callback"):
                    try:
                        widget["callback"]()     # <- this calls create_conversation(...), per the plan
                    except Exception as cb_ex:
                        smx.error(f"Button callback '{key}' failed: {cb_ex}")
            elif wtype == "dropdown":
                val = request.form.get(key)
                if val is not None:
                    widget["value"] = val

        # 2) Branch: non-stream vs stream
        stream_flag = (request.form.get("stream") or request.args.get("stream") or "").lower()
        is_stream = stream_flag in ("1", "true", "yes")

        if not is_stream:
            # Non-stream: create_conversation() already ran and updated state. Just mirror UI.
            return jsonify({
                "chat_html": render_chat_history(smx),
                "system_output_buffer_html": (smx.system_output_buffer or "").strip(),
                "system_output_html": smx.get_plottings() if hasattr(smx, "get_plottings") else ""
            })

        # 3) Stream: read prepared args from smx
        try:
            prepared = smx.get_stream_args()
        except Exception:
            prepared = getattr(smx, "stream_args", None)

        if not prepared:
            return jsonify({"error": "no_stream_args", "message": "stream mode is not enambled."})

        sa = dict(prepared)
        if "history" not in sa and "conversations" in sa:
            sa["history"] = sa.pop("conversations")
        sa.pop("sources", None)  # not needed by provider

        def _delta_text(piece):
            # 1) plain strings/bytes
            if isinstance(piece, str):
                return piece
            if isinstance(piece, bytes):
                try:
                    return piece.decode("utf-8", "ignore")
                except Exception:
                    return ""

            # 2) dict-like payloads from different providers
            if isinstance(piece, dict):
                # common direct keys
                for k in ("delta", "content", "text", "output_text"):
                    v = piece.get(k)
                    if isinstance(v, str):
                        return v
                    if isinstance(v, bytes):
                        return v.decode("utf-8", "ignore")
                    if isinstance(v, dict):
                        for kk in ("content", "text", "output_text"):
                            vv = v.get(kk)
                            if isinstance(vv, str):
                                return vv
                            if isinstance(vv, bytes):
                                return vv.decode("utf-8", "ignore")

                # OpenAI-sdk-style: {"choices":[{"delta":{"content":"..."}}, ...]}
                ch = piece.get("choices")
                if isinstance(ch, list) and ch:
                    d = (ch[0] or {}).get("delta") or {}
                    c = d.get("content")
                    if isinstance(c, str):
                        return c
                    if isinstance(c, bytes):
                        return c.decode("utf-8", "ignore")

                # Gemini-style: {"candidates":[{"content":{"parts":[{"text":"..."}]}}]}
                cand = piece.get("candidates")
                if isinstance(cand, list) and cand:
                    content = (cand[0] or {}).get("content") or {}
                    parts = content.get("parts") or []
                    if parts and isinstance(parts[0], dict):
                        t = parts[0].get("text")
                        if isinstance(t, str):
                            return t
                        if isinstance(t, bytes):
                            return t.decode("utf-8", "ignore")

            return ""


        # --- streaming HTML strip helpers (new) ---
        def _strip_tags_streaming(delta: str, state: dict) -> str:
            """
            Remove HTML tags across chunk boundaries.
            state keeps 'in_tag' between calls.
            """
            out = []
            in_tag = state.get("in_tag", False)
            for ch in delta:
                if in_tag:
                    if ch == ">":
                        in_tag = False
                    continue
                if ch == "<":
                    in_tag = True
                    continue
                out.append(ch)
            state["in_tag"] = in_tag
            return "".join(out)
          # --- end helpers ---

        # routes.py — inside stream_and_forward(generator)
        def stream_and_forward(generator):
            collected_clean = []
            collected_raw = []                     # NEW: keep raw with tags
            strip_state = {"in_tag": False}

            try:
                yield "data: " + json.dumps({"event": "started"}) + "\n\n"
                for piece in generator:
                    delta_raw = _delta_text(piece) or ""                  # as produced by LLM
                    if not delta_raw:
                        continue
                    delta_clean = delta_raw  # _strip_tags_streaming(delta_raw, strip_state)  # existing helper

                    collected_raw.append(delta_raw)
                    if delta_clean:
                        collected_clean.append(delta_clean)
                        yield "data: " + json.dumps({
                            "event": "chunk",
                            "delta": delta_clean,     # what we type out live
                            "raw": delta_raw          # what we'll use to structure at the end
                        }) + "\n\n"

            except GeneratorExit:
                smx.info("Client aborted the stream.")
            except Exception as e:
                smx.error(f"Stream error: {e}")
                yield "data: " + json.dumps({"event": "error", "error": str(e)}) + "\n\n"
            finally:
                final_clean = "".join(collected_clean).strip()
                final_raw   = "".join(collected_raw).strip()
                cancelled = _stream_cancelled.pop(smx.get_session_id(), False)

                try:
                    persist_text = (final_raw or final_clean)
                    if persist_text:
                        if cancelled and not persist_text.endswith(" (partial)"):
                            persist_text = persist_text + " (partial)"
                        hist = smx.get_chat_history() or []
                        hist.append(("Bot", persist_text))
                        smx.set_chat_history(hist)
                except Exception as e:
                    smx.warning(f"Could not persist streamed answer: {e}")

                # Let the client know whether we finished or cancelled
                if not cancelled:
                    yield "data: " + json.dumps({
                        "event": "done",
                        "answer": final_clean,
                        "raw_answer": final_raw
                    }) + "\n\n"
                else:
                    yield "data: " + json.dumps({ "event": "cancelled" }) + "\n\n"

        try:
            gen = smx.process_query_stream(**sa)   # <- yes, this is where streaming is used
        except Exception as e:
            smx.error(f"Could not start stream: {e}")
            return jsonify({"error": "stream_start_failed", "message": str(e)})

        response = Response(stream_with_context(stream_and_forward(gen)),
                    mimetype="text/event-stream")
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"    # Nginx / some proxies
        response.headers["Connection"] = "keep-alive"
        return response

    @smx.app.route("/cancel_stream", methods=["POST"])
    def cancel_stream():
        sid = smx.get_session_id()
        _stream_cancelled[sid] = True  # flag for the active generator

        # Keep rollback only for anonymous users; logged-in keeps partials.
        if not session.get("user_id"):
            try:
                hist = smx.get_chat_history() or []
                if hist and (hist[-1][0] or "").lower() == "bot":
                    hist.pop()
                    smx.set_chat_history(hist)
            except Exception:
                pass

        # Mirror back into cookie session
        session["chat_history"] = smx.get_chat_history() or []
        session.modified = True
        return jsonify({"ok": True})


    @smx.app.route("/load_session", methods=["POST"])
    def load_session():
        # --- Execute "Ending Chat" for the current session ---
        current_history = smx.get_chat_history() or session.get("chat_history", [])
        current_session = session.get(
            "current_session",
            {"id": str(uuid.uuid4()), "title": "Current", "history": []}
        )
        past_sessions = session.get("past_sessions", [])
        exists = any(s["id"] == current_session["id"] for s in past_sessions)

        if current_history:
            if not exists:
                generated_title = smx.generate_contextual_title(current_history)
                current_session["title"] = generated_title
                current_session["history"] = current_history.copy()
                past_sessions.insert(0, current_session)
            else:
                for s in past_sessions:
                    if s["id"] == current_session["id"]:
                        s["history"] = current_history.copy()
                        break
                    
            session["past_sessions"] = past_sessions
            # — Persist the just-ended “Current” chat into chats.db for logged-in users —
            if session.get("user_id"):
                SQLHistoryStore.save(
                    session["user_id"],
                    current_session["id"],
                    current_history,
                    current_session["title"]
                )

        # --- Load the target session (the clicked chat) ---
        sess_id = request.form.get("session_id")
        target = next((s for s in past_sessions if s["id"] == sess_id), None)
        if target:
            # 1) Switch the active chat id FIRST
            session["active_chat_id"] = target["id"]

            # 2) Make a detached copy for current_session (avoid aliasing past_sessions)
            session["current_session"] = {
                "id": target["id"],
                "title": target.get("title", "Untitled"),
                "history": (target.get("history") or []).copy(),
            }

            # 3) Prefer canonical store; fallback to the detached snapshot
            hist = smx.get_chat_history() or session["current_session"]["history"]
            try:
                smx.set_chat_history(hist or [])
            except Exception:
                pass
            session["chat_history"] = (hist or []).copy()
            session.modified = True

        # Return both refreshed panes
        chat_html    = render_chat_history(smx)
        sidebar_html = _render_session_sidebar()
        return jsonify({
            "chat_html":    chat_html,
            "sidebar_html": sidebar_html
        })
    
        
    @smx.app.route("/rename_session", methods=["POST"])    
    def rename_session():
        sid = request.form.get("session_id", "").strip()
        new_title = (request.form.get("new_title") or "").strip() or "Untitled"

        past = session.get("past_sessions", [])
        # update past_sessions
        for s in past:
            if s.get("id") == sid:
                s["title"] = new_title
                break
        session["past_sessions"] = past

        # update current_session if it’s the same id
        if session.get("current_session", {}).get("id") == sid:
            session["current_session"]["title"] = new_title

        # persist if logged in
        try:
            if session.get("user_id"):
                # find history for this chat
                hist = None
                for s in past:
                    if s.get("id") == sid:
                        hist = s.get("history", [])
                        break
                if hist is None and session.get("current_session", {}).get("id") == sid:
                    hist = session["current_session"].get("history", [])
                if hist is not None:
                    SQLHistoryStore.save(session["user_id"], sid, hist, new_title)
        except Exception as e:
            smx.warning(f"rename_session persistence skipped: {e}")

        session.modified = True
        return jsonify({"new_title": new_title})


    @smx.app.route("/delete_session", methods=["POST"])
    def delete_session():
        sid = request.form.get("session_id", "").strip()

        # remove from past_sessions
        past = session.get("past_sessions", [])
        past = [s for s in past if s.get("id") != sid]
        session["past_sessions"] = past

        # if deleting the active chat, reset to a fresh 'Current'
        if session.get("current_session", {}).get("id") == sid:
            session["current_session"] = {"id": str(uuid.uuid4()), "title": "Current", "history": []}
            session["chat_history"] = []
            session["active_chat_id"] = session["current_session"]["id"]


        # delete from DB if logged in
        try:
            if session.get("user_id"):
                SQLHistoryStore.delete(session["user_id"], sid)
        except Exception as e:
            smx.warning(f"delete_session persistence skipped: {e}")

        session.modified = True
        chat_html = render_chat_history(smx)
        return jsonify({"chat_html": chat_html})


    @smx.app.route("/upload_user_file", methods=["POST"])
    def upload_user_file():
        import uuid
        from flask import jsonify
        # Define the upload folder for user files.
        upload_folder = os.path.join(_CLIENT_DIR, "uploads", "user")
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Retrieve list of files uploaded.
        uploaded_files = request.files.getlist("user_files")
        if not uploaded_files:
            return jsonify({"error": "No files provided"}), 400
        
        saved_files = []
        for file in uploaded_files:
            if file.filename == "":
                continue  # Skip files with empty filenames.
            # Create a unique filename.
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            filepath = os.path.join(upload_folder, unique_filename)
            try:
                file.save(filepath)
                saved_files.append(unique_filename)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        if not saved_files:
            return jsonify({"error": "No valid files uploaded"}), 400
        
        return jsonify({"message": "Your files have been uploaded successfully", "uploaded_files": saved_files})

    @smx.app.route("/stream")
    def stream():
        def event_stream():
            while True:
                data = _stream_q.get()        
                yield f"data:{data}\n\n"
        return Response(event_stream(),
                        mimetype="text/event-stream")
    
    @smx.app.route("/clear_eda_panel", methods=["POST"])
    def clear_eda_panel_api():
        smx.set_plottings("")
        return {"success": True}

    @smx.app.route("/widget_event", methods=["POST"])
    def widget_event():
        data = request.get_json()
        key = data.get("widget_key")
        value = data.get("widget_value")
        if key in smx.widgets:
            smx.widgets[key]["value"] = value
            callback = smx.widgets[key].get("callback")
            if callback:
                callback()  # This should call your plotting function!
        # Re-render
        widgets_html = _render_widgets()
        plottings_html = smx.get_plottings()
        return {"system_output_html": plottings_html, "widgets_html": widgets_html}
    
    @smx.app.route("/admin", methods=["GET", "POST"])
    # @superadmin_required
    @admin_required
    def admin_panel():
        bp = Blueprint("admin", __name__)

        # ======== NEW LAYOUT & THEME (drop-in) ========
        admin_layout_css = """
        <style>
          :root{
            --nav-h: 46px;
            --sidenav-w: 160px;
            --sidenav-w-sm: 96px;
            --gap: 12px;
            --gap-lg: 20px;
            --card-bg: #F2F2F2;
            --card-br: 12px;
            --card-shadow: 1px 2px 10px rgba(.1,0,0.1,.4);
            --section-bg: #f7f8fa;
            --section-border: #e6e6e6;
            --text: #1f2937;
            --font-size: 0.7rem;
            --right: 10px;
          }

          /* Fixed left sidebar */
          .admin-sidenav{
            position: fixed;
            top: var(--nav-h);
            left: 0;
            width: var(--sidenav-w);
            height: calc(100vh - var(--nav-h));
            background:#EDEDED;
            border-right:1px solid #e5e5e5;
            padding:10px 8px;
            overflow-y:auto;
            z-index:900;
            box-shadow:0 1px 6px rgba(0,0,0,.06);
            border-radius:0 10px 10px 0;
          }
          .admin-sidenav .snav-title{font-weight:700;font-size:1rem;margin-bottom:6px}
          .admin-sidenav a{
            display:block; padding:6px 8px; margin:4px 0;
            border-radius:8px; text-decoration:none; color:#333; font-size:.8rem;
          }
          .admin-sidenav a:hover,.admin-sidenav a.active{background:#DADADA}

          /* Main content with balanced margins */
          @media (min-width: 901px){
          .admin-main{
            margin-left: calc(var(--sidenav-w) + 3px); /* 1px for the border */
            margin-top: var(--nav-h);
            margin-bottom: 0;
            padding: 0 10px; /* keep your left gutter */
            margin-right: 0 !important;                          /* stop over-wide total */
            width: calc(100% - var(--sidenav-w)) !important;     /* % not vw */
            padding-right: var(--right) !important;              /* keep your right gutter */
            box-sizing: border-box;
            max-width: 100%;
          }
          @media (max-width: 768px) {
            body {
              padding-top: 0;
            }
          }
          /* undo the mobile overflow clamp on large screens */
          html, body, .admin-shell{ overflow-x: visible !important; }
          /* guard against grid items forcing overflow */
          .admin-grid, .admin-shell .card { min-width: 0; }
          }

          /* Section demarcation */
          .section{
            background: var(--section-bg);
            border: 1px solid var(--section-border);
            border-radius: 14px;
            padding: 9px;
            margin-bottom: 26px;
            scroll-margin-top: calc(var(--nav-h) + 10px);
          }
          .section > h2{
            margin: 0 0 8px;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing:.2px;
          }

          /* Grid: 12 columns; dense packing so short cards fill gaps.
            We mostly use span-6 for a neat 2-column desktop baseline. */
          .admin-grid{
            display: grid;
            grid-template-columns: repeat(12, minmax(0, 1fr));
            grid-auto-flow: row dense;
            gap: var(--gap);
            top: 12px;
          }

          /* Card */
          .admin-shell .card{
            background: var(--card-bg);
            border-radius: var(--card-br);
            box-shadow: var(--card-shadow);
            font-size: var(--font-size);
            padding: 10px;
            display: flex;
            flex-direction: column;
            height: 100%;
            width: auto !important; /* suppress legacy inline widths */
          }
          .admin-shell .card h3,.admin-shell .card h4{
            margin:0 0 .6rem; font-size:1.05rem;
          }

          /* Utility spans (desktop baseline: 2 columns = span-6, full = span-12) */
          .span-2  { grid-column: span 2; }
          .span-3  { grid-column: span 3; }
          .span-4  { grid-column: span 4; }
          .span-5  { grid-column: span 5; }
          .span-6  { grid-column: span 6; }
          .span-7  { grid-column: span 7; }
          .span-8  { grid-column: span 8; }
          .span-9  { grid-column: span 9; }
          .span-10  { grid-column: span 10; }
          .span-12 { grid-column: span 12; }

          /* Lists */
          .catalog-list{max-height:120px;overflow:auto;margin:0;padding:0;list-style:none}
          .catalog-list li{
            display:flex;align-items:center;justify-content:space-between;gap:4px;
            padding:1px 2px;border-bottom:1px solid #eee;font-size:.7rem;
            background: #fff;
          }

          /* Forms */
          .admin-shell .card input,
          .admin-shell .card select,
          .admin-shell .card textarea{
            font-size:.8rem;padding:4px 5px;border:1px solid #d9d9d9;border-radius:4px;
          }
          .admin-shell .card button, .admin-shell button, .admin-shell a.button{
            padding:4px 6px;font-size:.8rem;border-radius:5px;border:1px solid gray;cursor:pointer;background:DBDBDB;
          }
          .admin-shell .card button:hover, .admin-shell a.button:hover{
            background:#B0B0B0;color:#fff;border-color:#03159E
          }

          /* .badge { font-size: .7rem; opacity:.8; } */

          /* Popover base */
          .suggestion-popover{
            background:#fff;
            border:1px solid #d0d7de;
            border-radius:.5rem;
            font-size:.875rem;
            box-shadow: 0 4px 16px rgba(0,0,0,.08);
          }
          .suggestion-popover li{ padding:.25rem .5rem; border-radius:.25rem; cursor:pointer; }
          .suggestion-popover li:hover{ background:#f2f8ff; }

          /* Tablet */
          @media (max-width: 1200px){
            .admin-sidenav{ width: var(--sidenav-w); }
            /* reset the right margin so width + margins never exceed the viewport */
            .admin-main{
              margin-left: var(--sidenav-w);
              margin-right: 0;                          /* ← reset */
              width: calc(100% - var(--sidenav-w));     /* ← % not vw */
            }
          }

          /* Mobile */
          @media (max-width: 900px){
            .admin-sidenav{ width: var(--sidenav-w-sm); }
            .admin-main{
              margin-top: var(--nav-h);
              margin-left: calc(var(--sidenav-w-sm) - 1px); /* 1px for the border */
              margin-right: 4px;                               /* ← reset */
              width: calc(100% - var(--sidenav-w-sm));       /* ← % not vw */
              padding: 0;                                  /* keep the visual gutter as padding */
              box-sizing: border-box;
              max-width: 100%;                               /* belt & braces */
            }
          
            /* force all grid items to stack */
            .span-3, .span-4, .span-6, .span-8, .span-12 { grid-column: span 12; }
          }

          /* Global overflow guards (safe, won’t hide useful content inside lists) */
          html, body, .admin-shell { overflow-x: hidden; }

          /* Prevent any inner block from insisting on a width that causes overflow */
          .admin-shell .card, .admin-grid { min-width: 0; }

          /* Delete modal */
          .modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:9999}
          .modal{background:#fff;max-width:420px;width:92%;padding:16px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
          .modal h4{margin:0 0 .5rem}
          .modal .actions{display:flex;gap:.5rem;justify-content:flex-end;margin-top:1rem}
          .btn-danger{background:#b00;color:#fff}
          #del-embed-btn:hover, .del-btn:hover{
            background: red;
            border-radius: 5px;
          }
          .edit-btn:hover {        
            background: green;
            border-radius: 5px;
          }
          
          .info-btn { background: none; border: 1px solid gray; border-radius: 50%; }
          .clr-audits-btn {
            border-radius: 4px;
            background: none;
          }
          .del-role-btn {
            border: 1px solid grey;
            border-radius: 5px;
            margin-left: 4px;
            margin-right: 4px;
            padding: 2px 4px;
            color: #721c24;
            cursor: pointer;
            font-size: 0.8rem;
            text-decoration: none;
          }
          .del-role-btn:hover {
            background: red;
          }
           .clr-audits-btn {
            background: green;
           }
          /* max-height: 320px; */
          .catalog-list {
            overflow-y: auto;
            margin: 0;
            list-style: none;
            border-radius: 2px;
            border: 1px solid gray;
            scrollbar-width: thin;
            scrollbar-color: #cbd5e1 #f1f5f9;
          }
          .catalog-list::-webkit-scrollbar {
            width: 8px;
          }
          .catalog-list::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
          }
          .catalog-list::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
          }
          .catalog-list li {
            font-size: 0.7rem;
            padding: 2px;
            border: 1px solid #E3E3E3;
          }
         .catalog-list li:nth-child(odd) { background: #E9F5E9; }
         .catalog-list li:nth-child(even) { background: #F5F7F7; }

          .catalog-list li:last-child {
            border-bottom: none;
          }
          .catalog-list li:hover {
            background: #D3E3D3;
          }
          #users > div > div > ul > li > form > button {
            font-size: 0.7rem;
            margin: 0;
            padding: 0 !important;
            border: 0.5px dashed gray;
          }
          /* Fix: stop inputs/selects inside cards spilling out (desktop & tablet) */
          .admin-shell .card > * { min-width: 0; }               /* allow flex children to shrink */
          .admin-shell .card input,
          .admin-shell .card select,
          .admin-shell .card textarea {
            display: block;                                     
            width: 100%;                                         
            max-width: 100%;                                    
            box-sizing: border-box;                             
          }
          .admin-shell .card input:not([type="checkbox"]):not([type="radio"]),
          .admin-shell .card select,
          .admin-shell .card textarea{
            display:block;
            width:100%;
            max-width:100%;
            box-sizing:border-box;
          }

          /* Restore normal checkbox/radio sizing & alignment */
          .admin-shell .card input[type="checkbox"],
          .admin-shell .card input[type="radio"]{
            display:inline-block;
            width:auto;
            max-width:none;
            box-sizing:content-box;
            margin:0 .5rem 0 0;
            vertical-align:middle;
          }

          /* Optional: tidy label rows that contain a checkbox */
          .admin-shell .card label.checkbox-row{
            display:inline-flex;
            align-items:center;
            gap:.5rem;
          }
          /* If fixed and its height is constant (e.g., 56px) */
          body { padding-top: 46px; }                 /* make room for the bar */
          .admin-main { margin-top: 0; }              /* remove the manual bump */
          .admin-sidenav {                            /* keep the sidebar aligned */
            top: 56px;
            height: calc(100vh - 56px);
          }
          #del-embed-btn, .del-btn {
            padding: 0;
            font-size: 0.6rem;
            border: none;
            text-decoration: none;
          }
    
        </style>
        """

        SYS_DIR = os.path.join(_CLIENT_DIR, "uploads", "sys")

        if request.method == "POST":
            action = request.form.get("action")

            catalog = _llms.list_models()

            # ────────────────────────────────────────────────────────────────────────────────
            #  SYSTEM FILES PROCESSING
            # ────────────────────────────────────────────────────────────────────────────────
            if action == "upload_files":
                files = request.files.getlist("upload_files")
                upload_folder = SYS_DIR
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                new_pdf_paths = []
                for f in files:
                    if f and f.filename.lower().endswith(".pdf"):
                        dest = os.path.join(upload_folder, f.filename)
                        f.save(dest)
                        new_pdf_paths.append(dest)

                processed_files = {}
                for path in new_pdf_paths:
                    file_name = os.path.basename(path)
                    try:
                        text = extract_pdf_text(path)
                        cleaned = " ".join(text.split())
                        chunks = recursive_text_split(cleaned)
                        for idx, chunk in enumerate(chunks):
                            add_pdf_chunk(file_name, idx, chunk)
                            emb = embed_text(chunk)
                            insert_embedding(
                                vector=emb,
                                metadata={"file_name": file_name, "chunk_index": idx}
                            )
                        processed_files[file_name] = chunks
                    except Exception as e:
                        smx.warning(f"Failed to process {file_name}: {e}")

                smx.admin_pdf_chunks.update(processed_files)
                total_chunks = sum(len(c) for c in processed_files.values())
                session["upload_msg"] = (
                    f"Uploaded {len(new_pdf_paths)} new PDF(s); "
                    f"Generated {total_chunks} chunk(s)."
                )

            elif action == "add_page":
                page_name = request.form.get("page_name", "").strip()
                page_name = page_name.lower()
                site_desc = request.form.get("site_desc", "").strip()
                if site_desc != "":
                    smx.set_website_description(site_desc)
                page_content_html = _genpage.generate_page_html(page_name, smx.website_description)
                if page_name and page_name not in smx.pages:
                    db.add_page(page_name, page_content_html)


            elif action == "save_llm":
                save = False
                k = request.form.get("api_key","").strip()
                if k and k != "********":
                    save = smx.save_embed_model(
                        request.form["provider"],
                        request.form["model"],
                        k.rstrip("*")
                    )
                if save:
                    flash(f"Embed model is saved ✓: <br>{request.form['model']}")
                else:
                    flash(f"ERROR: Embed model is not saved.")

            elif action == "delete_embed_model":
                deleted = smx.delete_embed_key()
                flash("LLM API key removed ") if deleted else flash("Something is wrong!")
                return redirect(url_for("admin_panel"))

            elif action == "add_profile":
                prov  = request.form["provider"]
                model = request.form["model"]
                tag   = request.form["purpose"]
                desc  = request.form["desc"]

                if not any(r for r in catalog if r["provider"] == prov and r["model"] == model):
                    flash("Provider/model not in catalog", "error")
                    return redirect(url_for("admin_panel"))

                _llms.upsert_profile(
                    name = request.form.get("profile_name", "").strip(),
                    provider = request.form.get("provider", "").strip(),
                    model = request.form.get("model", "").strip(),
                    api_key = request.form.get("api_key", "").strip(),
                    purpose = request.form.get("purpose", "").strip() or "general",
                    desc = request.form.get("desc", "").strip(),
                )
                _prof.refresh_profiles_cache()

                # If the just-saved profile is currently cached in-memory for any purpose,
                # clear that live dict so next use reloads the fresh version.
                _saved_name = (request.form.get("profile_name") or "").strip()
                if _saved_name:
                    for _attr in dir(smx):
                        if "profile" not in _attr.lower():
                            continue
                        _val = getattr(smx, _attr, None)
                        if isinstance(_val, dict) and _val.get("name") == _saved_name:
                            setattr(smx, _attr, {})

            elif action == "delete_profile":
                name = (request.form.get("profile_name") or "").strip()
                if name:
                    ok = _llms.delete_profile(name)
                    if ok:
                        _evict_profile_caches_by_name(name)

                    # drop only the matching cached entry in profiles.py
                    _prof.drop_cached_profile_by_name(name)


                    # if any live cached profile on smx matches this name, clear it
                    for attr in ("_chat_profile", "_admin_profile", "_coding_profile", "_classification_profile", "_summarization_profile"):
                        prof = getattr(smx, attr, None)
                        if isinstance(prof, dict) and prof.get("name") == name:
                            setattr(smx, attr, {})

            elif action == "add_model":
                prov = request.form.get("catalog_provider","").strip()
                model = request.form.get("catalog_model","").strip()
                tag = request.form.get("catalog_purpose","").strip()
                desc = request.form.get("catalog_desc","").strip()
                if prov and model and tag and desc:
                    if not _llms.add_model(prov, model, tag, desc):
                        flash("Provider/model already exists in catalog", "info")

            elif action == "delete_model":
                row_id = request.form.get("catalog_id","").strip()
                if row_id:
                    _llms.delete_model(int(row_id))
                    flash("Model deleted successfully", "info")

            elif action == "create_role":
                if (session.get("role") or "").lower() != "superadmin":
                    flash("Only the superadmin can create roles.", "error")
                else:
                    name = (request.form.get("role_name") or "").strip()
                    desc = (request.form.get("role_desc") or "").strip()
                    is_employee = 1 if request.form.get("role_is_employee") == "on" else 0
                    is_admin    = 1 if request.form.get("role_is_admin")    == "on" else 0
                    ok = _auth.create_role(
                        name,
                        desc,
                        is_employee=bool(is_employee),
                        is_admin=bool(is_admin),
                    )
                    flash(f"Role '{name}' created.", "info") if ok else flash("Could not create role (reserved/exists/invalid).", "error")

            elif action == "set_user_role":
                actor_role = (session.get("role") or "").lower()
                actor_id = session.get("user_id")
                user_id = int(request.form.get("user_id") or 0)
                to_role = (request.form.get("to_role") or "").lower()

                target_before = _auth.get_user_basic(user_id)
                actor_basic = _auth.get_user_basic(actor_id) if actor_id else None
                actor_label = (actor_basic.get("username") or actor_basic.get("email")) if actor_basic else "system"

                if _auth.set_user_role(actor_role, user_id, to_role):
                    target_after = _auth.get_user_basic(user_id)
                    _auth.add_role_audit(
                        actor_id or 0,
                        actor_label,
                        user_id,
                        (target_after.get("username") or target_after.get("email") or f"user-{user_id}"),
                        (target_before.get("role") if target_before else "user"),
                        target_after.get("role")
                    )
                    flash("Role updated.", "info")
                else:
                    flash("Not allowed or invalid role change.", "error")

            elif action == "confirm_delete_user":
                if (session.get("role") or "").lower() != "superadmin":
                    flash("Only superadmin can delete accounts.", "error")
                else:
                    session["pending_delete_user_id"] = int(request.form.get("user_id") or 0)
                    flash("Confirm deletion below.", "warning")

            elif action == "cancel_delete_user":
                session.pop("pending_delete_user_id", None)

            elif action == "delete_user":
                if (session.get("role") or "").lower() != "superadmin":
                    flash("You don't have permission to delete account.", "error")
                else:
                    target_id = session.get("pending_delete_user_id")
                    if target_id:
                        target_before = _auth.get_user_basic(int(target_id))
                        actor_id = session.get("user_id")
                        actor_basic = _auth.get_user_basic(actor_id) if actor_id else None
                        actor_label = (actor_basic.get("username") or actor_basic.get("email")) if actor_basic else "system"

                        ok = _auth.delete_user(actor_id, int(target_id))
                        if ok:
                            if target_before:
                                _auth.add_role_audit(
                                    actor_id or 0,
                                    actor_label,
                                    int(target_id),
                                    (target_before.get("username") or target_before.get("email") or f"user-{target_id}"),
                                    (target_before.get("role") or "user"),
                                    "deleted"
                                )
                            flash("Account deleted.", "info")
                        else:
                            flash("Could not delete account.", "error")
                    else:
                        flash("No deletion pending.", "error")
                    session.pop("pending_delete_user_id", None)

        # ────────────────────────────────────────────────────────────────────────────────
        #  EMBEDDING MODELS
        # ────────────────────────────────────────────────────────────────────────────────
        embedding_model = _llms.load_embed_model()
        embeddings_setup_card = f"""
          <div class="card span-4">
            <h4>Setup Embedding Model</h4>
            <form method="post" style="display:inline-block; margin-right:8px;">
              <input type="hidden" name="action" value="save_llm">

              <label>Provider</label>
              <select id="prov" name="provider" onchange="updModels()" required></select>

              <label style="margin-top:6px;">Model</label>
              <select id="model" name="model" required></select>

              <!-- <label style="margin-top:6px;">API Key</label> -->
              <input type="password" name="api_key" placeholder="API key" value="" required/>
              <button type="submit" style="margin-top:6px;">Save</button>
            </form>

            {{% if llm['api_key'] %}}
              <form method="post" style="display:inline-block;">
                <div class="li-row">{embedding_model['provider']} | {embedding_model['model']}
                    <input type="hidden" name="action" value="delete_embed_model">
                    <button id="del-embed-btn" title="Delete api key"
                      onclick="return confirm('Delete stored API key?');">🗑️</button>
                </div>
              </form>
            {{% endif %}}

            <script>
              const MAP = {json.dumps(EMBEDDING_MODELS)};
              const CURRENT_PROVIDER = "{embedding_model['provider']}";
              const CURRENT_MODEL    = "{embedding_model['model']}";

              function updModels() {{
                const provSel  = document.getElementById('prov');
                const modelSel = document.getElementById('model');
                modelSel.innerHTML = '';
                (MAP[provSel.value] || []).forEach(m => {{
                  const o = document.createElement('option');
                  o.value = o.text = m;
                  modelSel.appendChild(o);
                }});
              }}

              document.addEventListener("DOMContentLoaded", () => {{
                const provSel = document.getElementById('prov');
                Object.keys(MAP).forEach(p => {{
                  const o = document.createElement('option');
                  o.value = o.text = p;
                  if (p === CURRENT_PROVIDER) o.selected = true;
                  provSel.appendChild(o);
                }});
                updModels();
                document.getElementById('model').value = CURRENT_MODEL;
              }});
            </script>
          </div>
        """

        # ────────────────────────────────────────────────────────────────────────────────
        #                  LLMs
        # ────────────────────────────────────────────────────────────────────────────────
        Add_model_catalog_card = f"""
          <div class="card span-4">
            <h3>Add Model To Catalogue</h3>
            <form method="post" style="margin-bottom:0.5rem;">
              <label for="catalog_prov">Provider</label>
              <select id="catalog_prov" name="catalog_provider"
                      onchange="updCatalogModels()" required></select>

              <label for="catalog_model">Model</label>
              <select id="catalog_model" name="catalog_model" required></select>

              <label for="catalog_purpose">Purpose</label>
              <select id="catalog_purpose" name="catalog_purpose" required></select>

              <label class="form-label mb-1" style="display:block; position:relative;">
                Description
                <button id="catalog-desc-help" type="button" class="info-btn btn-link p-0 text-muted"
                        style="font-size:0.8rem; line-height:1; padding:2px; display:inline-block;"
                        aria-haspopup="true" aria-expanded="false"
                        title="Click to read model description">ⓘ</button>
              </label>

              <div id="catalog-desc-popover" role="tooltip"
                  class="suggestion-popover card shadow-sm p-2"
                  style="display:none; position:absolute; width:360px; z-index:1050;">
                <strong class="d-block mb-1">Model description</strong>
                <div id="catalog-desc-content" style="white-space:pre-wrap; font-size:0.9rem;"></div>
              </div>

              <input type="hidden" id="catalog_desc" name="catalog_desc">
              <button type="submit" name="action" value="add_model" style="margin-top:4px;">Add</button>
            </form>

            <script>
              const MODEL_MAP = {json.dumps(PROVIDERS_MODELS)};
              const PURPOSE_TAGS = {json.dumps(PURPOSE_TAGS)};
              const DESCRIPTION_MAP = {json.dumps(MODEL_DESCRIPTIONS)};

              function updCatalogModels() {{
                const prov = document.getElementById('catalog_prov').value;
                const mdlSel = document.getElementById('catalog_model');
                mdlSel.innerHTML = '';
                (MODEL_MAP[prov] || []).forEach(model => {{
                  const o = document.createElement('option');
                  o.value = o.text  = model;
                  mdlSel.appendChild(o);
                }});
                updCatalogDescription();
              }}

              function updCatalogDescription() {{
                const model = document.getElementById('catalog_model').value;
                const desc  = DESCRIPTION_MAP[model] || 'No description available.';
                document.getElementById('catalog_desc').value = desc;
                const content = document.getElementById('catalog-desc-content');
                if (content) content.textContent = desc;
              }}

              document.addEventListener('DOMContentLoaded', () => {{
                const provSel = document.getElementById('catalog_prov');
                Object.keys(MODEL_MAP).forEach(prov => {{
                  const o = document.createElement('option');
                  o.value = o.text = prov;
                  provSel.appendChild(o);
                }});
                const purSel = document.getElementById('catalog_purpose');
                PURPOSE_TAGS.forEach(tag => {{
                  const o = document.createElement('option');
                  o.value = o.text = tag;
                  purSel.appendChild(o);
                }});
                updCatalogModels();
                document.getElementById('catalog_model').addEventListener('change', updCatalogDescription);

                const descBtn = document.getElementById('catalog-desc-help');
                const descPopover = document.getElementById('catalog-desc-popover');
                function showDescPopover() {{
                  const r = descBtn.getBoundingClientRect();
                  descPopover.style.left = (r.left + window.scrollX) + 'px';
                  descPopover.style.top  = (r.bottom + 6 + window.scrollY) + 'px';
                  descPopover.style.display = 'block';
                  descBtn.setAttribute('aria-expanded','true');
                }}
                function hideDescPopover() {{
                  descPopover.style.display = 'none';
                  descBtn.setAttribute('aria-expanded','false');
                }}
                descBtn.addEventListener('click', () => {{
                  (descPopover.style.display === 'block') ? hideDescPopover() : showDescPopover();
                }});
                document.addEventListener('click', e => {{
                  if (!descPopover.contains(e.target) && e.target !== descBtn) hideDescPopover();
                }});
                document.addEventListener('keydown', e => {{ if (e.key === 'Escape') hideDescPopover(); }});
              }});
            </script>
          </div>
        """

        catalog = _llms.list_models()
        cat_items = ""
        for row in catalog:
            cat_items += f"""
              <li class="li-row"
                  data-row-id="{row['id']}"
                  data-provider="{row['provider']}"
                  data-model="{row['model']}"
                  data-purpose="{row['purpose']}"
                  data-desc="{row['desc']}"
                  style="font-size:0.9rem;">
                <span style="cursor:pointer;"
                      title="Double-click to populate Profile">{row['provider']} | {row['model']} | {row['purpose']}</span>
                <button type="button" class="info-btn btn-link p-0 text-muted"
                        style="cursor:default; line-height:1; padding:2px; display:inline-block;"
                        aria-haspopup="true" aria-expanded="false"
                        title="{row['desc']}">ⓘ</button>

                <a href="#"
                  class="del-btn"
                  data-action="open-delete-modal"
                  data-delete-url="/admin/delete.json"
                  data-delete-field="id"
                  data-delete-id="{row['id']}"
                  data-delete-label="model {row['model']}"
                  data-delete-extra='{{"resource":"model"}}'
                  data-delete-remove="[data-row-id='{row['id']}']">
                  🗑️
                </a>
              </li>
            """

        models_catalog_list_card = f"""
          <div class="card span-4">
            <h4>Models Catalog</h4>
            <ul class="catalog-list">
              {cat_items or "<li class='li-row'>No models yet.</li>"}
            </ul>
          </div>
        """
        # ────────────────────────────────────────────────────────────────────────────────
        #  MODEL PROFILES
        # ────────────────────────────────────────────────────────────────────────────────
        profiles = _llms.list_profiles()
        add_profiles_card = f"""
          <div class='card span-4'>
            <h4>Setup Profiles</h4>
            <form method="post" style="margin-bottom:0.5rem;">
              <label for="profile_name" class="form-label mb-1">
                Profile Name
                <button id="name-help" type="button" class="info-btn btn-link p-0 text-muted"
                        style="font-size:0.8rem; line-height:1; padding:2px; display:inline-block;"
                        aria-haspopup="true" aria-expanded="false"
                        title="Click to see naming suggestions">ⓘ</button>
              </label>
              <input id="profile_name" name="profile_name" type="text" class="form-control"
                    placeholder="Profile name" required>

              <div id="name-suggestions" role="tooltip"
                    class="suggestion-popover card shadow-sm p-2"
                    style="display:none; position:absolute; width:300px; z-index:1050;">
                  <strong class="d-block mb-1">Quick suggestions:</strong>
                  <ul class="list-unstyled mb-0" id="suggestion-list"></ul>
              </div>

              <select id='provider-dd' name='provider' required></select>
              <select id='model-dd' name='model' required></select>
              <input type="password" name="api_key" placeholder="API key" value="" required/>

              <input type='hidden' id='purpose-field' name='purpose'>
              <input type='hidden' id='desc-field' name='desc'>

              <button class='btn btn-primary' type='submit' name='action' value='add_profile'>Add / Update</button>
            </form>
          </div>
        """
        profiles = _llms.list_profiles()
        profile_items = ""
        for row in profiles:
            name = row["name"]
            provider = row["provider"]
            model = row["model"]
            profile_items += f"""
              <li class="li-row" data-row-id="{name}">
                {name} ({provider} | {model})
                <a href="#"
                  class="del-btn"
                  data-action="open-delete-modal"
                  data-delete-url="/admin/delete.json"
                  data-delete-field="profile_name"
                  data-delete-id="{name}"
                  data-delete-label="profile {name}"
                  data-delete-extra='{{"resource":"profile"}}'
                  data-delete-remove="[data-row-id='{name}']">🗑️</a>
              </li>
            """

        list_profiles_card = f"""
          <div class='card span-4'>
            <h4>Active Profiles</h4>
            <ul class="catalog-list" style="padding-left:1rem; margin-bottom:0;">
              {profile_items or "<li class='li-row'>No profiles yet.</li>"}
            </ul>
          </div>
        """

        # ────────────────────────────────────────────────────────────────────────────────
        #  SYSTEM FILES
        # ────────────────────────────────────────────────────────────────────────────────
        sys_files_card = f"""
          <div class="card span-6">
            <h4>Upload System Files (PDFs only)</h4>
            <form id="form-upload" method="post" enctype="multipart/form-data" style="display:inline-block;">
              <input type="file" name="upload_files" accept=".pdf" multiple>
              <button type="submit" name="action" value="upload_files">Upload</button>
            </form>
          </div>
        """

        sys_files = []
        if os.path.isdir(SYS_DIR):
            sys_files = [f for f in os.listdir(SYS_DIR) if f.lower().endswith(".pdf")]

        sys_files_html = ""
        for f in sys_files:
            rid = f
            sys_files_html += f"""
              <li class="li-row" data-row-id="{rid}">
                {f}
                <a href="#"
                  class="del-btn"
                  data-action="open-delete-modal"
                  data-delete-url="/admin/delete.json"
                  data-delete-field="sys_file"
                  data-delete-id="{rid}"
                  data-delete-label="file {f}"
                  data-delete-extra='{{"resource":"sys_file"}}'
                  data-delete-remove="[data-row-id='{rid}']">🗑️</a>
              </li>
            """

        manage_sys_files_card = f"""
          <div class='card span-6'>
            <h4>Manage System Files</h4>
            <ul class="catalog-list" style="list-style:none; padding-left:0; margin:0;">
              {sys_files_html or "<li>No system file has been uploaded yet.</li>"}
            </ul>
          </div>
        """

        # ────────────────────────────────────────────────────────────────────────────────
        #  PAGES
        # ────────────────────────────────────────────────────────────────────────────────
        smx.pages = db.get_pages()
        upload_msg = session.pop("upload_msg", "")
        alert_script = f"<script>alert('{upload_msg}');</script>" if upload_msg else ""

        pages_html = ""
        for p in smx.pages:
            pages_html += f"""
              <li class="li-row" data-row-id="{p}">
                <span>{p}</span>
                <span style="float:right;">
                  <a class="edit-btn" href="/admin/edit/{p}" title="Edit {p}">🖊️</a>
                  <a href="#"
                    class="del-btn" title="Delete {p}"
                    data-action="open-delete-modal"
                    data-delete-url="/admin/delete.json"
                    data-delete-field="page_name"
                    data-delete-id="{p}"
                    data-delete-label="page {p}"
                    data-delete-extra='{{"resource":"page"}}'
                    data-delete-remove="[data-row-id='{p}']">🗑️</a>
                </span>
              </li>
            """

        add_new_page_card = f"""
        <div class="card span-9">
          <h4>Add New Page</h4>
          <form id="form-add-page" method="post">
            <input type="text" name="page_name" placeholder="Page Name" required>
            <textarea name="site_desc" placeholder="Website description"></textarea>
            <div style="text-align:right;">
              <button type="submit" name="action" value="add_page">Add Page</button>
            </div>
          </form>
        </div>
      """

        manage_page_card = f"""
          <div class="card span-3">
            <h4>Manage Pages</h4>
            <ul class="catalog-list">
              {pages_html or "<li>No page has been added yet.</li>"}
            </ul>
          </div>
        """

        # ────────────────────────────────────────────────────────────────────────────────
        #  USERS & ROLES
        # ────────────────────────────────────────────────────────────────────────────────
        roles = _auth.list_roles()
        viewer_is_super = (session.get("role") or "").lower() == "superadmin"
        _reserved = {"superadmin", "admin", "employee", "user"}

        _roles_items = []
        for r in roles:
            badge_role = ""
            if r.get("is_superadmin"):
                badge_role = "superadmin"
            elif r.get("is_admin"):
                badge_role = "admin"
            elif r.get("is_employee"):
                badge_role = "employee"
            badge = f" ({badge_role})" if (badge_role and badge_role != r["name"]) else ""
            actions = ""
            if viewer_is_super and r["name"].lower() not in _reserved:
                actions = (
                    f"<a href='#' class='del-btn badge' data-action='open-delete-modal' "
                    f"data-delete-url='/admin/delete.json' "
                    f"data-delete-field='role_name' "
                    f"data-delete-id='{r['name']}' "
                    f"data-delete-label='role {r['name']}' "
                    f"""data-delete-extra='{{"resource":"role"}}' """
                    f"""data-delete-remove="[data-role-row='{r['name']}']">🗑️</a>"""
                )
            _roles_items.append(
                f"<li class='li-row' data-role-row='{r['name']}'>"
                f"<b>{r['name']}</b><span class='badge'>{badge} — </span>"
                f"<span style='opacity:.7'>{r['description'] or ''}</span>"
                f"<span>{actions}</span>"
                f"</li>"
            )
        roles_list_html = "".join(_roles_items) or "<li>No roles yet.</li>"

        create_role_form = ""
        if (session.get("role") or "").lower() == "superadmin":
            create_role_form = """
              <form method="post" style="margin-top:10px;">
                <input type="hidden" name="action" value="create_role">
                <label>Role name</label>
                <input name="role_name" placeholder="e.g., analyst" required>
                <label>Description (optional)</label>
                <textarea name="role_desc" rows="2" placeholder="What this role is for"></textarea>
                <label style="display:flex;gap:.5rem;align-items:center;margin-top:.5rem;">
                  <input type="checkbox" name="role_is_employee"> Employee?
                </label>
                <label style="display:flex;gap:.5rem;align-items:center;margin:.25rem 0 1rem;">
                  <input type="checkbox" name="role_is_admin"> Admin?
                </label>
                <button type="submit">Create Role</button>
              </form>
            """

        roles_card = f"""
          <div class="card span-12">
            <h4>Roles</h4>
            <ul class="catalog-list">{roles_list_html}</ul>
            {create_role_form}
          </div>
        """

        viewer_role = (session.get("role") or "").lower()
        viewer_id = session.get("user_id")
        all_users = _auth.list_users()
        employees = [u for u in all_users if (u["role"] or "user").lower() != "user"]
        eligible_registrants = [u for u in all_users if (u["role"] or "user").lower() == "user"]

        def _action_btn(user_id: int, to_role: str, label: str) -> str:
            return f"""
            <form method="post" style="display:inline;margin-right:.5rem">
              <input type="hidden" name="action" value="set_user_role">
              <input type="hidden" name="user_id" value="{user_id}">
              <input type="hidden" name="to_role" value="{to_role}">
              <button type="submit">{label}</button>
            </form>
            """

        roles2 = _auth.list_roles()
        admin_role_names = [r["name"] for r in roles2 if r.get("is_admin") and not r.get("is_superadmin")]

        emp_items = []
        for u in employees:
            role_lower = (u["role"] or "user").lower()
            is_self = bool(viewer_id and u["id"] == viewer_id)
            display_name = u.get("username") or u.get("email") or f"user-{u['id']}"
            controls = ""
            if viewer_role == "superadmin" and role_lower != "superadmin" and not is_self:
                admin_buttons = "".join(
                    _action_btn(u["id"], rname, f"Set {rname}")
                    for rname in admin_role_names
                    if rname != role_lower
                )
                demote_buttons = (
                    (_action_btn(u["id"], "employee", "Set Employee") if role_lower != "employee" else "")
                    + _action_btn(u["id"], "user", "Set User")
                )
                controls = admin_buttons + demote_buttons
                controls += (
                    f"<a class='del-btn badge' href=\"#\" data-action=\"open-delete-modal\" "
                    f"data-delete-url=\"/admin/delete.json\" "
                    f"data-delete-field=\"id\" data-delete-id=\"{u['id']}\" "
                    f"data-delete-label=\"{display_name}\" "
                    f"data-delete-extra='{{\"resource\":\"user\"}}' "
                    f"""data-delete-remove="[data-row-id='{u['id']}']">🗑️</a>"""
                )
            elif viewer_role == "admin":
                if role_lower == "employee" and not is_self:
                    controls = _action_btn(u["id"], "user", "Set User")

            emp_items.append(
                f"<li class='li-row' data-row-id=\"{u['id']}\"><b>{display_name}</b>"
                f"<span class='badge'> — role: <code>{role_lower}</code></span> {controls}</li>"
            )

        opts = []
        for u in eligible_registrants:
            disp = u.get("username") or u.get("email") or f"user-{u['id']}"
            opts.append(f"<option value=\"{u['id']}\">{disp}</option>")
        options = "\n".join(opts) if opts else "<option disabled>No eligible users</option>"

        add_form = ""
        if viewer_role in ("admin", "superadmin"):
            add_form = f"""
              <form method="post" style="margin-top:10px;">
                <input type="hidden" name="action" value="set_user_role">
                <input type="hidden" name="to_role" value="employee">
                <label>Add employee from registrants</label>
                <select name="user_id" required style="min-width:240px">{options}</select>
                <button type="submit" style="margin-left:.5rem">Add Employee</button>
              </form>
            """

        employees_card = f"""
          <div class="card span-12">
            <h4>Employees</h4>
            <ul class="catalog-list">
              {''.join(emp_items) or "<li>No employees yet.</li>"}
            </ul>
            {add_form}
          </div>
        """
        from datetime import datetime, timedelta
        # Audit (always its own row)
        audit_card = ""
        if (session.get("role") or "").lower() == "superadmin":
            audits = _auth.list_role_audit(limit=50)

            cutoff_dt  = datetime.utcnow() - timedelta(days=30)
            cutoff_iso = cutoff_dt.isoformat(timespec="seconds")

            def _parse_dt(s: str):
                if not s:
                    return None
                s2 = s.replace(" ", "T")
                try:
                    return datetime.fromisoformat(s2)
                except Exception:
                    try:
                        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        return None

            items = []
            for a in audits:
                created = a.get("created_at") or ""
                dt = _parse_dt(created)
                is_old = bool(dt and dt < cutoff_dt)
                cls = "li-row audit-row old30" if is_old else "li-row audit-row"
                items.append(
                    f"<li class='{cls}'><code>{created}</code> — "
                    f"<b>{a.get('actor_label') or 'system'}</b> set <b>{a.get('target_label') or ''}</b> "
                    f"from <code>{a.get('from_role')}</code> to <code>{a.get('to_role')}</code></li>"
                )

            audit_card = f"""
              <div class="card span-12">
                <h4>Audit (Role Changes)</h4>

                <div style="display:flex; gap:.5rem; align-items:center; margin:.5rem 0 1rem;">
                  <a href="/admin/audit.csv?limit=1000"><button type="button">Download CSV</button></a>

                  <!-- Clear ALL -->
                  <a href="#"
                    class="del-role-btn"
                    title="Delete all records"
                    data-action="open-delete-modal"
                    data-delete-url="/admin/delete.json"
                    data-delete-field="scope"
                    data-delete-id="all"
                    data-delete-label="ALL audit records"
                    data-delete-extra='{{"resource":"audit"}}'
                    data-delete-remove="#audit-list .audit-row"
                    data-delete-empty="#audit-list"
                    data-empty-html="<li>No role changes yet.</li>">Clear all
                  </a>
                  <a href="#"
                    class="del-role-btn"
                    data-action="open-delete-modal"
                    data-delete-url="/admin/delete.json"
                    data-delete-field="scope"
                    data-delete-id="older_than_30"
                    data-delete-label="audit records that are 30+ days old"
                    data-delete-extra='{{"resource":"audit"}}'
                    data-delete-remove="#audit-list .audit-row.old30"
                    data-delete-empty="#audit-list"
                    data-empty-html="<li>No role changes yet.</li>">Clear 30-days
                  </a>
                  <a href="#"
                    class="del-role-btn"
                    data-action="open-delete-modal"
                    data-delete-url="/admin/delete.json"
                    data-delete-field="scope"
                    data-delete-id="older_than"                   
                    data-delete-label="audit records older than n-days"
                    data-delete-extra='{{"resource":"audit"}}'
                    data-delete-prompt="Enter number of days"     
                    data-delete-param="days"                     
                    data-delete-reload="1">Clear n-days+
                  </a>  <!-- auto-refresh on success -->
                </div>
                <ul id="audit-list" class="catalog-list" style="background:none;">
                  {''.join(items) or "<li>No role changes yet.</li>"}
                </ul>
              </div>
            """
        
        smx.page = "admin"

        side_nav = """
        <aside class="admin-sidenav">
          <div class="snav-title">Admin</div>
          <a href="#models">Models & Profiles</a>
          <a href="#pages">Pages</a>
          <a href="#system">System</a>
          <a href="#users">Users</a>
          <a href="#audits">Audits</a>
        </aside>
        """

        # Sections (cards have span classes; no extra column wrappers)
        models_section = f"""
          <section id="models" class="section">
            <h2>Models & Profiles</h2>
            <div class="admin-grid">
              {embeddings_setup_card}
              {Add_model_catalog_card}
              {models_catalog_list_card}
              {add_profiles_card}
              {list_profiles_card}       
            </div>
          </section>
        """

        pages_section = f"""
          <section id="pages" class="section">
            <h2>Pages</h2>
            <div class="admin-grid">
              {add_new_page_card}
              {manage_page_card}
            </div>
          </section>
        """

        system_section = f"""
          <section id="system" class="section">
            <h2>System</h2>
            <div class="admin-grid">
              {sys_files_card}
              {manage_sys_files_card}
            </div>
          </section>
        """

        users_section = f"""
          <section id="users" class="section">
            <h2>Users</h2>
            <div class="admin-grid">
              {roles_card}
              {employees_card}
            </div>
          </section>
        """

        audits_section = f"""
          <section id="audits" class="section">
            <h2>Audits</h2>
            <div class="admin-grid">
              {audit_card}
            </div>
          </section>
        """

        admin_shell = f"""{admin_layout_css}
          <div class="admin-shell">
          {side_nav}
          <div class="admin-main">
            {models_section}
            {pages_section}
            {system_section}
            {users_section}
            {audits_section}
          </div>
        </div>
        """

        # ─────────────────────────────────────────────────────────
        #  DELETE MODAL (safe, idempotent)
        # ─────────────────────────────────────────────────────────
        delete_modal_block = """
          <div id="delBackdrop" class="modal-backdrop">
            <div class="modal">
              <h4>Confirm deletion</h4>
              <p id="delMsg">Are you sure?</p>
              <div id="delPrompt" style="display:none; margin-top:.5rem;">
                <label id="delPromptLabel" for="delPromptInput" style="display:block; font-size:.85rem;"></label>
                <input id="delPromptInput" type="number" min="1" step="1"
                      style="width:140px; padding:.25rem .4rem; border:1px solid #d0d7de; border-radius:6px;">
              </div>
              <div class="actions">
                <button id="delCancel" type="button">Cancel</button>
                <button id="delConfirm" class="btn-danger" type="button">Delete</button>
              </div>
            </div>
          </div>
        """

        return render_template_string(f"""
          {head_html()}
          <body>
            {_generate_nav()}
            {{% for m in get_flashed_messages() %}}
              <div style="color:green;">{{ m }}</div>
            {{% endfor %}}
            {alert_script}
            {admin_shell}
            {delete_modal_block}
                      
            <!-- Profiles helper scripts -->
            <script>
              /* Name suggestions popover */
              const nameExamples = {{
                'Customer Support': 'GPT-4o — Support Chat',
                'Marketing': 'Claude Sonnet — Ad Copy',
                'HR / Recruiting': 'GPT-4o — Candidate Screening',
                'Finance': 'Claude Opus — Earnings Summary',
                'Healthcare': 'MedLM — Clinical Notes',
                'Legal': 'GPT-4o — Contract Review',
                'Education': 'GPT-4o — Lesson Tutor',
                'R&D / Science': 'Claude Sonnet — Literature Search'
              }};
              const txt = document.getElementById('profile_name');
              const infoBtn = document.getElementById('name-help');
              const popover = document.getElementById('name-suggestions');
              const listUL = document.getElementById('suggestion-list');

              function showPopover(){{
                const r = infoBtn.getBoundingClientRect();
                popover.style.left = `${{r.left + window.scrollX}}px`;
                popover.style.top  = `${{r.bottom + 6 + window.scrollY}}px`;
                popover.style.display = 'block';
                infoBtn.setAttribute('aria-expanded','true');
              }}
              function hidePopover(){{
                popover.style.display = 'none';
                infoBtn.setAttribute('aria-expanded','false');
              }}
              if (infoBtn && popover){{
                infoBtn.addEventListener('click', () => popover.style.display === 'block' ? hidePopover() : showPopover());
                document.addEventListener('click', e => {{ if (!popover.contains(e.target) && e.target !== infoBtn) hidePopover(); }});
                document.addEventListener('keydown', e => {{ if (e.key === 'Escape') hidePopover(); }});
              }}
              document.addEventListener('DOMContentLoaded', () => {{
                if (listUL){{
                  for (const [sector, example] of Object.entries(nameExamples)) {{
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${{sector}}:</strong> ${{example}}`;
                    li.title = 'Click to use';
                    li.tabIndex = 0;
                    li.addEventListener('click', () => {{ if (!txt.value.trim()) txt.value = example; hidePopover(); txt && txt.focus(); }});
                    li.addEventListener('keypress', e => {{ if (e.key === 'Enter') li.click(); }});
                    listUL.appendChild(li);
                  }}
                }}
              }});
            </script>

            <!-- Catalogue -> Profiles double-click fill + dropdown populate -->
            <script>
              const catalog = {json.dumps(catalog)};
              const provMap = {{}}, purposeMap = {{}}, descMap = {{}};
              catalog.forEach(function(row){{
                (provMap[row.provider] ||= []).push(row.model);
                purposeMap[row.provider + '|' + row.model] = row.purpose;
                descMap[row.provider + '|' + row.model] = row.desc;
              }});
              const provDD = document.getElementById('provider-dd');
              const modelDD = document.getElementById('model-dd');
              const purposeField = document.getElementById('purpose-field');
              const descField = document.getElementById('desc-field');

              if (provDD){{
                Object.keys(provMap).sort().forEach(function(prov){{
                  provDD.options.add(new Option(prov, prov));
                }});
                function refreshModels(){{
                  const models = provMap[provDD.value] || [];
                  modelDD.innerHTML = '';
                  models.forEach(function(m){{ modelDD.options.add(new Option(m, m)); }});
                  modelDD.dispatchEvent(new Event('change'));
                }}
                provDD.addEventListener('change', refreshModels);
                modelDD && modelDD.addEventListener('change', function(){{
                  const key = provDD.value + '|' + modelDD.value;
                  purposeField.value = purposeMap[key] || '';
                  descField.value = descMap[key] || '';
                }});
                if (provDD.options.length){{ provDD.selectedIndex = 0; refreshModels(); }}
              }}

              document.addEventListener('DOMContentLoaded', function(){{
                document.querySelectorAll('.catalog-list .li-row').forEach(function(li){{
                  li.addEventListener('click', function(){{
                    document.querySelectorAll('.cat-row.selected').forEach(el => el.classList.remove('selected'));
                    li.classList.add('selected');
                  }});
                  li.addEventListener('dblclick', function(){{
                    const provider = li.dataset.provider;
                    const model = li.dataset.model;
                    const purpose = li.dataset.purpose;
                    if (provDD && modelDD){{
                      provDD.value = provider; provDD.dispatchEvent(new Event('change'));
                      modelDD.value = model;   modelDD.dispatchEvent(new Event('change'));
                      document.getElementById('purpose-field').value = purpose;
                    }}
                  }});
                }});
              }});
            </script>

            <!-- Guarded helper scripts (won't error if elements missing) -->
            <script>
              const mediaForm = document.getElementById("media-upload-form");
              if (mediaForm){{
                mediaForm.addEventListener("submit", function(e){{
                  e.preventDefault();
                  const formData = new FormData(this);
                  fetch("/admin/upload_media", {{ method: "POST", body: formData }})
                    .then(r => r.json())
                    .then(data => {{
                      const resultDiv = document.getElementById("media-upload-result");
                      if (!resultDiv) return;
                      if (data.file_paths && data.file_paths.length > 0){{
                        resultDiv.innerHTML = "<p>Uploaded Media Files:</p><ul>" +
                          data.file_paths.map(path => `<li>${{path}}</li>`).join("") +
                          "</ul><p>Copy a path into your HTML.</p>";
                      }} else {{
                        resultDiv.innerHTML = "<p>No files were uploaded.</p>";
                      }}
                    }})
                    .catch(err => {{
                      console.error("Error uploading media:", err);
                      const resultDiv = document.getElementById("media-upload-result");
                      if (resultDiv) resultDiv.innerHTML = "<p>Error uploading files.</p>";
                    }});
                }});
              }}
            </script>
            <script>
              document.addEventListener('DOMContentLoaded', function () {{
                const form = document.getElementById('add-page-form');
                const btn = document.getElementById('add-page-btn');
                const overlay = document.getElementById('loader-overlay'); // already defined in admin template

                if (form) {{
                  form.addEventListener('submit', function () {{
                    if (btn) {{ btn.disabled = true; btn.textContent = 'Adding…'; }}
                    if (overlay) overlay.style.display = 'flex';
                  }});
                }}

                // safety: hide overlay if we return via back/forward cache
                window.addEventListener('pageshow', function () {{
                  const o = document.getElementById('loader-overlay');
                  if (o) o.style.display = 'none';
                  const b = document.getElementById('add-page-btn');
                  if (b) {{ b.disabled = false; b.textContent = 'Add Page'; }}
                }});
              }});
            </script>
            <script>
              (function(){{
                if (window.__delModalInit) return;
                window.__delModalInit = true;

                const backdrop = document.getElementById('delBackdrop');
                const msg = document.getElementById('delMsg');
                const btnCancel = document.getElementById('delCancel');
                const btnConfirm = document.getElementById('delConfirm');

                let cfg = null;
                let trigger = null;

                function openModal(t){{
                  trigger = t;
                  const url = t.getAttribute('data-delete-url');
                  const id = t.getAttribute('data-delete-id');
                  const field = t.getAttribute('data-delete-field') || 'id';
                  const label = t.getAttribute('data-delete-label') || ('item ' + id);
                  const method = (t.getAttribute('data-delete-method') || 'POST').toUpperCase();
                  const removeSel = t.getAttribute('data-delete-remove') || '';
                  const emptySel  = t.getAttribute('data-delete-empty')  || '';
                  const emptyHtml = t.getAttribute('data-empty-html')    || '<li>No items.</li>';
                  const promptTxt = t.getAttribute('data-delete-prompt') || '';
                  const paramName = t.getAttribute('data-delete-param')  || '';
                  const wantsReload = t.hasAttribute('data-delete-reload');
                  let extra = {{}};
                  const extraRaw = t.getAttribute('data-delete-extra');
                  if (extraRaw){{ try {{ extra = JSON.parse(extraRaw); }} catch(e){{}} }}

                  cfg = {{ url, id, field, method, removeSel, emptySel, emptyHtml, extra, promptTxt, paramName, wantsReload }};
                  msg.textContent = "Delete " + label + "? This cannot be undone.";

                  // show/hide input
                  const pBox = document.getElementById('delPrompt');
                  const pLab = document.getElementById('delPromptLabel');
                  const pInp = document.getElementById('delPromptInput');
                  if (cfg.promptTxt && cfg.paramName){{
                    if (pLab) pLab.textContent = cfg.promptTxt;
                    if (pInp) pInp.value = '';
                    if (pBox) pBox.style.display = 'block';
                  }} else {{
                    if (pBox) pBox.style.display = 'none';
                  }}

                  backdrop.style.display = 'flex';
                }}

                function closeModal(){{
                  backdrop.style.display = 'none';
                  cfg = null;
                  trigger = null;
                  btnConfirm.disabled = false;
                  btnConfirm.removeAttribute('data-busy');
                }}

                document.addEventListener('click', function (e) {{
                  const bd = document.getElementById('delBackdrop');
                  if (bd && bd.style.display === 'flex' && bd.contains(e.target)) return;

                  const t = e.target.closest('[data-action="open-delete-modal"]');
                  if (!t) return;
                  e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
                  openModal(t);
                }}, true);

                btnConfirm.addEventListener('click', async function(e){{
                  e.preventDefault(); e.stopPropagation();
                  if(!cfg || btnConfirm.dataset.busy) return;
                  btnConfirm.dataset.busy = '1';
                  btnConfirm.disabled = true;

                  const fd = new FormData();
                  fd.append(cfg.field, cfg.id);
                  for (const k in cfg.extra){{ fd.append(k, cfg.extra[k]); }}

                  // include prompted value, if any
                  if (cfg.paramName){{
                    const pInp = document.getElementById('delPromptInput');
                    const val = (pInp && pInp.value != null) ? String(pInp.value).trim() : '';
                    if (!val){{
                      alert('Please provide a value.');
                      btnConfirm.disabled = false; btnConfirm.removeAttribute('data-busy');
                      return;
                    }}
                    fd.append(cfg.paramName, val);
                  }}

                  try{{
                    const res = await fetch(cfg.url, {{ method: cfg.method, body: fd, credentials: 'same-origin' }});
                    const ct = (res.headers.get('content-type')||'').toLowerCase();
                    const payload = ct.includes('application/json') ? await res.json() : {{ ok:false, error: await res.text() || ('HTTP '+res.status) }};

                    if (res.ok && payload && payload.ok){{
                      // bulk-friendly path: reload if asked
                      if (cfg.wantsReload){{
                        window.location.replace('/admin#audits');
                        window.location.reload();
                        return;
                      }}

                      // existing single/multi selector removal
                      let removed = false;
                      if (cfg.removeSel){{
                        const nodes = document.querySelectorAll(cfg.removeSel);
                        if (nodes.length){{ nodes.forEach(n => n.remove()); removed = true; }}
                      }}
                      if (!removed && trigger){{
                        const el = trigger.closest('[data-row],[data-row-id],li,.row,.card-item');
                        if (el){{ el.remove(); removed = true; }}
                      }}
                      if (cfg.emptySel){{
                        const box = document.querySelector(cfg.emptySel);
                        if (box && box.children.length === 0){{ box.innerHTML = cfg.emptyHtml; }}
                      }}
                      closeModal();
                    }} else {{
                      alert((payload && payload.error) ? payload.error : ('HTTP '+res.status));
                      closeModal();
                    }}
                  }} catch(err){{
                    alert('Network error.');
                    closeModal();
                  }}
                }});
                btnCancel.addEventListener('click', function (e) {{
                  e.preventDefault();
                  e.stopPropagation();
                  e.stopImmediatePropagation();
                  closeModal();
                }});
                document.addEventListener('keydown', function (e) {{
                  if (e.key === 'Escape') closeModal();
                }});
                backdrop.addEventListener('click', function(e){{
                  if(e.target === backdrop) closeModal();
                }});
              }})();
          </script>
          </body>
          </html>
        """,
          flash_messages=get_flashed_messages(with_categories=True),
          llm=embedding_model,
          catalog=_llms.list_models(),
          profiles=profiles
        )

    @smx.app.route("/admin/delete.json", methods=["POST"])
    def admin_delete_universal():

        role = (session.get("role") or "").lower()
        if role != "superadmin":
            return jsonify(ok=False, error="Not authorized"), 403
        try:
          # read resource first; don't require a generic 'id' for all resources
          resource = (request.form.get("resource") or "").lower()
          if not resource:
              return jsonify(ok=False, error="missing resource"), 400

          rid = request.form.get("id")  # optional; used by some branches

          if resource == "profile":
              # profiles use 'profile_name' (or fallback to 'id' if you ever send it that way)
              prof_name = request.form.get("profile_name") or rid
              if not prof_name:
                  return jsonify(ok=False, error="missing profile_name"), 400

              delete_fn = getattr(_llms, "delete_profile", None)
              if not callable(delete_fn):
                  return jsonify(ok=False, error="delete_profile() not implemented"), 500
              try:
                  result = delete_fn(prof_name)
              except Exception as e:
                  return jsonify(ok=False, error=str(e)), 500

              if isinstance(result, tuple):
                  ok, err = result
              elif result is None:
                  ok, err = True, None
              else:
                  ok, err = (bool(result), None)
              if ok:
                  _evict_profile_caches_by_name(prof_name)

              return (jsonify(ok=True), 200) if ok else (jsonify(ok=False, error=err or "delete failed"), 400)

          if resource == "model":
              if not rid:
                  return jsonify(ok=False, error="missing id"), 400
              try:
                  rid_int = int(rid)
              except Exception:
                  return jsonify(ok=False, error="bad id"), 400

              delete_fn = getattr(_llms, "delete_model", None)
              if not callable(delete_fn):
                  return jsonify(ok=False, error="delete_model() not implemented"), 500
              try:
                  result = delete_fn(rid_int)
              except Exception as e:
                  return jsonify(ok=False, error=str(e)), 500

              if isinstance(result, tuple):
                  ok, err = result
              elif result is None:
                  ok, err = True, None
              else:
                  ok, err = (bool(result), None)
              return (jsonify(ok=True), 200) if ok else (jsonify(ok=False, error=err or "delete failed"), 400)

          if resource == "user":
              if not rid:
                  return jsonify(ok=False, error="missing id"), 400
              try:
                  rid_int = int(rid)
              except Exception:
                  return jsonify(ok=False, error="bad id"), 400

              actor_id = session.get("user_id") or 0
              target_before = _auth.get_user_basic(rid_int)
              if not target_before:
                  return jsonify(ok=False, error="not found"), 404
              if _auth.delete_user(actor_id, rid_int):
                  actor = _auth.get_user_basic(actor_id) or {}
                  _auth.add_role_audit(
                      actor_id, (actor.get("username") or actor.get("email") or "system"),
                      rid_int, (target_before.get("username") or target_before.get("email") or f"user-{rid_int}"),
                      (target_before.get("role") or "user"), "deleted"
                  )
                  return jsonify(ok=True), 200
              return jsonify(ok=False, error="delete failed"), 400

          if resource == "role":
              role_name = (request.form.get("role_name") or rid or "").strip()
              if not role_name:
                  return jsonify(ok=False, error="missing role_name"), 400

              if role_name.lower() in {"superadmin","admin","employee","user"}:
                  return jsonify(ok=False, error="reserved role cannot be deleted"), 400

              delete_fn = getattr(_auth, "delete_role", None)
              if not callable(delete_fn):
                  return jsonify(ok=False, error="delete_role() not implemented"), 500

              try:
                  result = delete_fn(role_name)
              except Exception as e:
                  return jsonify(ok=False, error=str(e)), 500

              if isinstance(result, tuple):
                  ok, err = result
              elif result is None:
                  ok, err = True, None
              else:
                  ok, err = (bool(result), None)

              return (jsonify(ok=True), 200) if ok else (jsonify(ok=False, error=err or "delete failed"), 400)

          if resource == "page":
              page_name = request.form.get("page_name") or rid
              if not page_name:
                  return jsonify(ok=False, error="missing page_name"), 400
              try:
                  result = db.delete_page(page_name)
              except Exception as e:
                  return jsonify(ok=False, error=str(e)), 500

              ok = bool(result) if result is not None else True
              return (jsonify(ok=True), 200) if ok else (jsonify(ok=False, error="delete failed"), 400)
  
          if resource == "sys_file":
              SYS_DIR = os.path.join(_CLIENT_DIR, "uploads", "sys")
              file_name = request.form.get("sys_file", "").strip()
              if file_name:
                  # where our system PDFs live
                  remove_admin_pdf_file(SYS_DIR, file_name)
                  smx.admin_pdf_chunks.pop(file_name, None)
                  session["upload_msg"] = f"Deleted {file_name} and its chunks."
                  return jsonify(ok=True), 200
              return jsonify(ok=False, error="delete failed"), 400

          if resource == "audit":
             
              scope = (request.form.get("scope") or "").strip().lower()

              if scope == "all":
                  # your existing clear-all logic stays untouched
                  deleted = int(_auth.clear_role_audit() or 0)
                  return jsonify(ok=True, deleted=deleted)

              elif scope == "older_than_30":
                  from datetime import datetime, timedelta, timezone
                  cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                  # match your DB format: 'YYYY-MM-DD HH:MM:SS'
                  cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
                  deleted = int(_auth.clear_role_audit(cutoff_str) or 0)
                  return jsonify(ok=True, deleted=deleted)
              
              elif scope == "older_than":
                  days_raw = (request.form.get("days") or "").strip()
                  try:
                      days = int(days_raw)
                      if days < 1: raise ValueError
                  except Exception:
                      return jsonify(ok=False, error="Invalid days."), 400

                  from datetime import datetime, timedelta, timezone
                  cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                  cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
                  deleted = int(_auth.clear_role_audit(cutoff_str) or 0)
                  return jsonify(ok=True, deleted=deleted)

              elif scope == "before":
                  before = (request.form.get("before") or "").strip()
                  if not before:
                      return jsonify(ok=False, error="Missing 'before'."), 400
                  deleted = int(_auth.clear_role_audit(before) or 0)
                  return jsonify(ok=True, deleted=deleted)

              else:
                  return jsonify(ok=False, error="Invalid scope."), 400
              
          return jsonify(ok=False, error="unsupported resource"), 400

        except Exception as e:
            smx.warning(f"/admin/delete.json error: {e}")
            return jsonify(ok=False, error=str(e)), 500

    # Override the generic page renderer to inject a gallery on the "service" page
    @smx.app.route('/page/<page_name>')
    def view_page(page_name):
        smx.page = page_name.lower()
        nav_html = _generate_nav()
        content = smx.pages.get(page_name, f"No content found for page '{page_name}'.")
        
        # only on the service page, build a gallery
        media_html = ''
        if page_name.lower() == 'service':
            media_folder = os.path.join(_CLIENT_DIR, 'uploads', 'media')
            if os.path.isdir(media_folder):
                files = sorted(os.listdir(media_folder))
                # wrap each file in an <img> tag (you can special‑case videos if you like)
                thumbs = []
                for fn in files:
                    src = url_for('serve_media', filename=fn)
                    thumbs.append(f'<img src="{src}" alt="{fn}" style="max-width:150px; margin:5px;"/>')
                if thumbs:
                    media_html = f'''
                      <section id="media-gallery" style="margin-top:20px;">
                        <h3>Media Gallery</h3>
                        <div style="display:flex; flex-wrap:wrap; gap:10px;">
                          {''.join(thumbs)}
                        </div>
                      </section>
                    '''  

        view_page_html = f"""
          {head_html()}
          {smx.get_favicon()}
          {nav_html}
          <div style=" width:100%; box-sizing:border-box; padding-top:5px;">
            <div style="text-align:center; border:1px solid #ccc; 
                        border-radius:8px; background-color:#f9f9f9;">
              <div>{content}</div>
              {media_html}
            </div>
          </div>
          {footer_html()}
        """
        return Response(view_page_html, mimetype="text/html")
    

    @smx.app.route('/docs')
    def docs():
        return render_template("docs.html", page_title="Documentation")


    @smx.app.route("/admin/audit.csv")
    def download_audit_csv():
        # superadmin only
        role = (session.get("role") or "").lower()
        if role != "superadmin":
            return jsonify({"error": "forbidden"}), 403

        # optional limit (defaults to 1000)
        try:
            limit = int(request.args.get("limit", 1000))
        except Exception:
            limit = 1000

        rows = _auth.list_role_audit(limit=limit)

        import io, csv, datetime
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["timestamp", "actor", "target", "from_role", "to_role"])
        for r in rows:
            writer.writerow([
                r["created_at"],
                r["actor_label"],
                r["target_label"],
                r["from_role"],
                r["to_role"],
            ])

        csv_text = buf.getvalue()
        filename = f"role_audit_{datetime.date.today().isoformat()}.csv"
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )


    @smx.app.route("/admin/chunks", methods=["GET"])
    def list_chunks():
        # Retrieve all chunks from the database
        chunks = db.get_all_pdf_chunks()
        # Render them in a simple HTML table (for demo purposes)
        html = "<h2>PDF Chunk Records</h2><table border='1'><tr><th>ID</th><th>Source File</th><th>Index</th><th>Text Snippet</th><th>Actions</th></tr>"
        for chunk in chunks:
            snippet = chunk['chunk_text'][:100] + "..."
            html += f"<tr><td>{chunk.get('id', 'N/A')}</td><td>{chunk['source_file']}</td><td>{chunk['chunk_index']}</td>"
            html += f"<td>{snippet}</td>"
            html += f"<td><a href='/admin/chunks/edit/{chunk.get('id')}'>Edit</a> "
            html += f"<a href='/admin/chunks/delete/{chunk.get('id')}'>Delete</a></td></tr>"
        html += "</table>"
        return html


    @smx.app.route("/admin/chunks/edit/<int:chunk_id>", methods=["GET", "POST"])
    def edit_chunk(chunk_id):
        if request.method == "POST":
            new_text = request.form.get("chunk_text")
            db.update_pdf_chunk(chunk_id, new_text)
            return redirect(url_for("list_chunks"))
        # For GET, load the specific chunk and render an edit form.
        conn = sqlite3.connect(db.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, source_file, chunk_index, chunk_text FROM pdf_chunks WHERE id = ?", (chunk_id,))
        chunk = cursor.fetchone()
        conn.close()
        if not chunk:
            return "Chunk not found", 404
        # Render a simple HTML form
        html = f"""
        <h2>Edit Chunk {chunk} (from {chunk}, index {chunk})</h2>
        <form method="post">
            <textarea name="chunk_text" rows="10" cols="80">{chunk}</textarea><br>
            <button type="submit">Save Changes</button>
        </form>
        """
        return html

    @smx.app.route("/admin/chunks/delete/<int:chunk_id>", methods=["GET"])
    def delete_chunk(chunk_id):
        db.delete_pdf_chunk(chunk_id)
        return redirect(url_for("list_chunks"))

    # ---- EDIT PAGE ------------------------------------------------
    @smx.app.route("/admin/edit/<page_name>", methods=["GET", "POST"])
    def edit_page(page_name):
        if request.method == "POST":
            new_page_name = request.form.get("page_name", "").strip()
            new_content = request.form.get("page_content", "").strip()
            if page_name in smx.pages and new_page_name:
                db.update_page(page_name, new_page_name, new_content)
                return redirect(url_for("admin_panel"))
        # Load the full content for the page to be edited.
        content = smx.pages.get(page_name, "")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Edit Page - {{ page_name }}</title>
          <style>
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background: #f4f7f9;
                padding: 20px;
            }
            .editor {
                max-width: 800px;
                margin: 0 auto;
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            input, textarea {
                width: 100%;
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 10px 20px;
                background: #007acc;
                border: none;
                color: #fff;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #005fa3;
            }
            a.button {
                padding: 10px 20px;
                background: #aaa;
                border: none;
                color: #fff;
                border-radius: 4px;
                text-decoration: none;
            }
            a.button:hover {
                background: #888;
            }
          </style>
        </head>
        <body>
          <div class="editor">
            <h1>Edit Page - {{ page_name }}</h1>
            <form method="post">
                <input type="text" name="page_name" value="{{ page_name }}" required>
                <textarea name="page_content" rows="20">{{ content }}</textarea>
                <div style="margin-top:15px;">
                  <button type="submit">Update Page</button>
                  <a class="button" href="{{ url_for('admin_panel') }}">Cancel</a>
                </div>
            </form>
          </div>
        </body>
        </html>
        """, page_name=page_name, content=content)
    
    # ────────────────────────────────────────────────────
    # ACCOUNTS
    # ────────────────────────────────────────────────────
    # ----Register ---------------------------------------
    @smx.app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
          email = request.form["email"].strip()
          username = request.form["username"].strip()
          password = request.form["password"]
          role = request.form.get("role", "user")
          if not email or not password:
              flash("email and password required.")
          else:
              success = register_user(email, username, password, role)
              if success:
                  flash("Registration successful—please log in.")
                  return redirect(url_for("login"))
              else:
                  flash("Email already taken.")
        return render_template("register.html")

    # ----- Login --------------------------------------------
    @smx.app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
          email = request.form["email"]
          password = request.form["password"]
          user = authenticate(email, password)
          if user:
              # put only the minimal info in session
              session["user_id"] = user["id"]
              session["email"] = user["email"]
              session["username"] = user["username"]
              session["role"] = user["role"]

              # ensure the just-logged-in user’s “Current” chat is closed on next GET
              session["needs_end_chat"] = True
              
              # — Load past chats from chats.db for this user —
              chat_ids = SQLHistoryStore.list_chats(user["id"])
              past = []
              for cid in chat_ids:
                  # load title *and* history; title was persisted earlier
                  title, history = SQLHistoryStore.load_with_title(user["id"], cid)
                  past.append({
                      "id": cid,
                      "title": title or "Untitled",
                      "history": history
                  })

              # Any chats still titled "Current" now have their full history available:
              # generate & persist a proper title for each one          
              for entry in past:
                  if entry["title"] == "Current" and entry["history"]:
                      new_title = smx.generate_contextual_title(entry["history"])
                      # update DB and in-memory entry
                      SQLHistoryStore.save(user["id"], entry["id"], entry["history"], new_title)
                      entry["title"] = new_title

              # Now store past into session
              session["past_sessions"] = past     

              flash("Logged in successfully.")
              return redirect(url_for("home"))
          else:
              flash("Invalid username or password.")
        return render_template("login.html")

      # ----- Logout -------------------------------------------
    @smx.app.route("/logout", methods=["POST"])
    def logout():
        """Clear session and return to login."""
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for("login"))
        
    @smx.app.context_processor
    def inject_role_helpers():
        def can_see_admin():
            if not getattr(current_user, "is_authenticated", False):
                return False
            # Accept either .roles (iterable) or .role (single string)
            roles = getattr(current_user, "roles", None)
            if roles is None:
                r = getattr(current_user, "role", None)
                roles = [r] if r else []
            return any(r in ("admin", "superadmin") for r in roles if r)
        return dict(can_see_admin=can_see_admin)

    # --- UPLOAD MEDIA --------------------------------------
    @smx.app.route("/admin/upload_media", methods=["POST"])
    def upload_media():               
        # Retrieve uploaded media files (images, videos, etc.).
        uploaded_files = request.files.getlist("media_files")
        file_paths = []
        for file in uploaded_files:
            if file.filename:
                filepath = os.path.join(MEDIA_FOLDER, file.filename)
                file.save(filepath)
                # This path can be copied by the developer. Adjust if you have a web server serving these files.
                file_paths.append(f"/uploads/media/{file.filename}")
        return jsonify({"file_paths": file_paths})
    
    # Serve the raw media files
    @smx.app.route('/uploads/media/<path:filename>')
    def serve_media(filename):
        media_dir = os.path.join(_CLIENT_DIR, 'uploads', 'media')
        return send_from_directory(media_dir, filename)
    
    # ──────────────────────────────────────────────────────────────────────────────────────── 
    # DASHBOARD
    # ──────────────────────────────────────────────────────────────────────────────────────── 
    # ── DASHBOARD VIEW DETAILS -----------------------------
    @smx.app.route("/dashboard", methods=["GET", "POST"])
    # @login_required
    def dashboard():
        DATA_FOLDER = os.path.join(_CLIENT_DIR, "uploads", "data")
        os.makedirs(DATA_FOLDER, exist_ok=True)

        ####################################################################
        
        _CELL_REPAIR_RULES = """
        Fix the Python cell to satisfy:
        - Single valid cell; imports at the top.
        - No top-level statements between if/elif/else branches.
        - Regression must use either sklearn with train_test_split (then X_test exists) and R^2/MAE/RMSE, or statsmodels OLS. No accuracy_score in regression.
        - Keep all plotting + savefig + BytesIO + display inside the branch that created the figure.
        Return ONLY the corrected cell.
        """

        def _smx_repair_python_cell(py_code: str) -> str:
            code = textwrap.dedent(py_code or "").strip()
            needs_fix = False
            if re.search(r"\baccuracy_score\b", code) and re.search(r"\bLinearRegression\b|\bOLS\b", code):
                needs_fix = True
            if re.search(r"\bX_test\b", code) and not re.search(r"\bX_test\s*=", code):
                needs_fix = True
            try:
                ast.parse(code)
            except SyntaxError:
                needs_fix = True
            if not needs_fix:
                return code
            prof = _prof.get_profile("coding") or _prof.get_profile("admin")
            if not prof:
                return code
            
            _prompt = f"```python\n{code}\n```"
            _client = _prof.get_client(prof)
            _model = prof["model"]

            if prof['provider'] == "google":    
                fixed = _out(_client.models.generate_content(
                              model=_model, 
                              contents=f"{_CELL_REPAIR_RULES}\n\n{_prompt}",
                            )
                        ).strip()
                
            elif prof["provider"] == "openai" and _model in smx.gpt_models_latest():
                args = set_args(model=prof.get("model"), instructions=_CELL_REPAIR_RULES,
                          input=_prompt, previous_id=None, store=False,
                          reasoning_effort="minimal", verbosity="low")
                fixed = _out(_client.responses.create(**args)).strip()

            elif prof["provider"] == "anthropic":                    
                fixed = _out(_client.messages.create(
                            model=_model,
                            max_tokens=1024,
                            system=_CELL_REPAIR_RULES,
                            messages=[{"role": "user", "content":_prompt}]
                        )).strip()
                
            else:
                fixed = _out(_client.chat.completions.create(
                            model=_model,
                            messages=[
                                {"role": "system", "content":_CELL_REPAIR_RULES},
                                {"role": "user", "content":_prompt},
                            ]
                          )
                        ).strip()
                
            try:
                ast.parse(fixed); return fixed
            except SyntaxError:
                return code
        ################################################################

        section = request.args.get("section", "explore")
        datasets = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith(".csv")]
        selected_dataset = request.form.get("dataset") or request.args.get("dataset")
        if not selected_dataset and datasets:
            selected_dataset = datasets[0]

        # selected_dataset = selected_dataset or ""

        # Handle file upload
        if request.method == "POST" and "dataset_file" in request.files:
            f = request.files["dataset_file"]
            if f.filename.lower().endswith(".csv"):
                path = os.path.join(DATA_FOLDER, f.filename)
                f.save(path)
                flash(f"Uploaded {f.filename}")
                return redirect(url_for("dashboard", section=section, dataset=f.filename))

        # Load dataframe if available
        df = pd.read_csv(os.path.join(DATA_FOLDER, selected_dataset)) if selected_dataset else None

        # --- Jupyter kernel management ---
        session_id = session.get('smx_kernel_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['smx_kernel_id'] = session_id

        km, kc = SyntaxMatrixKernelManager.start_kernel(session_id)

        # --- Handle Ask AI ---
        ai_outputs = []
        askai_question = ""
        refined_question = None
        ai_code = None

        if request.method == "POST" and "askai_question" in request.form:
            askai_question = request.form["askai_question"].strip()
            if df is not None:      
                
                refined_question = refine_eda_question(askai_question, df)
                intent = classify(refined_question)
                ai_code = smx.ai_generate_code(refined_question, intent, df)
                ai_code = auto_inject_template(ai_code, intent, df)
                ai_code = fix_scatter_and_summary(ai_code)
                ai_code = fix_importance_groupby(ai_code)
                ai_code = inject_auto_preprocessing(ai_code)
                ai_code = patch_plot_code(ai_code, df, refined_question)
                ai_code = patch_pairplot(ai_code, df)
                ai_code = get_plotting_imports(ai_code)
                ai_code = ensure_image_output(ai_code)      
                ai_code = fix_numeric_sum(ai_code)
                ai_code = ensure_accuracy_block(ai_code)
                ai_code = ensure_output(ai_code)
                ai_code = fix_plain_prints(ai_code)
                ai_code = fix_print_html(ai_code) 
                ai_code = fix_to_datetime_errors(ai_code)
                ai_code = _smx_repair_python_cell(ai_code)

                 # Always make sure 'df' is in the kernel before running user code
                df_init_code = (
                    f"import pandas as pd\n"
                    f"df = pd.read_csv(r'''{os.path.join(DATA_FOLDER, selected_dataset)}''')"
                )
                execute_code_in_kernel(kc, df_init_code)

                outputs, errors = execute_code_in_kernel(kc, ai_code)
                ai_outputs = [Markup(o) for o in (outputs + errors)]
                rendered_html = "".join(str(x) for x in (outputs + errors))

                from syntaxmatrix.commentary import (
                    MPL_PROBE_SNIPPET, MPL_IMAGE_PROBE_SNIPPET,
                    parse_mpl_probe_output, parse_image_probe_output,
                    build_display_summary, phrase_commentary_vision, wrap_html
                )


                # Probe axes/labels/legend
                probe1_out, probe1_err = execute_code_in_kernel(kc, MPL_PROBE_SNIPPET)
                axes_info = parse_mpl_probe_output([str(x) for x in (probe1_out + probe1_err)])

                # Probe figure images (PNG → base64)
                probe2_out, probe2_err = execute_code_in_kernel(kc, MPL_IMAGE_PROBE_SNIPPET)
                figs_info = parse_image_probe_output([str(x) for x in (probe2_out + probe2_err)])
                images_b64 = [fi.get("png_b64","") for fi in figs_info if isinstance(fi, dict) and fi.get("png_b64")]

                # Build context and get the vision commentary and append under the visuals
                display_summary = build_display_summary(refined_question, axes_info, [rendered_html])
                commentary_text = phrase_commentary_vision(display_summary, images_b64)
                ai_outputs.append(Markup(wrap_html(commentary_text)))               
                ################################################################

                # ----- Build a single HTML with Result + Commentary + AI Code ----------
                _buf_out, _buf_err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(_buf_out), contextlib.redirect_stderr(_buf_err):
                    # 1 Exact result blocks (already cleaned by kernel_manager)
                    result_html = rendered_html if rendered_html.strip() else "<pre>No output.</pre>"

                    # 2 Commentary (we already have the raw HTML via wrap_html)
                    commentary_html = wrap_html(commentary_text)

                    code_html = _render_code_block("AI Generated Code", ai_code)                

                    full_body_html = "\n" + askai_question + "\n" + result_html + "\n" + commentary_html + "\n" + code_html

                    html_doc = (
                      "<!doctype html>"
                      "<html>"
                        "<head>"
                          "<meta charset='utf-8'>"
                          "<title>Result</title>"
                          "<style>"
                          "  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 42px; padding:24 32; }"
                          "  img { max-width: 100%; height: auto; }"
                          "  table { border-collapse: collapse; margin: 16px 0; }"
                          "  th, td { border: 1px solid #ddd; padding: 6px 10px; }"
                          "</style>"                
                        "</head>"
                        "<body>"
                          + (full_body_html) +
                          "<script>_smxHighlightNow();</script>"
                        "</body>"
                      "</html>"
                    )

                    _last_result_html[session_id] = html_doc

                    # 2.4 Append a single download button (explicit click → fetch → download)
                    download_url = url_for("download_result_html", session_id=session_id)
                    dl_html = f"""
                      <a href="{download_url}">
                        <button type="button"
                                class="btn"
                                style="margin:14px 0;padding:8px 12px;border:1px solid #0b6;border-radius:6px;background:#fff;color:#0b6;cursor:pointer;">
                          Download
                        </button>
                      </a>
                    """
                    ai_outputs.append(Markup(dl_html))

                ################################################################


        # --- EDA/static cells ---
        data_cells = []
        if df is not None:
            num_records = df.shape
            ds = selected_dataset.replace("_"," ").replace(".csv","").capitalize()
            data_cells.append({
                "title": f"{ds} size",
                "output": num_records,
                "code": "df.shape"
            })
            preview_cols = df.columns[:8]
            data_cells.append({
                "title": "Data Preview",
                "output": Markup(datatable_box(df[preview_cols].head(8))),
                "code": f"df[{list(preview_cols)}].head(8)"
            })
            data_cells.append({
                "title": "Summary Statistics",
                "output": Markup(datatable_box(df.describe())),
                "code": "df.describe()"
            })
            nulls = df.isnull().sum()
            nulls_pct = (df.isnull().mean() * 100).round(1)
            missing_df = pd.DataFrame({
                "Missing Values": nulls,
                "Missing (%)": nulls_pct
            })
            missing = missing_df[missing_df["Missing Values"] > 0]
            data_cells.append({
                "title": "Missing Values",
                "output": Markup(datatable_box(missing)) if not missing.empty else "<em>No missing values detected.</em>",
                "code": (
                    "nulls = df.isnull().sum()\n"
                    "nulls_pct = (df.isnull().mean() * 100).round(1)\n"
                    "missing_df = pd.DataFrame({'Missing Values': nulls, 'Missing (%)': nulls_pct})\n"
                    "missing_df[missing_df['Missing Values'] > 0]"
                )
            })
            dtype_df = pd.DataFrame({
                "Type": df.dtypes.astype(str),
                "Non-Null Count": df.notnull().sum(),
                "Unique Values": df.nunique()
            })
            data_cells.append({
                "title": "Column Types",

                "output": Markup(datatable_box(dtype_df)),
                "code": (
                    "pd.DataFrame({\n"
                    "    'Type': df.dtypes.astype(str),\n"
                    "    'Non-Null Count': df.notnull().sum(),\n"
                    "    'Unique Values': df.nunique()\n"
                    "})"
                )
            })
            for cell in data_cells:
              cell["highlighted_code"] = Markup(_pygmentize(cell["code"]))
        highlighted_ai_code = _pygmentize(ai_code)
        return render_template(
          "dashboard.html",
          section=section,
          datasets=datasets,
          selected_dataset=selected_dataset,
          ai_outputs=ai_outputs,
          ai_code=ai_code,  # AI-generated code for toggle
          highlighted_ai_code=highlighted_ai_code if ai_code else None,
          askai_question=smx.sanitize_rough_to_markdown_task(askai_question),  
          refined_question=refined_question,  # Refined question
          data_cells=data_cells,
          session_id=session_id,
        )
    

    @smx.app.route("/download/result/html/<session_id>", methods=["GET"])
    def download_result_html(session_id):
        """Stream the last-built result HTML as a browser download (no server save)."""
        html_doc = _last_result_html.get(session_id)
        if not html_doc:
            return ("No result available.", 404)

        buf = io.BytesIO(html_doc.encode("utf-8"))
        buf.seek(0)

        # keep a copy if you wish, or free it:
        _last_result_html.pop(session_id, None)

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = f"result_{session_id}_{stamp}.html"
        return send_file(
            buf,
            mimetype="text/html; charset=utf-8",
            as_attachment=True,
            download_name=filename
        )
        
    # ── UPLOAD DATASET --------------------------------------
    @smx.app.route("/dashboard/upload", methods=["POST"])
    def upload_dataset():
        if "dataset_file" not in request.files:
            flash("No file part.")
            return redirect(url_for("dashboard"))
        file = request.files["dataset_file"]
        if file.filename == "":
            flash("No selected file.")
            return redirect(url_for("dashboard"))
        if file and file.filename.lower().endswith(".csv"):
            filename = werkzeug.utils.secure_filename(file.filename)
            file.save(os.path.join(DATA_FOLDER, filename))
            flash(f"Uploaded: {filename}")
        else:
            flash("Only CSV files are supported.")
        return redirect(url_for("dashboard"))
    
    # ── DELETE A DATASET --------------------------------------
    @smx.app.route("/dashboard/delete_dataset/<path:dataset_name>", methods=["POST"])
    def delete_dataset(dataset_name):
        file_path   = os.path.join(DATA_FOLDER, dataset_name)

        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                flash(f"Deleted {dataset_name}")
            except Exception as exc:
                flash(f"Could not delete {dataset_name}: {exc}", "error")
        else:
            flash(f"{dataset_name} not found.", "error")

        # go back to the dashboard; dashboard() will auto-select the next file
        return redirect(url_for("dashboard"))


    def _pdf_fallback_reportlab(full_html: str):
        """ReportLab fallback: extract text + base64 <img> and lay them out."""
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        import base64

        # Extract base64 images (PNG/JPEG/SVG-as-png)
        img_b64s = re.findall(
            r'src=["\']data:image/(?:png|jpeg|jpg);base64,([^"\']+)["\']',
            full_html, flags=re.I
        )

        # Strip scripts/styles, then crude HTML→text
        clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", full_html, flags=re.S|re.I)
        text = re.sub(r"<br\s*/?>", "\n", clean, flags=re.I)
        text = re.sub(r"</(p|div|li|h[1-6])>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = html.unescape(text).strip()
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
        styles = getSampleStyleSheet()
        flow = []

        # Title
        flow.append(Paragraph("Result", styles["Heading2"]))
        flow.append(Spacer(1, 6))

        # Paragraphs
        for para in [p.strip() for p in text.split("\n") if p.strip()]:
            flow.append(Paragraph(para, styles["Normal"]))
            flow.append(Spacer(1, 4))

        # Images (scaled to content width)
        max_w = 178 * mm  # A4 width minus margins
        for b64 in img_b64s:
            try:
                img_data = base64.b64decode(b64)
                flow.append(RLImage(io.BytesIO(img_data), width=max_w))
                flow.append(Spacer(1, 8))
            except Exception:
                continue

        doc.build(flow)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="result.pdf", mimetype="application/pdf")

    @smx.app.errorhandler(500)
    def internal_server_error(e):
      head = head_html()
      nav = _generate_nav()
      footer = footer_html()

      # now use render_template_string so we can drop the same head/nav/footer
      return render_template_string(f"""
        {head}
        <body>
          {nav}

          <div style="max-width:700px;margin:4rem auto;padding:2rem;
                      background:#fff;border-radius:8px;
                      box-shadow:0 4px 16px rgba(0,0,0,0.1);
                      text-align:center;">
            <div style="font-size:3rem;line-height:1;">😞</div>
            <h1 style="color:#c0392b;margin:1rem 0 2rem;
                      font-size:2rem;">
              Oops! Something went wrong.
            </h1>
            <pre style="background:#f4f4f4;padding:1rem;
                        border-radius:4px;text-align:left;
                        overflow-x:auto;max-height:200px;">
  {{{{ error_message }}}}
            </pre>
            <p>
              <a href="{{{{ url_for('home') }}}}"
                style="display:inline-block;
                        margin-top:2rem;
                        padding:0.75rem 1.25rem;
                        background:#007acc;
                        color:#fff;
                        text-decoration:none;
                        border-radius:4px;">
                ← Back to Home
              </a>
            </p>
          </div>

          {footer}
        </body> 
        </html>
      """, error_message=str(e)), 500