from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq 

import streamlit as st

from sqlalchemy.exc import DatabaseError, OperationalError
from urllib.parse import quote_plus  # For password encoding




def init_database(user:str,password:str,host:str,port:str,database:str,echo: bool = False)->SQLDatabase:
    """
    Initialize and return a SQLDatabase connection.
    
    Args:
        user: MySQL username
        password: MySQL password
        host: MySQL host (default: localhost)
        port: MySQL port (default: 3306)
        database: Database name
        pool_pre_ping: Test connections for liveness (default: True)
        pool_recycle: Recycle connections after seconds (default: 3600)
        echo: Log SQL queries (default: False)
        
    Returns:
        SQLDatabase instance or None if connection fails
    """
    try:
        # Encode special characters in password
        encoded_password = quote_plus(password)
        db_uri = f"mysql+mysqlconnector://{user}:{encoded_password}@{host}:{port}/{database}"
        
        # Create database connection with validation
        db = SQLDatabase.from_uri(
            db_uri,
            engine_args={
                "pool_pre_ping": True,
                "echo": echo
            }
        )
        
        # Test connection with simple query
        db.run("SELECT 1")
        return db
        
    except (DatabaseError, OperationalError) as e:
        st.error(f"Database connection failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def get_sql_chain(db):
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: Print first 5 users in alphabetical order by username
    SQL Query: SELECT username FROM users ORDER BY username ASC LIMIT 5;
    Question: How many users in users table?
    SQL Query: SELECT COUNT(*) FROM users;
    Question: Name 10 articles
    SQL Query: SELECT title FROM articles LIMIT 10;
    Question : Find all users whose email address ends with b@example.com
    SQL Query: SELECT username, email FROM users WHERE email LIKE '%@example.com';
   
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  llm = ChatGroq(model="llama-3.1-8b-instant",temperature=0,api_key=st.secrets['groq_api_key'])


  def get_schema(_):
    return db.get_table_info() 
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  ) 

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
  sql_chain = get_sql_chain(db)
  # Initialize variables
  sql_query = ""
  query_result = ""
    
  try:
        # First get the SQL query
    sql_query = sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
        })
        
        # Then execute the query
    query_result = db.run(sql_query)
  except Exception as e:
    query_result = f"Error executing query: {str(e)}"
        # Return early if there was an error
    return f"SQL Query:\n```sql\n{sql_query}\n```\n\n{query_result}"
    
  
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
  
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
  llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0,api_key=st.secrets['groq_api_key'])
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  # Get the natural language response
  nl_response = chain.invoke({
  "question": user_query,
  "chat_history": chat_history,
  "query": sql_query,
  "response": query_result,
    })
    
    # Combine both parts
  full_response = f"SQL Query:\n```sql\n{sql_query}\n```\n\n{nl_response}"
    
  return full_response
#   return chain.invoke({
#     "question": user_query,
#     "chat_history": chat_history,
#   })

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! Connect me to your Database and ask me anything about your database in Natural Language."),
    ]



load_dotenv()

st.set_page_config(page_title = "MySQLDatabase Conversation App",page_icon=":speech_balloon:")
st.title("MySQL Database Dialogue Engine")

with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root", key="User")
    st.text_input("Password", type="password", value="admin", key="Password")
    st.text_input("Database", value="mysql", key="Database")
    
    if st.button("Connect"):
        
        with st.spinner("Connecting to a database..."):
            
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            
        
            if db is not None:
            # Store the SQLDatabase object in a NEW session state key, not tied to a widget
                st.session_state.sql_database_object = db
                st.success("✅ Successfully connected to the database!")
                st.session_state.connected = True
            else:
            # Clear the session state if connection failed to prevent stale object
                if "sql_database_object" in st.session_state:
                    del st.session_state.sql_database_object



for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type your message here")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        sql_chain = get_sql_chain( st.session_state.sql_database_object)
        # response = sql_chain.invoke({"chat_history":st.session_state.chat_history,"question":user_query})
        response =get_response(user_query, st.session_state.sql_database_object, st.session_state.chat_history)
        st.markdown(response)
    st.session_state.chat_history.append(AIMessage(content=response))
    
