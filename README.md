# Customer Engagement & Product Utilization Analytics for Retention Strategy

## Project Overview
Banks increasingly recognize that customer engagement and product utilization play a critical role in long-term retention. Customers may appear financially strong based on balance or salary but may still churn due to weak engagement with banking services.

This project analyzes customer engagement patterns, product adoption behavior, and financial commitment indicators to understand how they influence customer churn.

The project includes Exploratory Data Analysis (EDA), retention KPIs, and an interactive Streamlit dashboard for real-time analytics.

---

## Project Objectives

### Primary Objectives
• Evaluate the relationship between customer engagement and churn  
• Measure the retention impact of product count and product mix  
• Identify high-value disengaged customers  

### Secondary Objectives
• Support engagement-driven retention strategies  
• Improve product bundling decisions  
• Reduce silent churn among premium customers  

---

## Dataset Description

The dataset contains customer-level banking information including engagement indicators, product usage, and churn labels.

CustomerId – Unique customer identifier  
CreditScore – Customer creditworthiness  
Geography – Customer location (France, Spain, Germany)  
Gender – Male / Female  
Age – Customer age  
Tenure – Years with the bank  
Balance – Customer account balance  
NumOfProducts – Number of banking products used  
HasCrCard – Credit card ownership  
IsActiveMember – Activity indicator  
EstimatedSalary – Estimated annual salary  
Exited – Churn indicator (target variable)

---

## Key Performance Indicators (KPIs)

Engagement Retention Ratio  
Comparison of churn rates between active and inactive customers.

Product Depth Index  
Analysis of how the number of products used affects customer loyalty.

High-Balance Disengagement Rate  
Detection of premium customers who are financially valuable but behaviorally disengaged.

Credit Card Stickiness Score  
Impact of credit card ownership on customer retention.

Relationship Strength Index  
Composite score combining engagement and product usage indicators.

---

## Analytical Methodology

The project follows a structured analytics workflow:

1. Data Ingestion and Validation  
2. Exploratory Data Analysis (EDA)  
3. Engagement Classification  
4. Product Utilization Analysis  
5. Financial Commitment vs Engagement Analysis  
6. Retention Strength Assessment  
7. KPI Construction  
8. Dashboard Development  

---

## Streamlit Dashboard

An interactive Streamlit dashboard was developed to provide real-time insights into customer engagement and retention behavior.

### Core Modules

• Engagement vs Churn Overview  
• Product Utilization Impact Analysis  
• High-Value Disengaged Customer Detector  
• Retention Strength Scoring Panel  

### User Capabilities

The dashboard allows dynamic analysis using:

• Engagement filters  
• Product count sliders  
• Balance thresholds  
• Salary thresholds  

---

## Technologies Used

Python  
Pandas  
Plotly  
Streamlit  
Data Visualization  
Exploratory Data Analysis  

---

## How to Run the Project

Install required libraries:

pip install streamlit pandas plotly

Run the dashboard:

streamlit run app.py

---

## Live Dashboard

https://bank-retention-dashboard-vnxumdgpvj2zq6frqoecbx.streamlit.app/

---

