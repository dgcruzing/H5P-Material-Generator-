# H5P Material Generator

A Streamlit app that transforms PDFs into interactive H5P Course Presentations, powered by AI APIs (Groq, OpenAI, Claude, Google Gemini). Built with Grok 3 from xAI, this tool generates 10-slide presentations with customizable content types and a Markdown export for editing.

---

## Setup

### Prerequisites
- **Python 3.8+**: Installed on your system.
- **Pip**: For package management.
- **API Keys**: Get keys from:
  - [Groq](https://console.groq.com)
  - [OpenAI](https://platform.openai.com)
  - [Anthropic (Claude)](https://console.anthropic.com)
  - [Google Gemini](https://makersuite.google.com)

### Installation
1. **Clone the Repo**:
   ```bash
   git clone https://github.com/yourusername/h5p-material-generator.git
   cd h5p-material-generator


2. **Install Dependencies**
```bash
pip install streamlit groq pdfplumber openai anthropic google-generativeai
```
3. **Verify Files:**
    
    -   Ensure app.py and h5p_builder.py are in the root directory.

### Running the App
 - **Launch Locally:**
 -   Open your terminal (e.g., Command Prompt, PowerShell, or Bash).
    
 -   Navigate to the project directory if not already there
```bash
cd path/to/h5p-material-generator
```
 - Run the Streamlit command

```bash
streamlit run app.py
```
-   What Happens: The terminal will display a local URL (typically http://localhost:8501). Streamlit will automatically open this URL in your default web browser, launching the app. If it doesn’t auto-open, copy the URL from the terminal and paste it into your browser.

**3.  Usage:**
   -   Upload a PDF.
   -   Pick an API and enter its key (temporary, per-run).
   -   Choose a content type (Multiple Choice, Fill in the Blanks, True/False, Text).
   -   Select or write a prompt, then generate.
   -   Download the .h5p file and Markdown summary.   
        

### Database

-   Prompts: Stored in prompt_frameworks.db (SQLite). Add via:
    
   ```sql
sql

sqlite3 prompt_frameworks.db
INSERT INTO frameworks (name, prompt) VALUES ('Your Prompt Name', 'Your prompt text here.');
```
    
-   Management: Delete via UI; add/edit externally.

**Version Description**

This H5P Material Generator, crafted with Grok 3 from xAI, delivers a polished prototype for creating educational content:

 - **Core Features:**
    - **PDF to H5P:** Converts uploaded PDFs into 10-slide H5P Course Presentations.
	 - **Content Types:** Supports Multiple Choice, Fill in the Blanks, True/False, and Text slides with outlines and speaker note
	  - **AI-Powered:** Integrates Groq, OpenAI, Claude, and Google Gemini APIs for dynamic content generation.

    -  **Markdown Export:** Downloads a .md file with slide details for easy editing.
    -   **Prompt Database:** Stores creative prompts (e.g., 5E Instructional Model) in SQLite, selectable via UI.

        
**-   Achievements:**

 - Iterative Wins: Fixed file path errors, JSON parsing, and H5P compatibility (e.g., H5P.Text to H5P.AdvancedText).
	 - Session Persistence: Ensured H5P and Markdown downloads coexist without resets using st.session_state.
	 - Flexibility: Handles varied API outputs with fallbacks, keeping slides at a consistent 10.

        
**-   How We Got Here:**
   

 - Collaborated with Grok 3 to debug and refine—Grok’s quick iterations crushed issues like KeyError: 'text' and H5P validation errors.
 - Locked app.py for stability after core tweaks, focusing enhancements in h5p_builder.py.
 -
**Things to do**

- Fill in the blanks is not placing correcting on the import into H5P, it still builds so you can manually edit it out of the Markdown questions created.   
- Add more activities   
- At the moment it will only build 10 slides of single activities so you have to copy and paste to mis them up, easy enough to do in the copy/paste commands on H5P. But it would be nice to get an auto create going.
