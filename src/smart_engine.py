from datetime import date
import pandas as pd

def deadline_risk(due_date, status):
    if status == "Completed":
        return "No Risk"
    due = date.fromisoformat(str(due_date))
    days = (due - date.today()).days
    if days < 0:
        return "Overdue"
    if days <= 2:
        return "High Risk"
    if days <= 5:
        return "Medium Risk"
    return "Low Risk"

def suggest_priority(due_date, status="To Do"):
    if status == "Completed":
        return "Low"
    due = date.fromisoformat(str(due_date))
    days = (due - date.today()).days
    if days < 0 or days <= 1:
        return "Critical"
    if days <= 3:
        return "High"
    if days <= 7:
        return "Medium"
    return "Low"

def workload_summary(tasks_df, interns_df):
    if interns_df.empty:
        return pd.DataFrame(columns=["intern_id","name","active_tasks","total_tasks"])
    active = tasks_df[~tasks_df["status"].eq("Completed")] if not tasks_df.empty else tasks_df
    counts = active.groupby("assignee_id").size().to_dict() if not active.empty else {}
    totals = tasks_df.groupby("assignee_id").size().to_dict() if not tasks_df.empty else {}
    result = interns_df[["id","name"]].copy()
    result["active_tasks"] = result["id"].map(counts).fillna(0).astype(int)
    result["total_tasks"] = result["id"].map(totals).fillna(0).astype(int)
    return result.rename(columns={"id":"intern_id"})

def skill_gap(required_skills, intern_skills):
    required = {x.strip().lower() for x in (required_skills or "").split(",") if x.strip()}
    owned = {x.strip().lower() for x in (intern_skills or "").split(",") if x.strip()}
    return sorted(required - owned)
