## API Configuration:

**Domain Name:** http://192.168.10.185:8800 

#### (this is for web view)
---

## 1. API for Summary and Query Suggestions

- **Endpoint:**
  http://192.168.10.185:8800/api/pdf_to_summary

- **Method:**
  POST

- **Request Format:**
```yml
  - Body Type: Form Data
  - Key: pdf
  - Value: Any valid PDF file.
```
- **Expected Response Format (JSON):**
```json
  {
    "status": "success",
    "extracted_text": "<extracted text from the PDF>",
    "summary": "<summary of the extracted text>",
    "suggested_queries": [
      "<first suggested query>",
      "<second suggested query>",
      "<third suggested query>",
      "<fourth suggested query>",
      "<fifth suggested query>"
    ]
  }
  ```

---

## 2. API for Text to Query

- **Endpoint:**
  http://192.168.10.185:8800/api/text_with_query

- **Method:**
  POST

- **Request Format:**
  - Body Type: Raw JSON
  - Body Content:
    ```json
    {
      "text": "<extracted text from the PDF>",
      "query": "<Any question>"
    }
    ```

- **Expected Response Format (JSON):**
```json
{
    "status": "success",
    "answer": "<answer based on the extracted text>"
}
  ```

---
