from flask import Flask, request, send_file, render_template_string
import pandas as pd
import os
import uuid

app = Flask(__name__)

# Function to generate HTML from CSV
def generate_html_from_csv(csv_filename, output_filename):
    df = pd.read_csv(csv_filename)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCQ Table</title>
        <style>
            table {
                width: 80%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            h2 {
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        <h2>MCQ Questions</h2>
        <table>
    """
    
    for idx, row in df.iterrows():
        html_content += f"""
        <tr>
            <th rowspan="3">{idx + 1}</th>
            <th colspan="4">{row['Question']}</th>
        </tr>
        <tr>
            <td>A)</td>
            <td>{row['OptionA']}</td>
            <td>B)</td>
            <td>{row['OptionB']}</td>
        </tr>
        <tr>
            <td>C)</td>
            <td>{row['OptionC']}</td>
            <td>D)</td>
            <td>{row['OptionD']}</td>
        </tr>
        """
    
    html_content += """
        </table>
        <h2>Answer Key</h2>
        <table>
            <tr>
                <th>Q. No.</th>
                <th>Correct Option</th>
            </tr>
    """
    
    for idx, row in df.iterrows():
        html_content += f"""
            <tr>
                <td>{idx + 1}</td>
                <td>{row['CorrectOption']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    return output_filename


# Home page: upload form + instructions
@app.route('/')
def home():
    return render_template_string("""
        <div style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 20px;">
            <h1 style="color:#2c3e50;">MCQ → HTML Generator</h1>
            <p>Please upload a CSV file in the following format:</p>
            <pre style="background:#f4f4f4; padding:10px; border-radius:5px; border:1px solid #ccc;">
Question,OptionA,OptionB,OptionC,OptionD,CorrectOption
"What is the capital of France?", "Paris", "London", "Berlin", "Rome", "A"
"Which planet is known as the Red Planet?", "Earth", "Mars", "Jupiter", "Venus", "B"
            </pre>
            <form action="/upload" method="post" enctype="multipart/form-data" style="margin-top:20px;">
                <input type="file" name="file" accept=".csv" required style="margin-bottom:10px;">
                <br>
                <button type="submit" style="background:#2c3e50; color:white; padding:10px 20px; border:none; border-radius:5px;">
                    Generate HTML
                </button>
            </form>
        </div>
    """)


# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Empty filename", 400
    
    os.makedirs("uploads", exist_ok=True)

    unique_id = str(uuid.uuid4())
    csv_path = os.path.join("uploads", f"{unique_id}.csv")
    output_file = os.path.join("uploads", f"{unique_id}.html")

    file.save(csv_path)
    generate_html_from_csv(csv_path, output_file)

    return render_template_string(f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; text-align:center;">
            <h2 style="color:green;">✅ HTML Generated Successfully!</h2>
            <p>You can now <a href="/download/{unique_id}" style="color:#2c3e50; font-weight:bold;">download your HTML file</a>.</p>
            <p>➡️ Open it in your browser, copy it into Word, and then paste it into your original table.</p>
            <a href="/" style="display:inline-block; margin-top:15px; background:#2c3e50; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">Upload Another</a>
        </div>
    """)


# Download route
@app.route('/download/<file_id>')
def download(file_id):
    output_file = os.path.join("uploads", f"{file_id}.html")
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
