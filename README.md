# 🏦 Banking Analytics & AI Assistant

### End-to-End Data Engineering + Data Analytics + AI Project

**Banking Analytics & AI Assistant** is an end-to-end project that takes raw banking data, processes and transforms it through a data pipeline, stores the cleaned data in PostgreSQL, creates business insights using Power BI, and provides an AI-powered chatbot for asking questions about the banking data.

---

## 📌 What Does This Project Do?

This project converts **raw banking data → useful information → business insights → AI answers**.

### Simple Flow

```text
Raw Banking Data
       ↓
    PySpark
       ↓
Data Cleaning & Transformation
       ↓
 Bronze → Silver → Gold
       ↓
   PostgreSQL
       ↓
 ┌───────────────┬
 ↓               ↓
Power BI       AI Assistant
Dashboard       Chatbot
```

---

## 🎯 Project Goal

The main goal is to build a complete banking data platform that can:

* Process large amounts of banking data
* Clean and transform raw data
* Store organized data in a database
* Automate the data pipeline
* Create useful business reports
* Allow users to ask questions using an AI chatbot

---

# 🛠️ Technologies Used

| Technology        | Used For                   |
| ----------------- | -------------------------- |
| 🐍 Python         | Programming                |
| 🔥 PySpark        | Data Processing            |
| 🗄️ PostgreSQL    | Database                   |
| ⚙️ Apache Airflow | Pipeline Automation        |
| 🐳 Docker         | Containerization           |
| 📊 Power BI       | Dashboard & Visualization  |
| 🤖 AI             | Natural Language Questions |
| 🖥️ Streamlit     | AI Chatbot Interface       |
| 🐙 Git & GitHub   | Version Control            |

---

# 🏗️ Project Architecture

```text
                         ┌──────────────────┐
                         │   Banking CSV    │
                         │      Data        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     PySpark      │
                         │ Data Processing  │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     BRONZE LAYER        │
                    │       Raw Data          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     SILVER LAYER        │
                    │ Cleaned & Transformed   │
                    │          Data           │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      GOLD LAYER         │
                    │ Business Ready Data     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │    PostgreSQL    │
                       │     Database     │
                       └────────┬─────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             ┌──────────────┐       ┌───────────────┐
             │   Power BI   │       │ AI Assistant  │
             │   Dashboard  │       │   Streamlit   │
             └──────────────┘       └───────────────┘
```

---

# 🔄 Data Pipeline

The project follows a simple **Bronze → Silver → Gold** architecture.

### 🥉 Bronze Layer

Stores the original/raw banking data.

**Purpose:**

* Keep the original data
* Maintain a raw copy
* Prepare data for processing

```text
Raw CSV → Bronze
```

---

### 🥈 Silver Layer

Contains cleaned and standardized data.

**Operations include:**

* Removing duplicates
* Handling missing values
* Cleaning text
* Standardizing data
* Converting data types
* Validating records

```text
Bronze → Cleaning → Silver
```

---

### 🥇 Gold Layer

Contains business-ready data used for analytics and reporting.

Examples:

```text
Customer Summary
Job Summary
Education Summary
Marital Summary
Monthly Summary
Deposit Summary
```

```text
Silver → Business Transformation → Gold
```

---

# ⚙️ Apache Airflow

Apache Airflow is used to **automate the complete data pipeline**.

### Pipeline Workflow

```text
Start
  ↓
Load Bronze
  ↓
Load Silver
  ↓
Load Gold
  ↓
Update Customer History
  ↓
Pipeline Complete
```

Airflow helps with:

* Scheduling
* Task management
* Dependencies
* Monitoring
* Automatic retries

---

# 🗄️ PostgreSQL Database

PostgreSQL acts as the main database for the processed banking data.

### Database Structure

```text
PostgreSQL
│
├── Bronze
│   └── Raw Data
│
├── Silver
│   └── Cleaned Data
│
└── Gold
    ├── Customer Data
    ├── Job Data
    ├── Education Data
    ├── Marital Data
    ├── Monthly Data
    └── Deposit Data
```

---

# 📊 Power BI Dashboard

Power BI is connected to the processed banking data to create interactive business reports.

### Dashboard Provides Insights About:

* 👥 Customers
* 💰 Customer Balance
* 📈 Average Balance
* 🎂 Customer Age
* 💼 Job Categories
* 🎓 Education
* 💍 Marital Status
* 📅 Monthly Trends
* 🏦 Deposit Subscription

### Example Business Questions

```text
How many customers are there?

What is the average balance?

Which job category has the most customers?

How many customers subscribed to deposits?

Which month has the highest subscriptions?
```

---

# 🤖 AI Banking Assistant

The project also includes an **AI-powered Banking Assistant**.

The chatbot provides a simple way for users to interact with banking data using normal English questions.

### How It Works

```text
User Question
      ↓
Streamlit Chatbot
      ↓
Question Processing
      ↓
Database Query
      ↓
PostgreSQL
      ↓
Banking Data
      ↓
AI Response
      ↓
User
```

### Example Questions

💬 **"What is the total balance?"**

💬 **"What is the average customer balance?"**

💬 **"How many customers are there?"**

💬 **"How many customers subscribed to deposits?"**

💬 **"Which job has the most customers?"**

💬 **"Show me customer information by education."**

The purpose is to make data analysis easier for users who do not want to manually write SQL queries.

---

# 🧩 Slowly Changing Dimension — SCD Type 2

The project uses **SCD Type 2** to maintain historical changes in customer information.

Instead of replacing old information, the system keeps the previous record and creates a new version.

### Example

```text
Customer Information

Old Record
Start Date → 2026-01-01
End Date   → 2026-05-01
Current    → No

        ↓ Change

New Record
Start Date → 2026-05-02
End Date   → NULL
Current    → Yes
```

This helps maintain **customer history over time**.

---

# 🐳 Docker

Docker is used to run the project services in separate containers.

### Main Services

```text
Docker
│
├── Airflow
├── PostgreSQL
└── Spark
```

Docker makes the project easier to:

* Run
* Configure
* Manage
* Deploy
* Share

---

# 📂 Project Structure

```text
Banking_Data_Engginering/
│
├── 📁 ai_application/
│   ├── agents/
│   ├── models/
│   ├── pages/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── router.py
│   ├── styles.py
│   └── utils.py
│
├── 📁 dags/
│   └── Airflow DAG files
│
├── 📁 data/
│   └── Banking Dataset
│
├── 📁 spark/
│   ├── load_bronze.py
│   ├── load_silver.py
│   ├── load_gold.py
│   └── SCD processing files
│
├── 📁 jars/
│   └── PostgreSQL JDBC Driver
│
├── 📁 postgres/
│   └── PostgreSQL configuration
│
├── 🐳 docker-compose.yml
├── 🐳 Dockerfile
├── ⚙️ airflow.env
├── 📄 requirements.txt
├── 🧪 test_connection.py
├── 🧪 test_full_suite.py
├── 🧪 test_gemini.py
└── 📖 README.md
```

---

# 🚀 How to Run the Project

## 1. Clone Repository

```bash
git clone https://github.com/Ashwini203205/Banking_Data_Engginering.git
```

```bash
cd Banking_Data_Engginering
```

---

## 2. Start Docker Services

Make sure **Docker Desktop** is running.

```bash
docker compose up -d
```

Check containers:

```bash
docker ps
```

---

## 3. Open Airflow

Open:

```text
http://localhost:8080
```

From Airflow, run and monitor the banking data pipeline.

---

## 4. Run AI Assistant

Go to:

```bash
cd ai_application
```

Install requirements:

```bash
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py
```

The AI Banking Assistant will open in your browser.

---

# 🔗 Complete Project Flow

The entire project can be understood in one line:

```text
CSV
 ↓
PySpark
 ↓
Bronze
 ↓
Silver
 ↓
Gold
 ↓
PostgreSQL
 ↓
 ├── Power BI → Business Insights
 │
 └── AI Assistant → Natural Language Answers
```

**Airflow** controls and automates the pipeline.

**Docker** provides the environment for running the services.

---

# ⭐ Key Features

* ✅ End-to-End Data Engineering Pipeline
* ✅ PySpark Data Processing
* ✅ Bronze-Silver-Gold Architecture
* ✅ Data Cleaning & Transformation
* ✅ PostgreSQL Data Warehouse
* ✅ Apache Airflow Automation
* ✅ SCD Type 2 Historical Tracking
* ✅ Dockerized Environment
* ✅ Power BI Dashboard
* ✅ AI-Powered Banking Assistant
* ✅ Streamlit Chatbot Interface
* ✅ Natural Language Data Queries

---

# 📚 What I Learned From This Project

This project helped me understand how different technologies work together in a real-world data project.

### Data Engineering

* ETL pipelines
* Data ingestion
* Data cleaning
* Data transformation
* Data warehousing
* Data modeling

### Big Data

* PySpark
* Distributed data processing

### Database

* PostgreSQL
* SQL
* Database schemas

### Workflow

* Apache Airflow
* DAGs
* Task dependencies

### Visualization

* Power BI
* Business KPIs
* Data analysis

### AI Application

* AI assistant development
* Natural language questions
* Database integration
* Streamlit

### DevOps

* Docker
* Docker Compose
* Git
* GitHub

---

# 🔮 Future Improvements

Some possible future improvements are:

* 🔹 Real-time data processing using Kafka
* 🔹 Cloud deployment
* 🔹 AWS / Azure integration
* 🔹 Databricks integration
* 🔹 Advanced fraud detection
* 🔹 Predictive analytics
* 🔹 More advanced AI features
* 🔹 CI/CD automation

---

# 👩‍💻 Author

## Ashwini Giri

**Information Technology | Data Engineering | Data Science | AI**

Interested in building practical solutions using:

**Python • SQL • PySpark • Airflow • PostgreSQL • Docker • Power BI • AI**

---

# ⭐ Project Repository

**GitHub:**
https://github.com/Ashwini203205/Banking_Data_Engginering

If you find this project useful, consider giving it a ⭐ **Star**.

---

## 💡 Project in One Sentence

> **A complete banking data platform that transforms raw customer data into business insights through an automated Data Engineering pipeline, Power BI dashboard, and AI-powered Banking Assistant.**

### 🚀 Raw Data → Data Pipeline → Database → Dashboard + AI Assistant
