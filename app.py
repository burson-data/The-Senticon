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
        
        try:
            # Ideal for Streamlit Community Cloud deployment
            gemini_api_key = st.secrets.get("GEMINI_API_KEY")
            gemini_base_url = st.secrets.get("GEMINI_BASE_URL")
        except Exception:
            # Fallback for local development using .env file
            from config import GEMINI_API_KEY, GEMINI_BASE_URL
            gemini_api_key = GEMINI_API_KEY
            gemini_base_url = GEMINI_BASE_URL

        # Initialize AI modules with credentials
        self.sentiment_analyzer = SentimentAnalyzer(api_key=gemini_api_key, base_url=gemini_base_url)
        self.journalist_detector = JournalistDetector()
        self.summarizer = ArticleSummarizer(api_key=gemini_api_key, base_url=gemini_base_url)
        
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
                :root {
                    --card-background-color: var(--streamlit-secondary-background-color);
                    --card-border-color: var(--streamlit-gray-20);
                    --tab-inactive-background-color: var(--streamlit-gray-10);
                }
                .main .block-container {
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                }
                .st-emotion-cache-z5fcl4 {
                    border-radius: 10px;
                    padding: 20px !important;
                    border: 1px solid var(--card-border-color);
                    background-color: var(--card-background-color);
                }
                .st-emotion-cache-1g6gooi {
                    border-radius: 10px;
                    padding: 15px;
                    background-color: var(--card-background-color);
                    border: 1px solid var(--card-border-color);
                }
                .stButton>button {
                    border-radius: 8px;
                    font-weight: bold;
                }
                .stTabs [data-baseweb="tab-list"] { gap: 2px; }
                .stTabs [data-baseweb="tab"] {
                    height: 50px;
                    white-space: pre-wrap;
                    background-color: transparent;
                    border-radius: 4px 4px 0 0;
                    gap: 8px;
                    padding: 10px;
                    border-bottom: 2px solid transparent;
                    transition: border-color 0.3s ease, color 0.3s ease;
                }
                .stTabs [data-baseweb="tab"]:hover { background-color: var(--tab-inactive-background-color); }
                .stTabs [aria-selected="true"] {
                    background-color: transparent;
                    font-weight: bold;
                    border-bottom: 2px solid var(--streamlit-primary-color);
                }
            </style>
        """, unsafe_allow_html=True)

        with open("The Senticon.png", "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(f"""
            <style>
            .title-container {{ display: flex; align-items: center; gap: 15px; }}
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
                    sentiment_context = st.text_area("Konteks Sentimen", placeholder="Contoh: Toyota Avanza, harga mobil", help="Masukkan objek/aspek untuk analisis sentimen")

            if enable_summarize:
                with st.expander("📝 **Konfigurasi Summarize**"):
                    summarize_config = {
                        'summary_type': st.selectbox("Tipe Ringkasan", ["Ringkas", "Detail", "Poin-poin Utama", "Custom"], help="Pilih jenis ringkasan"),
                        'max_length': st.slider("Panjang Maksimal (kata)", 50, 500, 150, 25, help="Jumlah kata maksimal"),
                        'language': st.selectbox("Bahasa Ringkasan", ["Bahasa Indonesia", "English", "Sama dengan artikel"], help="Bahasa untuk ringkasan"),
                        'focus_aspect': st.text_input("Aspek yang Difokuskan (Opsional)", placeholder="Contoh: aspek ekonomi", help="Aspek tertentu untuk difokuskan")
                    }
                    if summarize_config['summary_type'] == 'Custom':
                        summarize_config['custom_instruction'] = st.text_area("Instruksi Custom", placeholder="Contoh: Buat ringkasan format bullet points", help="Instruksi khusus")

            if enable_scraping:
                with st.expander("🔧 **Opsi Scraping**"):
                    scraping_timeout = st.slider("Timeout (detik)", 10, 60, 30, help="Waktu tunggu maksimal untuk setiap URL")
        
        return {
            'enable_scraping': enable_scraping, 'enable_date': enable_date,
            'enable_sentiment': enable_sentiment, 'enable_journalist': enable_journalist,
            'enable_summarize': enable_summarize, 'sentiment_context': sentiment_context,
            'summarize_config': summarize_config, 'scraping_timeout': scraping_timeout
        }

    def get_column_mapping(self, df: pd.DataFrame):
        st.subheader("📋 Mapping Kolom")
        st.info("Pilih kolom yang sesuai dari file Excel Anda")
        col1, col2 = st.columns(2)
        with col1:
            url_column = st.selectbox("Kolom URL", options=df.columns.tolist(), index=0 if 'URL' in df.columns else 0, help="Pilih kolom yang berisi URL")
        with col2:
            snippet_column = st.selectbox("Kolom Snippet (Opsional)", options=["Tidak Ada"] + df.columns.tolist(), index=df.columns.tolist().index('Snippet') + 1 if 'Snippet' in df.columns else 0, help="Pilih kolom berisi snippet")
        return {'url_column': url_column, 'snippet_column': snippet_column if snippet_column != "Tidak Ada" else None}

    async def process_single_url_async(self, url_data: Dict, config: Dict, progress_info: Dict):
        url = url_data['url']
        manual_title = url_data.get('title')
        
        try:
            result = {'URL': url}
            if manual_title and config.get('use_manual_title', False):
                result['Title'] = manual_title

            content, scraping_success, article_data = "", False, {}
            if config['enable_scraping']:
                article_data = await self.scraper.scrape_article(url, timeout=config['scraping_timeout'])
                if article_data and article_data.get('content') and len(article_data.get('content', '').strip()) > 100:
                    if 'Title' not in result: result['Title'] = article_data.get('title', 'Gagal mengambil judul')
                    result['Publish_Date'] = article_data.get('publish_date', '')
                    result['Content'] = article_data.get('content', '')
                    result['Scraping_Method'] = article_data.get('method', 'unknown')
                    content, scraping_success = article_data.get('content', ''), True
                else:
                    if 'Title' not in result: result['Title'] = self.scraper.get_title_newspaper3k(url)
                    result.update({'Content': 'Gagal scraping', 'Scraping_Method': 'failed'})
            else:
                article_data = await self.scraper.scrape_article(url, basic_only=True)
                if article_data and len(article_data.get('content', '').strip()) > 100:
                    content, scraping_success = article_data.get('content', ''), True

            if config['enable_journalist']:
                result['Journalist'] = self.journalist_detector.detect_journalist(article_data, content) if scraping_success and content else 'Tidak diproses'
            
            analysis_text, analysis_source = "", "none"
            if scraping_success and len(content.strip()) > 100:
                analysis_text, analysis_source = content, "content"
            elif result.get('Title') and result['Title'] != 'Gagal mengambil judul':
                analysis_text, analysis_source = result['Title'], "title"

            if config['enable_sentiment'] and config['sentiment_context'] and analysis_text:
                sentiment = self.sentiment_analyzer.analyze_sentiment(analysis_text, config['sentiment_context'])
                result.update(sentiment or {'Sentiment': 'Gagal analisis AI'})
                result['Sentiment_Source'] = analysis_source
            
            if config['enable_summarize'] and scraping_success and len(content.strip()) > 200:
                summary = self.summarizer.summarize_article(content, config['summarize_config'])
                result['Summary'] = summary.get('summary', 'Gagal membuat ringkasan')

            return result
        except Exception as e:
            return {'URL': url, 'Title': f'Error: {str(e)}', 'Content': 'Error'}
        finally:
            async with progress_info['lock']:
                progress_info['completed'] += 1
                progress = progress_info['completed'] / progress_info['total']
                progress_info['bar'].progress(progress)
                progress_info['text'].text(f"({progress_info['completed']}/{progress_info['total']}) Selesai: {url[:70]}...")

    async def process_urls_manual_async(self, url_data_list: List[Dict], config: Dict):
        progress_info = {
            'lock': asyncio.Lock(), 'completed': 0, 'total': len(url_data_list),
            'bar': st.progress(0), 'text': st.empty()
        }
        tasks = [self.process_single_url_async(url_data, config, progress_info) for url_data in url_data_list]
        results = await asyncio.gather(*tasks)
        
        original_urls = [d['url'] for d in url_data_list]
        url_map = {res['URL']: res for res in results}
        ordered_results = [url_map[url] for url in original_urls]
        
        progress_info['text'].text("✅ Semua proses selesai!")
        return ordered_results

    async def process_single_row_async(self, row_tuple, column_mapping: Dict, config: Dict, progress_info: Dict):
        index, row = row_tuple
        
        result = row.to_dict()
        result['original_index'] = index
        url = row.get(column_mapping['url_column'], '')
        
        if not url:
            return result

        snippet = str(row.get(column_mapping.get('snippet_column'), '')) if column_mapping.get('snippet_column') else ""
        content, scraping_success, article_data = "", False, {}

        if config['enable_scraping']:
            article_data = await self.scraper.scrape_article(url, timeout=config['scraping_timeout'])
            if article_data and article_data.get('content') and len(article_data.get('content', '').strip()) > 100:
                result['Title_New'] = article_data.get('title', 'Gagal')
                result['Publish_Date_New'] = article_data.get('publish_date', '')
                result['Content_New'] = article_data.get('content', '')
                result['Scraping_Method_New'] = article_data.get('method', 'unknown')
                content, scraping_success = article_data.get('content', ''), True
            else:
                result.update({'Content_New': 'Gagal scraping', 'Scraping_Method_New': 'failed'})
        
        analysis_text, analysis_source = "", "none"
        title = result.get('Title_New', row.get('Title', ''))

        if scraping_success and content:
            analysis_text, analysis_source = content, "scraped_content"
        elif title:
            analysis_text, analysis_source = title, "title"
        elif snippet:
            analysis_text, analysis_source = snippet, "snippet"

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
                result.update({'Sentiment_New': 'Gagal AI', 'Sentiment_Source': analysis_source})

        if config['enable_summarize'] and len(analysis_text.strip()) > 200:
            summary = self.summarizer.summarize_article(analysis_text, config['summarize_config'])
            result['Summary_New'] = summary.get('summary', 'Gagal') if summary else 'Gagal AI'
            result['Summary_Source'] = analysis_source
        
        return result
    
    async def process_excel_data_async(self, df: pd.DataFrame, column_mapping: Dict, config: Dict) -> pd.DataFrame:
        progress_info = {
            'lock': asyncio.Lock(), 'completed': 0, 'total': len(df),
            'bar': st.progress(0), 'text': st.empty()
        }

        tasks = []
        for row_tuple in df.iterrows():
            task = self.process_single_row_async(row_tuple, column_mapping, config, progress_info)
            tasks.append(task)

        processed_results = await asyncio.gather(*tasks)
        
        results_df = pd.DataFrame(processed_results).set_index('original_index').sort_index()
        
        progress_info['text'].text("✅ Semua proses selesai!")
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

        url_col = 'URL' if 'URL' in df.columns else (config.get('column_mapping', {}).get('url_column') if is_excel_data else 'URL')
        if url_col in df.columns:
            df['Media'] = df[url_col].apply(lambda x: self.scraper._get_domain(x))

        rename_map = {
            'Title': 'Judul', 'Title_New': 'Judul', 
            'Publish_Date': 'Tanggal Rilis', 'Publish_Date_New': 'Tanggal Rilis',
            'Journalist': 'Reporter', 'Journalist_New': 'Reporter',
            'Content': 'Isi', 'Content_New': 'Isi'
        }
        df.rename(columns=rename_map, inplace=True)

        desired_order = ['Media', 'Judul']
        if config.get('enable_date', True) and 'Tanggal Rilis' in df.columns:
            desired_order.append('Tanggal Rilis')
        
        desired_order.extend(['Reporter', 'Isi'])
        
        final_columns = [col for col in desired_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in final_columns]
        df = df[final_columns + other_columns]

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
            st.dataframe(df_display, use_container_width=True)
            st.caption("Data lengkap tersedia di tab Export.")

        with tab3:
            self.display_export_section(df, config, is_excel_data)

    def display_metrics_and_summary(self, df: pd.DataFrame, config: Dict, is_excel_data: bool):
        st.subheader("📈 Metrik Kinerja")
        total_count = len(df)
        
        scraping_success = 0
        if config.get('enable_scraping'):
            method_col = 'Scraping_Method_New' if 'Scraping_Method_New' in df.columns else 'Scraping_Method'
            if method_col in df.columns:
                scraping_success = len(df[df[method_col].str.contains('newspaper3k|manual|simple|playwright', na=False)])

        col1, col2 = st.columns(2)
        col1.metric("Total Data Diproses", total_count)
        if config.get('enable_scraping'):
            success_rate = (scraping_success / total_count * 100) if total_count > 0 else 0
            col2.metric("Scraping Berhasil", f"{scraping_success}/{total_count}", f"{success_rate:.1f}%")
        
        active_funcs = {'📄 Full Teks': 'enable_scraping', '📅 Tanggal': 'enable_date', '😊 Sentimen': 'enable_sentiment', '👤 Jurnalis': 'enable_journalist', '📝 Summarize': 'enable_summarize'}
        st.info(f"**Fungsi Aktif:** {' | '.join([f for f, e in active_funcs.items() if config.get(e)])}")

    def display_export_section(self, df: pd.DataFrame, config: Dict, is_excel_data: bool):
        st.subheader("📤 Export Data ke Excel")
        
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
            use_container_width=True
        )

    def run(self):
        self.setup_page()
        config = self.setup_sidebar()
        
        st.header("📝 Input Data")
        tab1, tab2 = st.tabs(["🔗 URL Manual", "📁 Upload File Excel"])
        
        active_input_method, url_data_list, df = None, [], None
        
        with tab1:
            use_manual_title = st.checkbox("Gunakan Judul dari Input Manual", value=True, help="Format: URL[tab]Judul. Jika tidak dicentang, hanya URL yang akan diproses.")
            config['use_manual_title'] = use_manual_title
            
            url_input = st.text_area("Masukkan URL (satu per baris):", height=250, placeholder="https://example.com/news1\nhttps://example.com/news2[tab]Ini Judul Manual")
            if url_input:
                lines = [line.strip() for line in url_input.split('\n') if line.strip()]
                for line in lines:
                    if '\t' in line and use_manual_title:
                        parts = line.split('\t', 1)
                        url_data_list.append({'url': parts[0].strip(), 'title': parts[1].strip()})
                    else:
                        url_data_list.append({'url': line.split('\t', 1)[0].strip()})
                st.info(f"Ditemukan {len(url_data_list)} URL untuk dianalisis.")
                active_input_method = "URL Manual"

        with tab2:
            uploaded_file = st.file_uploader("Upload file Excel (.xlsx, .xls)", type=['xlsx', 'xls'])
            if uploaded_file:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ Berhasil membaca {len(df)} baris dari {uploaded_file.name}")
                config['column_mapping'] = self.get_column_mapping(df)
                active_input_method = "Upload File Excel"

        if not active_input_method:
            st.warning("⚠️ Masukkan minimal satu URL atau upload file Excel")

        if st.button("🚀 Mulai Analisis", disabled=not active_input_method, use_container_width=True, type="primary"):
            st.header("📊 Hasil Analisis")
            with st.spinner("Memproses data..."):
                loop = asyncio.get_event_loop()
                if active_input_method == "URL Manual":
                    results = loop.run_until_complete(self.process_urls_manual_async(url_data_list, config))
                    self.display_results(results, config)
                elif df is not None:
                    results_df = loop.run_until_complete(self.process_excel_data_async(df, config['column_mapping'], config))
                    self.display_results(results_df, config, is_excel_data=True)

if __name__ == "__main__":
    app = NewsAnalyzerApp()
    app.run()
