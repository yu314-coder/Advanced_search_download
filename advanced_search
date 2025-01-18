import asyncio
import os
import random
import logging
from urllib.parse import urlparse
import re
from pathlib import Path
from io import BytesIO

import gradio as gr
import sys

# Playwright & Parsers
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

# ------------------------------------------------------------------------------
# If packaging with PyInstaller or similar:
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------------------
# Logging Setup
logging.basicConfig(
    filename='advanced_download_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# ------------------------------------------------------------------------------
# User-Agent Rotations
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) '
    'Version/16.4 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def sizeof_fmt(num, suffix='B'):
    """Convert a file size to a human-readable string."""
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

# ------------------------------------------------------------------------------
# Playwright Helper Functions
async def human_like_scroll(page):
    scroll_height = await page.evaluate('document.body.scrollHeight')
    viewport_height = await page.evaluate('window.innerHeight')
    current_scroll = 0
    while current_scroll < scroll_height:
        await page.evaluate(f'window.scrollTo(0, {current_scroll})')
        await asyncio.sleep(random.uniform(0.5, 1.5))
        current_scroll += viewport_height * random.uniform(0.5, 1.5)
        scroll_height = await page.evaluate('document.body.scrollHeight')

async def human_like_interactions(page):
    await page.mouse.move(random.randint(0, 1000), random.randint(0, 1000))
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.mouse.click(random.randint(0, 1000), random.randint(0, 1000))
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.evaluate("window.scrollBy(0, window.innerHeight / 2)")
    await asyncio.sleep(random.uniform(0.5, 1.5))

async def get_file_size(url, page):
    try:
        response = await page.request.head(url)
        length = response.headers.get('Content-Length', None)
        if length:
            return sizeof_fmt(int(length))
        else:
            return "Unknown Size"
    except Exception:
        return "Unknown Size"

async def get_pdf_metadata(url, page):
    try:
        resp = await page.request.get(url, timeout=15000)
        if resp.ok:
            content = await resp.body()
            pdf = BytesIO(content)
            reader = PdfReader(pdf)
            return {
                'Title': reader.metadata.title if reader.metadata.title else 'N/A',
                'Author': reader.metadata.author if reader.metadata.author else 'N/A',
                'Pages': len(reader.pages),
            }
        else:
            return {}
    except Exception:
        return {}

# ------------------------------------------------------------------------------
# Bing Search & File Extraction
async def perform_bing_search(query, num_results, page):
    bing_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&count={num_results}"
    try:
        await page.goto(bing_url, timeout=30000)
        await page.wait_for_selector('li.b_algo', timeout=30000)
        await human_like_scroll(page)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('li', class_='b_algo')
        urls = []
        for r in results:
            link = r.find('a')
            if link and 'href' in link.attrs:
                urls.append(link['href'])
                if len(urls) >= num_results:
                    break
        return urls
    except TimeoutError:
        logger.error("Bing search timed out.")
        return []
    except Exception as e:
        logger.error(f"Bing search error: {e}")
        return []

async def extract_downloadable_files(url, page, custom_ext_list):
    """
    Analyze the page for direct file links or Google Drive links.
    `custom_ext_list` is a list of additional file extensions to consider.
    """
    found_files = []
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('networkidle', timeout=30000)
        await human_like_interactions(page)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Base file extensions we always look for:
        default_exts = [
            '.pdf', '.docx', '.zip', '.rar', '.exe', '.mp3',
            '.mp4', '.avi', '.mkv', '.png', '.jpg', '.jpeg', '.gif'
        ]
        # Merge them with the user's custom list
        all_exts = set(default_exts + [ext.strip().lower() for ext in custom_ext_list if ext.strip()])

        anchors = soup.find_all('a', href=True)
        for a in anchors:
            href = a['href'].strip()

            # 1) Known or custom extension
            if any(href.lower().endswith(ext) for ext in all_exts):
                if href.startswith('http'):
                    file_url = href
                elif href.startswith('/'):
                    parsed = urlparse(url)
                    file_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    continue

                size_str = await get_file_size(file_url, page)
                meta = {}
                # PDF metadata
                if file_url.lower().endswith('.pdf'):
                    meta = await get_pdf_metadata(file_url, page)

                found_files.append({
                    'url': file_url,
                    'filename': os.path.basename(file_url.split('?')[0]),
                    'size': size_str,
                    'metadata': meta
                })

            # 2) Google Drive link
            elif "drive.google.com" in href:
                file_id = None
                match1 = re.search(r'/file/d/([^/]+)/', href)
                if match1:
                    file_id = match1.group(1)
                match2 = re.search(r'open\?id=([^&]+)', href)
                if match2:
                    file_id = match2.group(1)
                match3 = re.search(r'id=([^&]+)', href)
                if match3:
                    file_id = match3.group(1)
                if file_id:
                    direct = f"https://drive.google.com/uc?export=download&id={file_id}"
                    size_str = await get_file_size(direct, page)
                    found_files.append({
                        'url': direct,
                        'filename': f"drive_file_{file_id}",
                        'size': size_str,
                        'metadata': {}
                    })

        return found_files
    except TimeoutError:
        logger.error(f"Timeout extracting from {url}")
        return []
    except Exception as e:
        logger.error(f"Error extracting from {url}: {e}")
        return []

async def download_file(file_info, save_dir, page, referer):
    file_url = file_info['url']
    fname = file_info['filename']
    path = os.path.join(save_dir, fname)

    base, ext = os.path.splitext(fname)
    i = 1
    while os.path.exists(path):
        path = os.path.join(save_dir, f"{base}({i}){ext}")
        i += 1

    os.makedirs(save_dir, exist_ok=True)

    try:
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': referer
        }
        await human_like_interactions(page)
        resp = await page.request.get(file_url, headers=headers, timeout=30000)
        if resp.status == 403:
            logger.error(f"403 Forbidden: {file_url}")
            return None
        if not resp.ok:
            logger.error(f"Failed to download {file_url}: Status {resp.status}")
            return None

        # If it's Google Drive, refine filename
        if "drive.google.com" in file_url.lower():
            cdisp = resp.headers.get("Content-Disposition")
            if cdisp:
                mt = re.search(r'filename\*?="?([^";]+)', cdisp)
                if mt:
                    real_fname = mt.group(1).strip('"').strip()
                    if real_fname:
                        path = os.path.join(save_dir, real_fname)
                        b2, e2 = os.path.splitext(real_fname)
                        j = 1
                        while os.path.exists(path):
                            path = os.path.join(save_dir, f"{b2}({j}){e2}")
                            j += 1

        data = await resp.body()
        with open(path, 'wb') as f:
            f.write(data)
        logger.info(f"Downloaded: {path}")
        return path
    except TimeoutError:
        logger.error(f"Timeout downloading {file_url}")
        return None
    except Exception as e:
        logger.error(f"Error downloading {file_url}: {e}")
        return None

# ------------------------------------------------------------------------------
# DownloadManager
class DownloadManager:
    def __init__(self, use_proxy=False, proxy=None, query=None, num_results=5):
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.query = query
        self.num_results = num_results

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        opts = {"headless": True}
        if self.use_proxy and self.proxy:
            opts["proxy"] = {"server": self.proxy}

        self.browser = await self.playwright.chromium.launch(**opts)
        self.context = await self.browser.new_context(user_agent=get_random_user_agent())
        self.page = await self.context.new_page()

        # Extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bing.com/'
        })
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()

    async def search_bing(self):
        if not self.query:
            return []
        return await perform_bing_search(self.query, self.num_results, self.page)

    async def analyze_url(self, url, custom_ext_list):
        """ Now includes a list of custom extensions. """
        return await extract_downloadable_files(url, self.page, custom_ext_list)

    async def download_files(self, file_list, directory, referer):
        out_paths = []
        for fi in file_list:
            saved = await download_file(fi, directory, self.page, referer)
            if saved:
                out_paths.append(saved)
        return out_paths

# ------------------------------------------------------------------------------
# BUILD THE APP (Two “pages” in one UI via radio + show/hide groups)
# ------------------------------------------------------------------------------
def build_gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Advanced Downloader with 'Two Pages' in One UI")
        gr.Markdown(
            "Use the radio below to switch between **Manual URL** mode and **Bing Search** mode. "
            "Use the **Advanced Options** to specify extra file extensions to detect. "
            "No API keys required!"
        )

        # Radio to choose the "page"
        mode_radio = gr.Radio(
            choices=["Manual URL", "Bing Search"],
            value="Manual URL",
            label="Select a mode:",
        )

        # Shared "Advanced Options" for user-specified file extensions
        # We'll pass them along to the extraction function
        with gr.Accordion("Advanced Options (Optional)", open=False):
            custom_extensions = gr.Textbox(
                label="Custom File Extensions (comma-separated)",
                placeholder=".csv, .txt, .torrent, etc."
            )
            gr.Markdown(
                "Any extensions here get **added** to the default set:\n"
                "`.pdf, .docx, .zip, .rar, .exe, .mp3, .mp4, .avi, .mkv, .png, .jpg, .jpeg, .gif`\n"
            )

        # A "Clear Logs" button to reset the logs box
        def clear_logs_action():
            return ""
        
        # ----------------------------------------------------------------
        # Page A: Manual URL
        # ----------------------------------------------------------------
        with gr.Group(visible=True) as manual_group:
            gr.Markdown("## Manual URL Workflow")
            manual_manager_state = gr.State(None)
            manual_files_label_state = gr.State([])
            manual_url_state = gr.State("")

            use_proxy_manual = gr.Checkbox(label="Use Proxy? (Manual)", value=False)
            proxy_manual = gr.Textbox(label="Proxy (http://ip:port)", placeholder="Optional")

            manual_url = gr.Textbox(label="Manual URL", placeholder="https://example.com")
            analyze_manual_btn = gr.Button("Analyze URL (Manual)")

            manual_files_checkbox = gr.CheckboxGroup(label="Files from Manual URL", choices=[])
            with gr.Row():
                select_all_manual_btn = gr.Button("Select All (Manual)")
                deselect_all_manual_btn = gr.Button("Deselect All (Manual)")

            directory_manual = gr.Textbox(label="Download Directory (Manual)", placeholder="./downloads_manual")
            delete_manual_ck = gr.Checkbox(label="Delete after download? (Manual)", value=False)
            download_manual_btn = gr.Button("Download (Manual)")

            manual_output = gr.Textbox(label="Manual Output / Logs", lines=5)

            # For clearing logs
            clear_manual_logs_btn = gr.Button("Clear Logs (Manual)")

            # Helper
            async def create_manual_manager(usep, prox):
                dm = DownloadManager(use_proxy=usep, proxy=prox)
                await dm.__aenter__()
                return dm

            async def analyze_manual_fn(url_val, usep, prox, mgr, custom_ext_str):
                if not url_val:
                    return (gr.update(choices=[], value=[]), [], None, "Please enter a URL first.")

                # Convert custom_ext_str (comma-separated) -> list
                exts = [x.strip() for x in custom_ext_str.split(",") if x.strip()]

                if mgr is None:
                    mgr = await create_manual_manager(usep, prox)

                discovered = await mgr.analyze_url(url_val, exts)
                if not discovered:
                    return (
                        gr.update(choices=[], value=[]),
                        [],
                        mgr,
                        f"No files found at {url_val}."
                    )

                label_list = []
                for i, f in enumerate(discovered):
                    detail_parts = []
                    if f['size']:
                        detail_parts.append(f"Size: {f['size']}")
                    meta = f.get("metadata", {})
                    if meta.get('Title') and meta['Title'] != 'N/A':
                        detail_parts.append(f"Title: {meta['Title']}")
                    if meta.get('Author') and meta['Author'] != 'N/A':
                        detail_parts.append(f"Author: {meta['Author']}")
                    if meta.get('Pages') is not None:
                        detail_parts.append(f"Pages: {meta['Pages']}")
                    label_str = f"{i}. {f['filename']} | " + " | ".join(detail_parts)
                    label_list.append(label_str)

                return (
                    gr.update(choices=label_list, value=[]),
                    label_list,
                    mgr,
                    f"Found {len(discovered)} files at {url_val}."
                )

            def select_all_manual_fn(file_labels):
                return gr.update(value=file_labels)

            def deselect_all_manual_fn():
                return gr.update(value=[])

            async def download_manual_fn(selected, label_list, folder, do_del, manager, last_url, custom_ext_str):
                if manager is None:
                    return "No manager. Please analyze a Manual URL first."
                if not last_url:
                    return "No last URL. Please analyze a URL first."
                if not selected:
                    return "No files selected."

                # Re-check the current files
                exts = [x.strip() for x in custom_ext_str.split(",") if x.strip()]
                discovered = await manager.analyze_url(last_url, exts)
                try:
                    indices = [int(x.split(".")[0]) for x in selected]
                except:
                    return "Error parsing selected items."

                chosen = []
                for i in indices:
                    if i < len(discovered):
                        chosen.append(discovered[i])

                if not chosen:
                    return "No valid files selected."

                if not folder:
                    folder = "./downloads_manual"

                downloaded = await manager.download_files(chosen, folder, referer=last_url)
                if not downloaded:
                    return "No files downloaded."

                if do_del:
                    for fp in downloaded:
                        try:
                            os.remove(fp)
                            logger.info(f"Deleted: {fp}")
                        except OSError as e:
                            logger.error(f"Error deleting {fp}: {e}")
                    return f"Downloaded & deleted {len(downloaded)} files: {downloaded}"
                else:
                    return f"Downloaded {len(downloaded)} files to '{folder}': {downloaded}"

            # Wire up
            analyze_manual_btn.click(
                fn=analyze_manual_fn,
                inputs=[manual_url, use_proxy_manual, proxy_manual, manual_manager_state, custom_extensions],
                outputs=[manual_files_checkbox, manual_files_label_state, manual_manager_state, manual_output]
            ).then(
                fn=lambda x: x,
                inputs=[manual_url],
                outputs=[manual_url_state]
            )

            select_all_manual_btn.click(
                fn=select_all_manual_fn,
                inputs=[manual_files_label_state],
                outputs=[manual_files_checkbox]
            )

            deselect_all_manual_btn.click(
                fn=deselect_all_manual_fn,
                outputs=[manual_files_checkbox]
            )

            download_manual_btn.click(
                fn=download_manual_fn,
                inputs=[manual_files_checkbox, manual_files_label_state, directory_manual,
                        delete_manual_ck, manual_manager_state, manual_url_state, custom_extensions],
                outputs=[manual_output]
            )

            clear_manual_logs_btn.click(
                fn=clear_logs_action,
                inputs=[],
                outputs=[manual_output]
            )

        # ----------------------------------------------------------------
        # Page B: Bing Search
        # ----------------------------------------------------------------
        with gr.Group(visible=False) as search_group:
            gr.Markdown("## Bing Search Workflow")
            search_manager_state = gr.State(None)
            search_file_label_state = gr.State([])
            search_url_state = gr.State("")

            use_proxy_search = gr.Checkbox(label="Use Proxy? (Search)", value=False)
            proxy_search = gr.Textbox(label="Proxy (http://ip:port)", placeholder="Optional")

            query_inp = gr.Textbox(label="Bing Search Query")
            num_results_sl = gr.Slider(label="Number of Results", minimum=1, maximum=50, value=5, step=1)
            search_btn = gr.Button("Search Bing")

            results_dd = gr.Dropdown(label="Bing Results", choices=[], value=None)
            analyze_search_btn = gr.Button("Analyze Selected URL")

            search_files_checkbox = gr.CheckboxGroup(label="Files from Search", choices=[])
            with gr.Row():
                select_all_search_btn = gr.Button("Select All (Search)")
                deselect_all_search_btn = gr.Button("Deselect All (Search)")

            directory_search = gr.Textbox(label="Download Directory (Search)", placeholder="./downloads_search")
            delete_search_ck = gr.Checkbox(label="Delete after download? (Search)", value=False)
            download_search_btn = gr.Button("Download (Search)")

            search_output = gr.Textbox(label="Search Output / Logs", lines=5)

            # For clearing logs
            clear_search_logs_btn = gr.Button("Clear Logs (Search)")

            async def create_search_manager(usep, px, query, numr):
                dm = DownloadManager(use_proxy=usep, proxy=px, query=query, num_results=numr)
                await dm.__aenter__()
                return dm

            async def do_search_fn(usep, px, query, numr):
                if not query:
                    return (gr.update(choices=[], value=[]), None, "No query entered.")
                mgr = await create_search_manager(usep, px, query, numr)
                results = await mgr.search_bing()
                if not results:
                    return (gr.update(choices=[], value=[]), mgr, "No results or Bing error.")
                return (gr.update(choices=results, value=results[0]), mgr, f"Found {len(results)} results.")

            async def analyze_search_fn(sel_url, mgr, custom_ext_str):
                if not sel_url:
                    return (gr.update(choices=[], value=[]), [], "No URL selected.")
                if mgr is None:
                    return (gr.update(choices=[], value=[]), [], "No manager. Please search again.")

                exts = [x.strip() for x in custom_ext_str.split(",") if x.strip()]
                discovered = await mgr.analyze_url(sel_url, exts)
                if not discovered:
                    return (gr.update(choices=[], value=[]), [], "No files found on that page.")

                labels = []
                for i, f in enumerate(discovered):
                    detail_parts = []
                    if f['size']:
                        detail_parts.append(f"Size: {f['size']}")
                    meta = f.get("metadata", {})
                    if meta.get('Title') and meta['Title'] != 'N/A':
                        detail_parts.append(f"Title: {meta['Title']}")
                    if meta.get('Author') and meta['Author'] != 'N/A':
                        detail_parts.append(f"Author: {meta['Author']}")
                    if meta.get('Pages') is not None:
                        detail_parts.append(f"Pages: {meta['Pages']}")
                    labels.append(f"{i}. {f['filename']} | " + " | ".join(detail_parts))

                return (gr.update(choices=labels, value=[]), labels, f"Found {len(discovered)} files.")

            def select_all_search_fn(file_labels):
                return gr.update(value=file_labels)

            def deselect_all_search_fn():
                return gr.update(value=[])

            async def download_search_fn(selected, label_list, folder, do_del, mgr, sel_url, custom_ext_str):
                if mgr is None:
                    return "No manager. Please search first."
                if not sel_url:
                    return "No selected URL from results."
                if not selected:
                    return "No files selected."

                exts = [x.strip() for x in custom_ext_str.split(",") if x.strip()]
                discovered = await mgr.analyze_url(sel_url, exts)
                try:
                    idxs = [int(x.split(".")[0]) for x in selected]
                except:
                    return "Error parsing selected items."

                chosen = []
                for i in idxs:
                    if i < len(discovered):
                        chosen.append(discovered[i])
                if not chosen:
                    return "No valid files selected."

                if not folder:
                    folder = "./downloads_search"

                downloaded = await mgr.download_files(chosen, folder, referer=sel_url)
                if not downloaded:
                    return "No files downloaded."

                if do_del:
                    for fp in downloaded:
                        try:
                            os.remove(fp)
                            logger.info(f"Deleted: {fp}")
                        except OSError as e:
                            logger.error(f"Error deleting {fp}: {e}")
                    return f"Downloaded & deleted {len(downloaded)} files: {downloaded}"
                else:
                    return f"Downloaded {len(downloaded)} files to '{folder}': {downloaded}"

            # Wire up
            search_btn.click(
                fn=do_search_fn,
                inputs=[use_proxy_search, proxy_search, query_inp, num_results_sl],
                outputs=[results_dd, search_manager_state, search_output]
            )

            analyze_search_btn.click(
                fn=analyze_search_fn,
                inputs=[results_dd, search_manager_state, custom_extensions],
                outputs=[search_files_checkbox, search_file_label_state, search_output]
            ).then(
                fn=lambda x: x,
                inputs=[results_dd],
                outputs=[search_url_state]
            )

            select_all_search_btn.click(
                fn=select_all_search_fn,
                inputs=[search_file_label_state],
                outputs=[search_files_checkbox]
            )

            deselect_all_search_btn.click(
                fn=deselect_all_search_fn,
                outputs=[search_files_checkbox]
            )

            download_search_btn.click(
                fn=download_search_fn,
                inputs=[search_files_checkbox, search_file_label_state, directory_search,
                        delete_search_ck, search_manager_state, search_url_state, custom_extensions],
                outputs=[search_output]
            )

            clear_search_logs_btn.click(
                fn=clear_logs_action,
                inputs=[],
                outputs=[search_output]
            )

        # ------------------------------------------------------------------
        # Toggle which Group is visible based on radio selection
        # ------------------------------------------------------------------
        def switch_mode(mode_choice):
            return (
                gr.update(visible=(mode_choice == "Manual URL")),
                gr.update(visible=(mode_choice == "Bing Search"))
            )

        mode_radio.change(
            fn=switch_mode,
            inputs=[mode_radio],
            outputs=[manual_group, search_group],
        )

    return demo

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import asyncio
    app = build_gradio_app()
    asyncio.run(app.launch(server_name="127.0.0.1", server_port=7860))
