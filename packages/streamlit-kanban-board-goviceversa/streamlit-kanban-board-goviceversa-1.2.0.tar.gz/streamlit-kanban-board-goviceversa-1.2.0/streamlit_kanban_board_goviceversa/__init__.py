import os
import streamlit.components.v1 as components

__version__ = "1.2.0"
__author__ = "Pierluigi Segatto"
__email__ = "pier@goviceversa.com"

# Export the main function
__all__ = ["kanban_board"]

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_kanban_board_goviceversa",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_kanban_board_goviceversa", path=build_dir)

def kanban_board(
    stages,
    deals,
    key=None,
    height=600,
    allow_empty_stages=True,
    draggable_stages=None,
    user_info=None,
    drag_validation_function=None,
    drag_restrictions=None,
    permission_matrix=None,
    business_rules=None,
    show_tooltips=True
):
    """
    Create a Kanban board for deal pipeline management with DLA V2 permissions.
    
    DLA V2 Architecture:
    -------------------
    All permissions are pre-computed by the backend DealPermissionEngine and attached 
    to each deal as 'dla_permissions'. The React component reads these permissions 
    directly, eliminating the need for client-side permission calculations.
    
    Parameters
    ----------
    stages : list of dict
        Column definitions for the kanban board.
        [{"id": "initial_review", "name": "Initial Review", "color": "#e3f2fd"}, ...]
    
    deals : list of dict
        Deal data with pre-computed DLA permissions. Each deal must have:
        
        Required fields:
        - id: unique identifier (str)
        - stage: current stage ID (str, must match a stage id)
        - deal_id: deal identifier for display (str)
        - company_name: company name (str)
        
        DLA V2 fields (pre-computed by backend):
        - dla_permissions: dict containing:
            - deal_info: {currency, amount, current_stage, deal_id}
            - user_info: {username, role, role_level, authority_type, authority_amount, ic_threshold}
            - stage_permissions: {[stage_id]: {allowed, reason, warning, visual_hint, ...}}
            - summary: {can_touch_deal, can_approve, can_reject, needs_ic_review, blocked_reason}
            - ui_hints: {allowed_drop_zones, blocked_drop_zones, drag_enabled, can_drag_from_current_stage}
        
        Optional display fields:
        - product_type, date, underwriter, priority, ready_to_be_moved, ic_review_completed, etc.
        
        Example DLA V2 deal:
        {
            "id": "deal_123",
            "stage": "initial_review", 
            "deal_id": "D-2024-001",
            "company_name": "Acme Corp",
            "currency": "EUR",
            "amount": 150000,
            "ic_review_completed": False,
            "ready_to_be_moved": False,
            "dla_permissions": {
                "deal_info": {"currency": "EUR", "amount": 150000, ...},
                "user_info": {"role": "underwriter", "authority_amount": 110000, ...},
                "stage_permissions": {
                    "initial_review": {"allowed": True, "visual_hint": {"color": "gray", ...}},
                    "underwriting": {"allowed": True, "visual_hint": {"color": "green", ...}},
                    "ic_review": {"allowed": True, "visual_hint": {"color": "green", ...}},
                    "approved": {"allowed": False, "reason": "Exceeds DLA authority", ...}
                },
                "summary": {"can_touch_deal": True, "needs_ic_review": True, ...},
                "ui_hints": {"drag_enabled": True, "can_drag_from_current_stage": True, ...}
            }
        }
    
    key : str, optional
        Unique key for the component (for Streamlit state management)
    
    height : int, default=600
        Height of the kanban board in pixels
        
    allow_empty_stages : bool, default=True
        Whether to show stages with no deals
        
    draggable_stages : list of str, optional
        LEGACY - Not used in DLA V2 (drag permissions are in dla_permissions.ui_hints)
        
    user_info : dict, optional
        Current user information and DLA configuration:
        {
            "username": "john.doe",
            "role": "underwriter",
            "email": "john@example.com",
            "dla_config": {  # DLA configuration embedded here
                "stages": [...],
                "user_facilities_info": {
                    "EUR": {"authority_amount": 110000, "ic_threshold_amount": 70000, ...},
                    "GBP": {...}
                }
            },
            "data_batch_id": "uuid-v4",  # Stable ID for data refresh detection
            "working_copy_version": 5     # Version for incremental updates
        }
        
    drag_validation_function : callable, optional
        LEGACY - Not used in DLA V2 (validations are pre-computed)
        
    drag_restrictions : dict, optional
        LEGACY - Not used in DLA V2 (restrictions are in dla_permissions)
        
    permission_matrix : dict, optional
        Role-based permission matrix (passed through but not used by React in DLA V2)
        
    business_rules : list, optional
        Business rules list (passed through but not used by React in DLA V2)
        
    show_tooltips : bool, default=True
        Whether to show tooltips with drag feedback messages
    
    Returns
    -------
    dict
        Component state with:
        - deals: updated deals list with new stages after user interactions
        - moved_deal: {deal_id, from_stage, to_stage} | None
        - clicked_deal: full deal object | None
        - validation_error: {deal_id, message, blocked} | None
        
        Additional state for background processing:
        - type: "stage_change" | "deal_click" | "ready_toggle" | None
        - changeId: sequential change ID
        - timestamp: change timestamp
        - dealId, fromStage, toStage: change details
        - resetReadyStatus: whether to reset ready_to_be_moved flag
    
    Notes
    -----
    DLA V2 uses a "pre-compute permissions, single source of truth" architecture:
    1. Backend computes all permissions via DealPermissionEngine
    2. Permissions attached to each deal as 'dla_permissions'
    3. React reads and displays based on these permissions
    4. No client-side permission calculations needed
    5. State changes trigger backend recomputation and re-render
    
    The working_copy_version in user_info enables efficient incremental updates
    when deals are modified via dialogs (without full page refresh).
    """
    
    # Normalize stages format
    normalized_stages = []
    for stage in stages:
        if isinstance(stage, str):
            normalized_stages.append({"id": stage, "name": stage, "color": None})
        else:
            normalized_stages.append({
                "id": stage.get("id", stage.get("name", "")),
                "name": stage.get("name", stage.get("id", "")),
                "color": stage.get("color", None)
            })
    
    # Validate deals have required fields
    for deal in deals:
        required_fields = ["id", "stage", "deal_id", "company_name"]
        missing_fields = [field for field in required_fields if field not in deal]
        if missing_fields:
            raise ValueError(f"Deal {deal.get('id', 'unknown')} missing required fields: {missing_fields}")
    
    # Handle draggable_stages parameter
    if draggable_stages is None:
        # Default behavior - all stages are draggable
        draggable_stages = [stage["id"] for stage in normalized_stages]
    elif draggable_stages == []:
        # Explicitly disable all dragging
        draggable_stages = []
    
    # Prepare drag restrictions data
    prepared_drag_restrictions = drag_restrictions or {}
    
    # Add user-specific drag validation if provided
    if user_info and drag_validation_function:
        # Pre-compute restrictions for all deals
        for deal in deals:
            deal_id = deal["id"]
            if deal_id not in prepared_drag_restrictions:
                prepared_drag_restrictions[deal_id] = {
                    "draggable": True,
                    "allowed_stages": [],
                    "blocked_stages": [],
                    "reasons": {}
                }
            
            # Check each stage for this deal
            for stage in normalized_stages:
                if stage["id"] != deal["stage"]:  # Don't check current stage
                    validation_result = drag_validation_function(
                        deal, deal["stage"], stage["id"], user_info
                    )
                    
                    if validation_result.get("allowed", True):
                        prepared_drag_restrictions[deal_id]["allowed_stages"].append(stage["id"])
                    else:
                        prepared_drag_restrictions[deal_id]["blocked_stages"].append(stage["id"])
                        prepared_drag_restrictions[deal_id]["reasons"][stage["id"]] = validation_result.get("reason", "Not authorized")
    
    component_value = _component_func(
        stages=normalized_stages,
        deals=deals,
        height=height,
        allow_empty_stages=allow_empty_stages,
        draggable_stages=draggable_stages,
        user_info=user_info,
        drag_restrictions=prepared_drag_restrictions,
        permission_matrix=permission_matrix,
        business_rules=business_rules,
        show_tooltips=show_tooltips,
        key=key,
        default={"deals": deals, "moved_deal": None, "clicked_deal": None, "validation_error": None}
    )
    
    return component_value 