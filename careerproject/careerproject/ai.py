try:
    import ollama
except ImportError:
    ollama = None

# ============================================
# CAREER ASSESSMENT QUESTIONS
# ============================================

CAREER_QUESTIONS = [

    "What course are you studying or have you completed?",

    "Which subjects do you enjoy the most?",

    "What are your hobbies and interests?",

    "What technical skills do you have? (Programming, software, tools, etc.)",

    "Have you completed any projects? Briefly describe one.",

    "What do you think are your biggest strengths?",

    "Which skills would you like to improve?",

    "Do you prefer working alone or in a team? Why?",

    "Have you ever led a team or organized an event? Tell us about it.",

    "What type of work do you enjoy the most? (Coding, Designing, Teaching, Business, etc.)",

    "Which industries interest you? (IT, Healthcare, Finance, Education, etc.)",

    "What kind of work environment do you prefer? (Office, Remote, Hybrid)",

    "Do you have any certifications or extra courses?",

    "Do you already have a career in mind? If yes, what is it?",
    
    "Is there anything else you would like to share that could help us understand you better?"

]

# ============================================
# CAREER GUIDANCE AI FUNCTIONS
# ============================================

def generate_report(messages):

    if ollama is None:
        return "AI report generation not available. Ollama is not installed."

    conversation = ""

    student_answers = [
        msg for msg in messages
        if msg.sender == "student"
    ]

    for i, answer in enumerate(student_answers):

        if i < len(CAREER_QUESTIONS):

            conversation += f"""Question {i+1}:
    {CAREER_QUESTIONS[i]}

    Answer:
    {answer.message}

----------------------------------------

"""

    prompt = f"""
You are Career-Assistant AI, an intelligent career counselor.

Your job is to analyze the student's complete career assessment and generate a professional career report.

Important Rules:

1. Use ONLY the information given by the student.
2. Never invent skills, projects, or achievements.
3. Recommend exactly THREE different careers.
4. The careers must NOT be very similar.
5. Explain why each career suits the student.
6. Do not repeat the same explanation.
7. Keep the report professional and personalized.
8. Give practical learning advice.
9. If the student lacks skills, clearly mention them.
10. Write in simple English.
11. Do not repeat the same career, skill, or explanation.
12. If the student has web development skills, consider Python Developer, Backend Developer, or Full Stack Developer.
13. If the student has strong interest in AI, statistics, data analysis, visualization, or machine learning as a career goal, consider Data Analyst or Machine Learning Engineer.14. If the student lacks required skills, clearly state that they need to learn them.
15. Recommend careers based on the student's strongest skills and interests, not only one project.
16. The student's stated career goal has the highest priority.
17. If the student mentions cybersecurity, ethical hacking, networking, Linux, Kali Linux, Nmap, or security tools, prioritize cybersecurity careers.
18. Never recommend Data Analyst or Machine Learning Engineer as the first career only because of one machine learning project.
19. Database knowledge, SQL, or a machine learning project alone does not mean the student wants a data career.
20. The first recommended career must match the student's career interest whenever possible.
21. Do not show your reasoning, scoring, or these instructions in the final answer.

-------------------------------------
Important Career Decision Rules:

1. The student's stated career interest is the strongest factor in career recommendation.

2. If the student mentions cybersecurity, ethical hacking, networking, Linux, Kali Linux, Nmap, security tools, or security analysis:
   - The first recommended career MUST be cybersecurity-related.

3. Never recommend:
   - Data Analyst
   - Machine Learning Engineer

   as the first career unless the student explicitly says they want a career in:
   - Data analysis
   - Statistics
   - Artificial Intelligence
   - Machine Learning
   - Data science

4. A machine learning project, stock prediction project, Python skill, or SQL skill alone does not indicate interest in data careers.

5. Database knowledge is NOT the same as Data Analyst interest.

6. Career recommendations must follow this priority:

   1. Career goal and interest
   2. Skills
   3. Projects
   4. Future learning potential
--------------------------------------------------
IMPORTANT:

Before writing the report, start with exactly this format:
Do not use Markdown formatting.
Do not use **, ##, or bullet formatting for career titles.
Use plain text only.

Career: <Career Name>
Confidence: <0-100>

Career: <Career Name>
Confidence: <0-100>

Career: <Career Name>
Confidence: <0-100>

After these three careers, continue with the complete report.

--------------------------------------------------


# Career Summary

Write 5–8 sentences summarizing:

• Education
• Interests
• Strengths
• Personality
• Technical abilities
• Career potential

--------------------------------------------------

# Recommended Certifications

Recommend 3-5 certifications or learning platforms.

--------------------------------------------------

# Learning Roadmap

Month 1

Topics to learn

Practice

Mini Project

Month 2

Topics

Project

Month 3

Advanced Topics

Portfolio

Interview Preparation

--------------------------------------------------

# Final Career Advice

Write an encouraging conclusion in about 8–10 lines.

--------------------------------------------------

Student Assessment:

{conversation}
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# ============================================
# CAREER ROADMAP AI FUNCTIONS
# ============================================

def generate_roadmap(student, career):

    if ollama is None:
        return "AI roadmap generation not available. Ollama is not installed."

    prompt = f"""
You are an expert Career Mentor.

Create a personalized career roadmap for this student.

Student Details

Education:
{student.qualification}

Skills:
{student.skills}

Current Career Goal:
{career.career_name}

Instructions:

1. Create a realistic roadmap.
2. Use simple English.
3. Divide the roadmap into 5 phases.
4. Mention the duration for each phase.
5. Include topics to learn.
6. Include one or two mini projects in each phase.
7. Recommend certifications.
8. Give interview preparation tips.
9. End with a final goal.

Return the response exactly in this format.

==================================================

CAREER

OVERVIEW

ESTIMATED DURATION

----------------------------------------

PHASE 1

Title:

Duration:

Topics:
-

Projects:
-

----------------------------------------

PHASE 2

Title:

Duration:

Topics:
-

Projects:
-

----------------------------------------

PHASE 3

Title:

Duration:

Topics:
-

Projects:
-

----------------------------------------

PHASE 4

Title:

Duration:

Topics:
-

Projects:
-

----------------------------------------

PHASE 5

Title:

Duration:

Topics:
-

Projects:
-

----------------------------------------

CERTIFICATIONS

-

----------------------------------------

INTERVIEW PREPARATION

-

----------------------------------------

FINAL GOAL

==================================================

Return only the roadmap.
Do not return JSON.
Do not use markdown.
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# ============================================
# SKILL GAP AI FUNCTIONS
# ============================================

def generate_skill_gap(student, career):

    if ollama is None:
        return "AI skill gap analysis not available. Ollama is not installed."

    prompt = f"""
You are an experienced Career Mentor.

Current Skills:
{student.skills}

Career Goal:
{career.career_name}

Analyze the student's current skills and compare them with the skills required for the selected career.

Rules:
- Current Skills are the skills the student already has.
- Do NOT list any Current Skill again under Missing Skills.
- Compare the student's Current Skills with the skills required for the selected career.
- List ONLY the missing skills needed to become a successful {career.career_name}.
- If the student already has a required skill, do not include it in Missing Skills.
- Suggest the learning priority based only on the missing skills.
Return ONLY plain text.

=====================================

CAREER GOAL

{career.career_name}

----------------------------------

CURRENT SKILLS

✔ Skill
✔ Skill
✔ Skill

----------------------------------

MISSING SKILLS

✖ Skill
✖ Skill
✖ Skill
✖ Skill
✖ Skill
✖ Skill

----------------------------------

LEARNING PRIORITY

Provide exactly 5 numbered learning priorities.


1.
2.
3.
4.
5.

----------------------------------

RECOMMENDATION

Explain in simple English what the student should learn first and why.
=====================================
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response["message"]["content"]

# ============================================
# MOCK INTERVIEW AI FUNCTIONS
# ============================================

def generate_questions(career, difficulty, total_questions,previous_questions=None):

    if ollama is None:
        # Return fallback questions if ollama is not available
        fallback_questions = [
            "Tell me about yourself?",
            "Why are you interested in this role?",
            "Describe one of your projects.",
            "What are your strengths?",
            "What are your weaknesses?",
            "Tell me about a challenge you faced.",
            "How do you approach problem-solving?",
            "Where do you see yourself in five years?",
            "Why should we hire you?",
            "Do you have any questions for us?"
        ]
        return fallback_questions[:total_questions]
    if previous_questions is None:
        previous_questions = []

    previous_questions_text = "\n".join(previous_questions)

    prompt = f"""
You are a professional technical interviewer.
The candidate is applying for the role of:
{career}

Interview difficulty: {difficulty}
Generate exactly {total_questions} interview questions.


Requirements:
1. The FIRST question MUST be exactly:
Tell me about yourself?.

2. Every remaining question MUST be specifically related to the career "{career}":
- HR questions
- Technical questions
- Project questions
- Problem-solving questions

Previous interview questions:
{previous_questions_text}
Do NOT repeat previous questions except "Tell me about yourself?".

Generate new interview questions only.
Do NOT repeat any of the above questions.
Generate new interview questions only.
Rules:
3. Output ONLY interview questions.
4. Every line must end with a question mark (?).
5. Do NOT provide answers.
6. Do NOT introduce yourself.
7. Do NOT write explanations.
8. Do NOT use JSON.
9. Do NOT use numbering.
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response["message"]["content"]

    questions = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove numbering if present
        if line[0].isdigit():
            line = line.split(".", 1)[-1].strip()

        # Keep only questions
        if line.endswith("?"):
            questions.append(line)

    if len(questions) < total_questions:

        fallback_questions = [
            "Why are you interested in this role?",
            "Describe one of your projects.",
            "What are your strengths?",
            "What are your weaknesses?",
            "Tell me about a challenge you faced.",
            "How do you approach problem-solving?",
            "Where do you see yourself in five years?",
            "Why should we hire you?",
            "Do you have any questions for us?"
        ]

        for q in fallback_questions:
            if len(questions) >= total_questions:
                break

            if q not in questions:
                questions.append(q)
    return questions[:total_questions]


def evaluate_interview(career, questions):

    if ollama is None:
        return "AI interview evaluation not available. Ollama is not installed."

    prompt = f"""
You are an experienced technical interviewer.

Career:
{career}

Below are the interview questions and the student's answers.

"""

    for q in questions:

        prompt += f"""

Question:
{q.question}

Answer:
{q.answer}

"""

    prompt += """

Evaluate the interview.

Provide:

Overall Score: __/100

Technical Score: __/100

Communication Score: __/100

Confidence Score: __/100

Strengths:
- item
- item

Weaknesses:
- item
- item

Suggestions:
- item
- item

Question 1 Feedback:
...

Question 2 Feedback:
...
Return the interview evaluation as plain text only.
Do not use Markdown formatting.
Do not use **, *, #, -, or backticks.
- Do not use JSON.
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
