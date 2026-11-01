import streamlit as st
import pandas as pd
from datetime import date, timedelta
from src.database import get_connection

def reports_view():
    st.title("📈 Reports & Weekly Performance")
    with get_connection() as con:
        tasks=pd.read_sql_query("""SELECT t.id,t.title,u.name AS intern,t.priority,t.status,
                                   t.due_date,t.created_at,t.updated_at
                                   FROM tasks t JOIN users u ON t.assignee_id=u.id""",con)
        subs=pd.read_sql_query("""SELECT s.*,u.name AS intern,t.title AS task_title
                                  FROM submissions s JOIN users u ON s.intern_id=u.id
                                  JOIN tasks t ON t.id=s.task_id""",con)
    if tasks.empty:
        st.info("No task data available for reporting.")
        return
    completed=tasks[tasks.status=="Completed"]
    rate=(len(completed)/len(tasks))*100
    st.metric("Overall completion rate",f"{rate:.1f}%")
    st.subheader("Weekly activity")
    cutoff=(date.today()-timedelta(days=7)).isoformat()
    weekly=tasks[pd.to_datetime(tasks.updated_at,errors="coerce") >= pd.Timestamp(cutoff)]
    st.write(f"Tasks updated in the last 7 days: **{len(weekly)}**")
    st.write(f"Completed tasks: **{len(completed)}**")
    st.subheader("Task report")
    st.dataframe(tasks,use_container_width=True,hide_index=True)
    st.download_button("Download task report (CSV)",tasks.to_csv(index=False).encode("utf-8"),
                       "task_report.csv","text/csv")
    st.subheader("Work submission log")
    if not subs.empty:
        st.dataframe(subs,use_container_width=True,hide_index=True)
        st.download_button("Download submissions (CSV)",subs.to_csv(index=False).encode("utf-8"),
                           "submission_report.csv","text/csv")
    else:
        st.info("No work submissions recorded yet.")
