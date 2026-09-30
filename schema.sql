CREATE DATABASE IF NOT EXISTS talentmatch_db;
USE talentmatch_db;

CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    company VARCHAR(150) NOT NULL,
    location VARCHAR(100) NOT NULL,
    required_skills TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    internship_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    skills TEXT NOT NULL,
    resume_summary TEXT NOT NULL,
    match_score FLOAT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- Seed baseline internship roles
INSERT INTO internships (title, company, location, required_skills, description) VALUES
('AI / Machine Learning Intern', 'Apex Labs', 'Remote', 'Python, PyTorch, TensorFlow, Scikit-Learn, NLP, Data Pipelines', 'Assist in training NLP models, data wrangling, and pipeline deployment for generative search products.'),
('Full-Stack Web Developer Intern', 'CloudScale Inc', 'Bengaluru, India', 'Flask, Python, React, MySQL, REST APIs, Docker', 'Design API endpoints, connect relational databases, and build scalable front-end components.'),
('Data Analyst Intern', 'Metrics Dynamics', 'Hyderabad, India', 'SQL, Python, Pandas, PowerBI, Data Visualization, Excel', 'Clean business data, run exploratory query analysis, and produce KPI summaries for executive reporting.'),
('DevOps & Cloud Intern', 'Nova Infra', 'Remote', 'Linux, Docker, Kubernetes, AWS, CI/CD, Python Scripting', 'Maintain continuous integration systems and containerize microservice apps on cloud environments.');