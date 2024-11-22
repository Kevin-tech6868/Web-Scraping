import streamlit as st
from fpdf import FPDF
from io import BytesIO
from serpapi import GoogleSearch
import requests
import random

# Sample course data
courses = {
    "Data Science": {
        "Python for Data Science": "Learn Python basics, Pandas, Matplotlib, and machine learning.",
        "Machine Learning": "Master supervised and unsupervised algorithms using scikit-learn.",
        "Deep Learning with TensorFlow": "Build neural networks with TensorFlow and Keras."
    },
    "Web Development": {
        "HTML, CSS, JavaScript": "Create static web pages and add interactivity with JavaScript.",
        "Flask Web Development": "Build dynamic websites using Python and Flask.",
        "Full Stack Development": "Combine React frontend with a Django backend."
    },
    # Add more categories and courses...
}

# AI-powered course recommendation function
def recommend_courses(user_interest):
    recommendations = {}
    for category, course_list in courses.items():
        for course_name, description in course_list.items():
            if user_interest.lower() in course_name.lower() or user_interest.lower() in description.lower():
                if category not in recommendations:
                    recommendations[category] = {}
                recommendations[category][course_name] = description
    return recommendations

# Function to generate trending courses using SerpAPI
def generate_trending_courses(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": "99032d11f4529779ed8b321c24eedeee0575114010305c719dd19fc019542c7d"  # Replace with your SerpAPI key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    trending_courses = []
    if 'organic_results' in results:
        for result in results['organic_results']:
            title = result['title']
            link = result['link']
            snippet = result.get('snippet', "No description available")
            trending_courses.append((title, link, snippet))
    return trending_courses

# Function to create a downloadable PDF with selected courses
def create_course_pdf(selected_courses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for category, course_desc in selected_courses.items():
        pdf.multi_cell(0, 10, f"Category: {category}")
        for course, description in course_desc.items():
            pdf.multi_cell(0, 10, f"Course: {course}")
            pdf.multi_cell(0, 10, f"Description: {description}\n")

    buffer = BytesIO()
    pdf.output(buffer, 'S')
    buffer.seek(0)
    return buffer

# Streamlit App
def main():
    st.title("AI-Powered Course Maker")

    # Collect user interests for recommendations
    user_interest = st.text_input("Enter your interests (e.g., AI, Web Development, Data Science):")

    # AI-powered recommendations based on user interests
    if st.button("Get AI-Powered Course Recommendations"):
        if user_interest:
            recommended_courses = recommend_courses(user_interest)
            if recommended_courses:
                st.subheader("Recommended Courses Based on Your Interest:")
                selected_courses = {}
                for category, course_desc in recommended_courses.items():
                    for course_name, course_desc in course_desc.items():
                        if st.checkbox(f"{course_name} ({category})"):
                            st.write(f"**Description**: {course_desc}")
                            if category not in selected_courses:
                                selected_courses[category] = {}
                            selected_courses[category][course_name] = course_desc

                # Generate PDF for download
                if selected_courses:
                    pdf_buffer = create_course_pdf(selected_courses)
                    st.download_button(
                        label="Download Selected Courses as PDF",
                        data=pdf_buffer,
                        file_name="recommended_courses.pdf",
                        mime="application/pdf"
                    )
            else:
                st.write("No courses match your interest. Try another keyword.")
        else:
            st.error("Please enter a keyword to get recommendations.")

    # Trending course recommendations using SerpAPI
    if st.button("Get Trending Courses"):
        trending_courses = generate_trending_courses("popular programming courses")
        if trending_courses:
            st.subheader("Trending Courses Based on Search Results:")
            for title, link, snippet in trending_courses:
                st.write(f"**{title}**\n{snippet}\n[Read More]({link})\n")
        else:
            st.write("No trending courses found. Please try again later.")

if __name__ == "__main__":
    main()
