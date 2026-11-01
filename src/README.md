# Smart Internship Task Tracking System — DIT Task 07

A single shared Python + Streamlit application for internship task assignment, progress tracking, deadline-risk detection, workload insights, skill-gap analysis and CSV reporting.

## 1. Requirements
- Python 3.10 or newer
- pip
- Git
- Internet only for installing packages (the app itself runs locally)

## 2. Setup
```bash
# From the project root
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Run
```bash
streamlit run app.py
```
The SQLite database is created automatically at `data/internship_tracker.db`.

## 4. Demo admin
- Username: `admin`
- Password: `Admin@12345`

Change the demo password before any wider deployment. This project is a learning/demo application, not a production identity system. Keep the database private.

Interns can register from the login screen or be added by the admin. Use synthetic names and sample skills for evaluation.

## 5. Features
- Admin and intern role-based screens.
- PBKDF2-HMAC-SHA256 password hashing with unique salt.
- Intern registration and account activation/deactivation.
- Task assignment, priority, deadline and four-state workflow.
- Intern work-detail submissions.
- Rule-based deadline risk and priority suggestions.
- Workload distribution and skill gap comparison.
- Team dashboard and CSV report downloads.
- Activity log for key events.

## 6. Run tests
```bash
python -m unittest discover -s tests -v
```
The included unit tests cover password hashing and smart-rule functions. Complete the manual test cases in `docs/TEST_CASES.md` before submission.

## 7. Team Git collaboration
1. One member creates a private/shared GitHub repository and adds the other two as collaborators.
2. All members clone the same repository.
3. Create feature branches: `feature/member1-auth`, `feature/member2-tasks`, `feature/member3-dashboard`.
4. Work only in assigned module files; communicate changes to shared interfaces.
5. Commit small changes with meaningful messages.
6. Push branches and open pull requests.
7. Another member reviews each PR; resolve conflicts together.
8. Merge to `main` only after tests pass.
9. Everyone pulls the integrated `main` branch and runs the complete app.

Example:
```bash
git clone <team-repository-url>
cd DIT_Automation_Project
git checkout -b feature/member2-tasks
git add src/tasks.py src/smart_engine.py
git commit -m "Add task workflow and deadline rules"
git push -u origin feature/member2-tasks
```

Never commit `.env`, credentials, private datasets or the generated SQLite database. The `.gitignore` excludes the database.

## 8. Suggested member ownership
- Member 1: `src/auth.py`, `src/interns.py`
- Member 2: `src/tasks.py`, `src/smart_engine.py`
- Member 3: `src/database.py`, `src/dashboard.py`, `src/reports.py`, `tests/`
- All: `app.py` integration, reviews, documentation, demo and testing.

## 9. Folder structure
```text
DIT_Automation_Project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── input/
│   ├── output/
│   └── sample/
├── src/
├── tests/
├── reports/
├── screenshots/
└── docs/
```

## 10. Demo sequence
1. Log in as admin.
2. Register/add two synthetic interns with different skills.
3. Assign tasks with different due dates and required skills.
4. Open dashboard and explain status, workload, risk and skill-gap insights.
5. Log out and sign in as an intern.
6. Update a task status and submit work details.
7. Return to admin and show the updated dashboard and CSV reports.

## 11. Limitations and honest claims
Smart recommendations are transparent rule-based logic, not a trained AI model. Weekly activity is based on task update timestamps and submission records; it is not a formal productivity or attendance measure. Skill gaps depend on manually entered skill names. Add stronger audit, password reset, authorization review and deployment security before real-world use.

## 12. Documentation
See `docs/` for requirements, business rules, backlog, sprint plan, Agile workflow, flowchart, meeting notes, issue log, test cases and contribution log.
