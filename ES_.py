from auth import login, validate_user
import streamlit as st
import requests
import uuid
import json
from datetime import datetime
import os
import time
import functools
from dotenv import load_dotenv
load_dotenv()
 
 
def track_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"{func.__name__} call duration: {duration:.4f} seconds")
        return result
    return wrapper
 
# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/chat")
API_BASE_URL = "http://localhost:5555"
 
def get_requests_session():
    session = requests.Session()
    session.headers.update({
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'GSC-ARB-Chatbot-Frontend/1.0'
    })
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=3
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
 
@track_time
def test_api_connection():
    try:
        session = get_requests_session()
        response = session.get(f"{API_BASE_URL}/health", timeout=60)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        return False, str(e)
 
@track_time
def get_feedback_stats(headers):
    session = get_requests_session()
    for attempt in range(3):
        try:
            stats_response = session.get(f"{API_BASE_URL}/chatbot/feedback/stats", headers=headers, timeout=60)
            if stats_response.status_code == 200:
                return True, stats_response.json()
            else:
                return False, f"Status: {stats_response.status_code}"
        except requests.exceptions.RequestException as e:
            if attempt == 2:
                return False, str(e)
            time.sleep(0.5 * (attempt + 1))
    return False, "Max retries exceeded"
 
@track_time
def get_user_feedback(headers):
    try:
        feedback_response = requests.get(f"{API_BASE_URL}/chatbot/feedback/my-feedback", headers=headers, timeout=60)
        if feedback_response.status_code == 200:
            return True, feedback_response.json()
        else:
            return False, f"Status: {feedback_response.status_code}"
    except Exception as e:
        return False, str(e)
@track_time
def get_system_status(headers):
    try:
        status_response = requests.get(f"{API_BASE_URL}/chatbot/system/status", timeout=60, headers=headers)
        if status_response.status_code == 200:
            return True, status_response.json()
        else:
            return False, f"Status: {status_response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def check_admin_access(email):
    admin_emails_str = os.getenv("ADMIN_EMAILS", "")
    if not admin_emails_str:
        return False
    admin_emails = [email.strip().lower() for email in admin_emails_str.split(",") if email.strip()]
    return email.lower() in admin_emails
 
@track_time
def get_admin_dashboard(headers):
    try:
        session = get_requests_session()
        response = session.get(f"{API_BASE_URL}/admin/dashboard", headers=headers, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def get_admin_documents(headers, status_filter=None, source_filter=None):
    try:
        session = get_requests_session()
        params = {}
        if status_filter:
            params['status_filter'] = status_filter
        if source_filter:
            params['source_filter'] = source_filter
       
        response = session.get(f"{API_BASE_URL}/admin/documents", headers=headers, params=params, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def get_admin_users(headers):
    try:
        session = get_requests_session()
        response = session.get(f"{API_BASE_URL}/admin/users", headers=headers, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def get_admin_analytics(headers, days=30):
    try:
        session = get_requests_session()
        response = session.get(f"{API_BASE_URL}/admin/analytics", headers=headers, params={"days": days}, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def get_admin_safety_logs(headers, event_type=None, content_blocked=None):
    try:
        session = get_requests_session()
        params = {}
        if event_type:
            params['event_type'] = event_type
        if content_blocked is not None:
            params['content_blocked'] = content_blocked
       
        response = session.get(f"{API_BASE_URL}/admin/safety-logs", headers=headers, params=params, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
@track_time
def get_top_questions(headers):
    try:
        session = get_requests_session()
       
 
        response = session.get(f"{API_BASE_URL}/faq", headers=headers, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)
 
# Page config and Custom CSS
st.set_page_config(
    page_title="GSC ARB Chatbot",
    page_icon="GSK",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Custom CSS
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
   
   
   
    /* Title styling */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
   
    /* Tile container */
    .tile-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        justify-content: center;
        animation: fadeInUp 1s ease-out 0.6s both;
    }
   
    /* Individual tiles */
    .control-tile {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        border: 2px solid transparent;
        min-width: 150px;
        position: relative;
        overflow: hidden;
    }
   
    .control-tile::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
   
    .control-tile:hover::before {
        left: 100%;
    }
   
    .control-tile:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
   
    .tile-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
        transition: transform 0.3s ease;
    }
   
    .control-tile:hover .tile-icon {
        transform: scale(1.2) rotate(5deg);
    }
   
    .tile-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
   
    .tile-description {
        font-size: 0.85rem;
        color: #7f8c8d;
        line-height: 1.4;
    }
   
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
   
    .status-online {
        background-color: #2ecc71;
        box-shadow: 0 0 10px rgba(46, 204, 113, 0.5);
    }
   
    .status-offline {
        background-color: #e74c3c;
        box-shadow: 0 0 10px rgba(231, 76, 60, 0.5);
    }
   
    /* FAQ styling */
    .faq-item {
        background:linear-gradient(135deg, #ffff 80%, #FF4500 100%);
        border-radius: 10px;
        padding: 0.11rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #f4a460;
        color: grey;
    }
   
    .faq-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        border-left-color: #764ba2;
    }
   
    /* Table styling */
    .table-row:hover {
        background-color: #f8f9fa;
    }
   
    .table-row:last-child {
        border-bottom: none;
    }
   
    /* Pagination styling */
    .pagination-btn {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
   
    .pagination-btn:hover {
        background: #764ba2;
        transform: translateY(-2px);
    }
   
    .pagination-btn:disabled {
        background: #bdc3c7;
        cursor: not-allowed;
        transform: none;
    }
   
    /* Safety log styling */
    .safety-log-item {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
        border-left: 5px solid;
        transition: all 0.3s ease;
    }
   
   
    .safety-log-allowed {
        border-left-color: #2ecc71;
    }
   
    .safety-log-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
   
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
   
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
   
    /* Chat message styling */
    .stChatMessage {
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
   
    .stChatMessage:hover {
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
   
    /* Button enhancements */
    .stButton > button {
        border-radius: 10px;
        transition: all 0.3s ease;
        font-weight: 500;
    }
   
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
   
    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
   
   
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
   
    /* scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
   
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
   
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
   
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
   
   
    /*selectbox and input styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
   
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
   
    .stTextInput > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
   
    .stTextInput > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
   
    /*expander styling */
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateY(-1px);
    }
 
    /*sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
   
</style>
""", unsafe_allow_html=True)
 
st.sidebar.markdown(
                        """
                        <style>
                        div.stButton > button {
                            # width: 300px;
                            # text-align: left;
                            # background-color: white;
                            # border: none;
                            # color: inherit;
                            # padding: 8px 0;
                            background:linear-gradient(135deg, #ffff 80%, #FF4500 100%);
                            border-radius: 10px;
                            padding: 0.11rem;
                            margin-bottom: 0.01rem;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                            transition: all 0.3s ease;
                            border-left: 4px solid #f4a460;
                            color: grey;
                        }
                        div.stButton > button:hover {
                            # background-color: #f0f0f0;
                            transform: translateX(5px);
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
                            border-left-color: #764ba2;
                            background-color: white !important;
                            color: darkorange !important;
                        }
                        div.stButton > button:focus {
                            outline: none;
                        }
                        /* FAQ-specific button styling for uniform width */
                        div.stButton > button[data-testid*="faq_"] {
                            width: 280px !important;
                            min-width: 280px !important;
                            max-width: 280px !important;
                        }
                        /* Alternative selector for FAQ buttons */
                        div[data-testid*="faq_"] button {
                            width: 280px !important;
                            min-width: 280px !important;
                            max-width: 280px !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                        )
 
st.markdown("""
<div class="info-note">
    <strong>💡 Note:</strong> Ask Questions related to ARB Process, Platform Provisioning
</div>
""", unsafe_allow_html=True)
 
import os
 
gif_path = os.path.abspath("gsk_logo_animated.gif")
 
if os.path.exists(gif_path):
    st.image(gif_path, use_container_width=False, caption="GSC Chatbot")
           
else:
    st.error("GIF file not found. Please check the file path.")
 
def add_document(doc_id, resource_name, page_url):
    # Retrieve token from the cookie manager
    token = st.session_state["access_token"]
    if not token:
        st.error("Session expired. Please log in again.")
        st.stop()
 
    # Prepare the endpoint and headers
    endpoint = f"{API_BASE_URL}/admin/documents/add"
    payload = {
        "doc_id": doc_id,
        "resource_name": resource_name,
        "page_url": page_url
    }
    headers = {"Authorization": f"Bearer {token}"}
 
    # Send the POST request
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.text
            try:
                error_detail = response.json().get("detail", error_detail)
            except:
                pass
            st.error(f"Failed to add document: {error_detail}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
 
 
def get_all_cookies():
    '''
    WARNING: This uses unsupported feature of Streamlit
    Returns the cookies as a dictionary of kv pairs
    '''
    #from streamlit.web.server.websocket_headers import _get_websocket_headers
    # https://github.com/streamlit/streamlit/pull/5457
    from urllib.parse import unquote
 
    headers = st.context.headers
    if headers is None:
        return {}
   
    if 'Cookie' not in headers:
        return {}
   
    cookie_string = headers['Cookie']
    # A sample cookie string: "K1=V1; K2=V2; K3=V3"
    cookie_kv_pairs = cookie_string.split(';')
 
    cookie_dict = {}
    for kv in cookie_kv_pairs:
        k_and_v = kv.split('=')
        k = k_and_v[0].strip()
        v = k_and_v[1].strip()
        cookie_dict[k] = unquote(v)
    return cookie_dict
 
if __name__ == "__main__":
    if 'admin_docs' not in st.session_state:
        st.session_state['admin_docs'] = None
    if 'safety_logs' not in st.session_state:
        st.session_state['safety_logs'] = None
    if 'faqs' not in st.session_state:
        st.session_state['faqs'] = None
    if 'feedback' not in st.session_state:
        st.session_state['feedback'] = None
    if 'feedback_stats' not in st.session_state:
        st.session_state['feedback_stats'] = None
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'cookies' not in st.session_state:
        res = get_all_cookies()
        st.session_state['cookies'] = res
        st.rerun()
    if 'access_token' not in st.session_state:
        if 'access_token' in  st.session_state['cookies']:
            st.session_state['access_token'] = st.session_state['cookies']['access_token']
    if 'access_token' in st.session_state:
        if validate_user(st.session_state['access_token']):
            st.session_state["authenticated"] = True
    if st.session_state['authenticated'] == False:
        login()
    else:
        print(st.session_state['access_token'])
        # Check if user has admin access
        user_email = st.session_state['email_id']
        st.write(f"User Email: {user_email}")
        is_admin = check_admin_access(user_email)
       
        # Admin Panel UI
        def render_admin_panel():
            st.title("Admin Panel")
            st.markdown("---")
           
            # Get admin token
            token = st.session_state["access_token"]
            if not token:
                st.error("Authentication required for admin access.")
                return
           
            headers = {"Authorization": f"Bearer {token}"}
           
            # Admin navigation tabs
            admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
                "📄 Documents", "🛡️ Safety", "➕ Add Document", "📋 Manage Process Owners"
            ])
           
           
            with admin_tab1:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFA500 0%, #FF4500 100%);
                           color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
                    <h2 style="margin: 0; color: white; font-size: 1.8rem;">📄 Document Management</h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Manage and monitor document indexing status</p>
                </div>
                """, unsafe_allow_html=True)
               
                # Document filters
                st.markdown("### 🔍 Filters & Controls")
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    status_filter = st.selectbox(
                        "Filter by Status",
                        ["All", "processed", "processing", "failed", "pending"],
                        key="doc_status_filter"
                    )
                with col2:
                    source_filter = st.text_input("🔗 Filter by Source", key="doc_source_filter")
                with col3:
                    active_filter = st.selectbox(
                        "⚡ Active Status",
                        ["All", "Active", "Inactive"],
                        key="doc_active_filter"
                    )
                with col4:
                    if st.button("🔄 Refresh", use_container_width=True, key="refresh_button_1"):
                        st.session_state["admin_docs"] = None
                        st.rerun()
               
                # Get documents
                status_param = None if status_filter == "All" else status_filter
                source_param = source_filter if source_filter else None
                if not st.session_state["admin_docs"]:
                    status, admin_docs = get_admin_documents(headers, status_param, source_param)
                    if status:
                        st.session_state["admin_docs"] = admin_docs
               
                if st.session_state["admin_docs"]:
                    documents = st.session_state["admin_docs"].get("documents", [])
                   
                    # Apply active status filter
                    if active_filter != "All":
                        if active_filter == "Active":
                            documents = [doc for doc in documents if doc.get('is_active', True)]
                        else:  # Inactive
                            documents = [doc for doc in documents if not doc.get('is_active', True)]
                   
                    # Pagination setup
                    ITEMS_PER_PAGE = 25
                    total_documents = len(documents)
                    total_pages = (total_documents + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
                   
                    # Initialize page state
                    if 'doc_page' not in st.session_state:
                        st.session_state.doc_page = 1
                   
                    # Ensure page is within bounds
                    if st.session_state.doc_page > total_pages and total_pages > 0:
                        st.session_state.doc_page = total_pages
                    elif st.session_state.doc_page < 1:
                        st.session_state.doc_page = 1
                   
                    # Document summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="color: #667eea; margin: 0;">{total_documents}</h3>
                            <p style="margin: 0; color: #7f8c8d;">Total Documents</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        active_count = sum(1 for doc in documents if doc.get('is_active', True))
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="color: #2ecc71; margin: 0;">{active_count}</h3>
                            <p style="margin: 0; color: #7f8c8d;">Active Documents</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        processed_count = sum(1 for doc in documents if doc.get('indexing_status') == 'processed')
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="color: #f39c12; margin: 0;">{processed_count}</h3>
                            <p style="margin: 0; color: #7f8c8d;">Processed</p>
                        </div>
                        """, unsafe_allow_html=True)
                   
                    if documents:
                        # Pagination controls at top
                        if total_pages > 1:
                            st.markdown("### 📄 Page Navigation")
                            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                           
                            with col1:
                                if st.button("⏮️ First", disabled=(st.session_state.doc_page == 1)):
                                    st.session_state.doc_page = 1
                                    st.rerun()
                           
                            with col2:
                                if st.button("◀️ Previous", disabled=(st.session_state.doc_page == 1)):
                                    st.session_state.doc_page -= 1
                                    st.rerun()
                           
                            with col3:
                                st.markdown(f"""
                                <div style="text-align: center; padding: 0.5rem; background: #f8f9fa;
                                           border-radius: 8px; border: 2px solid #667eea;">
                                    <strong>Page {st.session_state.doc_page} of {total_pages}</strong>
                                    <br><small>Showing {ITEMS_PER_PAGE} items per page</small>
                                </div>
                                """, unsafe_allow_html=True)
                           
                            with col4:
                                if st.button("Next ▶️", disabled=(st.session_state.doc_page == total_pages)):
                                    st.session_state.doc_page += 1
                                    st.rerun()
                           
                            with col5:
                                if st.button("Last ⏭️", disabled=(st.session_state.doc_page == total_pages)):
                                    st.session_state.doc_page = total_pages
                                    st.rerun()
                       
                        # Calculate pagination
                        start_idx = (st.session_state.doc_page - 1) * ITEMS_PER_PAGE
                        end_idx = start_idx + ITEMS_PER_PAGE
                        page_documents = documents[start_idx:end_idx]
                       
                        #table
                        st.markdown("### 📋 Document Table")
                        st.markdown("""
                        <div class="professional-table">
                            <div class="table-header">
                                <div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr 1fr 1fr; gap: 1rem; align-items: center;">
                                    <div><strong>Title</strong></div>
                                    <div><strong>Source</strong></div>
                                    <div><strong>Status</strong></div>
                                    <div><strong>Active</strong></div>
                                    <div><strong>Updated</strong></div>
                                    <div><strong>Action</strong></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                       
                        # Document rows
                        for i, doc in enumerate(page_documents):
                            # Determine row styling based on status
                            status = doc.get('indexing_status', 'Unknown')
                            is_active = doc.get('is_active', True)
                           
                            row_style = "background: #f8f9fa;" if i % 2 == 0 else "background: white;"
                            if status == 'failed':
                                row_style += " border-left: 4px solid #e74c3c;"
                            elif status == 'processing':
                                row_style += " border-left: 4px solid #f39c12;"
                            elif status == 'processed' and is_active:
                                row_style += " border-left: 4px solid #2ecc71;"
                           
                            st.markdown(f"""
                            <div class="table-row" style="{row_style}">
                                <div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr 1fr 1fr; gap: 1rem; align-items: center; padding: 0.75rem;">
                            """, unsafe_allow_html=True)
                           
                            # Create columns for this row
                            doc_cols = st.columns([3, 2, 1, 1, 1, 1])
                           
                            with doc_cols[0]:
                                # Title with URL link
                                title = doc.get('title', 'Untitled')
                                display_title = title[:45] + ("..." if len(title) > 45 else "")
                               
                                if doc.get('page_url'):
                                    st.markdown(f"🔗 [{display_title}]({doc['page_url']})")
                                else:
                                    st.markdown(f"📄 {display_title}")
                               
                                # Show error message if exists
                                if doc.get('error_message'):
                                    st.error(f"❌ {doc['error_message'][:80]}...")
                           
                            with doc_cols[1]:
                                source = doc.get('source', 'N/A')
                                st.markdown(f"🏷️ {source[:20]}{'...' if len(source) > 20 else ''}")
                           
                            with doc_cols[2]:
                                status = doc.get('indexing_status', 'Unknown')
                                if status == 'processed':
                                    st.success(f"✅ {status}")
                                elif status == 'processing':
                                    st.info(f"⏳ {status}")
                                elif status == 'failed':
                                    st.error(f"❌ {status}")
                                else:
                                    st.markdown(f"✅ {status}")
                           
                            with doc_cols[3]:
                                is_active = doc.get('is_active', True)
                                if is_active:
                                    st.markdown("🟢 Active")
                                else:
                                    st.error("🔴 Inactive")
                           
                            with doc_cols[4]:
                                updated = doc.get('last_updated_at', 'N/A')
                                if updated != 'N/A':
                                    try:
                                        from datetime import datetime
                                        if isinstance(updated, str):
                                            dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                                            st.write(f"📅 {dt.strftime('%m/%d')}")
                                        else:
                                            st.write(f"📅 {str(updated)[:10]}")
                                    except:
                                        st.write(f"📅 {str(updated)[:10]}")
                                else:
                                    st.write('📅 N/A')
                           
                            with doc_cols[5]:
                                #toggle button
                                current_status = doc.get('is_active', True)
                                button_text = "Deactivate" if current_status else "Activate"
                                button_type = "secondary" if current_status else "primary"
                               
                                if st.button(button_text, key=f"toggle_{doc.get('id')}_{start_idx + i}", type=button_type, use_container_width=True):
                                    try:
                                        session = get_requests_session()
                                        doc_id = doc['id']
                                       
                                        with st.spinner("Updating document status..."):
                                            response = session.put(
                                                f"{API_BASE_URL}/admin/documents/{doc_id}/toggle-active",
                                                headers=headers,
                                                timeout=30
                                            )
                                            if response.status_code == 200:
                                                result = response.json()
                                                new_status = "activated" if result.get('is_active') else "deactivated"
                                                st.success(f"✅ Document {new_status} successfully!")
                                               
                                                if result.get('database_found') is False:
                                                    st.warning("⚠️ Document not found in database but configuration updated")
 
                                                st.session_state['admin_docs'] = None
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Failed to toggle status: {response.text}")
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")

# Delete button
                           
                            if st.button("Delete", key=f"delete_{doc.get('id')}_{start_idx + i}", type="tertiary", use_container_width=True):
                                try:
                                    with st.spinner("Deleting document..."):
                                        session = get_requests_session()
                                        response = session.delete(
                                            f"{API_BASE_URL}/admin/documents/{doc['id']}",
                                            headers=headers
                                        )
                                        if response.status_code == 200:
                                            st.success(response.json().get("message", "✅ Document deleted successfully!"))
                                            # get_admin_documents_cached.clear()
                                            st.rerun()
                                        elif response.status_code == 404:
                                            st.error(response.json().get("detail", "❌ Document not found"))
                                        elif response.status_code == 500:
                                            st.error(response.json().get("detail", "❌ Failed to delete document due to server error"))
                                        else:
                                            st.error(f"❌ Unexpected error: {response.text}")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
 
                            st.markdown("</div></div>", unsafe_allow_html=True)
                           
                            # Add subtle separator
                            if i < len(page_documents) - 1:
                                st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #e9ecef;">', unsafe_allow_html=True)
                       
                        # Pagination controls at bottom (if more than one page)
                        if total_pages > 1:
                            st.markdown("---")
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.markdown(f"""
                                <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                                           border-radius: 10px; border: 1px solid #dee2e6;">
                                    <strong>📄 Showing {start_idx + 1}-{min(end_idx, total_documents)} of {total_documents} documents</strong>
                                    <br><small>Page {st.session_state.doc_page} of {total_pages}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                                   border-radius: 15px; border: 2px dashed #dee2e6;">
                            <h3 style="color: #6c757d; margin-bottom: 1rem;">📄 No Documents Found</h3>
                            <p style="color: #6c757d; margin: 0;">No documents match the current filters. Try adjusting your search criteria.</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Failed to load documents")
           
            with admin_tab2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFA500 0%, #FF4500 100%);
                        color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
                    <h2 style="margin: 0; color: white; font-size: 1.8rem;">🛡️ Content Safety Monitoring</h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Monitor and analyze content safety events and PII detection</p>
                </div>
                """, unsafe_allow_html=True)
               
                # Safety filters
                st.markdown("### Safety Filters & Controls")
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    categories_filter = st.selectbox(
                        "📂 Categories",
                        ["All", "Sensitive", "PII", "Other"],
                        key="safety_categories_filter"
                    )
                with col2:
                    severity_filter = st.selectbox(
                        "⚠️ Severity",
                        ["All", "Low", "Medium", "High"],
                        key="safety_severity_filter"
                    )
                with col3:
                    time_filter = st.selectbox(
                        "⏰ Time Range",
                        ["All Time", "Last 24h", "Last 7d", "Last 30d"],
                        key="safety_time_filter"
                    )
                with col4:
                    if st.button("🔄 Refresh", use_container_width=True):
                        st.session_state['safety_logs'] = None
                        st.rerun()
               
                # Get safety logs
                categories_param = None if categories_filter == "All" else categories_filter
                severity_param = None if severity_filter == "All" else severity_filter
               
                success, safety_data = get_admin_safety_logs(headers, categories_param, severity_param)
                if success:
                    st.session_state['safety_logs'] = safety_data
                if success:
                    safety_logs = st.session_state['safety_logs'].get("safety_logs", [])
                    total_count = st.session_state['safety_logs'].get("total_count", 0)
 
                    # Safety logs display
                    st.markdown(f"### 🛡️ Safety Logs ({total_count} total)")
                    for log in safety_logs:
                        st.markdown(f"""
                        <div style="border: 2px solid #3498db; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                            <strong>Log ID:</strong> {log['id']}<br>
                            <strong>Chat ID:</strong> {log['chat_id']}<br>
                            <strong>Categories:</strong> {log['categories']}<br>
                            <strong>Severity:</strong> {log['severity']}<br>
                            <strong>PII Details:</strong> {log['pii_details']}<br>
                            <strong>Created Date:</strong> {log['created_date']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Failed to load safety logs: {safety_data}")
 
 
            with admin_tab3:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFA500 0%, #FF4500 100%);
                        color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
                    <h2 style="margin: 0; color: white; font-size: 1.8rem;">➕ Add Document</h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Submit new documents for indexing</p>
                </div>
                """, unsafe_allow_html=True)
               
                # Admin Document Submission Form
                st.markdown("### Add a new document to the system")
               
                # Input fields
                doc_id = st.text_input("Document ID", placeholder="Enter unique document ID")
                # resource_name = st.text_input("Resource Name", placeholder="Enter resource name (e.g., Confluence, VQD)")
                resource_name = st.selectbox(
                                "Resource Name",
                                options=["Confluence", "VQD", "Sharepoint", "ServiceNow", "Other"],  # Add more options as needed
                                help="Select a resource name from the dropdown"
                )
                page_url = st.text_input("Document Link", placeholder="Enter the document link")
                # admin_email = st.text_input("Admin Email", placeholder="Enter your email")
               
                # Submit button
                if st.button("Submit Document"):
                    if doc_id and resource_name and page_url:
                        try:
                            response = add_document(doc_id, resource_name, page_url)
                            st.success(f"Document added successfully! Response: {response}")
                        except Exception as e:
                            st.error(f"Error adding document: {str(e)}")
                    else:
                        st.error("All fields are required!")
 
            # Admin Tab 4: Manage Tabular Data
            # admin_tab4 = st.tab("📋 Manage Process Owners")
 
            with admin_tab4:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFA500 0%, #FF4500 100%);
                        color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
                    <h2 style="margin: 0; color: white; font-size: 1.8rem;">📋 Manage Process Owners</h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Add, view, and edit Process Owners</p>
                </div>
                """, unsafe_allow_html=True)
 
                # Check for authentication token
                token = st.session_state.get("access_token")
                if not token:
                    st.error("Authentication required. Please log in.")
                    st.stop()
 
                headers = {"Authorization": f"Bearer {token}"}
 
                # Fetch data from the backend
                if st.button("Fetch Data"):
                    try:
                        response = requests.get(f"{API_BASE_URL}/admin/process-owners", headers=headers, timeout=60)
                        if response.status_code == 200:
                            data = response.json()  # Assuming the backend returns JSON data
                            st.success("Data fetched successfully!")
                        else:
                            st.error(f"Failed to fetch data: {response.text}")
                            data = []
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {str(e)}")
                        data = []
 
                # Display data in a table
                if 'data' in locals() and data:
                    st.markdown("### Process Owners")
                    editable_data = st.data_editor(data, num_rows="dynamic", key="editable_table")
 
                    # Save changes
                    if st.button("Save Changes"):
                        try:
                            for row in editable_data:
                                owner_id = row.get("id")
                                if owner_id:  # Update existing row
                                    update_response = requests.put(
                                        f"{API_BASE_URL}/admin/process-owners/{owner_id}",
                                        json=row,
                                        headers=headers,
                                        timeout=60
                                    )
                                    if update_response.status_code == 200:
                                        st.success(f"Row with ID {owner_id} updated successfully!")
                                    else:
                                        st.error(f"Failed to update row with ID {owner_id}: {update_response.text}")
                                else:
                                    st.error("Row ID is missing. Cannot update.")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error saving changes: {str(e)}")
 
                # Add new row
                # Add new row
                st.markdown("### Add New Row")
                with st.form("add_row_form"):
                    domain = st.text_input("Domain", placeholder="Enter domain")
                    primary_owner = st.text_input("Primary Process Owner", placeholder="Enter primary process owner")
                    secondary_owner = st.text_input("Secondary Process Owner", placeholder="Enter secondary process owner")
                    remark = st.text_input("Remark", placeholder="Enter remark")
                    comments = st.text_area("Comments", placeholder="Enter comments")
                    submitted = st.form_submit_button("Add Row")
 
                    if submitted:
                        if domain and primary_owner:
                            # Use the exact field names expected by the backend
                            new_row = {
                                "Domain": domain,  # Capitalized to match backend
                                "PrimaryProcessOwner": primary_owner,  # Capitalized to match backend
                                "SecondaryProcessOwner": secondary_owner,
                                "Remark": remark,
                                "Comments": comments
                            }
                            try:
                                add_response = requests.post(f"{API_BASE_URL}/admin/process-owners", json=new_row, headers=headers, timeout=60)
                                if add_response.status_code == 200:
                                    st.success("New row added successfully!")
                                else:
                                    st.error(f"Failed to add row: {add_response.text}")
                            except requests.exceptions.RequestException as e:
                                st.error(f"Error adding row: {str(e)}")
                        else:
                            st.error("Domain and Primary Process Owner are required!")
 
                # Delete a row
                st.markdown("### Delete Row")
                delete_id = st.text_input("Enter ID of the row to delete", placeholder="Enter row ID")
                if st.button("Delete Row"):
                    if delete_id:
                        try:
                            delete_response = requests.delete(f"{API_BASE_URL}/admin/process-owners/{delete_id}", headers=headers, timeout=60)
                            if delete_response.status_code == 200:
                                st.success(f"Row with ID {delete_id} deleted successfully!")
                            else:
                                st.error(f"Failed to delete row with ID {delete_id}: {delete_response.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error deleting row: {str(e)}")
                    else:
                        st.error("Please enter a valid row ID to delete.")
       
 
        #Sidebar with only FAQs and Feedback
        with st.sidebar:
            # Admin status indicator
            if is_admin:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FFA500 0%, #FF4500 100%);
                           color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: white;">Admin Access</h3>
                    <p style="margin: -0.9rem 0 0 0; opacity: 0.9;">{}</p>
                </div>
                """.format(user_email), unsafe_allow_html=True)
 
        # Main app logic - show admin panel or regular chat
        if is_admin and st.sidebar.button("Admin Panel", use_container_width=True):
            st.session_state.show_admin = True
 
        if st.session_state.get('show_admin') and is_admin:
            # Show admin panel
            if st.sidebar.button("💬 Back to Chat", use_container_width=True):
                st.session_state.show_admin = False
                st.rerun()
            render_admin_panel()
        else:
            # Regular chat interface
            # FAQs
            st.sidebar.header("FAQs")
            try:
                # Cached version that runs in background thread
                status = True
                if not st.session_state["faqs"]:
                    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                    status, top_questions = get_top_questions(headers)
                    st.session_state["faqs"] = top_questions
               
                if status:
                    for i, (q, cnt) in enumerate(st.session_state["faqs"].items()):
                        # st.sidebar.markdown(f'<div class="faq-btn-wrap">', unsafe_allow_html=True)
                        # Standardize all FAQ button text to exactly 45 characters for consistency
                        truncated_q = q[:45] + "..." if len(q) > 45 else q
                        button_text = f"Q: {truncated_q}\n(Asked {cnt} times)"
                        if st.sidebar.button(
                            button_text,
                            key=f"faq_{i}"
                        ):
                            st.session_state["input_text"] = q
 
                       
                else:
                    st.info("No FAQs available at the moment.")
            except Exception as e:
                st.warning("FAQs temporarily unavailable")
 
 
        # Backend-only session creation function
        def create_new_session(reset_chat_state=False):
            """
            Backend-only session creation - maintains backend as single source of truth
            Args:
                reset_chat_state (bool): Whether to reset chat messages and feedback
            Returns:
                str: The created session ID from backend, or None if failed
            """
            try:
                token = st.session_state["access_token"]
                if not token:
                    st.error("Authentication required. Please refresh and log in again.")
                    st.stop()
               
                headers = {"Authorization": f"Bearer {token}"}
                session = get_requests_session()
                response = session.post(f"{API_BASE_URL}/sessions", headers=headers, timeout=60)
               
                if response.status_code == 200:
                    result = response.json()
                    new_session_id = result["session_id"]
                    print(f"Frontend: Created new session via backend API: {new_session_id}")
                   
                    # Update session state
                    st.session_state.session_id = new_session_id
                    if reset_chat_state:
                        st.session_state.messages = []
                        st.session_state.feedback_given = {}
                   
                    return new_session_id
                else:
                    # Backend session creation failed
                    error_msg = f"Backend session creation failed: HTTP {response.status_code}"
                    try:
                        error_detail = response.json().get('detail', response.text)
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                   
                    print(f"Frontend: {error_msg}")
                    st.error(f"Unable to create session. {error_msg}")
                    st.error("Please check if the backend service is running and try again.")
                    st.stop()
                   
            except requests.exceptions.RequestException as e:
                print(f"Frontend: Network error creating session: {e}")
                st.error(f"Network error: Unable to connect to backend service.")
                st.error("Please check your connection and ensure the backend is running.")
                st.stop()
            except Exception as e:
                print(f"Frontend: Unexpected error creating session: {e}")
                st.error(f"Unexpected error creating session: {str(e)}")
                st.error("Please refresh the page and try again.")
                st.stop()
 
        # Initialize session state using consolidated function
        if "session_id" not in st.session_state:
            create_new_session(reset_chat_state=False)
 
        if "messages" not in st.session_state:
            st.session_state.messages = []
 
        if "feedback_given" not in st.session_state:
            st.session_state.feedback_given = {}
       
        print(f"Frontend: Using session_id: {st.session_state.session_id}")
 
        # Memory optimization by limiting message history to prevent memory issues
        def optimize_message_history():
            MAX_MESSAGES = 100
            if len(st.session_state.messages) > MAX_MESSAGES:
                st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
                valid_message_ids = {f"msg_{i}" for i in range(len(st.session_state.messages))}
                st.session_state.feedback_given = {
                    k: v for k, v in st.session_state.feedback_given.items() if k in valid_message_ids
                }
 
       
        def validate_sso_token_with_backend(token):
            try:
                session = get_requests_session()
                headers = {"Authorization": f"Bearer {token}"}
                response = session.get(f"{API_BASE_URL}/sso/validate-token", headers=headers, timeout=60)
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, f"Status: {response.status_code}"
            except Exception as e:
                return False, str(e)
 
        #Feedback UI
        def render_feedback_ui(message_id, message_index=None):
            # Render feedback UI for a specific message
            if message_id in st.session_state.feedback_given:
                st.success("Feedback submitted! Thank you..!!")
                return
           
            # Get the message data
            if message_index is not None and message_index < len(st.session_state.messages):
                message = st.session_state.messages[message_index]
                response_id = message.get("response_id")
                chat_history_id = message.get("chat_history_id")
            else:
                response_id = None
                chat_history_id = None
           
            st.markdown("---")
            st.markdown("**Was this response helpful?**")
           
            # Create unique keys for this message
            col1, col2, col3 = st.columns([1, 1, 2])
           
            with col1:
                if st.button("👍 Helpful", key=f"up_{message_id}"):
                    submit_feedback(
                        response_id=response_id,
                        chat_history_id=chat_history_id,
                        is_helpful=True,
                        message_id=message_id
                    )
           
            with col2:
                if st.button("👎 Not Helpful", key=f"down_{message_id}"):
                    submit_feedback(
                        response_id=response_id,
                        chat_history_id=chat_history_id,
                        is_helpful=False,
                        message_id=message_id
                    )
           
            # Detailed feedback form
            with st.expander("Provide detailed feedback (optional)"):
                rating = st.select_slider(
                    "Rate this response (1-5 stars)",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"rating_{message_id}"
                )
               
                feedback_category = st.selectbox(
                    "What aspect needs improvement?",
                    ["accuracy", "helpfulness", "clarity", "completeness", "relevance", "other"],
                    key=f"category_{message_id}"
                )
               
                feedback_text = st.text_area(
                    "Additional comments",
                    placeholder="Tell us how we can improve...",
                    key=f"text_{message_id}"
                )
               
                # Detailed ratings
                col_acc, col_rel, col_clear, col_comp = st.columns(4)
                with col_acc:
                    is_accurate = st.checkbox("Accurate", key=f"acc_{message_id}")
                with col_rel:
                    is_relevant = st.checkbox("Relevant", key=f"rel_{message_id}")
                with col_clear:
                    is_clear = st.checkbox("Clear", key=f"clear_{message_id}")
                with col_comp:
                    is_complete = st.checkbox("Complete", key=f"comp_{message_id}")
               
                if st.button("Submit Detailed Feedback", key=f"submit_{message_id}"):
                    submit_feedback(
                        response_id=response_id,
                        chat_history_id=chat_history_id,
                        rating=rating,
                        is_helpful=None,
                        feedback_text=feedback_text,
                        feedback_category=feedback_category,
                        is_accurate=is_accurate,
                        is_relevant=is_relevant,
                        is_clear=is_clear,
                        is_complete=is_complete,
                        message_id=message_id
                    )
 
        def submit_feedback(response_id=None, chat_history_id=None, message_id=None, **feedback_data):
            # Submit feedback to the API
            try:
                # Debug logging
                print(f"Submitting feedback - response_id: {response_id}, chat_history_id: {chat_history_id}")
               
                # Retrieve token from the cookie
                token = st.session_state["access_token"]
                if not token:
                    st.error("Session expired. Please log in again.")
                    st.stop()
 
                # Add the  token to the headers
                headers = {"Authorization": f"Bearer {token}"}
               
                #to find response identifiers
                if not response_id and not chat_history_id:
                    # Try to find from the most recent assistant message
                    for msg in reversed(st.session_state.messages):
                        if msg["role"] == "assistant":
                            response_id = msg.get("response_id")
                            chat_history_id = msg.get("chat_history_id")
                            if response_id or chat_history_id:
                                print(f"Found identifiers from recent message: response_id={response_id}, chat_history_id={chat_history_id}")
                                break
               
                feedback_payload = {
                    "response_id": response_id,
                    "chat_history_id": chat_history_id,
                    "session_id": st.session_state.session_id,  # Add session_id
                    **feedback_data
                }
               
                # Remove message_id from payload as its only for UI state
                feedback_payload.pop("message_id", None)
               
                # Remove None values to avoid sending unnecessary data
                feedback_payload = {k: v for k, v in feedback_payload.items() if v is not None}
               
                # If no identifiers at all, we can add a flag for backend to use the latest chat
                if not response_id and not chat_history_id:
                    feedback_payload["use_latest_chat"] = True
               
                print(f"Final feedback payload: {feedback_payload}")
               
                response = requests.post(
                    f"{API_BASE_URL}/chatbot/feedback",
                    json=feedback_payload,
                    headers=headers,
                    timeout=30
                )
               
                if response.status_code == 200:
                    st.session_state.feedback_given[message_id] = True
                    st.success("Thank you for your feedback!")
                    st.rerun()
                else:
                    error_detail = "Unknown error"
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_json = response.json()
                            error_detail = error_json.get('detail', response.text)
                        else:
                            error_detail = response.text
                    except:
                        error_detail = f"HTTP {response.status_code}: {response.reason}"
                   
                    st.error(f"Failed to submit feedback: {error_detail}")
                    print(f"Feedback submission failed: {response.status_code} - {error_detail}")
                   
            except requests.exceptions.RequestException as e:
                st.error(f"Network error submitting feedback: {str(e)}")
                print(f"Network error: {e}")
            except Exception as e:
                st.error(f"Error submitting feedback: {str(e)}")
                print(f"Unexpected error: {e}")
 
   
        # Validate SSO token with backend
        token = st.session_state["access_token"]
        if token:
            token_valid = validate_user(token)
            if not token_valid:
                st.error("SSO token validation failed. Please refresh and login again.")
                st.session_state["access_token"] = None
                st.session_state["authenticated"] = False
                login()
 
        #Control Tiles
        def render_control_tiles():
            # Get system status for tile display
            is_connected, health_data = test_api_connection()
            status_class = "status-online" if is_connected else "status-offline"
            status_text = "Online" if is_connected else "Offline"
 
           
           
            # Create tiles
            col1, col2, col3, col4, col5 = st.columns(5)
           
            with col3:
 
                st.markdown(f"""
                    <div class="tile-description">
                        <span class="status-indicator {status_class}"></span>
                        {status_text}
                    </div>
                """, unsafe_allow_html=True)
           
            with col1:
 
               
                if st.button("New Session", key="new_session_tile_btn", use_container_width=True):
                    try:
                        new_session_id = create_new_session(reset_chat_state=True)
                        if new_session_id:
                            st.success(f"New session created: {new_session_id[:8]}...")
                            st.rerun()
                    except Exception as e:
                        print(f"New session creation failed: {e}")
           
            with col2:
 
               
                if st.button("Clear Session", key="clear_session_tile_btn", use_container_width=True):
                    st.session_state.messages = []
                    st.session_state.feedback_given = {}
                    st.success("Session cleared!")
                    st.rerun()
           
            with col4:
                if is_admin:
                    #For Testing additional features
                    pass
                else:
                    pass
 
           
            with col5:
                if "show_session_details" not in st.session_state:
                    st.session_state.show_session_details = False
 
                    st.session_state.show_session_details = not st.session_state.show_session_details

# Render the control tiles
        render_control_tiles()
       
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
 
        # Display chat messages
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
               
 
                if message["role"] == "assistant":
                    result_json = message["content"]
                    st.markdown(result_json.get("answer"))
                    if len(result_json.get("citation")) > 0:
                        st.markdown("---")
                        st.markdown("**Citations:**")
                        st.markdown("\n".join([f"- [Reference {i+1}]({citation})" for i, citation in enumerate(result_json.get("citation"))]))
                    if len(result_json.get("follow_up")) > 0:
                        st.markdown("---")
                        st.markdown("**Follow Up:**")
                        st.markdown("\n".join([f"{i+1}. {follow} " for i, follow in enumerate(result_json.get("follow_up"))]))
                else:
                    st.markdown(message['content'])
                if "timestamp" in message:
                    st.caption(f"*{message['timestamp']}*")
               
                # Feedback UI for assistant messages
                if message["role"] == "assistant":
                    render_feedback_ui(
                        message_id=f"msg_{i}",
                        message_index=i
                    )
 
        # Chat input
        # Chat Input Section
        if "input_text" not in st.session_state:
            st.session_state["input_text"] = ""  # Initialize input text state
        st.toast("Welcome..!!")
        # if prompt := st.chat_input("What's on your mind?"):
        prompt = st.chat_input("What's on your mind?") or st.session_state["input_text"]
        if prompt:
            # Clear the input text after submission
            st.session_state["input_text"] = ""
 
            if not test_api_connection()[0]:
                st.error("Cannot connect to ARB Chatbot API.")
                st.stop()
 
            # Add user message to session state
            user_message = {
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "session_id": st.session_state.session_id  # Store session_id for reference
            }
            st.session_state.messages.append(user_message)
            optimize_message_history()
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"*{user_message['timestamp']}*")
 
            # Get response from API
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
 
                with st.spinner("ARB Chatbot is Generating Response..."):
                    try:
                        # Retrieve token from the cookie
                        token = st.session_state["access_token"]
                        if not token:
                            st.error("Session expired. Please log in again.")
                            st.stop()
 
                        # Add the token to the headers
                        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
 
                        # Prepare request data - CRITICAL: Always send session_id
                        request_data = {
                            "message": prompt,
                            "session_id": st.session_state.session_id['session_id']
                        }
                       
                        print(f"Frontend: Sending chat request with session_id: {st.session_state.session_id}")
 
                        # Persistent session for better performance
                        session = get_requests_session()
                        response = session.post(
                            f"{API_BASE_URL}/chat",
                            json=request_data,
                            timeout=120,
                            headers=headers
                        )
 
                        if response.status_code == 200:
                            result = response.json()
                            print(result)
                            result_json = None
                            try:
                                result_json = json.loads(result["response"])
                            except:
                                result_json = {"answer": result["response"],
                                               "citation": [],
                                               "follow_up": []}
                                pass
 
                            assistant_response = result_json["answer"]
                            response_id = result.get("request_id") or result.get("response_id")
                            chat_history_id = result.get("chat_history_id")
                            returned_session_id = result.get("session_id")
 
                            # Verify session_id consistency
                            if returned_session_id and returned_session_id != st.session_state.session_id:
                                print(f"Frontend: Session ID mismatch! Sent: {st.session_state.session_id}, Received: {returned_session_id}")
                            else:
                                print(f"Frontend: Session ID consistent: {st.session_state.session_id}")
 
                            # Generate a response_id if not provided by API
                            if not response_id:
                                response_id = str(uuid.uuid4())
                                print(f"Generated fallback response_id: {response_id}")
 
                            # Extract token usage details
                            prompt_tokens = result.get("prompt_tokens")
                            completion_tokens = result.get("completion_tokens")
                            total_tokens = result.get("total_tokens")
                            total_cost = result.get("total_cost")
 
                            # Clear placeholder and show response
                            message_placeholder.empty()
                            st.markdown(assistant_response)
                            if len(result_json.get("citation")) > 0:
                                st.markdown("---")
                                st.markdown("**Citations:**")
                                st.markdown("\n".join([f"- [Reference {i+1}]({citation})" for i, citation in enumerate(result_json.get("citation"))]))
                            if len(result_json.get("follow_up")) > 0:
                                st.markdown("---")
                                st.markdown("**Follow Up:**")
                                st.markdown("\n".join([f"{i+1}. {follow} " for i, follow in enumerate(result_json.get("follow_up"))]))
                                # st.info(f"prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}, total_tokens={total_tokens}, total_cost={total_cost}")
 
                            # Add response to chat history with identifiers
                            assistant_message = {
                                "role": "assistant",
                                "content": result_json,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "response_id": response_id,
                                "chat_history_id": chat_history_id,
                                "session_id": st.session_state.session_id  # Store session_id for reference
                            }
                            st.session_state.messages.append(assistant_message)
                            st.caption(f"*{assistant_message['timestamp']}*")
 
                            # Show feedback UI for this new message
                            message_id = f"msg_{len(st.session_state.messages) - 1}"
                            render_feedback_ui(
                                message_id=message_id,
                                message_index=len(st.session_state.messages) - 1
                            )
                           
                            print(f"Frontend: Chat completed for session {st.session_state.session_id}, total messages: {len(st.session_state.messages)}")
 
                        elif response.status_code == 429:
                            message_placeholder.error("Rate limit exceeded. Please wait before sending another message.")
                        elif response.status_code == 503:
                            message_placeholder.warning("ARB Chatbot Server busy. Request queued for processing.")
                        else:
                            error_detail = response.text
                            try:
                                error_json = response.json()
                                error_detail = error_json.get("detail", error_detail)
                            except:
                                pass
                            message_placeholder.error(f"Error {response.status_code}: {error_detail}. Please refresh the page and try again.")
 
                    except requests.exceptions.Timeout:
                        message_placeholder.error("Request timed out after 120 seconds. Please re-submit your query.")
                    except requests.exceptions.ConnectionError:
                        message_placeholder.error("Connection error. Is the FastAPI server running on port 8000?")
                    except requests.exceptions.RequestException as e:
                        message_placeholder.error(f"Request error: {str(e)}")
 
        #Sidebar with only FAQs and Feedback
        with st.sidebar:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e8f5e8 100%, #d4edda 50%);
                       padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;">
                <h2 style="margin: 0 0 0.25rem 0; color: #2c3e50; font-size: 1.0rem;">Feedback & Stats</h2>
            </div>
            """, unsafe_allow_html=True)
           
            # Feedback action buttons
            col1, col2 = st.columns(2)
           
            with col1:
                if st.button("📝 My Feedback", use_container_width=True):
                    st.session_state['feedback'] = None
                    st.rerun()
           
            with col2:
                if st.button("📈 Overall Stats", use_container_width=True):
                    st.session_state['feedback_stats'] = None
                    st.rerun()
           
            #feedback statistics
            try:
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                if not st.session_state['feedback_stats']:
                    success, stats = get_feedback_stats(headers)
                    if success:
                        st.session_state['feedback_stats'] = stats
                if st.session_state["feedback_stats"]:
                    # Statistics cards
                    st.markdown("### Quick Stats")
                   
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="color: #667eea; margin: 0;">{st.session_state["feedback_stats"].get('total_feedback', 0)}</h3>
                            <p style="margin: 0; color: #7f8c8d;">Total Feedback</p>
                        </div>
                        """, unsafe_allow_html=True)
                   
                    with col2:
                        helpfulness_rate = stats.get('helpfulness_rate', 0)
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="color: #2ecc71; margin: 0;">{helpfulness_rate:.1f}%</h3>
                            <p style="margin: 0; color: #7f8c8d;">Helpful Rate</p>
                        </div>
                        """, unsafe_allow_html=True)
                   
                    if stats.get("average_rating"):
                        st.markdown(f"""
                        <div class="metric-container" style="margin-top: 0.5rem;">
                            <h3 style="color: #f39c12; margin: 0;">{stats['average_rating']:.1f}/5 ⭐</h3>
                            <p style="margin: 0; color: #7f8c8d;">Average Rating</p>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning("Stats temporarily unavailable")
           
            # Show recent feedback history
            try:
                if not st.session_state['feedback']:
                    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                    success, feedback_data = get_user_feedback(headers)
                    if success:
                        st.session_state['feedback'] = feedback_data
                if st.session_state['feedback'] and st.session_state['feedback'].get("feedback_history"):
                    st.markdown("### 📝 Recent Feedback")
                    for feedback in st.session_state['feedback']["feedback_history"][:2]:  # Show last 2 for sidebar
                        with st.expander(f"Feedback from {feedback['timestamp'][:10]}", expanded=False):
                            if feedback.get('rating'):
                                st.write(f"⭐ **Rating:** {feedback['rating']}/5")
                            st.write(f"👍 **Helpful:** {'Yes' if feedback.get('is_helpful') else 'No' if feedback.get('is_helpful') is False else 'N/A'}")
                            if feedback.get('feedback_text'):
                                st.write(f"💬 **Comment:** {feedback['feedback_text'][:100]}{'...' if len(feedback.get('feedback_text', '')) > 100 else ''}")
                elif success:
                    st.info("💡 No feedback history yet. Start giving feedback to see your history here!")
            except Exception as e:
                st.warning("Feedback history temporarily unavailable")
 
        # Footer
        st.markdown("---")
        st.markdown("**GSC ARB Chatbot** - Team ARB")