"""
Navigation Menu Builder
=======================
Generates the hierarchical sidebar navigation tree tailored to user roles,
tenant module subscriptions, and permissions.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

_CACHED_TREE = None

CONTRIBUTIONS_NAV = {
    "_id": "nav-contributions",
    "title": "Contributions",
    "icon": {
        "iconName": "MdStars",
        "iconPackage": "react-icons/md"
    },
    "mainRoute": "/contributions/dashboard",
    "order": 1,
    "hasChildren": True,
    "isParent": True,
    "children": [
        {
            "_id": "nav-contributions-dashboard",
            "title": "Equity & Profit Share",
            "icon": {
                "iconName": "MdPieChart",
                "iconPackage": "react-icons/md"
            },
            "mainRoute": "/contributions/dashboard",
            "order": 1,
            "hasChildren": False,
            "isParent": False,
            "parentId": "nav-contributions",
            "children": []
        },
        {
            "_id": "nav-contributions-add",
            "title": "Add Work Status",
            "icon": {
                "iconName": "MdAddCircleOutline",
                "iconPackage": "react-icons/md"
            },
            "mainRoute": "/contributions/add",
            "order": 2,
            "hasChildren": False,
            "isParent": False,
            "parentId": "nav-contributions",
            "children": []
        },
        {
            "_id": "nav-contributions-followups",
            "title": "Follow-Up Radar",
            "icon": {
                "iconName": "MdNotificationsActive",
                "iconPackage": "react-icons/md"
            },
            "mainRoute": "/contributions/follow-ups",
            "order": 3,
            "hasChildren": False,
            "isParent": False,
            "parentId": "nav-contributions",
            "children": []
        },
        {
            "_id": "nav-contributions-reports",
            "title": "Contribution Reports",
            "icon": {
                "iconName": "MdAssessment",
                "iconPackage": "react-icons/md"
            },
            "mainRoute": "/contributions/reports",
            "order": 4,
            "hasChildren": False,
            "isParent": False,
            "parentId": "nav-contributions",
            "children": []
        }
    ]
}

# Module mapping for top-level navigation roots
MODULE_KEY_MAP = {
    "contributions": "contributions",
    "attendance": "attendance",
    "payroll": "payroll",
    "crm": "crm",
    "tasks": "tasks",
    "tickets": "tickets",
    "accounts": "accounts",
    "assets": "assets",
    "hrms": "hrms",
}

EXCLUDED_TITLES = {"Logout", "Profile", "Search"}


def _load_base_tree() -> List[Dict[str, Any]]:
    global _CACHED_TREE
    if _CACHED_TREE is not None:
        return _CACHED_TREE

    sidebar_file = Path(__file__).resolve().parent.parent.parent / "scripts" / "playground" / "sidebar.json"
    if not sidebar_file.exists():
        # Fallback to local copy if path differences occur
        sidebar_file = Path("scripts/playground/sidebar.json")

    items = []
    if sidebar_file.exists():
        try:
            with open(sidebar_file, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception:
            items = []

    id_map = {}
    for it in items:
        clean = dict(it)
        clean["children"] = []
        id_map[str(clean["_id"])] = clean

    raw_tree = []
    for it in items:
        node = id_map[str(it["_id"])]
        pid = it.get("parentId")
        if pid and str(pid) in id_map:
            id_map[str(pid)]["children"].append(node)
        elif not pid:
            raw_tree.append(node)

    # Sort each level by order
    def sort_level(nodes):
        nodes.sort(key=lambda x: x.get("order", 0))
        for n in nodes:
            if n.get("children"):
                sort_level(n["children"])

    sort_level(raw_tree)

    # Filter out utility screens (Logout, Profile, Search) from sidebar
    filtered_tree = [node for node in raw_tree if node.get("title") not in EXCLUDED_TITLES]

    # Insert Contributions right after Dashboard (or at order 1)
    filtered_tree.insert(1, CONTRIBUTIONS_NAV)

    _CACHED_TREE = filtered_tree
    return _CACHED_TREE


def get_user_navigation(user: Any, enabled_modules: List[str] = None, is_superadmin: bool = False) -> List[Dict[str, Any]]:
    """
    Returns filtered navigation nodes for the requesting user and tenant.
    """
    base_tree = _load_base_tree()
    if enabled_modules is None:
        enabled_modules = []

    enabled_set = set(m.lower() for m in enabled_modules)

    # If is_superadmin and has all or many modules, allow full module list
    filtered = []
    for node in base_tree:
        title_lower = (node.get("title") or "").lower()
        route_lower = (node.get("mainRoute") or "").lower()

        # Core items always visible
        if title_lower in ("dashboard", "feed", "master data", "settings", "teams", "policies"):
            filtered.append(node)
            continue

        # Check module matching
        matched_mod = None
        for mod, key in MODULE_KEY_MAP.items():
            if key in title_lower or key in route_lower or (key == "tasks" and route_lower == "/t"):
                matched_mod = mod
                break

        if not matched_mod:
            # Undefined module item, show for superadmin
            if is_superadmin:
                filtered.append(node)
            continue

        if is_superadmin or matched_mod in enabled_set:
            filtered.append(node)

    return filtered

