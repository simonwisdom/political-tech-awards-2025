import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st
from config import TOTAL_BUDGET, MAX_PROJECTS
import database as db

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_allocation_amount(amount: int) -> bool:
    """Validate a single allocation amount."""
    return isinstance(amount, int) and amount >= 0

def validate_total_allocation(email: str, new_amount: int, 
                            project_id: str) -> Tuple[bool, str]:
    """Validate total allocation against budget."""
    current_total = db.get_total_allocated(email)
    
    # Adjust for updating existing allocation
    current_allocations = db.get_user_allocations(email)
    if project_id in current_allocations:
        current_total -= current_allocations[project_id]
    
    new_total = current_total + new_amount
    
    if new_total > TOTAL_BUDGET:
        remaining = TOTAL_BUDGET - current_total
        return False, f"Allocation exceeds budget. Remaining: £{remaining:,}"
    
    return True, ""

@st.cache_data
def load_projects() -> pd.DataFrame:
    """Load and cache projects data."""
    try:
        df = pd.read_csv('data/projects.csv')
        required_columns = ['project_id', 'name', 'description', 
                          'category', 'status']
        
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in projects.csv")
            
        return df
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        return pd.DataFrame(columns=['project_id', 'name', 'description', 
                                   'category', 'status'])

def filter_projects(df: pd.DataFrame, 
                   search_query: str = "",
                   categories: List[str] = None,
                   statuses: List[str] = None) -> pd.DataFrame:
    """Filter projects based on search query and filters."""
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    # Apply text search
    if search_query:
        search_mask = (
            filtered_df['name'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Apply category filter
    if categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    
    # Apply status filter
    if statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(statuses)]
    
    return filtered_df

def format_currency(amount: int) -> str:
    """Format amount as currency."""
    return f"£{amount:,}"

def calculate_allocation_metrics(email: str) -> Dict[str, int]:
    """Calculate allocation metrics for a user."""
    allocations = db.get_user_allocations(email)
    total_allocated = sum(allocations.values())
    remaining_budget = TOTAL_BUDGET - total_allocated
    num_projects = len(allocations)
    
    return {
        'total_allocated': total_allocated,
        'remaining_budget': remaining_budget,
        'num_projects': num_projects,
        'max_projects': MAX_PROJECTS
    }

def get_category_allocation_data(email: str) -> pd.DataFrame:
    """Get allocation data grouped by category."""
    projects_df = load_projects()
    allocations = db.get_user_allocations(email)
    
    # Create DataFrame with allocations
    alloc_df = pd.DataFrame.from_dict(
        allocations, 
        orient='index', 
        columns=['amount']
    ).reset_index()
    alloc_df.columns = ['project_id', 'amount']
    
    # Merge with projects data
    merged_df = alloc_df.merge(
        projects_df[['project_id', 'category']], 
        on='project_id'
    )
    
    # Group by category
    category_data = merged_df.groupby('category')['amount'].agg([
        'sum', 'count'
    ]).reset_index()
    
    category_data.columns = ['category', 'total_amount', 'project_count']
    return category_data

def export_allocations(email: str) -> pd.DataFrame:
    """Export user allocations as DataFrame."""
    projects_df = load_projects()
    allocations = db.get_user_allocations(email)
    
    # Create DataFrame with allocations
    alloc_df = pd.DataFrame.from_dict(
        allocations, 
        orient='index', 
        columns=['amount']
    ).reset_index()
    alloc_df.columns = ['project_id', 'amount']
    
    # Merge with projects data
    export_df = alloc_df.merge(
        projects_df[['project_id', 'name', 'category', 'status']], 
        on='project_id'
    )
    
    # Reorder columns
    export_df = export_df[[
        'project_id', 'name', 'category', 'status', 'amount'
    ]]
    
    return export_df 