# 📝 Streamlit To-Do List Application

A simple yet powerful **To-Do List application** built with Streamlit, using SQLModel for local data persistence (SQLite), and integrating Google's Gemini API for AI-powered translation.

---

## ✨ Features

- **Add To-Do Items:** Add tasks with a title, optional description, priority, and due date.
- **Mark as Completed:** Mark tasks as done to move them to the "Completed Tasks" section.
- **Delete To-Do Items:** Remove tasks when no longer needed.
- **Priority Levels:** Organize tasks with **Low**, **Medium**, and **High** priority.
- **Due Dates:** Set specific due dates for tasks.
- **AI-Powered Translation:** Translate task titles and descriptions into multiple languages using the Google Gemini API.
- **Persistent Storage:** All tasks are saved locally using SQLite/SQLModel, so they persist even after the app is closed.

---

## 🚀 Getting Started

Follow these steps to set up and run the application locally.

### Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)

### Setup Instructions

1. **Clone the Repository**
    ```
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    *Replace `your-username/your-repo-name` with your actual repository information.*

2. **Create a Virtual Environment (Recommended)**
    ```
    python -m venv venv
    ```

3. **Activate the Virtual Environment**

    - **Windows**
      ```
      .\venv\Scripts\activate
      ```

    - **macOS/Linux**
      ```
      source venv/bin/activate
      ```

4. **Install Dependencies**

    Create a file named `requirements.txt` in your project root with:
    ```
    streamlit
    google-generativeai
    python-dotenv
    sqlmodel
    pydantic
    sqlalchemy
    ```

    Then install:
    ```
    pip install -r requirements.txt
    ```

5. **Set Up Google Gemini API Key**

    - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Create a `.env` file in your project root (where `app.py` is).
    - Add:
      ```
      GOOGLE_API_KEY="YOUR_API_KEY_HERE"
      ```
      *Replace `YOUR_API_KEY_HERE` with your real key.*
    - **Note:** `.env` is **ignored by git** for your security by default.

---

## ▶ Running the Application

After setup, launch the app with:
`streamlit run app.py`

This opens the To-Do List application in your browser.

---

## 💡 Usage

- **Add New To-Do:** Use "Add New To-Do" at the top of the page to enter task details and click "Add To-Do".
- **Manage Tasks:**
    - In **Pending Tasks**, you can "Mark Completed" or "Delete".
    - **Completed Tasks** provide a "Delete" option.
- **Translate Tasks:** In the sidebar "Translation Settings", select a target language and click "Translate to [Selected Language]" next to any pending task to view its translation.

---

## 📂 Project Structure
your-repo-name/
├── app.py # Main Streamlit application file
├── .streamlit
    └──config.toml
├── .env # Environment variables (e.g., API keys) - IGNORED BY GIT
├── sql_app.db # SQLite database file - IGNORED BY GIT
├── requirements.txt # Python dependencies
├── .gitignore # Specifies files/directories ignored by Git
└── README.md # This file


---

## ☁️ Deployment (Streamlit Cloud)

- Push code to a **public GitHub repository**.
- Go to [Streamlit Cloud](https://streamlit.io/cloud), connect your repo, and select `app.py` as your app file.
- Set your `GOOGLE_API_KEY` under app settings (Advanced settings → Secrets).

---

## 🤝 Contributing

Contributions are welcome!  
Fork the repository, create a branch for your changes, and submit a pull request.


