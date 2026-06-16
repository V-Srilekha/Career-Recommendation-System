from flask import Flask, render_template, request
import spacy

app = Flask(__name__)

nlp = spacy.load("en_core_web_md")

# Define career categories and keywords for NLP similarity
CAREER_CATEGORIES = {
    "Technology & IT": ["Software Developer", "Data Scientist", "AI Engineer","ML Engineer","Data Analyst", "Network Administrator"],
    "Business & Management": ["Marketing Manager", "Business Analyst", "Sales Executive", "Financial Advisor"],
    "Healthcare & Life Sciences": ["Doctor", "Nurse", "Pharmacist", "Medical Researcher"],
    "Arts & Creative Fields": ["Graphic Designer", "Musician", "Writer", "Photographer"],
    "Engineering & Technical Fields": ["Mechanical Engineer", "Civil Engineer", "Electrical Engineer"],
    "Science & Research": ["Physicist", "Chemist", "Research Scientist"],
    "Social Sciences & Education": ["Teacher", "Social Worker", "Counselor"],
    "Government & Public Services": ["Police Officer", "Civil Servant", "Diplomat"],
}

career_keywords = {
    "Technology & IT": ["programming", "data analysis", "technology", "software", "ai", "ml", "coding", "development"],
    "Business & Management": ["business", "marketing", "sales", "management", "finance", "leadership", "strategy", "commerce"],
    "Healthcare & Life Sciences": ["healthcare", "medicine", "nurse", "doctor", "biology", "pharmacy", "medical", "patient care"],
    "Arts & Creative Fields": ["art", "design", "creative", "music", "writing", "photography", "dance", "film"],
    "Engineering & Technical Fields": ["engineering", "mechanical", "civil", "electrical", "technical", "construction", "manufacturing"],
    "Science & Research": ["science", "research", "physics", "chemistry", "biology", "laboratory", "analysis"],
    "Social Sciences & Education": ["education", "teaching", "social", "counseling", "psychology", "community"],
    "Government & Public Services": ["government", "public service", "police", "diplomacy", "administration", "law enforcement"],
}

def get_recommendations(user_terms, threshold=0.7):
    recommendations = set()
    user_docs = [nlp(term.lower()) for term in user_terms if term.strip() != ""]

    for category, keywords in career_keywords.items():
        keyword_docs = [nlp(k) for k in keywords]
        for user_doc in user_docs:
            for key_doc in keyword_docs:
                if user_doc.similarity(key_doc) >= threshold:
                    recommendations.add(category)
                    break
            if category in recommendations:
                break
    return recommendations

def recommend_careers(form_data):
    recommendations = set()

    # Personal info
    age = form_data.get("age", "")
    gender = form_data.get("gender", "").lower()

    # Academic background
    education_level = form_data.get("education_level", "").lower()
    stream = form_data.get("stream", "").lower()
    grades = form_data.get("grades", "")

    # Skills
    technical_skills = [s.strip() for s in form_data.get("technical_skills", "").split(",") if s.strip() != ""]
    soft_skills = [s.strip() for s in form_data.get("soft_skills", "").split(",") if s.strip() != ""]

    # Interests and preferences
    field_of_interest = form_data.getlist("field_of_interest")
    work_style = form_data.getlist("work_style")
    work_environment = form_data.getlist("work_environment")

    # Personality traits
    introvert_extrovert = form_data.get("introvert_extrovert", "").lower()
    creative_analytical = form_data.get("creative_analytical", "").lower()
    risk_taking = form_data.get("risk_taking", "")

    # Goals and aspirations
    career_goals = form_data.get("career_goals", "").lower()
    

    # Rule-based recommendation example with academic stream
    if "science" in stream:
        recommendations.update(["Technology & IT", "Engineering & Technical Fields", "Healthcare & Life Sciences", "Science & Research"])
    elif "computers" in stream:
        recommendations.add("Technology & IT")
    elif "commerce" in stream:
        recommendations.add("Business & Management")
    elif "arts" in stream or "humanities" in stream:
        recommendations.update(["Arts & Creative Fields", "Social Sciences & Education", "Government & Public Services"])

    # Combine various textual inputs for NLP matching
    combined_terms = technical_skills + soft_skills + field_of_interest + [introvert_extrovert, creative_analytical, career_goals]

    nlp_recommendations = get_recommendations(combined_terms)
    recommendations.update(nlp_recommendations)

    # Personality-based tweaks
    if "introvert" in introvert_extrovert:
        recommendations.add("Science & Research")
    if "extrovert" in introvert_extrovert:
        recommendations.add("Business & Management")

    # Fallback to all if empty
    if not recommendations:
        recommendations.update(CAREER_CATEGORIES.keys())

    # Prepare output with sample careers
    career_suggestions = {cat: CAREER_CATEGORIES[cat] for cat in recommendations}

    return career_suggestions

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        recommendations = recommend_careers(request.form)
        return render_template("index.html", recommendations=recommendations, form_data=request.form)
    return render_template("index.html", recommendations=None)

if __name__ == "__main__":
    app.run(debug=True)
