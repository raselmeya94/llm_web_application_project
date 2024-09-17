# Project Deployment

## Prerequisites

### Python 3.10 or Above:
This guide assumes you have Python 3.10 or a later version installed. If not, refer to the official documentation for your operating system (OS) on how to install Python. Package manager commands like `sudo apt` (Ubuntu), `curl` (generic), or `brew` (macOS) might be used.

### Package Manager (Pip):
Verify that you have either `pip` (the default package manager for Python) or `con installed. If not, installation instructions are usually available online for your specific OS.



## Creating a Project Directory and Virtual Environment


### Create a Project Directory:

1. Open your terminal or command prompt.
2. Use the `mkdir` command to create a directory for your project. For example:

    ```bash
   mkdir my_django_project
    ```
3. Navigate into the project directory:
    ```bash
   cd my_django_project
    ```

### Clone Git repository:

```bash
    git clone https://github.com/raselmeya94/llm_web_application_project.git
```



### Create a Virtual Environment:

1. Use the `python -m venv` command to create a virtual environment named `llm_environment` (replace with your desired name):

    ```bash
   python -m venv llm_environment
    ```
### Directory Structure:
```
my_django_project/  (your local dir)
├── llm_web_application_project/  (git repo)
│   ├── llm_web_application/  (project dir)
│   │   ├── manage.py
│   │   └── ...  (other project files)
│   ├── requirements.txt
│   ├── API Deployment.md
│   └── Project Deployment.md
└── llm_environment/  (your environment directory)
```
### Activating the Virtual Environment:

#### macOS/Linux:
source llm_environment/bin/activate
Inside the project directory where located `llm_environment` and run the following command
    
```bash
source llm_environment/bin/activate
```   


Your terminal prompt will change to indicate that you're working within the virtual environment.


### Dependencies Installation:
Change directory and go to `llm_web_application_project` and run `pip install -r requirements.txt` for installation dependencies.
```bash
cd llm_web_application_project
```
Then run the following command
```bash
    pip install -r requirements.txt
```

### Run llm web application:
Go to `llm_web_application` and run the following commands
```bash
cd llm_web_application
```
Then run the following command
```bash
python manage.py runserver
```

The server will typically listen on the default port 8000. You can access your application by opening http://localhost:8000/ in your web browser.


