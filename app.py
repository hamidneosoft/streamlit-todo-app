import streamlit as st
from typing import List, Dict, Optional, ClassVar
from datetime import date
import google.generativeai as genai
import os
from dotenv import load_dotenv

from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from sqlalchemy import exc

# Load environment variables (for GOOGLE_API_KEY)
load_dotenv()

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./sql_app.db"

# --- Define SQLModel Classes ---
# These class definitions must remain at the top level for SQLModel to properly register them with MetaData
class TodoItem(SQLModel, table=True):
    __tablename__ = "todoitem"


    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = Field(default=None, max_length=50)
    due_date: Optional[date] = Field(default=None)
    __table_args__ = {"extend_existing": True}
    # Annotate sa_table_kwargs as ClassVar
    #sa_table_kwargs: ClassVar[Dict] = {"extend_existing": True}

    class Config:
        arbitrary_types_allowed = True


class TodoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

# --- Gemini API Configuration ---
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("GOOGLE_API_KEY not found in environment variables. Please set it as a Streamlit Secret.")
        gemini_model = None
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Error configuring Google Gemini API: {e}")
    gemini_model = None

# --- Database Engine Initialization and Table Creation (Cached) ---
@st.cache_resource
def get_db_engine_and_create_tables():
    """
    Initializes and caches the database engine, and creates tables.
    This function runs only once per Streamlit app session.
    """
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    try:
        SQLModel.metadata.create_all(engine)
        st.success("Database tables initialized (or already exist).")
    except Exception as e:
        st.error(f"Error during database initialization: {e}")
    return engine

# Get the cached database engine
engine = get_db_engine_and_create_tables()

# --- Streamlit App Starts Here ---

st.set_page_config(page_title="Streamlit To-Do App", layout="wide")
st.title("Simple To-Do List")

# Initialize session state for translations
if 'translations' not in st.session_state:
    st.session_state.translations = {}

# --- Database Operations ---
# These functions now use the globally available and cached 'engine'

def get_all_todos_db() -> List[TodoItem]:
    """Fetches all to-do items directly from the database."""
    with Session(engine) as session:
        todos = session.exec(select(TodoItem)).all()
        return todos

def create_todo_db(todo_create: TodoItemCreate) -> TodoItem:
    """Adds a new to-do item to the database."""
    with Session(engine) as session:
        db_todo = TodoItem.model_validate(todo_create)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo

def update_todo_db(todo_id: int, todo_update: TodoItemUpdate) -> Optional[TodoItem]:
    """Updates a to-do item in the database."""
    with Session(engine) as session:
        todo = session.get(TodoItem, todo_id)
        if not todo:
            return None
        update_data = todo_update.model_dump(exclude_unset=True)
        todo.sqlmodel_update(update_data)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

def delete_todo_db(todo_id: int) -> bool:
    """Deletes a to-do item from the database."""
    with Session(engine) as session:
        todo = session.get(TodoItem, todo_id)
        if not todo:
            return False
        session.delete(todo)
        session.commit()
        return True

# --- Translation Function ---
def translate_text_gemini(text: str, target_language: str) -> Optional[str]:
    if not gemini_model:
        st.error("Translation service not available. API key might be missing or invalid.")
        return None
    try:
        prompt = f"Translate the following text into {target_language}: {text}"
        response = gemini_model.generate_content(prompt)
        translated_content = response.text
        return translated_content
    except Exception as e:
        st.error(f"Gemini translation error: {e}")
        return None

# --- Streamlit UI ---

st.sidebar.header("Translation Settings")
LANGUAGES = {
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Hindi": "Hindi",
    "Marathi": "Marathi",
    "Japanese": "Japanese",
    "Chinese (Simplified)": "Chinese (Simplified)",
    "Korean": "Korean",
    "Portuguese": "Portuguese"
}
selected_language_name = st.sidebar.selectbox(
    "Translate to:",
    list(LANGUAGES.keys()),
    index=0
)
target_language = LANGUAGES[selected_language_name]


# Add New To-Do Item
st.header("Add New To-Do")
with st.form("add_todo_form", clear_on_submit=True):
    new_title = st.text_input(
        "Title",
        key="add_todo_title_input"
    )
    new_description = st.text_area(
        "Description (optional)",
        key="add_todo_description_input"
    )
    new_priority = st.selectbox(
        "Priority",
        ["None", "Low", "Medium", "High"],
        key="add_todo_priority_input"
    )
    new_due_date = st.date_input(
        "Due Date (optional)",
        min_value=date.today(),
        value=None,
        key="add_todo_due_date_input"
    )

    add_button = st.form_submit_button("Add To-Do")

    if add_button:
        submitted_title = new_title
        submitted_description = new_description
        submitted_priority = new_priority if new_priority != "None" else None
        submitted_due_date = new_due_date

        if submitted_title:
            try:
                create_todo_db(
                    TodoItemCreate(
                        title=submitted_title,
                        description=submitted_description,
                        priority=submitted_priority,
                        due_date=submitted_due_date
                    )
                )
                st.success("To-Do item added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding todo: {e}")
        else:
            st.warning("Please enter a title for the To-Do item.")

st.markdown("---")

# List Existing To-Do Items
st.header("Your To-Do List")
todos = get_all_todos_db()

if todos:
    # Access attributes directly, not with .get()
    incomplete_todos = [todo for todo in todos if not todo.completed]
    completed_todos = [todo for todo in todos if todo.completed]

    if incomplete_todos:
        st.subheader("Pending Tasks")
        task_number = 1
        for todo in incomplete_todos:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([0.5, 0.2, 0.2, 0.1])
                with col1:
                    st.markdown(f"{task_number}. **{todo.title}**")
                    if todo.description:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;_{todo.description}_")
                    if todo.priority:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**Priority:** {todo.priority}")
                    if todo.due_date:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**Due:** {todo.due_date}")

                    if todo.id in st.session_state.translations and \
                       target_language in st.session_state.translations[todo.id]:
                        st.markdown(f"**Translated ({selected_language_name}):** *{st.session_state.translations[todo.id][target_language]}*")

                with col2:
                    if st.button("Mark Completed", key=f"complete_{todo.id}"):
                        update_todo_db(todo.id, TodoItemUpdate(completed=True))
                        st.rerun()
                with col3:
                    if st.button(f"Translate to {selected_language_name}", key=f"translate_{todo.id}"):
                        text_to_translate = todo.title
                        if todo.description:
                            text_to_translate += f" (Description: {todo.description})"
                        if todo.priority:
                            text_to_translate += f" (Priority: {todo.priority})"
                        if todo.due_date:
                            text_to_translate += f" (Due Date: {todo.due_date})"

                        translated_text = translate_text_gemini(text_to_translate, target_language)
                        if translated_text:
                            if todo.id not in st.session_state.translations:
                                st.session_state.translations[todo.id] = {}
                            st.session_state.translations[todo.id][target_language] = translated_text
                            st.rerun()
                with col4:
                    if st.button("Delete", key=f"delete_incomplete_{todo.id}"):
                        delete_todo_db(todo.id)
                        if todo.id in st.session_state.translations:
                            del st.session_state.translations[todo.id]
                        st.rerun()
            st.divider()
            task_number += 1

    if completed_todos:
        st.subheader("Completed Tasks")
        completed_task_number = 1
        for todo in completed_todos:
            with st.container(border=True):
                col1, col2, col3 = st.columns([0.7, 0.2, 0.1])
                with col1:
                    st.markdown(f"<del>**{completed_task_number}. {todo.title}**</del>", unsafe_allow_html=True)
                    if todo.description:
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;_{todo.description}_</del>", unsafe_allow_html=True)
                    if todo.priority:
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;**Priority:** {todo.priority}</del>", unsafe_allow_html=True)
                    if todo.due_date:
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;**Due:** {todo.due_date}</del>", unsafe_allow_html=True)

                    if todo.id in st.session_state.translations and \
                       target_language in st.session_state.translations[todo.id]:
                        st.markdown(f"<del>**Translated ({selected_language_name}):** *{st.session_state.translations[todo.id][target_language]}*</del>", unsafe_allow_html=True)
                with col2:
                    pass
                with col3:
                    if st.button("Delete", key=f"delete_completed_{todo.id}"):
                        delete_todo_db(todo.id)
                        if todo.id in st.session_state.translations:
                            del st.session_state.translations[todo.id]
                        st.rerun()
            st.divider()
            completed_task_number += 1
else:
    st.info("No To-Do items yet! Add one above.")
