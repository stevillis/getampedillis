# Image Generator for GetAmped Tournaments

This app allows users to create images for teams and tournaments. The app takes user-input data and generates images based on the provided information.

## Running the Project Locally

### Step 1: Install Python

If you don't have Python installed on your computer, download the latest version from the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/).

### Step 2: Download the Project

Download the project zip file by clicking the "Code" button, then "Download ZIP".

### Step 3: Extract the Project

Extract the project zip file to a folder on your computer. Move the extracted folder to disk `C:\` directory.

The final structure of the project folder must match the following:
```
C:\tournament_image_creator/
├─ data/
├─ generated_images/
├─ pages/
├─ utils/
├─ .gitignore
├─ .pre-commit-config.yaml
├─ 🏠Home.py
├─ README.md
├─ requirements_dev.txt
├─ requirements.txt
```

### Step 5: Create a Virtual Environment and Install Dependencies

Open a terminal or command prompt and navigate to the project folder. Create a virtual environment using the following command:

```bash
python -m venv venv
```

Activate the virtual environment using the following command:

```bash
venv\Scripts\activate
```

Install the project dependencies using the following command:

```bash
pip install -r requirements.txt
```

### Step 6: Run the App

Run the app using the following command:

```bash
python streamlit run 🏠Home.py
```

This will start the Streamlit app, and you can access it in your web browser at [http://localhost:8501](http://localhost:8501/)

**Note: The commands `python -m venv venv` and `pip install -r requirements.txt` only need to be executed once.**
