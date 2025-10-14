import streamlit as st
import pandas as pd
from io import BytesIO
import asyncio
import nest_asyncio
from datetime import datetime
import re
import os
from typing import List, Dict, Optional
import json
import base64

# Import modules
from scraper import NewsScraper
from sentiment_analyzer import SentimentAnalyzer
from journalist_detector import JournalistDetector
from summarizer import ArticleSummarizer

class NewsAnalyzerApp:
    def __init__(self):
        self.scraper = NewsScraper()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.journalist_detector = JournalistDetector()
        self.summarizer = ArticleSummarizer()
        
        # Set API key from Streamlit secrets
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            self.sentiment_analyzer.set_api_key(GEMINI_API_KEY)
            self.summarizer.set_api_key(GEMINI_API_KEY)
        
        # Apply nest_asyncio to allow running asyncio in Streamlit
        nest_asyncio.apply()

    def setup_page(self):
        st.set_page_config(
            page_title="The Senticon",
            page_icon="The Senticon.png",
            layout="wide"
        )
        
        # Custom CSS for modern look
        st.markdown("""
            <style>
                /* Use Streamlit theme variables for dark/light mode compatibility */
                :root {
                    --card-background-color: var(--streamlit-secondary-background-color);
                    --card-border-color: var(--streamlit-gray-20);
                    --tab-inactive-background-color: var(--streamlit-gray-10);
                }
                
                /* Main container styling */
                .main .block-container {
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                }
                
                /* Card-like containers for input area */
                .st-emotion-cache-z5fcl4 {
                    border-radius: 10px;
                    padding: 20px !important;
                    border: 1px solid var(--card-border-color);
                    background-color: var(--card-background-color);
                }
                
                /* Metric styling */
                .st-emotion-cache-1g6gooi {
                    border-radius: 10px;
                    padding: 15px;
                    background-color: var(--card-background-color);
                    border: 1px solid var(--card-border-color);
                }
                
                /* Button styling */
                .stButton>button {
                    border-radius: 8px;
                    font-weight: bold;
                }
                
                /* Modern Tab styling with bottom border */
                .stTabs [data-baseweb="tab-list"] {
                    gap: 2px; /* Reduce gap between tabs */
                }
                .stTabs [data-baseweb="tab"] {
                    height: 50px;
                    white-space: pre-wrap;
                    background-color: transparent; /* Remove background */
                    border-radius: 4px 4px 0 0;
                    gap: 8px;
                    padding: 10px;
                    border-bottom: 2px solid transparent; /* Inactive state */
                    transition: border-color 0.3s ease, color 0.3s ease;
                }
                .stTabs [data-baseweb="tab"]:hover {
                    background-color: var(--tab-inactive-background-color);
                }
                .stTabs [aria-selected="true"] {
                    background-color: transparent;
                    font-weight: bold;
                    border-bottom: 2px solid var(--streamlit-primary-color); /* Active state */
                }
            </style>
        """, unsafe_allow_html=True)

        with open("The Senticon.png", "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(f"""
            <style>
            .title-container {{
                display: flex;
                align-items: center; /* Vertically center items */
                gap: 15px;           /* Space between logo and title */
            }}
            </style>
            <div class="title-container">
                <img src="data:image/png;base64,{data}" width="60">
                <h1>The Senticon</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("Tool cerdas untuk ekstraksi, analisis sentimen, deteksi jurnalis, dan peringkasan artikel berita.")

    def setup_sidebar(self):
        with st.sidebar:
            st.header("⚙️ Konfigurasi")
            
            with st.expander("🎯 **Pilih Fungsi Analisis**", expanded=True):
                enable_scraping = st.checkbox("📄 Tarik Full Teks Berita", value=True, help="Mengambil konten lengkap berita dari URL")
                enable_date = st.checkbox("📅 Deteksi Tanggal Rilis", value=True, help="Mendeteksi tanggal publikasi artikel")
                enable_sentiment = st.checkbox("😊 Analisis Sentimen", value=False, help="Menganalisis sentimen berdasarkan konteks")
                enable_journalist = st.checkbox("👤 Deteksi Jurnalis", value=False, help="Mendeteksi nama penulis/jurnalis")
                enable_summarize = st.checkbox("📝 Summarize Artikel", value=False, help="Membuat ringkasan artikel menggunakan AI")

            sentiment_context = None
            summarize_config = {}
            scraping_timeout = 30

            if enable_sentiment:
                with st.expander("😊 **Konfigurasi Sentimen**"):
                    sentiment_context = st.text_area(
                        "Konteks Sentimen",
                        placeholder="Contoh: Toyota Avanza, harga mobil, kualitas produk",
                        help="Masukkan objek/aspek untuk analisis sentimen"
                    )

            if enable_summarize:
                with st.expander("📝 **Konfigurasi Summarize**"):
                    summarize_config = {
                        'summary_type': st.selectbox(
                            "Tipe Ringkasan",
                            ["Ringkas", "Detail", "Poin-poin Utama", "Custom"],
                            help="Pilih jenis ringkasan yang diinginkan"
                        ),
                        'max_length': st.slider(
                            "Panjang Maksimal (kata)", 50, 500, 150, 25,
                            help="Jumlah kata maksimal dalam ringkasan"
                        ),
                        'language': st.selectbox(
                            "Bahasa Ringkasan",
                            ["Bahasa Indonesia", "English", "Sama dengan artikel"],
                            help="Bahasa yang digunakan untuk ringkasan"
                        ),
                        'focus_aspect': st.text_input(
                            "Aspek yang Difokuskan (Opsional)",
                            placeholder="Contoh: aspek ekonomi, dampak sosial",
                            help="Aspek tertentu yang ingin difokuskan dalam ringkasan"
                        )
                    }
                    if summarize_config['summary_type'] == 'Custom':
                        summarize_config['custom_instruction'] = st.text_area(
                            "Instruksi Custom",
                            placeholder="Contoh: Buat ringkasan format bullet points fokus pada angka dan statistik",
                            help="Instruksi khusus untuk pembuatan ringkasan"
                        )

            if enable_scraping:
                with st.expander("🔧 **Opsi Scraping**"):
                    scraping_timeout = st.slider(
                        "Timeout (detik)", 10, 60, 30,
                        help="Waktu tunggu maksimal untuk setiap URL"
                    )
        
        return {
            'enable_scraping': enable_scraping,
            'enable_date': enable_date,
            'enable_sentiment': enable_sentiment,
            'enable_journalist': enable_journalist,
            'enable_summarize': enable_summarize,
            'sentiment_context': sentiment_context,
            'summarize_config': summarize_config,
            'scraping_timeout': scraping_timeout
        }

    def get_column_mapping(self, df: pd.DataFrame, input_method: str):
        """Get column mapping for Excel files"""
        if input_method != "Upload File Excel":
            return {}
        
        st.subheader("📋 Mapping Kolom")
        st.info("Pilih kolom yang sesuai dari file Excel Anda")
        
        col1, col2 = st.columns(2)
        
        with col1:
            url_column = st.selectbox(
                "Kolom URL",
                options=df.columns.tolist(),
                index=0 if 'URL' in df.columns else 0,
                help="Pilih kolom yang berisi URL artikel"
            )
        
        with col2:
            snippet_column = st.selectbox(
                "Kolom Snippet (Opsional)",
                options=["Tidak Ada"] + df.columns.tolist(),
                index=df.columns.tolist().index('Snippet') + 1 if 'Snippet' in df.columns else 0,
                help="Pilih kolom yang berisi snippet/ringkasan artikel"
            )
        
        return {
            'url_column': url_column,
            'snippet_column': snippet_column if snippet_column != "Tidak Ada" else None
        }

    async def process_single_url_async(self, url: str, config: Dict) -> Dict:
        """Asynchronously process a single URL."""
        try:
            result = {'URL': url}
            content = ""
            scraping_success = False
            article_data = {}

            # 1. Scraping (if enabled)
            if config['enable_scraping']:
                article_data = await self.scraper.scrape_article(
                    url,
                    timeout=config['scraping_timeout']
                )
                
                if article_data and article_data.get('content') and len(article_data.get('content', '').strip()) > 100:
                    result['Title'] = article_data.get('title', 'Gagal mengambil judul')
                    result['Publish_Date'] = article_data.get('publish_date', '')
                    result['Content'] = article_data.get('content', '')
                    result['Scraping_Method'] = article_data.get('method', 'unknown')
                    content = article_data.get('content', '')
                    scraping_success = True
                else:
                    result['Title'] = self.scraper.get_title_newspaper3k(url) # Fallback title
                    result['Content'] = 'Gagal scraping - konten tidak memadai'
                    result['Scraping_Method'] = 'failed'
            else:
                # Basic extraction if scraping is disabled but other features need content
                article_data = await self.scraper.scrape_article(url, basic_only=True)
                if article_data and len(article_data.get('content', '').strip()) > 100:
                    content = article_data.get('content', '')
                    scraping_success = True

            # 2. Journalist Detection
            if config['enable_journalist']:
                if scraping_success and content:
                    result['Journalist'] = self.journalist_detector.detect_journalist(article_data, content)
                else:
                    result['Journalist'] = 'Tidak diproses - scraping gagal'

            # 3. Sentiment Analysis
            if config['enable_sentiment'] and config['sentiment_context']:
                analysis_text = ""
                analysis_source = "none"

                if scraping_success and len(content.strip()) > 100:
                    analysis_text = content
                    analysis_source = "content"
                elif result.get('Title') and result['Title'] != 'Gagal mengambil judul':
                    analysis_text = result['Title']
                    analysis_source = "title"

                if analysis_text:
                    sentiment = self.sentiment_analyzer.analyze_sentiment(analysis_text, config['sentiment_context'])
                    if sentiment:
                        result.update({
                            'Sentiment': sentiment.get('sentiment', 'Gagal analisis'),
                            'Confidence': sentiment.get('confidence', ''),
                            'Reasoning': sentiment.get('reasoning', ''),
                            'Sentiment_Source': analysis_source
                        })
                    else:
                        result.update({'Sentiment': 'Gagal analisis AI', 'Sentiment_Source': analysis_source})
                else:
                    result.update({'Sentiment': 'Tidak diproses - konten & judul tidak memadai', 'Sentiment_Source': 'none'})

            # 4. Summarization
            if config['enable_summarize']:
                if scraping_success and len(content.strip()) > 200:
                    summary = self.summarizer.summarize_article(content, config['summarize_config'])
                    if summary:
                        result['Summary'] = summary.get('summary', 'Gagal membuat ringkasan')
                    else:
                        result['Summary'] = 'Gagal analisis AI'
                else:
                    result['Summary'] = 'Tidak diproses - konten tidak memadai'
            
            return result

        except Exception as e:
            return {
                'URL': url, 'Title': f'Error: {str(e)}', 'Content': 'Error dalam pemrosesan',
                'Scraping_Method': 'error', 'Journalist': 'Error', 'Sentiment': 'Error'
            }

    async def process_urls_manual_async(self, urls: List[str], config: Dict) -> List[Dict]:
        """Process manual URL input asynchronously with a progress bar."""
        results = []
        total_urls = len(urls)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        tasks = [self.process_single_url_async(url, config) for url in urls]
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            
            # Update progress centrally
            progress = (i + 1) / total_urls
            progress_bar.progress(progress)
            status_text.text(f"({i + 1}/{total_urls}) Selesai: {result.get('URL', '')[:70]}...")

        # Reorder results to match original URL order
        url_map = {res['URL']: res for res in results}
        ordered_results = [url_map[url] for url in urls]
        
        status_text.text("✅ Semua proses selesai!")
        return ordered_results

    async def process_single_row_async(self, row_tuple, column_mapping: Dict, config: Dict) -> Dict:
        """Asynchronously process a single DataFrame row."""
        index, row = row_tuple
        
        result = row.to_dict()
        result['original_index'] = index  # Store original index for sorting
        url = row.get(column_mapping['url_column'], '')
        
        if not url:
            return result

        snippet = str(row.get(column_mapping['snippet_column'], '')) if column_mapping['snippet_column'] else ""
        content = ""
        scraping_success = False
        analysis_source = "none"
        article_data = {}

        if config['enable_scraping']:
            article_data = await self.scraper.scrape_article(url, timeout=config['scraping_timeout'])
            if article_data and article_data.get('content') and len(article_data.get('content', '').strip()) > 100:
                result['Title_New'] = article_data.get('title', 'Gagal mengambil judul')
                result['Publish_Date_New'] = article_data.get('publish_date', '')
                result['Content_New'] = article_data.get('content', '')
                result['Scraping_Method_New'] = article_data.get('method', 'unknown')
                content = article_data.get('content', '')
                scraping_success = True
            else:
                result['Content_New'] = 'Gagal scraping - konten tidak memadai'
                result['Scraping_Method_New'] = 'failed'
        
        # Determine text for analysis (Content > Title > Snippet)
        analysis_text = ""
        analysis_source = "none"
        title = result.get('Title_New', row.get('Title', '')) # Get new or original title

        if scraping_success and content:
            analysis_text = content
            analysis_source = "scraped_content"
        elif title:
            analysis_text = title
            analysis_source = "title"
        elif snippet:
            analysis_text = snippet
            analysis_source = "snippet"

        if config['enable_journalist'] and analysis_text:
            result['Journalist_New'] = self.journalist_detector.detect_journalist(article_data, analysis_text)
            result['Journalist_Source'] = analysis_source

        if config['enable_sentiment'] and config['sentiment_context'] and analysis_text:
            sentiment = self.sentiment_analyzer.analyze_sentiment(analysis_text, config['sentiment_context'])
            if sentiment:
                result.update({
                    'Sentiment_New': sentiment.get('sentiment', 'Gagal'), 'Confidence_New': sentiment.get('confidence', ''),
                    'Reasoning_New': sentiment.get('reasoning', ''), 'Sentiment_Source': analysis_source
                })
            else:
                result.update({'Sentiment_New': 'Gagal analisis AI', 'Sentiment_Source': analysis_source})
        elif config['enable_sentiment']:
             result.update({'Sentiment_New': 'Tidak diproses - data tidak memadai', 'Sentiment_Source': 'none'})

        if config['enable_summarize'] and len(analysis_text.strip()) > 200:
            summary = self.summarizer.summarize_article(analysis_text, config['summarize_config'])
            if summary:
                result['Summary_New'] = summary.get('summary', 'Gagal')
                result['Summary_Source'] = analysis_source
            else:
                result['Summary_New'] = 'Gagal analisis AI'
        
        return result

    async def process_excel_data_async(self, df: pd.DataFrame, column_mapping: Dict, config: Dict) -> pd.DataFrame:
        """Process Excel file data asynchronously."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_rows = len(df)

        tasks = [self.process_single_row_async(row_tuple, column_mapping, config) for row_tuple in df.iterrows()]
        
        processed_results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            processed_results.append(result)
            
            # Update progress centrally
            progress = (i + 1) / total_rows
            progress_bar.progress(progress)
            url = result.get(column_mapping.get('url_column', ''), '')
            status_text.text(f"({i + 1}/{total_rows}) Selesai: {url[:70]}...")

        # Reorder results to match original DataFrame index
        results_df = pd.DataFrame(processed_results).set_index('original_index').sort_index()
        
        status_text.text("✅ Semua proses selesai!")
        return results_df

    def display_results(self, results, config: Dict, is_excel_data: bool = False):
        if isinstance(results, pd.DataFrame):
            df = results
        elif results:
            df = pd.DataFrame(results)
        else:
            st.warning("Tidak ada hasil untuk ditampilkan.")
            return

        if df.empty:
            st.warning("Tidak ada hasil untuk ditampilkan.")
            return

        total_count = len(df)
        
        # --- Data Processing for Display ---
        url_col = 'URL' if 'URL' in df.columns else (column_mapping.get('url_column') if is_excel_data else 'URL')
        if url_col in df.columns:
            df['Media'] = df[url_col].apply(lambda x: self.scraper._get_domain(x))

        rename_map = {
            'Title': 'Judul', 'Title_New': 'Judul', 
            'Publish_Date': 'Tanggal Rilis', 'Publish_Date_New': 'Tanggal Rilis',
            'Journalist': 'Reporter', 'Journalist_New': 'Reporter',
            'Content': 'Isi', 'Content_New': 'Isi'
        }
        df.rename(columns=rename_map, inplace=True)

        # Conditionally build the desired column order
        desired_order = ['Media', 'Judul']
        if config.get('enable_date', True) and 'Tanggal Rilis' in df.columns:
            desired_order.append('Tanggal Rilis')
        
        desired_order.extend(['Reporter', 'Isi'])
        
        final_columns = [col for col in desired_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in final_columns]
        df = df[final_columns + other_columns]

        # --- Tabbed Results Display ---
        tab1, tab2, tab3 = st.tabs(["📊 Ringkasan & Metrik", "📋 Data Lengkap", "📤 Export"])

        with tab1:
            self.display_metrics_and_summary(df, config, is_excel_data)

        with tab2:
            st.subheader("📋 Preview Hasil Analisis")
            df_display = df.copy()
            text_columns = ['Isi', 'Summary', 'Summary_New', 'Reasoning', 'Reasoning_New']
            for col in text_columns:
                if col in df_display.columns:
                    df_display[col] = df_display[col].astype(str).apply(lambda x: x[:150] + "..." if len(x) > 150 else x)
            st.dataframe(df_display, width='stretch')
            st.caption("💡 Tabel di atas menampilkan preview dengan teks terpotong. Data lengkap tersedia di tab Export.")

        with tab3:
            self.display_export_section(df, config, is_excel_data)

    def display_metrics_and_summary(self, df: pd.DataFrame, config: Dict, is_excel_data: bool):
        st.subheader("📈 Metrik Kinerja")
        total_count = len(df)
        
        # Calculate success rates
        scraping_success = 0
        if config.get('enable_scraping'):
            method_col = 'Scraping_Method_New' if 'Scraping_Method_New' in df.columns else 'Scraping_Method'
            if method_col in df.columns:
                scraping_success = len(df[df[method_col].str.contains('newspaper3k|manual|simple|playwright', na=False)])

        ai_processed, ai_skipped = 0, 0
        if config.get('enable_sentiment'):
            sentiment_col = 'Sentiment_New' if is_excel_data else 'Sentiment'
            if sentiment_col in df.columns:
                ai_processed += len(df[~df[sentiment_col].astype(str).str.contains('Tidak diproses', na=True)])
                ai_skipped += len(df[df[sentiment_col].astype(str).str.contains('Tidak diproses', na=False)])
        if config.get('enable_summarize'):
            summary_col = 'Summary_New' if is_excel_data else 'Summary'
            if summary_col in df.columns:
                ai_processed += len(df[~df[summary_col].astype(str).str.contains('Tidak diproses', na=True)])
                ai_skipped += len(df[df[summary_col].astype(str).str.contains('Tidak diproses', na=False)])

        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Data Diproses", total_count)
        if config.get('enable_scraping'):
            success_rate = (scraping_success / total_count * 100) if total_count > 0 else 0
            col2.metric("Scraping Berhasil", f"{scraping_success}/{total_count}", f"{success_rate:.1f}%")
        
        if ai_processed > 0 or ai_skipped > 0:
            ai_total = ai_processed + ai_skipped
            ai_rate = (ai_processed / ai_total * 100) if ai_total > 0 else 0
            col3.metric("AI Analysis (Gemini)", f"{ai_processed}/{ai_total}", f"{ai_rate:.1f}%", help=f"{ai_skipped} request di-skip untuk hemat token.")
        
        active_funcs = {'📄 Full Teks': 'enable_scraping', '📅 Tanggal': 'enable_date', '😊 Sentimen': 'enable_sentiment', '👤 Jurnalis': 'enable_journalist', '📝 Summarize': 'enable_summarize'}
        st.info(f"**Fungsi Aktif:** {' | '.join([f for f, e in active_funcs.items() if config.get(e)])}")

    def display_export_section(self, df: pd.DataFrame, config: Dict, is_excel_data: bool):
        st.subheader("📤 Export Data ke Excel")
        
        if df.empty:
            st.warning("Tidak ada data untuk diexport.")
            return

        st.info(f"💡 File Excel akan berisi **{len(df.columns)} kolom** dan **{len(df)} baris** data lengkap.")
        
        with st.expander("📋 Preview Kolom yang Akan Diexport"):
            original_cols = [c for c in df.columns if not c.endswith('_New')]
            new_cols = [c for c in df.columns if c.endswith('_New')]
            col1, col2 = st.columns(2)
            with col1:
                st.write("**📁 Kolom Asli:**", original_cols)
            with col2:
                st.write("**🆕 Kolom Hasil Analisis:**", new_cols)

        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_type = "excel" if is_excel_data else "manual"
        features = "_".join(k for k, v in {'ft': 'enable_scraping', 'sent': 'enable_sentiment', 'jour': 'enable_journalist', 'sum': 'enable_summarize'}.items() if config.get(v))
        filename = f"news_analysis_{data_type}_{features}_{timestamp}.xlsx"
        
        st.download_button(
            label="📥 Download Laporan Excel",
            data=excel_buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

    def validate_configuration(self, config: Dict, urls: List[str], uploaded_file=None) -> List[str]:
        warnings = []
        
        if not any([config['enable_scraping'], config['enable_sentiment'], config['enable_journalist'], config['enable_summarize']]):
            warnings.append("⚠️ Pilih minimal satu fungsi untuk digunakan")
        
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
        if not GEMINI_API_KEY and (config['enable_sentiment'] or config['enable_summarize']):
            features = []
            if config['enable_sentiment']:
                features.append("analisis sentimen")
            if config['enable_summarize']:
                features.append("summarize")
            warnings.append(f"⚠️ API Key Gemini belum dikonfigurasi untuk {' dan '.join(features)}")
        
        if config['enable_sentiment']:
            if not config['sentiment_context']:
                warnings.append("⚠️ Konteks sentimen diperlukan untuk analisis sentimen")
        
        if not uploaded_file and not urls:
            warnings.append("⚠️ Masukkan minimal satu URL atau upload file Excel")
        
        return warnings

    def run(self):
        self.setup_page()
        config = self.setup_sidebar()
        
        st.header("📝 Input Data")
        
        tab1, tab2 = st.tabs(["🔗 URL Manual", "📁 Upload File Excel"])
        
        urls, uploaded_file, df, column_mapping = [], None, None, {}

        with tab1:
            url_input = st.text_area(
                "Masukkan URL (satu per baris):", height=250,
                placeholder="https://example.com/news1\nhttps://example.com/news2"
            )
            if url_input:
                urls = [url.strip() for url in url_input.split('\n') if url.strip()]
                st.info(f"Ditemukan {len(urls)} URL untuk dianalisis.")
            input_method = "URL Manual"

        with tab2:
            uploaded_file = st.file_uploader(
                "Upload file Excel (.xlsx, .xls)", type=['xlsx', 'xls'],
                help="Pastikan file Excel Anda memiliki kolom yang berisi URL."
            )
            if uploaded_file:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.success(f"✅ Berhasil membaca {len(df)} baris dari {uploaded_file.name}")
                    with st.expander("👀 Preview Data"):
                        st.dataframe(df.head())
                    column_mapping = self.get_column_mapping(df, "Upload File Excel")
                except Exception as e:
                    st.error(f"❌ Gagal membaca file: {e}")
            input_method = "Upload File Excel"

        # Determine active input method based on user action
        active_input_method = "URL Manual" if urls else "Upload File Excel" if uploaded_file else None

        warnings = self.validate_configuration(config, urls, uploaded_file)
        if warnings:
            for warning in warnings:
                st.warning(warning)
        
        if st.button("🚀 Mulai Analisis", disabled=not active_input_method or bool(warnings), width='stretch', type="primary"):
            st.header("📊 Hasil Analisis")
            with st.spinner("Memproses data... Ini mungkin memakan waktu beberapa saat tergantung jumlah data."):
                loop = asyncio.get_event_loop()
                if active_input_method == "URL Manual":
                    results = loop.run_until_complete(self.process_urls_manual_async(urls, config))
                    self.display_results(results, config, is_excel_data=False)
                elif df is not None:
                    results_df = loop.run_until_complete(self.process_excel_data_async(df, column_mapping, config))
                    self.display_results(results_df, config, is_excel_data=True)
        
        # Scraper Info Section
        with st.expander("ℹ️ Info Teknologi Scraper"):
            try:
                stats = self.scraper.get_user_agent_stats()
                supported_sites = self.scraper.get_supported_sites()
                col1, col2 = st.columns(2)
                col1.info(f"🔄 **Scraper Ready:** {stats['total']} User-Agents")
                col2.info(f"🎯 **Situs Terintegrasi:** {stats['supported_sites']} situs dengan selector khusus")
                
                st.write("**Situs yang Didukung Secara Khusus:**")
                cols = st.columns(4)
                for i, (site, info) in enumerate(supported_sites.items()):
                    with cols[i % 4]:
                        st.caption(f"🌐 {site.title()}")

            except Exception as e:
                st.info("🔄 Menggunakan Newspaper3k + BeautifulSoup dengan multiple User-Agents.")

if __name__ == "__main__":
    app = NewsAnalyzerApp()
    app.run()
