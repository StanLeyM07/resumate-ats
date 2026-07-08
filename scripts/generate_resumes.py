import os
from fpdf import FPDF
from docx import Document

os.makedirs('test_data/resumes', exist_ok=True)

# Helper for realistic template
def build_resume(name, email, profile, education, skills, experience, projects, certs):
    return f"""{name}
{email} | LinkedIn: linkedin.com/in/{name.split()[0].lower()} | GitHub: github.com/{name.split()[0].lower()}

Profile
{profile}

Education
{education}

Skills
{skills}

Experience
{experience}

Projects
{projects}

Certifications
{certs}
"""

resumes_data = [
    {
        "name": "1_Alice_Perfect_Match.pdf",
        "content": build_resume(
            "Alice Wang", "alice.wang@email.com",
            "Computer Engineering graduate specialising in AI and backend systems. Experienced in developing ML models and serving them via high-performance APIs.",
            "Massachusetts Institute of Technology\nBachelor of Science in Computer Science\nGraduated: May 2024",
            "– AI & Machine Learning: PyTorch, NLP, Pandas, Scikit-learn, Model Fine-tuning\n– Backend & API: Python, FastAPI, SQL, Docker\n– Tools: Git, GitHub, Linux",
            "AI Intern | TechNova | Jun 2023 – Present\n– Fine-tuned LLMs for sentiment analysis using PyTorch, achieving 94% accuracy.\n– Built a Python backend with FastAPI and SQL to serve the model to production users.\n– Automated data collection pipelines.",
            "Conversational AI Agent (Final Year Project) | Jan 2024 – May 2024\n– Designed and implemented an AI chatbot from scratch using Llama 3.\n– Deployed the model on AWS using Docker containers.",
            "AWS Certified Developer Associate\nDeepLearning.AI Natural Language Processing Specialization"
        )
    },
    {
        "name": "2_Bob_Heavy_Dev_No_AI.pdf",
        "content": build_resume(
            "Bob Smith", "bob.smith@email.com",
            "Experienced Backend Software Engineer with a focus on enterprise Java applications and high-availability microservices. Passionate about scalable architecture.",
            "State University\nBachelor of Science in Software Engineering\nGraduated: May 2020",
            "– Backend Development: Java, Spring Boot, Hibernate\n– Databases: MySQL, PostgreSQL, Oracle\n– DevOps: Jenkins, Kubernetes, AWS\n– Programming: Java, C#, Bash",
            "Backend Developer | EnterpriseCorp | Jul 2020 – Present\n– Maintained a monolithic Java application serving 10,000+ daily active users.\n– Wrote complex SQL queries to generate financial reports.\n– Migrated legacy code to Spring Boot microservices.",
            "E-Commerce Platform Backend\n– Designed the REST API for a high-traffic e-commerce platform.\n– Implemented OAuth2 authentication and payment gateway integration.",
            "Oracle Certified Professional, Java SE 11 Developer"
        )
    },
    {
        "name": "3_Charlie_High_Potential.docx",
        "content": build_resume(
            "Charlie Davis", "charlie.d@email.com",
            "Self-taught developer and AI enthusiast with a track record of winning hackathons and contributing to open-source ML projects. Fast learner driven by curiosity.",
            "Self-Taught Bootcamp | Software Engineering & AI\nOnline Resources: Coursera, Fast.ai, Udemy",
            "– AI & Machine Learning: Python, TensorFlow, HuggingFace, Transformers\n– Software Engineering: Docker, Node.js, FastAPI\n– Version Control: Git, GitHub Actions",
            "Freelance AI Developer | Upwork | Jan 2023 – Present\n– Built custom open-source AI agents for various clients, including a document parser that received 1k+ GitHub stars.\n– Automated data extraction pipelines using HuggingFace models.\n– Participated in and won 3 major AI Hackathons.",
            "Open-Source Document Extractor\n– Utilized Python and HuggingFace Transformers to extract entities from unstructured text.\n– Containerized the application using Docker for easy client deployment.",
            "Fast.ai Deep Learning for Coders"
        )
    },
    {
        "name": "4_Diana_Data_Analyst.docx",
        "content": build_resume(
            "Diana Prince", "diana.p@email.com",
            "Detail-oriented Data Analyst with 3 years of experience in data visualization, SQL scripting, and business intelligence. Skilled at turning raw data into actionable insights.",
            "University of Data Science\nMaster of Science in Data Analytics\nGraduated: May 2021",
            "– Data Analysis: SQL, Tableau, PowerBI, Excel\n– Scripting: Python (Pandas, scripting, automation)\n– Business Intelligence: KPI Tracking, Reporting",
            "Data Analyst | BigData Inc | Aug 2021 – Present\n– Built interactive Tableau dashboards for the executive team to monitor daily sales.\n– Wrote SQL scripts to clean and transform daily data pipelines.\n– Developed minor Python scripts for automated Excel report generation.",
            "Sales Forecasting Dashboard\n– Aggregated 5 years of sales data using complex SQL joins.\n– Visualized trends in PowerBI leading to a 10% increase in Q3 efficiency.",
            "Tableau Desktop Specialist"
        )
    },
    {
        "name": "5_Eve_Almost_Matching.pdf",
        "content": build_resume(
            "Eve Jackson", "eve.j@email.com",
            "Junior Machine Learning Engineer with experience in traditional ML algorithms and web deployment. Eager to expand into Deep Learning and NLP.",
            "Tech Institute\nBachelor of Science in Computer Science\nGraduated: Dec 2022",
            "– Traditional ML: Scikit-Learn, Random Forests, XGBoost, PCA\n– Programming: Python, R, SQL\n– Web Frameworks: Flask, Django",
            "Junior ML Engineer | StartupX | Feb 2023 – Present\n– Trained and deployed predictive models (Random Forests, Gradient Boosting) using Scikit-Learn.\n– Built a RESTful Flask API to serve model inference to the frontend team.\n– Managed PostgreSQL databases for user data storage.",
            "Customer Churn Predictor\n– Developed a machine learning pipeline to predict customer churn with 85% accuracy.\n– Created an interactive web app using Flask and Bootstrap.",
            "Coursera Machine Learning by Andrew Ng"
        )
    },
    {
        "name": "6_Frank_Too_Senior.pdf",
        "content": build_resume(
            "Frank Ocean", "frank.ocean@email.com",
            "Principal AI Architect with over a decade of experience leading large-scale AI research and deployment. Expert in distributed systems and custom neural network architectures.",
            "Stanford University\nPh.D. in Computer Science (Focus on Distributed Machine Learning)\nGraduated: May 2012",
            "– AI Architecture: Everything AI, Transformers, Custom CUDA Kernels\n– Programming: Python, C++, Rust, Go\n– Infrastructure: Distributed Systems, Kubernetes, AWS SageMaker, Slurm",
            "Principal AI Architect | MegaCorp | Jan 2018 – Present\n– Lead a team of 40 AI researchers and engineers.\n– Designed custom neural network architectures trained on clusters of 1000+ GPUs.\n– Reduced inference latency by 40% through C++ custom kernel optimization.\nSalary Expectation: $300k+",
            "Global Scale LLM Training\n– Architected the training pipeline for a 100B+ parameter model.\n– Implemented model parallelism and pipeline parallelism strategies.",
            "AWS Certified Solutions Architect - Professional"
        )
    },
    {
        "name": "7_Grace_Academic.txt",
        "content": build_resume(
            "Grace Hopper", "grace.h@email.com",
            "Recent Machine Learning postgraduate with a strong theoretical foundation in statistics, calculus, and deep learning architectures. Passionate about academic research.",
            "University of Oxford\nMaster of Science in Machine Learning\nGraduated: Aug 2024",
            "– AI & Math: PyTorch, Math, Statistics, Linear Algebra, Calculus\n– Programming: Python, MATLAB, R\n– Research: Academic Writing, LaTeX",
            "Graduate Researcher | AI Lab | Sep 2022 – Aug 2024\n– Conducted extensive theoretical research on Transformer attention mechanisms.\n– Co-authored a paper published at a major ML conference.\n– Focused purely on academic algorithms; no production or deployment experience (e.g., Docker, SQL, APIs).",
            "Attention Mechanism Optimization (Thesis)\n– Analysed the mathematical properties of sparse attention in large language models.\n– Developed proof-of-concept PyTorch scripts for benchmarking.",
            "None"
        )
    },
    {
        "name": "8_Harry_Wrong_Field.txt",
        "content": build_resume(
            "Harry Potter", "h.potter@email.com",
            "Dedicated and communicative professional with 5 years of experience in client relations and customer support. Seeking to transition into a new administrative role.",
            "Hogwarts University\nBachelor of Arts in History\nGraduated: May 2019",
            "– Skills: Customer Service, Communication, Conflict Resolution\n– Tools: Microsoft Word, Excel, Zendesk, Salesforce",
            "Customer Support Lead | TechMagic | Jun 2019 – Present\n– Managed a team of 5 support agents.\n– Answered 50+ high-priority client tickets daily.\n– Maintained a 99% customer satisfaction score across 3 years.",
            "Support Workflow Overhaul\n– Reorganized the Zendesk tagging system to improve ticket resolution time by 15%.",
            "Zendesk Customer Service Professional"
        )
    },
    {
        "name": "9_Ivy_Good_Match.pdf",
        "content": build_resume(
            "Ivy Chen", "ivy.c@email.com",
            "Software Engineer with a strong background in Natural Language Processing and high-performance backend systems. Proven ability to build scalable data infrastructure.",
            "University of California, Berkeley\nBachelor of Science in Computer Science\nGraduated: Dec 2021",
            "– AI & ML: Python, NLP, PyTorch, Spacy, Transformers\n– Backend Engineering: FastAPI, SQL, PostgreSQL, Docker\n– Cloud: AWS (EC2, S3), CI/CD",
            "Software Engineer II | NLP-Tech | Feb 2022 – Present\n– Developed named entity recognition models using PyTorch and HuggingFace.\n– Built highly scalable FastAPI services to expose NLP models to external clients.\n– Managed SQL database schemas and optimized queries for large training datasets.",
            "Real-time Document Analyzer\n– Architected a microservice in FastAPI that processes 100+ documents per minute.\n– Integrated PyTorch models directly into the web pipeline.",
            "Certified Kubernetes Administrator (CKA)"
        )
    },
    {
        "name": "10_Jack_Hardware_Eng.docx",
        "content": build_resume(
            "Jack Sparrow", "jack.s@email.com",
            "Embedded Systems Engineer with expertise in hardware-software co-design, real-time operating systems, and microcontroller programming. No machine learning experience.",
            "Institute of Technology\nBachelor of Science in Electrical Engineering\nGraduated: May 2022",
            "– Embedded Systems: C, C++, Verilog, RTOS, STM32, Arduino\n– Hardware: PCB Design, Soldering, Oscilloscopes\n– Scripting: Python (for hardware testing)",
            "Embedded Systems Engineer | BlackPearl Robotics | Jun 2022 – Present\n– Programmed microcontrollers in C for autonomous drone navigation.\n– Designed 4-layer PCBs for motor control circuits.\n– Used Python purely for hardware testing and serial communication scripts.",
            "Drone Flight Controller\n– Implemented a PID controller in C++ for stable flight dynamics.\n– Optimized sensor fusion (accelerometer/gyroscope) using Kalman filters.",
            "Altium Designer Certified"
        )
    }
]

for r in resumes_data:
    filepath = os.path.join('test_data/resumes', r['name'])
    
    # We must replace unicode dash characters for FPDF which only supports latin-1 natively easily
    safe_content = r['content'].replace('–', '-')

    if r['name'].endswith('.pdf'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(0, 5, safe_content, new_x="LMARGIN", new_y="NEXT")
        pdf.output(filepath)
    elif r['name'].endswith('.docx'):
        doc = Document()
        doc.add_paragraph(r['content'])
        doc.save(filepath)
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(r['content'])

print("Generated 10 REALISTIC test resumes based on the main.pdf format!")
