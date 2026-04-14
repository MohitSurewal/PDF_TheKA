from flask import Flask, request, send_file, render_template, session
import os
from PyPDF2 import PdfReader, PdfWriter
import random

app = Flask(__name__)
app.secret_key = "supersecretkey123"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



@app.route('/merge', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist("pdfs")
    writer = PdfWriter()

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    output_path = os.path.join(OUTPUT_FOLDER, "merged.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    return send_file(output_path, as_attachment=True)



@app.route('/split', methods=['POST'])
def split_pdf():
    file = request.files['pdf']
    start = int(request.form['start'])
    end = int(request.form['end'])

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    reader = PdfReader(path)
    writer = PdfWriter()

    for i in range(start-1, end):
        writer.add_page(reader.pages[i])

    output_path = os.path.join(OUTPUT_FOLDER, "split.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    return send_file(output_path, as_attachment=True)



@app.route('/extract-text', methods=['POST'])
def extract_text():
    file = request.files['pdf']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    txt_path = os.path.join(OUTPUT_FOLDER, "text.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return send_file(txt_path, as_attachment=True)



@app.route('/extract-images', methods=['POST'])
def extract_images():
    file = request.files['pdf']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    reader = PdfReader(path)
    count = 0

    for page in reader.pages:
        for image in page.images:
            img_path = os.path.join(OUTPUT_FOLDER, f"img_{count}.png")
            with open(img_path, "wb") as f:
                f.write(image.data)
            count += 1

    return f"{count} images extracted!"
    # PyPDF2 supports page.images extraction :contentReference[oaicite:2]{index=2}


@app.route('/compress', methods=['POST'])
def compress_pdf():
    file = request.files['pdf']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    reader = PdfReader(path)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()  # compression
        writer.add_page(page)

    output_path = os.path.join(OUTPUT_FOLDER, "compressed.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    return send_file(output_path, as_attachment=True)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/')
def base():
    return render_template("base.html")


@app.route("/services")
def services():
    services_list = [
        "Merge PDFs",
        "Split PDFs",
        "Extract Text",
        "Extract Images",
        "Compress PDF"
    ]
    return render_template("services.html", services=services_list)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        print("POST HIT")  

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        user_answer = request.form.get("captcha")
        real_answer = session.get("captcha_answer")

        print("USER:", user_answer, "REAL:", real_answer)  \

       
        if not real_answer or str(user_answer) != str(real_answer):
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            session["captcha_answer"] = num1 + num2

            return render_template(
                "contact.html",
                error="Wrong captcha ❌",
                num1=num1,
                num2=num2
            )

        
        with open("data.txt", "a", encoding="utf-8") as f:
            f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n")

        
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        session["captcha_answer"] = num1 + num2

        return render_template(
            "contact.html",
            success="Message saved ✅",
            num1=num1,
            num2=num2
        )

    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session["captcha_answer"] = num1 + num2

    return render_template("contact.html", num1=num1, num2=num2)
  
if __name__ == "__main__":
    app.run(debug=True)