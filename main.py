import gradio as gr
import requests
import json

# ------------------------------
#  CONFIGURATION
# ------------------------------
API_URL = "https://litellm-litemaas.apps.prod.rhoai.rh-aiservices-bu.com/v1/chat/completions"
API_TOKEN = "sk-LszPuMF92HVEMDjhYO4KEQ"

analysing_system_prompt = """You are a log analysis expert. Your task is to analyze the provided system logs and identify any anomalies, errors, or noteworthy patterns.
Provide a concise summary of your findings along with any recommendations for further investigation or action. Provide the results in bullet points for clarity."""


# ------------------------------
#  CORE FUNCTION
# ------------------------------
def log_analyser(logs):
    messages = [
        {"role": "system", "content": analysing_system_prompt},
        {"role": "user", "content": logs}
    ]

    payload = {
        "model": "Mistral-Small-24B-W8A8",
        "messages": messages,
        "temperature": 0.2,
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    analysis_text = ""
    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                data_str = line.decode("utf-8")[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    if "choices" in chunk:
                        delta = chunk["choices"][0].get("delta", {})
                        content_chunk = delta.get("content", "")
                        if content_chunk:
                            analysis_text += content_chunk
                            yield analysis_text
                except json.JSONDecodeError:
                    print("Error decoding chunk:", data_str)
        yield analysis_text

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


# ------------------------------
#  MAIN UI
# ------------------------------
def main():
    cert_logo = "/Users/sudheer/Downloads/Preview-21.png"
    redhat_logo = "/Users/sudheer/Downloads/Red_Hat-Logo.wine.svg"

    custom_css = """
    body {
        background: linear-gradient(135deg, #dfe9f3, #ffffff);
        font-family: 'Segoe UI', sans-serif;
        color: #003366;
    }

    .gradio-container {
        max-width: 900px !important;
        margin: 40px auto;
        border-radius: 18px;
        background: rgba(255,255,255,0.75);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        backdrop-filter: blur(10px);
        padding: 40px;
    }

    #header-bar {
        background: linear-gradient(90deg, #003366, #004b99);
        border-radius: 14px;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }

    #header-bar img {
        height: 60px !important;
        width: auto !important;
        object-fit: contain;
        background: transparent !important;
    }

    #header-bar h1 {
        flex: 1;
        text-align: center;
        color: #ffffff;
        font-size: 22px;
        font-weight: 600;
        margin: 0;
    }

    textarea {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 8px !important;
        color: #001933 !important;
    }

    button {
        background-color: #003366 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
    }

    /* --- Output text styling --- */
    #output-markdown {
        color: #001933 !important;
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 15px;
        font-size: 15px;
        line-height: 1.6;
        max-height: 400px;        /* scrollable result area */
        overflow-y: auto;
        box-shadow: inset 0 0 6px rgba(0,0,0,0.08);
    }
    """

    with gr.Blocks(css=custom_css) as demo:
        # Header Bar
        with gr.Row(elem_id="header-bar"):
            gr.Image(cert_logo, show_label=False, container=False)
            gr.Markdown("<h1>Log Analysis Agent</h1>")
            gr.Image(redhat_logo, show_label=False, container=False)

        # Main interface
        inp = gr.Textbox(
            placeholder="Paste system logs here...",
            label="System Logs",
            lines=6
        )
        out = gr.Markdown(label="Analysis Result", elem_id="output-markdown")
        analyze = gr.Button("Analyze Logs", variant="primary")
        analyze.click(fn=log_analyser, inputs=inp, outputs=out)

    demo.launch()


if __name__ == "__main__":
    main()
