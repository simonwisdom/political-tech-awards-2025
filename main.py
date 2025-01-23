import streamlit as st
import pandas as pd
from typing import Optional
import auth
import database as db
import utils
from config import TOTAL_BUDGET, MAX_PROJECTS

# Page configuration
st.set_page_config(
    page_title="Political Technology Awards",
    page_icon="🏆",
    layout="wide"
)

def render_login():
    """Render login/verification interface."""
    st.title("Political Technology Awards")
    st.subheader("£5M Budget Allocation System")
    
    # Check for verification token in URL
    token = st.query_params.get("token", None)
    email = st.query_params.get("email", None)
    
    if token and email:
        success, message = auth.verify_email(email, token)
        if success:
            st.success(message)
            st.query_params.clear()  # Clear URL parameters
            st.rerun()  # Rerun the app to show the explorer view
        else:
            st.error(message)
    
    if not auth.is_verified():
        with st.form("login_form"):
            email = st.text_input("Email address")
            submit = st.form_submit_button("Start Verification")
            
            if submit:
                if not utils.validate_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    success, message = auth.start_verification(email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def render_explorer():
    """Render project explorer tab."""
    # Custom CSS for fixed layout and scrollable columns
    st.markdown("""
        <style>
            /* Main container styles */
            .main > div {
                max-width: 100% !important;
                padding: 0 1rem;
            }
            
            /* Column container styles */
            [data-testid="stHorizontalBlock"] {
                width: 100%;
                gap: 1rem;
                padding: 1rem 0;
            }
            
            /* All columns base styles */
            [data-testid="stHorizontalBlock"] > div {
                min-width: 0;  /* Allow columns to shrink below content size */
                flex-shrink: 1;  /* Allow columns to shrink */
            }
            
            /* Left column scrollable container */
            [data-testid="stHorizontalBlock"] > div:first-child {
                overflow: auto !important;
                height: calc(100vh - 150px);
                flex: 1;
            }
            
            /* Middle column */
            [data-testid="stHorizontalBlock"] > div:nth-child(2) {
                overflow: auto !important;
                height: calc(100vh - 150px);
                flex: 1.5;
            }
            
            /* Right column */
            [data-testid="stHorizontalBlock"] > div:last-child {
                overflow: auto !important;
                height: calc(100vh - 150px);
                flex: 1.5;
            }
            
            /* Button styles */
            div.stButton > button {
                width: 100%;
                text-align: left;
                padding: 8px;
                background-color: #f0f5f0;
                color: #2c4a2c;
                border: 1px solid #c5d6c5;
                border-radius: 4px;
                margin-bottom: 8px;
                font-size: 0.9em;
            }
            div.stButton > button:hover {
                background-color: #e5efe5;
                border-color: #86a886;
            }
            div.stButton > button:active {
                background-color: #d8e6d8;
            }
            
            /* Hide scrollbar for Chrome, Safari and Opera */
            [data-testid="stHorizontalBlock"] > div::-webkit-scrollbar {
                display: none;
            }
            
            /* Hide scrollbar for IE, Edge and Firefox */
            [data-testid="stHorizontalBlock"] > div {
                -ms-overflow-style: none;  /* IE and Edge */
                scrollbar-width: none;  /* Firefox */
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Project Explorer")
    
    # Load website data
    try:
        df = pd.read_csv('data/website_data.csv')
        df = df.fillna('')  # Replace NaN with empty strings
    except Exception as e:
        st.error(f"Error loading website data: {str(e)}")
        return
    
    # Create three columns layout with explicit ratios
    col1, col2, col3 = st.columns([1, 1.5, 1.5], gap="small")
    
    with col1:
        st.subheader("Projects")
        
        # Create a search box with a unique key for each tab
        tab_name = st.session_state.get('active_tab', 'explorer')
        
        # Add surprise me button
        if st.button("🎲 Surprise Me!", key=f"surprise_{tab_name}"):
            random_row = df.sample(n=1).iloc[0]
            st.session_state['selected_website'] = random_row
            st.rerun()
            
        search = st.text_input("Search projects", key=f"website_search_{tab_name}")
        
        # Filter websites based on search
        if search:
            mask = (
                df['url'].str.contains(search, case=False, na=False) |
                df['title'].str.contains(search, case=False, na=False) |
                df['content_summary'].str.contains(search, case=False, na=False)
            )
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # Display website list with regular Streamlit buttons
        for _, row in filtered_df.iterrows():
            display_name = row['title'] if row['title'] else row['url']
            if len(display_name) > 50:
                display_name = display_name[:47] + "..."
            
            if st.button(display_name, key=f"btn_{tab_name}_{row['url']}"):
                st.session_state['selected_website'] = row
                st.rerun()
    
    with col2:
        if 'selected_website' in st.session_state and st.session_state['selected_website'] is not None:
            website = st.session_state['selected_website']
            
            # Display screenshot if available
            if website['screenshot_path']:
                try:
                    st.image(website['screenshot_path'], width=None)  # None means full width
                except Exception as e:
                    st.error(f"Error loading screenshot: {str(e)}")
            
            # Check if it's a GitHub repository
            if website['url'].startswith('https://github.com'):
                st.markdown("### GitHub Statistics")
                
                # Create two columns for GitHub stats
                stats_col1, stats_col2 = st.columns(2)
                
                with stats_col1:
                    st.metric("⭐ Stars", f"{website['stars']:,}")
                    st.metric("🔄 Forks", f"{website['forks']:,}")
                    st.metric("⚠️ Open Issues", f"{website['open_issues']:,}")
                
                with stats_col2:
                    st.metric("📅 Created", website['created_at'].split('T')[0] if website['created_at'] else 'N/A')
                    st.metric("🔄 Last Update", website['last_update'].split('T')[0] if website['last_update'] else 'N/A')
                    st.metric("💻 Language", website['language'] if website['language'] else 'N/A')
            else:
                # Display regular metadata for non-GitHub websites
                st.markdown("### Additional Information")
                metadata = {
                    'Type': website['type'],
                    'Status': website['status_code'],
                    'Server': website['server'],
                    'Creation Date': website['creation_date'],
                    'Registrar': website['registrar']
                }
                
                # Filter out empty values and display
                metadata = {k: v for k, v in metadata.items() if v}
                if metadata:
                    for key, value in metadata.items():
                        st.write(f"**{key}:** {value}")
    
    with col3:
        if 'selected_website' in st.session_state and st.session_state['selected_website'] is not None:
            website = st.session_state['selected_website']
            
            # Display website details
            st.markdown(f"### {website['title'] if website['title'] else website['url']}")
            st.markdown(f"[{website['url']}]({website['url']})")
            
            # Display summary if available
            if website['content_summary']:
                st.markdown("### Summary")
                st.write(website['content_summary'])
        else:
            st.info("Select a project from the list to view details")

def render_allocation_mockup():
    """Render allocation logic tab mockup."""
    st.header("Allocation Logic")
    
    # Coming soon banner
    st.warning("🚧 Coming Soon! 🚧")
    
    # Mockup content
    st.subheader("Define Your Allocation Rules")
    
    

def render_analysis_mockup():
    """Render analysis tab mockup."""
    st.header("Final Allocation Analysis")
    
    # Coming soon banner
    st.warning("🚧 Coming Soon! 🚧")
    

def main():
    """Main application entry point."""
    # Initialize session state but skip authentication
    auth.initialize_session_state()
    
    # Set session state as verified by default
    st.session_state[auth.SESSION_IS_VERIFIED] = True
    st.session_state[auth.SESSION_USER_EMAIL] = "demo@example.com"  # Demo user
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs([
        "Explorer", "Allocation Logic", "Analysis"
    ])
    
    with tab1:
        st.session_state['active_tab'] = 'explorer'
        render_explorer()
        
    with tab2:
        st.session_state['active_tab'] = 'allocation'
        render_allocation_mockup()
        
    with tab3:
        st.session_state['active_tab'] = 'analysis'
        render_analysis_mockup()

if __name__ == "__main__":
    main() 