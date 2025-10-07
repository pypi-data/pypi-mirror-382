from __future__ import annotations
import os, webbrowser, uuid, secrets, re

from flask import Flask, Response, session, request, has_request_context
from syntaxmatrix.history_store import SQLHistoryStore as Store, PersistentHistoryStore as _Store
from collections import OrderedDict
from syntaxmatrix.llm_store import save_embed_model, load_embed_model, delete_embed_key
from . import db, routes
from .themes import DEFAULT_THEMES
from .ui_modes import UI_MODES
from .plottings import render_plotly, pyplot, describe_plotly
from .file_processor import process_admin_pdf_files
from google.genai import types
from .vector_db import query_embeddings
from .vectorizer import embed_text
from syntaxmatrix.settings.prompts import SMXAI_CHAT_ID, SMXAI_CHAT_INSTRUCTIONS, SMXAI_WEBSITE_DESCRIPTION
from typing import List, Generator
from .auth import init_auth_db
from . import profiles as _prof
from syntaxmatrix.utils import strip_describe_slice, drop_bad_classification_metrics
from syntaxmatrix.smiv import SMIV
from .project_root import detect_project_root
from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args 
from dotenv import load_dotenv
from html import unescape
from .plottings import render_plotly, pyplot, describe_plotly, describe_matplotlib
from threading import RLock

# ──────── framework‐local storage paths ────────
# this ensures the key & data always live under the package dir,
# regardless of where the developer `cd` into before launching.
_CLIENT_DIR = detect_project_root()
_HISTORY_DIR   = os.path.join(_CLIENT_DIR, "data", "smx_history")
os.makedirs(_HISTORY_DIR, exist_ok=True)

_SECRET_PATH = os.path.join(_CLIENT_DIR, "data", ".smx_secret_key")

dotenv_path  = os.path.join(str(_CLIENT_DIR.parent), ".env")
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path, override=True)

EDA_OUTPUT = {}  # global buffer for EDA output by session

class SyntaxMUI:
    def __init__(self, 
            host="127.0.0.1", 
            port="5050", 
            user_icon="👩🏿‍🦲",
            bot_icon="/static/icons/favicon.png",
            favicon="/static/icons/favicon.png",      
            site_logo="/static/icons/favicon.png",           
            site_title="SyntaxMatrix", 
            project_name="smxAI", 
            theme_name="light",
            ui_mode = "default"
        ):
        self.app = Flask(__name__)         
        self.host = host
        self.port = port

        self.get_app_secrete()
        self.user_icon = user_icon
        self.bot_icon = f"<img src='{bot_icon}' width='20' alt='bot'/>"
        self.site_logo = f"<img src='{site_logo}' width='30' alt='logo'/>"
        self.favicon = f"<link rel='icon' type='image/png' href='{favicon}'/>"
        self.site_title = site_title
        self.project_name = project_name
        self.ui_mode = ui_mode
        self.theme_toggle_enabled = False
        self.user_files_enabled = False
        self.ai_chat_id = SMXAI_CHAT_ID
        self.ai_chat_instructions = SMXAI_CHAT_INSTRUCTIONS    
        self.website_description = SMXAI_WEBSITE_DESCRIPTION
        self._eda_output = {}      # {chat_id: html}
        self._eda_lock = RLock()

        db.init_db()
        self.page = ""
        self.pages = db.get_pages()
        init_auth_db() 

        self.widgets = OrderedDict()
        self.theme = DEFAULT_THEMES.get(theme_name, DEFAULT_THEMES["light"])     
        self.system_output_buffer = ""  # Ephemeral buffer initialized  
        self.app_token = str(uuid.uuid4())  # NEW: Unique token for each app launch.
        self.admin_pdf_chunks = {}   # In-memory store for admin PDF chunks
        self.user_file_chunks = {}  # In-memory store of user‑uploaded chunks, scoped per chat session
        routes.setup_routes(self)
        
        self._admin_profile = {}
        self._chat_profile = {}
        self._coding_profile = {}
        self._classification_profile = {}
        self._summarization_profile = {}
            
        self._gpt_models_latest_prev_resp_ids = {}
        self.is_streaming = False
        self.stream_args = {}

        self._recent_visual_summaries = []

        self.placeholder = ""

    @staticmethod
    def init_app(app):
        import secrets
        if not app.secret_key:
            app.secret_key = secrets.token_urlsafe(32)

    def get_app_secrete(self):  # keeping your name
        if os.path.exists(_SECRET_PATH):
            self.app.secret_key = open(_SECRET_PATH, "r", encoding="utf-8").read().strip()
        else:
            new_key = secrets.token_urlsafe(32)
            with open(_SECRET_PATH, "w", encoding="utf-8") as f:
                f.write(new_key)
            try:
                os.chmod(_SECRET_PATH, 0o600)
            except Exception:
                pass
            self.app.secret_key = new_key
            

    def _get_visual_context(self):
        """Return the concatenated summaries for prompt injection."""
        if not self._recent_visual_summaries:
            return ""
        joined = "\n• " + "\n• ".join(self._recent_visual_summaries)
        return f"\n\nRecent visualizations:{joined}"

    # add to class
    def _add_visual_summary(self, summary: str) -> None:
        if not summary:
            return
        if not hasattr(self, "_recent_visual_summaries"):
            self._recent_visual_summaries = []
        # keep last 6
        self._recent_visual_summaries = (self._recent_visual_summaries + [summary])[-6:]

    def set_plottings(self, fig_or_html, note=None):
        # prefer current chat id; fall back to per-browser sid; finally "default"
        sid = self.get_session_id() or self._sid() or "default"

        # Clear for this session if empty/falsy
        if not fig_or_html or (isinstance(fig_or_html, str) and fig_or_html.strip() == ""):
            with self._eda_lock:
                self._eda_output.pop(sid, None)
            return

        html = None

        # ---- Plotly Figure support ----
        try:
            import plotly.graph_objs as go
            if isinstance(fig_or_html, go.Figure):
                html = fig_or_html.to_html(full_html=False)
        except ImportError:
            pass

        # ---- Matplotlib Figure support ----
        if html is None and hasattr(fig_or_html, "savefig"):
            html = pyplot(fig_or_html)

        # ---- Bytes (PNG etc.) support ----
        if html is None and isinstance(fig_or_html, bytes):
            import base64
            img_b64 = base64.b64encode(fig_or_html).decode()
            html = f"<img src='data:image/png;base64,{img_b64}'/>"

        # ---- HTML string support ----
        if html is None and isinstance(fig_or_html, str):
            html = fig_or_html

        if html is None:
            raise TypeError("Unsupported object type for plotting.")

        if note:
            html += f"<div style='margin-top:10px; text-align:center; color:#888;'><strong>{note}</strong></div>"

        wrapper = f'''
        <div style="
            position:relative; max-width:650px; margin:30px auto 20px auto;
            padding:20px 28px 10px 28px; background:#fffefc;
            border:2px solid #2da1da38; border-radius:16px;
            box-shadow:0 3px 18px rgba(90,130,230,0.06); min-height:40px;">
            <button id="eda-close-btn" onclick="closeEdaPanel()" style="
                position: absolute; top: 20px; right: 12px;
                font-size: 1.25em; background: transparent;
                border: none; color: #888; cursor: pointer;
                z-index: 2; transition: color 0.2s;">&times;</button>
            {html}
        </div>
        '''

        with self._eda_lock:
            self._eda_output[sid] = wrapper

        html = None

        # ---- Plotly Figure support ----
        try:
            import plotly.graph_objs as go
            if isinstance(fig_or_html, go.Figure):
                html = fig_or_html.to_html(full_html=False)
        except ImportError:
            pass

        # ---- Matplotlib Figure support ----
        if html is None and hasattr(fig_or_html, "savefig"):
            html = pyplot(fig_or_html)

        # ---- Bytes (PNG etc.) support ----
        if html is None and isinstance(fig_or_html, bytes):
            import base64
            img_b64 = base64.b64encode(fig_or_html).decode()
            html = f"<img src='data:image/png;base64,{img_b64}'/>"

        # ---- HTML string support ----
        if html is None and isinstance(fig_or_html, str):
            html = fig_or_html

        if html is None:
            raise TypeError("Unsupported object type for plotting.")

        if note:
            html += f"<div style='margin-top:10px; text-align:center; color:#888;'><strong>{note}</strong></div>"

        wrapper = f'''
        <div style="
            position:relative; max-width:650px; margin:30px auto 20px auto;
            padding:20px 28px 10px 28px; background:#fffefc;
            border:2px solid #2da1da38; border-radius:16px;
            box-shadow:0 3px 18px rgba(90,130,230,0.06); min-height:40px;">
            <button id="eda-close-btn" onclick="closeEdaPanel()" style="
                position: absolute; top: 20px; right: 12px;
                font-size: 1.25em; background: transparent;
                border: none; color: #888; cursor: pointer;
                z-index: 2; transition: color 0.2s;">&times;</button>
            {html}
        </div>
        '''
        EDA_OUTPUT[sid] = wrapper


    def get_plottings(self):
        sid = self.get_session_id() or self._sid() or "default"
        with self._eda_lock:
            return self._eda_output.get(sid, "")
    

    def load_sys_chunks(self, directory: str = "uploads/sys"):
        """
        Process all PDFs in `directory`, store chunks in DB and cache in-memory.
        Returns mapping { file_name: [chunk, ...] }.
        """
        mapping = process_admin_pdf_files(directory)
        self.admin_pdf_chunks = mapping
        return mapping


    def smpv_search(self, q_vec: List[float], top_k: int = 5):
        """
        Embed the input text and return the top_k matching PDF chunks.
        Each result is a dict with keys:
        - 'id': the embedding record UUID
        - 'score': cosine similarity score (0–1)
        - 'metadata': dict, e.g. {'file_name': ..., 'chunk_index': ...}
        """
        # 2) Fetch nearest neighbors from our sqlite vector store
        results = query_embeddings(q_vec, top_k=top_k)
        return results


    def set_ui_mode(self, mode):
        if mode not in self.get_ui_modes():  # ["default", "card", "bubble", "smx"]:
            raise ValueError("UI mode must be one of: 'default', 'card', 'bubble', 'smx'.")
        self.ui_mode = mode

    @staticmethod
    def get_ui_modes():
        return list(UI_MODES.keys())
        # return "default", "card", "bubble", "smx"
    
    @staticmethod
    def get_themes():
        return list(DEFAULT_THEMES.keys())


    def set_theme(self, theme_name, theme=None):
        if theme_name in DEFAULT_THEMES:
            self.theme = DEFAULT_THEMES[theme_name]
        elif isinstance(theme, dict):
            DEFAULT_THEMES[theme_name] = theme
            self.theme = DEFAULT_THEMES[theme_name]
        else:
            self.theme = DEFAULT_THEMES["light"]
            self.error("Theme must be 'light', 'dark', or a custom dict.")

    
    def enable_theme_toggle(self):
        self.theme_toggle_enabled = True 
    
    def enable_user_files(self):
        self.user_files_enabled = True
    
    @staticmethod
    def columns(components):
        col_html = "<div style='display:flex; gap:10px;'>"
        for comp in components:
            col_html += f"<div style='flex:1;'>{comp}</div>"
        col_html += "</div>"
        return col_html

    def set_site_title(self, title):
        self.site_title = title
    
    def set_project_name(self, project_name):
        self.project_name = project_name

    @staticmethod
    def set_favicon(self, favicon):
        self.favicon = favicon
    
    def get_favicon(self):
        return self.favicon

    def set_site_logo(self, logo):
        self.site_logo = logo if str(logo).strip().startswith("<") else f"<img src='{logo}' width='30' alt='SMX Logo'/>"

    def set_user_icon(self, icon):
        self.user_icon = icon 
        return _CLIENT_DIR

    def set_bot_icon(self, icon):
        self.bot_icon = icon

    def text_input(self, key, id, label, placeholder=""):
        if not placeholder:
            placeholder = f"Ask {self.project_name} anything"
        if key not in self.widgets:
            self.widgets[key] = {
                "type": "text_input", "key": key, "id": id,
                "label": label, "placeholder": placeholder
            }

    def clear_text_input_value(self, key):
        session[key] = ""
        session.modified = True
    

    def button(self, key, id, label, callback, stream=False):
        if stream == True:
            self.is_streaming = True
        self.widgets[key] = {
            "type": "button", "key": key, "id": id, "label": label, "callback": callback, "stream":stream
        }

    def file_uploader(self, key, id, label, accept_multiple_files):
        if key not in self.widgets:
            self.widgets[key] = {
                "type": "file_upload",
                "key": key, "id":id, "label": label,
                "accept_multiple": accept_multiple_files,
        }


    def get_file_upload_value(self, key):
        return session.get(key, None)
    

    def dropdown(self, key, options, label=None, callback=None):
        self.widgets[key] = {
            "type": "dropdown",
            "key": key,
            "label": label if label else key,
            "options": options,
            "callback": callback,
            "value": options[0] if options else None
        }


    def get_widget_value(self, key):
        return self.widgets[key]["value"] if key in self.widgets else None


    # ──────────────────────────────────────────────────────────────
    # Session-safe chat-history helpers
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def _sid() -> str:
        sid = session.get("_smx_sid")
        if not sid:
            # use the new _sid helper on the store instead of the old ensure_session_id
            sid = _Store._sid(request.cookies.get("_smx_sid"))
        session["_smx_sid"] = sid
        session.modified = True
        return sid
    

    def get_chat_history(self) -> list[tuple[str, str]]:
        # now load the history for the _current_ chat session
        sid = self._sid()
        cid = self.get_session_id()
        return _Store.load(sid, cid)
    

    def set_chat_history(self, history: list[tuple[str, str]], *, max_items: int | None = None) -> list[tuple[str, str]]:
        sid = self._sid()
        cid = self.get_session_id()
        _Store.save(sid, cid, history)
        session["chat_history"] = history[-30:]  # still mirror a thin copy into Flask’s session cookie for the UI
        session.modified = True

        if session.get("user_id"):
            user_id = session["user_id"]
            cid = session["current_session"]["id"]
            title = session["current_session"]["title"]
            # persist both title + history 
            Store.save(user_id, cid, history, title)

        return history if max_items is None else history[-max_items:]


    def clear_chat_history(self):
        """
        Clear both the UI slice *and* the server-side history bucket
        for this session_id + chat_id.
        """
        if has_request_context():
            sid = self._sid()
            cid = self.get_session_id()

            # wipe server history for this chat
            _Store.save(sid, cid, [])

            # clear UI mirror
            session["chat_history"] = []

            # clear EDA panel for this chat id
            try:
                with self._eda_lock:
                    self._eda_output.pop(cid, None)
            except Exception:
                pass

            if "current_session" in session:
                session["current_session"]["history"] = []
            if "past_sessions" in session:
                session["past_sessions"] = [
                    {**s, "history": []} if s.get("id") == cid else s
                    for s in session["past_sessions"]
                ]
            session.modified = True
        else:
            self._fallback_chat_history = []

    
    def bot_message(self, content, max_length=20):
        history = self.get_chat_history()
        history.append(("Bot", content))
        self.set_chat_history(history)


    def plt_plot(self, fig):
        summary = describe_matplotlib(fig)
        self._add_visual_summary(summary)          
        html = pyplot(fig)
        self.bot_message(html)

    def plotly_plot(self, fig):
        try:
            summary = describe_plotly(fig)
            self._add_visual_summary(summary)      
            html = render_plotly(fig)
            self.bot_message(html)
        except Exception as e:
            self.error(f"Plotly rendering failed: {e}")


    def write(self, content):
        self.bot_message(content)

    def stream_write(self, chunk: str, end=False):
        """Push a token to the SSE queue and, when end=True,
        persist the whole thing to chat_history."""
        from .routes import _stream_q
        _stream_q.put(chunk)              # live update
        if end:                           # final flush → history
            self.bot_message(chunk)       # persists the final message


    def error(self, content):
        self.bot_message(f'<div style="color:red; font-weight:bold;">{content}</div>')


    def warning(self, content):
        self.bot_message(f'<div style="color:orange; font-weight:bold;">{content}</div>')


    def success(self, content):
        self.bot_message(f'<div style="color:green; font-weight:bold;">{content}</div>')


    def info(self, content):
        self.bot_message(f'<div style="color:blue;">{content}</div>')

    
    def get_session_id(self):
        """Return the chat id that is currently *active* in the UI."""
        # Prefer a sticky id set by /load_session or when a new chat is started.
        sticky = session.get("active_chat_id")
        if sticky:
            return sticky
        return session.get("current_session", {}).get("id")

    def add_user_chunks(self, session_id, chunks):
        """Append these text‐chunks under that session’s key."""
        self.user_file_chunks.setdefault(session_id, []).extend(chunks)


    def get_user_chunks(self, session_id):
        """Get any chunks that this session has uploaded."""
        return self.user_file_chunks.get(session_id, [])


    def clear_user_chunks(self, session_id):
        """Remove all stored chunks for a session (on chat‑clear or delete)."""
        self.user_file_chunks.pop(session_id, None)

    # ──────────────────────────────────────────────────────────────
    #  *********** LLM CLIENT HELPERS  **********************
    # ──────────────────────────────────────────────────────────────
    def set_prompt_profile(self, profile):
        self.ai_chat_id = profile
    

    def set_prompt_instructions(self, instructions):
        self.ai_chat_instructions = instructions


    def set_website_description(self, desc):
        self.website_description = desc


    def embed_query(self, q):
        return embed_text(q)
    
    def smiv_index(self, sid):
            chunks = self.get_user_chunks(sid) or []
            count = len(chunks)

            # Ensure the per-session index stores for user text exist
            if not hasattr(self, "_user_indices"):
                self._user_indices = {}              # gloval dict for user vecs
                self._user_index_counts = {}         # global dict of user vec counts

            # store two maps: _user_indices and _user_index_counts
            if (sid not in self._user_indices or self._user_index_counts.get(sid, -1) != count):
                # (re)build
                try:
                    vecs = [embed_text(txt) for txt in chunks]
                except Exception as e:
                    # show the embedding error in chat and stop building the index
                    self.error(f"Failed to embed user documents: {e}")
                    return None
                index = SMIV(len(vecs[0]) if vecs else 1536)
                for i,(txt,vec) in enumerate(zip(chunks,vecs)):
                    index.add(vector=vec, metadata={"chunk_text": txt, "chunk_index": i, "session_id": sid})
                self._user_indices[sid] = index
                self._user_index_counts[sid] = count
            return self._user_indices[sid]

    def load_embed_model(self):
        client = load_embed_model()
        os.environ["PROVIDER"] = client["provider"]
        os.environ["MAIN_MODEL"] = client["model"]
        os.environ["OPENAI_API_KEY"] = client["api_key"]
        return client
    
    def save_embed_model(self, provider:str, model:str, api_key:str):
        return save_embed_model(provider, model, api_key)
    
    def delete_embed_key(self):
        return delete_embed_key()

    def gpt_models_latest(self):
        from syntaxmatrix.settings.model_map import GPT_MODELS_LATEST
        return GPT_MODELS_LATEST

    def get_text_input_value(self, key, default=""):
        q = session.get(key, default)
        
        intent = self.classify_query_intent(q)         
        intent = intent.strip().lower() if intent else ""
        if intent not in {"none","user_docs","system_docs","hybrid"}:
            self.error("Classify agency error")
            return q, None
        return q, intent

    def enable_stream(self):
        self.is_streaming = True 
    
    def stream(self):
        return self.is_streaming
    
    def get_stream_args(self):
        return self.stream_args


    def classify_query_intent(self, query: str) -> str:
        from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args 
   
        if not self._classification_profile:
            classification_profile = _prof.get_profile('classification') or _prof.get_profile('chat') or _prof.get_profile('admin')
            if not classification_profile:
                return {"Error": "Set a profile for Classification"}
            self._classification_profile = classification_profile
            self._classification_profile['client'] = _prof.get_client(classification_profile)

        _client = self._classification_profile['client']
        _provider = self._classification_profile['provider']
        _model = self._classification_profile['model']

        # New instruction format with hybrid option
        _intent_profile = "You are an intent classifier. Respond ONLY with the intent name."
        _instructions = f"""
            Classify the given query into ONE of these intents You must return ONLY the intent name with no comment or any preamble:
            - "none": Casual chat/greetings
            - "user_docs": Requires user-uploaded documents
            - "system_docs": Requires company knowledge/docs
            - "hybrid": Requires BOTH user docs AND company docs
            
            Examples:
            Query: "Hi there!" → none
            Query: "Explain my uploaded contract" → user_docs
            Query: "What's our refund policy?" → system_docs
            Query: "How does my proposal align with company guidelines?" → hybrid
            Query: "What is the weather today?" → none
            Query: "Cross-reference the customer feedback from my uploaded survey results with our product's feature list in the official documentation." → hybrid

            Now classify:
            Query: "{query}"
            Intent: 
        """
        openai_sdk_messages = [
            {"role": "system", "content": _intent_profile},
            {"role": "user", "content": _instructions}
        ]

        def google_classify_query():
            response = _client.models.generate_content(
                model=_model,
                contents=f"{_intent_profile}\n{_instructions}\n\n"
            )
            return response.text.strip().lower()

        def gpt_models_latest_classify_query(reasoning_effort = "medium", verbosity = "low"):
                             
            args = set_args(
                model=_model,
                instructions=_intent_profile,
                input=_instructions,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
            )
            try:
                resp = _client.responses.create(**args)
                answer = _out(resp).strip().lower() 
                return answer if answer else ""
            except Exception as e:
                return f"Error!"
        
        def anthropic_classify_query():       
            try:
                response = _client.messages.create(
                    model=_model,
                    max_tokens=1024,
                    system=_intent_profile,
                    messages=[{"role": "user", "content":_instructions}],
                    stream=False,
                )
                return response.content[0].text.strip()    
                   
            except Exception as e:
                return f"Error: {str(e)}"

        def openai_sdk_classify_query():
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=openai_sdk_messages,
                    temperature=0,
                    max_tokens=100
                )
                intent = response.choices[0].message.content.strip().lower()
                return intent if intent else ""
            except Exception as e:
                return f"Error!"

        if _provider == "google":
            intent = google_classify_query()
            return intent
        if _model in self.gpt_models_latest():
            intent = gpt_models_latest_classify_query()
            return intent
        if _provider == "anthropic":
            intent = anthropic_classify_query()
            return intent
        else:
            intent = openai_sdk_classify_query()
            return intent
     

    def generate_contextual_title(self, chat_history):
        
        if not self._summarization_profile:
            summarization_profile = _prof.get_profile('summarization') or _prof.get_profile('chat') or _prof.get_profile('admin') 
            if not summarization_profile:
                return {"Error": "Chat profile not set yet."}
            
            self._summarization_profile = summarization_profile
            self._summarization_profile['client'] = _prof.get_client(summarization_profile)

        conversation = "\n".join([f"{role}: {msg}" for role, msg in chat_history])
        _title_profile = "You are a title generator that creates concise and relevant titles for the given conversations."
        _instructions = f"""
            Generate a contextual title (5 short words max) from the given Conversation History 
            The title should be concise - with no preamble, relevant, and capture the essence of this Conversation: \n{conversation}.\n\n
            return only the title.
        """
        
        _client = self._summarization_profile['client']
        _provider = self._summarization_profile['provider']
        _model = self._summarization_profile['model']

        def google_generated_title():
            try:
                response = _client.models.generate_content(
                    model=_model,
                    contents=f"{_title_profile}\n{_instructions}"
                )
                return response.text.strip()
            except Exception as e:
                return f"Summary agent error!"

        def gpt_models_latest_generated_title(reasoning_effort = "minimal", verbosity = "low"):
            try:                 
                args = set_args(
                    model=_model,
                    instructions=_title_profile,
                    input=_instructions,
                    reasoning_effort=reasoning_effort,
                    verbosity=verbosity,
                )
            
                resp = _client.responses.create(**args)
                return _out(resp).strip()
            except Exception as e:
                return f"Summary agent error!"
        
        def anthropic_generated_title():       
            try:
                response = _client.messages.create(
                    model=_model,
                    max_tokens=1024,
                    system=_title_profile,
                    messages=[{"role": "user", "content":_instructions}],
                    stream=False,
                )
                return response.content[0].text.strip()  
            except Exception as e:
                return f"Summary agent error!"
            
        def openai_sdk_generated_title():     
            prompt = [
                { "role": "system", "content": _title_profile }, 
                { "role": "user", "content": _instructions },
            ]

            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=prompt,
                    temperature=0,
                    max_tokens=50
                ) 
                title = response.choices[0].message.content.strip().lower()
                return title if title else ""
            except Exception as e:
               return f"Summary agent error!"

        if _provider == "google":
            title = google_generated_title()
        elif _model in self.gpt_models_latest():
            title = gpt_models_latest_generated_title()
        elif _provider == "anthropic":
            title = anthropic_generated_title()
        else:
            title = openai_sdk_generated_title()
        return title
    

    def stream_process_query(self, query, context, conversations, sources):
        self.stream_args['query'] = query
        self.stream_args['context'] = context
        self.stream_args['conversations'] = conversations
        self.stream_args['sources'] = sources
    

    def process_query_stream(self, query: str, context: str, history: list, stream=True) -> Generator[str, None, None]:
       
        if not self._chat_profile:
            chat_profile = _prof.get_profile("chat") or _prof.get_profile("admin")
            if not chat_profile:
                yield """<p style='color:red;'>Error: Chat profile is not configured. Add a chat profile inside the admin panel or contact your administrator.</p>
                """
                return
            self._chat_profile = chat_profile
            self._chat_profile['client'] = _prof.get_client(chat_profile)

        _provider = self._chat_profile['provider']
        _client = self._chat_profile['client']
        _model = self._chat_profile['model']

        _contents = f"""
            {self.ai_chat_instructions}\n\n 
            Question: {query}\n
            Context: {context}\n\n
            History: {history}\n\n
            Use conversation continuity if available.
        """       
        
        try:
            if _provider == "google":     # Google, non openai skd series                 
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=f"{self.ai_chat_id}\n\n{_contents}"),
                        ],
                    ),
                ]
                
                for chunk in _client.models.generate_content_stream(
                    model=_model,
                    contents=contents,
                ):
                    yield chunk.text
        
            elif _provider == "openai" and _model in self.gpt_models_latest():  # GPt 5 series
                input_prompt = (
                    f"{self.ai_chat_instructions}\n\n"
                    f"Generate a response to this query:\n{query}\n"
                    f"based on this given context:\n{context}\n\n"
                    f"(Use conversation continuity if available.)"
                )
                sid = self.get_session_id()
                prev_id = self._gpt_models_latest_prev_resp_ids.get(sid)
                args = set_args(model=_model, instructions=self.ai_chat_id, input=input_prompt, previous_id=prev_id, store=True)
                
                with _client.responses.stream(**args) as s:
                    for event in s:
                        if event.type == "response.output_text.delta" and event.delta:
                            yield event.delta
                        elif event.type == "response.error":
                            raise RuntimeError(str(event.error))
                    final = s.get_final_response()
                    if getattr(final, "id", None):
                        self._gpt_models_latest_prev_resp_ids[sid] = final.id
            
            elif _provider == "anthropic":
                with _client.messages.stream(
                    max_tokens=1024,
                    messages=[{"role": "user", "content":f"{self.ai_chat_id}\n\n {_contents}"},],
                    model=_model,
                ) as stream:
                    for text in stream.text_stream:
                        yield text  # end="", flush=True
                    
            else:  # Assumes standard openai_sdk
                openai_sdk_prompt = [
                    {"role": "system", "content": self.ai_chat_id},
                    {"role": "user", "content": f"{self.ai_chat_instructions}\n\nGenerate response to this query: {query}\nbased on this context:\n{context}\nand history:\n{history}\n\nUse conversation continuity if available.)"},
                ]
                response = _client.chat.completions.create(
                    model=_model, 
                    messages=openai_sdk_prompt, 
                    stream=True,
                )
                for chunk in response:
                    token = getattr(chunk.choices[0].delta, "content", "")
                    if token:
                        yield token
        except Exception as e:
            yield f"Error during streaming: {type(e).__name__}: {e}"
    
    def process_query(self, query, context, history, stream=False):

        if not self._chat_profile:
            chat_profile = _prof.get_profile("chat") or _prof.get_profile("admin")
            if not chat_profile:
                return """<p style='color:red;'>Error: Chat profile is not configured. Add a chat profile inside the admin panel or contact your administrator.</p>
                """
                return
                 
            self._chat_profile = chat_profile
            self._chat_profile['client'] = _prof.get_client(chat_profile) 
        
        _contents = f"""
                    {self.ai_chat_instructions}\n\n 
                    Question: {query}\n
                    Context: {context}\n\n
                    History: {history}\n\n
                    Use conversation continuity if available.
                """
        
        openai_sdk_prompt = [
                {"role": "system", "content": self.ai_chat_id},
                {"role": "user", "content": f"""{self.ai_chat_instructions}\n\n
                                                Generate response to this query: {query}\n
                                                based on this context:\n{context}\n
                                                and history:\n{history}\n\n
                                                Use conversation continuity if available.)
                                            """
                },
            ]

        _provider = self._chat_profile['provider']
        _client = self._chat_profile['client']
        _model = self._chat_profile['model']

        def google_process_query():
            try:
                response = _client.models.generate_content(
                    model=_model,
                    contents=f"{self.ai_chat_id}\n\n{_contents}"
                )
                answer = response.text
                
                # answer = strip_html(answer)
                return answer
            except Exception as e:
                return f"Error: {str(e)}"

        def gpt_models_latest_process_query(previous_id: str | None, reasoning_effort = "minimal", verbosity = "low"):
            """
            Returns (answer_text, new_response_id)
            """
            # Prepare the prompt with conversation history and context
            input = (
                f"{self.ai_chat_instructions}\n\n"
                f"Generate a response to this query:\n{query}\n"
                f"based on this given context:\n{context}\n\n"
                f"(Use conversation continuity if available.)"
            )

            sid = self.get_session_id()
            prev_id = self._gpt_models_latest_prev_resp_ids.get(sid)
            
            args = set_args(
                model=_model,
                instructions=self.ai_chat_id,
                input=input,
                previous_id=prev_id,
                store=True,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity
            )
            try:
                # Non-stream path
                resp = _client.responses.create(**args)
                answer = _out(resp)
                if getattr(resp, "id", None):
                    self._gpt_models_latest_prev_resp_ids[sid] = resp.id
                
                # answer = strip_html(answer)
                return answer

            except Exception as e:
                return f"Error: {type(e).__name__}: {e}"
                     
        def anthropic_process_query():      
            try:
                response = _client.messages.create(
                    model=_model,
                    max_tokens=1024,
                    system=self.ai_chat_id,
                    messages=[{"role": "user", "content":_contents}],
                    stream=False,
                )
                return response.content[0].text.strip()    
                   
            except Exception as e:
                return f"Error: {str(e)}"

        def openai_sdk_process_query():
        
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=openai_sdk_prompt,
                stream=False,
                )

                # -------- one-shot buffered --------
                answer = response.choices[0].message.content .strip() 
                return answer
            except Exception as e:
                return f"Error: {str(e)}"
  
        if _provider == "google":
            return google_process_query()
        if _provider == "openai" and _model in self.gpt_models_latest():
            return gpt_models_latest_process_query(self._gpt_models_latest_prev_resp_ids.get(self.get_session_id()))
        if _provider == "anthropic":
            return anthropic_process_query()
        return openai_sdk_process_query()


    def ai_generate_code(self, question, intent, df):
    
        if not self._coding_profile:            
            coding_profile = _prof.get_profile("coding") or _prof.get_profile("admin")
            if not coding_profile:
                # tell the user exactly what to configure
                return (
                    '<div class="smx-alert smx-alert-warn">'
                        'No LLM profile configured for <code>coding</code> (or <code>admin</code>). '
                        'Please,  contact your Administrator.'
                    '</div>'
                )

            self._coding_profile = coding_profile
            self._coding_profile['client'] = _prof.get_client(coding_profile)

        _client = self._coding_profile['client'] 
        _provider = self._coding_profile['provider']
        _model = self._coding_profile['model']

        context = f"Columns: {list(df.columns)}\n\nDtypes: {df.dtypes.astype(str).to_dict()}\n\n"
        ALLOWED_COLUMNS = list(df.columns)

        ai_profile = f"""
        You are a senior Python data scientist writing production-quality, **runnable** code for a Jupyter-like kernel. You are given a pandas DataFrame named `df`. Begin ONLY the data already in `df` (no file I/O).
        """

        instructions = f"""
        ### Context
        - Schema (names → dtypes): {context}
        - Row count: {len(df)}
        - Task: {question}
        - Task type: {intent}
        - Allowed columns: {ALLOWED_COLUMNS}

        ### Hard requirements
        1) **Code only**. No markdown, no comments, no explanations.
        2) Import everything you use explicitly. Assume: pandas≥2, numpy≥1.25, matplotlib≥3.8, seaborn≥0.13, scikit-learn≥1.4 are available.
        3) **Avoid deprecated / removed APIs**, e.g.:
        - pandas: do not use `.append`, `.ix`, `.as_matrix`, `DataFrame.select_dtypes(include='category')` is OK, but prefer current patterns.
        - seaborn: do not use `distplot`, `pairplot` on very large data without sampling; prefer `histplot`, `displot`, `regplot`, or FacetGrid with `.map_dataframe`.
        - scikit-learn: import from `sklearn.model_selection` (not `sklearn.cross_validation`); for confusion matrices use `ConfusionMatrixDisplay.from_estimator`; set `random_state=42` where relevant.
        4) Be **defensive**:
        - Verify required columns exist; if any are missing, raise `ValueError("Missing columns: ...")` early.
        - Handle missing values sensibly (e.g., drop rows for simple EDA; use `ColumnTransformer` + `SimpleImputer` for modeling).
        - For categorical features in ML, use `OneHotEncoder(handle_unknown="ignore")` inside a `Pipeline`/`ColumnTransformer` (no `LabelEncoder` on features).
        5) Keep it **fast** (kernel timeout ~8s):
        - For plots on large frames (>20k rows), downsample to ~1,000 rows (`df.sample(1000, random_state=42)`) unless aggregation is more appropriate.
        - Prefer vectorized ops; avoid O(n²) Python loops.
        6) Always **produce at least one visible result** at the end:
        - If plotting with matplotlib/seaborn: call `plt.tight_layout(); plt.show()`.
        - If producing a table or metrics: from `syntaxmatrix.display import show` then `show(object_or_dataframe)`.
        7) Follow task type conventions:
        - **EDA/Stats**: compute the requested stat, then show a relevant table (e.g., summary/crosstab) or plot.
        - **Classification**: train/valid split (`train_test_split`), build a pipeline with scaling/encoding as needed, fit, show accuracy **and** a confusion matrix via `ConfusionMatrixDisplay.from_estimator(...); plt.show()`. Also show `classification_report` as a dataframe if short.
        - **Regression**: train/valid split, pipeline as needed, fit, show R² and MAE; plot predicted vs actual scatter.
        - **Correlation/Chi-square/ANOVA**: compute the statistic + p-value and show a concise result table (with `show(...)`) and, when sensible, a small plot (heatmap/bar).
        8) Don't mutate or recreate target columns if they already exist (e.g., if asked to “predict TARGET”, use `y = df['TARGET']` as-is).
        9) Keep variable names short and clear; prefer `num_cols` / `cat_cols` discovery by dtype.
        10) You MUST NOT reference any column outside Allowed columns: {ALLOWED_COLUMNS}\n. 
        11) If asked to predict/classify, choose the target by matching the task text to Allowed columns: {ALLOWED_COLUMNS}\n and never invent a new name (e.g., 'whether', 'the').

        ### Output
        Return **only runnable Python** that:
        - Imports what it needs,
        - Validates columns,
        - Solves: {question},
        - And ends with at least one visible output (`show(...)` and/or `plt.show()`).
        """
        
        def google_generate_code():
            try:
                # Combine system prompt and instructions for Gemini
                full_prompt = f"{ai_profile}\n\n{instructions}"
                
                # Gemini expects a simple generate_content call with the model and contents
                response = _client.models.generate_content(
                    model=_model, 
                    contents=full_prompt
                )
                
                # Extract text from response
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate.content, 'parts'):
                        return ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                return str(response)
                    
            except Exception as e:
                print(f"Google Gemini code generation error: {e}")
                # Return a basic analysis code with ALL necessary imports
                return """
                import pandas as pd
                import matplotlib.pyplot as plt
                import seaborn as sns
                import numpy as np
                import io
                import base64
                from syntaxmatrix.display import show

                print("Basic DataFrame Info:")
                print(f"Shape: {df.shape}")
                print("\\nColumns and dtypes:")
                print(df.dtypes)
                print("\\nBasic statistics:")
                show(df.describe())

                print("\\nFirst few rows:")
                show(df.head())

                # Generate a simple visualization based on available columns
                plt.figure(figsize=(10, 6))

                if len(df.columns) >= 2:
                    # Try to find numeric columns for scatter plot
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) >= 2:
                        sns.scatterplot(data=df, x=numeric_cols[0], y=numeric_cols[1])
                        plt.title(f"Scatter plot: {numeric_cols[0]} vs {numeric_cols[1]}")
                        plt.tight_layout()
                        plt.show()
                    else:
                        # Use first column for bar plot
                        top_values = df[df.columns[0]].value_counts().head(10)
                        top_values.plot(kind='bar')
                        plt.title(f"Top 10 values in {df.columns[0]}")
                        plt.tight_layout()
                        plt.show()
                else:
                    # Single column analysis
                    if len(df.columns) == 1:
                        col_name = df.columns[0]
                        if df[col_name].dtype in ['object', 'category']:
                            df[col_name].value_counts().head(10).plot(kind='bar')
                            plt.title(f"Value counts for {col_name}")
                        else:
                            df[col_name].hist(bins=20)
                            plt.title(f"Distribution of {col_name}")
                        plt.tight_layout()
                        plt.show()
                    else:
                        print("Insufficient columns for detailed analysis")
                        show(df)
                """

        def gpt_models_latest_generate_code(reasoning_effort = "medium", verbosity = "medium"):
            try:                 
                args = set_args(
                    model=_model,
                    instructions=ai_profile,
                    input=instructions,
                    reasoning_effort=reasoning_effort,
                    verbosity=verbosity,
                )
            
                resp = _client.responses.create(**args)
                code = _out(resp)
                return code
            except Exception as e:
                return f"Error!"

        def anthropic_generate_code():        
            try:
                response = _client.messages.create(
                    model=_model,
                    max_tokens=1024,
                    system=ai_profile,
                    messages=[{"role": "user", "content":instructions}],
                    stream=False,
                )
                return response.content[0].text.strip()    
            except Exception as e:
                return f"Error!"

        def openai_sdk_generate_code():
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=[
                        {"role": "system", "content": ai_profile},
                        {"role": "user", "content": instructions},
                        ],
                    temperature=0.3,
                    max_tokens=2048,
                )
                return response.choices[0].message.content
            except Exception as e:
                return "Error!"

        if _provider == 'google':
            code = google_generate_code()
        elif _provider == "openai" and _model in self.gpt_models_latest():
            code = gpt_models_latest_generate_code()
        elif _provider == "anthropic":
            code = anthropic_generate_code()
        else:
            code = openai_sdk_generate_code()
        
        if code:
            m = re.search(r"```(?:python)?\s*(.*?)\s*```", code, re.DOTALL | re.IGNORECASE)
            if m:
                code = m.group(1).strip()
            code = drop_bad_classification_metrics(code, df)

            if "import io" not in code and "io.BytesIO" in code:
                lines = code.split('\n')
                import_lines = []
                other_lines = []
                
                for line in lines:
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_lines.append(line)
                    else:
                        other_lines.append(line)
                
                # Add missing io import
                if "import io" not in '\n'.join(import_lines):
                    import_lines.append('import io')
                
                code = '\n'.join(import_lines + [''] + other_lines)
        
            return code.strip()
    

    def sanitize_rough_to_markdown_task(self, rough: str) -> str:
        """
        Return only the Task text (no tags).
        Behaviour:
        - If <Task>...</Task> exists: return its inner text.
        - If not: return the input with <rough> wrapper and any <Error> blocks removed.
        - Never raises; always returns a string.
        """
        s = ("" if rough is None else str(rough)).strip()

        def _find_ci(hay, needle, start=0):
            return hay.lower().find(needle.lower(), start)

        # Prefer explicit <Task>...</Task>
        i = _find_ci(s, "<task")
        if i != -1:
            j = s.find(">", i)
            k = _find_ci(s, "</task>", j + 1)
            if j != -1 and k != -1:
                return s[j + 1:k].strip()
        # Otherwise strip any <Error>...</Error> blocks (if present)
        out = s
        while True:
            e1 = _find_ci(out, "<error")
            if e1 == -1:
                break
            e1_end = out.find(">", e1)
            e2 = _find_ci(out, "</error>", (e1_end + 1) if e1_end != -1 else e1 + 1)
            if e1_end == -1 or e2 == -1:
                break
            out = out[:e1] + out[e2 + len("</error>"):]

        # Drop optional <rough> wrapper
        return out.replace("<rough>", "").replace("</rough>", "").strip()


    def run(self):
        url = f"http://{self.host}:{self.port}/"
        webbrowser.open(url)
        self.app.run(host=self.host, port=self.port, debug=False)
