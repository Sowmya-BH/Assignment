# MySQL Database Dialogue Engine

This is a Streamlit application that allows users to interact with a MySQL database using natural language. It leverages **LangChain** for chaining conversational components and **Groq** for fast, efficient Large Language Model (LLM) inference to convert natural language questions into SQL queries.

## ✨ Features

  * **Natural Language to SQL:** Ask questions about your database in plain English, and the AI will generate and execute SQL queries.
  * **Conversational History:** The AI maintains context from previous interactions to provide more relevant responses.
  * **Dynamic Database Connection:** Connect to any MySQL database by providing credentials directly within the Streamlit sidebar.
  * **Secure API Key Handling:** Uses Streamlit's `st.secrets` for securely loading your Groq API key.

## 🚀 Getting Started

Follow these steps to get your MySQL Database Dialogue Engine up and running.

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.9+**
  * **MySQL Server:** Make sure your MySQL server is running and accessible. If you're on macOS and installed via Homebrew, you can start it with `brew services start mysql`.
  * **MySQL Database and User:** You'll need a MySQL database (e.g., `Testdb`) and a user (e.g., `root` or a dedicated app user) with appropriate permissions to access it.

### 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YourUsername/your-repo-name.git
    cd your-repo-name # Replace 'your-repo-name' with your actual repository name
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv myenv
    source myenv/bin/activate # On Windows: .\myenv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    (You'll need to create this file, see **`requirements.txt`** section below.)

4.  **Set up your Groq API Key:**

      * Get your API key from [Groq Console](https://console.groq.com/).
      * Create a folder named `.streamlit` in the root of your project directory.
      * Inside the `.streamlit` folder, create a file named `secrets.toml`.
      * Add your Groq API key to `secrets.toml` like this:
        ```toml
        # .streamlit/secrets.toml
        GROQ_API_KEY = "gsk_YOUR_GROQ_API_KEY_HERE"
        ```
        (Replace `gsk_YOUR_GROQ_API_KEY_HERE` with your actual key.)

### `requirements.txt`

Create a file named `requirements.txt` in your project root with the following contents:

```
streamlit
python-dotenv
langchain-community
langchain-core
langchain-groq
sqlalchemy
mysql-connector-python # Or mysqlclient, if you prefer
```

### ▶️ Running the App

Once you've completed the installation and setup:

```bash
streamlit run pages/Experiments.py # Adjust path if your main file is named differently
```

This will open the Streamlit application in your web browser.

## ⚙️ Usage

1.  **Connect to Database:**
      * In the **sidebar**, enter your MySQL `Host`, `Port`, `User`, `Password`, and `Database` name.
      * Click the **"Connect"** button. You should see a "Successfully connected to the database\!" message upon success.
2.  **Ask Questions:**
      * Once connected, use the chat input box at the bottom to ask natural language questions about your database.
      * The AI will attempt to convert your question into a SQL query and provide the answer.

## ⚠️ Important Notes

  * **MySQL User Permissions:** Ensure the MySQL user you're connecting with has sufficient permissions (`SELECT` on tables you want to query, and `SHOW TABLES`, `DESCRIBE` etc. for schema introspection) on the specified database.
  * **Root User Warning:** Using the `root` user for applications is generally discouraged in production environments due to security risks. Consider creating a dedicated user with minimal necessary privileges.
  * **Model Selection:** The `get_sql_chain` function uses `llama-3.1-8b-instant`. You can change this to other available Groq models (e.g., `llama3-70b-8192`) by modifying the `model` parameter in `ChatGroq` instantiation.

## 🤝 Contributing

Contributions are welcome\! If you have suggestions for improvements or find issues, please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

-----

Remember to replace placeholders like `https://github.com/YourUsername/your-repo-name.git`, `your-repo-name`, and consider creating a `LICENSE` file if you haven't already\! Good luck with your project\!
