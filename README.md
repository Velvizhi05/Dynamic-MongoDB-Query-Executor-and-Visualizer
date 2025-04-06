                                       Dynamic-MongoDB-Query-Executor-and-Visualizer
This project is an intelligent platform that allows users to dynamically interact with a MongoDB database using natural language queries, execute them in real-time, and visualize the results in an intuitive format. The system is enhanced by powerful AI models — OpenAI’s GPT-4o-Mini and cohere.


# 🎯 MongoDB Query and Plot Generator

A smart web-based tool that transforms **natural language queries** into **MongoDB commands** and visualizes the data using **interactive plots**. Designed to assist both technical and non-technical users in exploring databases without writing code manually.

---

## 📌 Table of Contents
1. [📖 Introduction](#-introduction)
2. [✨ Features](#-features)
3. [🧰 Technologies Used](#-technologies-used)
4. [🏗️ System Architecture](#-system-architecture)
5. [⚙️ Installation](#-installation)
6. [🔁 Application Workflow](#-application-workflow)
7. [🧩 Challenges and Solutions](#-challenges-and-solutions)
8. [🚀 Future Work](#-future-work)
9. [📌 Conclusion](#-conclusion)

---

## 📖 Introduction

**MongoDB Query and Plot Generator** is a web application that:
- Accepts user-friendly **natural language input**.
- Converts it into a **MongoDB query** using **Cohere AI**.
- **Visualizes** the output using **Plotly** in various plot formats.

Currently, the application supports querying across collections such as `singer` and `song`. The data merging and visualization components are under active development.

---

## ✨ Features

- 🔍 **Natural Language Querying**  
  Convert plain English queries into executable MongoDB syntax using Cohere.

- 📊 **Plot Generation**  
  Choose from bar charts, histograms, scatter plots, and more to visualize data.

- 🧩 **Multi-Collection Handling** *(In Progress)*  
  Supports querying from multiple MongoDB collections like `singer` and `song`.

- 🧼 **Data Formatting**  
  Utilizes Pandas for DataFrame manipulation and clean plot output.

---

## 🧰 Technologies Used

| Component     | Tool/Library                 |
|---------------|------------------------------|
| Backend       | Flask                        |
| Database      | MongoDB                      |
| AI Model      | Cohere API                   |
| Plotting      | Plotly                       |
| Data Handling | Pandas                       |
| Frontend      | HTML, CSS, Bootstrap         |

---

## 🏗️ System Architecture

### 🔹 Frontend
- Accepts user input and plot type selection.
- Displays generated plots and table output.

### 🔹 Backend (Flask)
- Sends the query to Cohere for conversion.
- Executes MongoDB query and processes data via Pandas.
- Returns interactive plots from Plotly.

### 🔹 Database
- MongoDB collections: `singer`, `song`.

### 🔹 AI Integration
- Cohere API converts natural language → MongoDB syntax.

### 📈 Data Flow
- User Input → Cohere API → MongoDB → Pandas → Plotly → Frontend

## ⚙️ Installation

### 🔑 Prerequisites

- Python 3.x  
- Flask  
- MongoDB (local or Atlas)  
- Valid **Cohere API key**

 🔁 Application Workflow:
 
📝 User Input: Enter a question like "Show all singers older than 30."
⚙️ Query Generation: Flask → Cohere API → MongoDB syntax
🗃️ Database Access: Retrieve data from collections
🧮 Data Processing: Pandas → DataFrame
📊 Plotting: Plotly visualizes selected chart
👁️ Output Displayed: Interactive chart or data table in frontend

🧩 Challenges and Solutions:

1️⃣ Combining Data from Multiple Collections
      Challenge: Properly merging singer and song fields.
      Solution: Working on aggregation queries or merging externally using Pandas.
2️⃣ Plot Type Matching
      Challenge: Adapting dynamic plot types like 3D plots.
      Solution: UI enhanced with better plot selectors and validations.
3️⃣ Multi-Collection Query Generation
      Challenge: Incomplete or irrelevant results due to AI confusion.
      Solution: Improving natural language context understanding and merging logic.

🚀 Future Work:

✅ Full multi-collection query support and visualizations
🧠 Smarter query parsing for complex user inputs
🎨 Advanced plot customization (color, labels, size, etc.)
🔐 User authentication and history tracking

📌 Conclusion:
MongoDB Query and Plot Generator bridges the gap between user-friendly language and complex database interactions. While the core features work well, multi-collection merging and smarter plot generation are actively being enhanced. Once complete, this project will become a robust and intuitive platform for data exploration.

Built with ❤️ by Velvizhi
Contact - 7418276791
Email - velvizhi1518@gmail.com 


