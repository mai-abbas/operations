from flask import Flask, render_template, request
import pandas as pd
import re



app = Flask(__name__)


# --- Home page ---
@app.route("/")
def index():
    return render_template("index.html")

def extract_grades(stage_range_text):
    """
    Extract grades like EG01, EG1, G11, EG10 from messy text
    Returns normalized list: EG01, EG04, G11
    """
    if not stage_range_text:
        return []

    text = str(stage_range_text).upper()

    # Ignore bad values
    if text in ["0", "#N/A"]:
        return []

    # Find EG or G followed by numbers
    matches = re.findall(r'(EG|G)\s*0?(\d{1,2})', text)

    grades = []
    for prefix, num in matches:
        grades.append(f"{prefix}{num.zfill(2)}")

    return grades

# --- Links page ---
@app.route("/links")
def links():
    resources_links = [
        {"title": "Nagwa Tutors, Web", "url": "https://tutors.nagwa.com/"},
        {"title": "Tutors' Bio and Photo", "url": "https://docs.google.com/forms/d/e/1FAIpQLSeevdfrTWuwoAJF8rLaFFREcF5kAgoXdBV-SH6UWJj4Be1NRw/viewform"},
        {"title": "Tutors' Bank Details", "url": "https://docs.google.com/forms/d/e/1FAIpQLSd7AAVYMxdiIq5vDpWkMkMhsx5tsOXFPI9nbZWhHrU1c2LtdA/viewform"},
        {"title": "كيفية الوصول للواجب على التطبيق", "url": "https://drive.google.com/file/d/176zg_my4UhsLziXJXKf9RrN_UZRr4ugk/view"},
        {"title": "ازاي المدرس يقدر يعمل scroll عشان يشوف باقي الشريحة لو كانت طويلة", "url": "https://drive.google.com/file/d/1aNW0ErEMqNSISlpM74W2ItmIzebMQ0Gx/view?usp=sharing"},
        {"title": "Adjust date & time", "url": "https://drive.google.com/file/d/1GMCiGoQCSK9L0YLZ3A1ioltKYKWS4GTq/view?usp=sharing"},
        {"title": "2025-2026 materials", "url": "https://drive.google.com/drive/folders/15khds8Aglie0IYOB9KDUuU9oktpXqXXv"},
        {"title": "Tutors Onboarding Presentation", "url": "https://docs.google.com/presentation/d/1vU86KMVRkqGZk1YNjAEqEFcH1OmVQHb8/edit?slide=id.p1#slide=id.p1"},
        {"title": "واجبات المعلم واللائحة التنظيمية 2025-2026", "url": "https://docs.google.com/document/d/11R_ZoLSKZXJqihZv68qf4zXFDHyFlXvPRVoHhbE7yUo/edit?tab=t.0"},
        {"title": "Branding Videos", "url": "https://docs.google.com/forms/d/e/1FAIpQLSeWhqtKzbwi8Xo_Tt-IuyKCWerOMFT2YZOrm964SVLlsBUB2A/viewform?usp=preview"},
        {"title": "اعتذار عن حصة", "url": "https://docs.google.com/forms/d/e/1FAIpQLSeK4pLRWd2qPGIrQlcVXHhRyOW_S6feDD3VN3ioZAzwOM8hwg/viewform?usp=preview"},
        {"title": "Content and Technical Issues", "url": "https://docs.google.com/forms/d/e/1FAIpQLSf34hoUO8MM24eLRS0Pxz5l1YbmiR3CohHAgSQ-QE5_lkIkew/viewform?usp=header"}
    ]
    return render_template("links.html", resources_links=resources_links)

# --- Tutors page with multi-field search ---
@app.route("/tutors")
def tutors():
    # 🔁 ALWAYS read the latest Excel file
    tutors_df = pd.read_excel("data/tutors.xlsx")
    tutors_list = tutors_df.to_dict(orient="records")

    name_query = request.args.get("name", "").strip().lower()
    email_query = request.args.get("email", "").strip().lower()
    subject_query = request.args.get("subject", "").strip().lower()
    stage_query = request.args.get("stage", "").strip().lower()
    stage_range_query = request.args.get("stage_range", "").strip().upper()
    status_query = request.args.get("status", "").strip().lower()

    filtered_tutors = []

    for t in tutors_list:
        match = True

        if name_query and name_query not in str(t.get("Tutor Name", "")).lower():
            match = False

        if email_query and email_query not in str(t.get("Email", "")).lower():
            match = False

        if subject_query and subject_query not in str(t.get("Subject", "")).lower():
            match = False

        if stage_query and stage_query != str(t.get("Stage", "")).strip().lower():
            match = False

        if status_query and status_query != str(t.get("Status", "")).strip().lower():
            match = False

        if stage_range_query:
            tutor_grades = extract_grades(t.get("Stage Range", ""))
            if stage_range_query not in tutor_grades:
                match = False

        if match:
            filtered_tutors.append(t)

    return render_template("tutors.html", tutors=filtered_tutors)



if __name__ == "__main__":
    app.run()

