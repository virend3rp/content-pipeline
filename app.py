import streamlit as st
import json
import os
from pathlib import Path

st.set_page_config(page_title="Content Pipeline", page_icon="🎬", layout="wide")
st.title("Content Pipeline")

STYLES_DIR = Path("styles")
STYLES_DIR.mkdir(exist_ok=True)

def load_styles():
    styles = {}
    for f in sorted(STYLES_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as file:
            styles[f.stem] = json.load(file)
    return styles

tab1, tab2, tab3 = st.tabs(["Reddit → Script", "Add Style", "Style Library"])

# ── Tab 1: Reddit → Script ──────────────────────────────────────────────────
with tab1:
    st.header("Reddit → Script")

    styles = load_styles()
    if not styles:
        st.warning("No style profiles found. Add one in the 'Add Style' tab.")
    else:
        reddit_url = st.text_input("Reddit Post URL", placeholder="https://reddit.com/r/...")
        style_name = st.selectbox("Style Profile", list(styles.keys()))

        if st.button("Generate Script", type="primary"):
            if not reddit_url:
                st.error("Please enter a Reddit URL.")
            else:
                try:
                    with st.spinner("Scraping Reddit..."):
                        from reddit_scraper import scrape_reddit_post
                        reddit_data = scrape_reddit_post(reddit_url)

                    with st.spinner("Writing script..."):
                        from script_generator import generate_script
                        script = generate_script(reddit_data, styles[style_name])

                    st.subheader("Your Script")
                    st.text_area("", script, height=400)
                    st.download_button("Download Script", script, file_name="script.txt")

                except Exception as e:
                    st.error(f"Error: {e}")

# ── Tab 2: Add Style ────────────────────────────────────────────────────────
with tab2:
    st.header("Add Style Profile")
    st.info("Supports YouTube channels. For Instagram, download videos locally and upload transcripts below.")

    col1, col2 = st.columns(2)
    with col1:
        profile_name = st.text_input("Profile Name", placeholder="e.g. carry_minati")
        source_url = st.text_input("YouTube Channel / Playlist URL")
        hook_formula = st.text_input("Hook Formula", placeholder="e.g. Bhai ye dekho...")
    with col2:
        num_videos = st.slider("Videos to sample", 5, 30, 15)

    if st.button("Run Pipeline", type="primary"):
        if not profile_name or not source_url or not hook_formula:
            st.error("Please fill all fields.")
        else:
            progress = st.progress(0)
            status = st.empty()

            try:
                status.text("Downloading audio...")
                from pipeline.downloader import download_audio
                audio_files = download_audio(source_url, f"temp_{profile_name}", num_videos)
                progress.progress(33)

                status.text(f"Transcribing {len(audio_files)} files with Groq...")
                from pipeline.transcriber import transcribe_all
                transcripts = transcribe_all(audio_files)
                progress.progress(66)

                status.text("Extracting writing style with Claude...")
                from pipeline.style_extractor import extract_style
                style = extract_style(profile_name, source_url, hook_formula, transcripts)

                style_path = STYLES_DIR / f"{profile_name}.json"
                with open(style_path, "w", encoding="utf-8") as f:
                    json.dump(style, f, ensure_ascii=False, indent=2)

                progress.progress(100)
                status.empty()
                st.success(f"Style '{profile_name}' saved! Go to Style Library to view it.")

            except Exception as e:
                st.error(f"Pipeline failed: {e}")

# ── Tab 3: Style Library ─────────────────────────────────────────────────────
with tab3:
    st.header("Style Library")

    styles = load_styles()
    if not styles:
        st.info("No styles yet. Add one in the 'Add Style' tab.")
    else:
        for name, style in styles.items():
            with st.expander(f"**{name}**  —  {style.get('source', '')}"):
                st.markdown(f"**Hook Formula:** `{style.get('hook_formula', 'N/A')}`")
                st.markdown(f"**Created:** {style.get('created_at', 'N/A')[:10]}")
                st.markdown("**Writing Prompt:**")
                st.text(style.get("writing_prompt", "N/A"))

                if st.button(f"Delete {name}", key=f"del_{name}"):
                    (STYLES_DIR / f"{name}.json").unlink()
                    st.rerun()
