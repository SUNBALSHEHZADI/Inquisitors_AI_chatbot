from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 980
image = Image.new("RGB", (WIDTH, HEIGHT), "#f2f8f5")
draw = ImageDraw.Draw(image)

font_paths = [
    "C:/Windows/Fonts/trebuc.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
bold_paths = [
    "C:/Windows/Fonts/trebucbd.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

def get_font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

font_title = get_font(bold_paths, 38)
font_subtitle = get_font(font_paths, 17)
font_head = get_font(bold_paths, 22)
font_body = get_font(font_paths, 17)
font_small = get_font(bold_paths, 14)


def rounded_box(xy, fill, outline="#d7e5e2", header=None):
    draw.rounded_rectangle(xy, radius=16, fill=fill, outline=outline, width=2)
    if header:
        x1, y1, x2, y2 = xy
        draw.rounded_rectangle((x1, y1, x2, y1 + 54), radius=16, fill=header)
        draw.rectangle((x1, y1 + 38, x2, y1 + 54), fill=header)


def arrow(start, end, color="#ef765d", width=4):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        points = [(x2, y2), (x2 - 14, y2 - 8), (x2 - 14, y2 + 8)]
    else:
        points = [(x2, y2), (x2 - 8, y2 - 14), (x2 + 8, y2 - 14)]
    draw.polygon(points, fill=color)


def text(x, y, value, font, fill="#27414a"):
    draw.text((x, y), value, font=font, fill=fill)

text(90, 45, "Inquisitors AI Assistant", font_title, "#102b3a")
text(90, 95, "Learn • Grow • Build | RAG-based educational chatbot architecture", font_subtitle, "#65777b")

draw.ellipse((1250, -70, 1610, 290), fill="#f5d9d0")
draw.ellipse((-100, 730, 340, 1170), fill="#d9efec")

rounded_box((90, 175, 390, 355), "#ffffff", header="#079bb4")
text(120, 192, "1. Browser Frontend", font_head, "#ffffff")
text(120, 260, "HTML / CSS / JavaScript", font_body)
text(120, 290, "Chat, voice, session UI", font_body)
text(120, 320, "Fetch API + localStorage", font_body)

rounded_box((500, 145, 1100, 385), "#14516a", outline="#14516a", header="#14516a")
text(545, 162, "2. FastAPI Application Layer", font_head, "#ffffff")
text(545, 220, "Same-origin frontend serving + REST API", font_body, "#ffffff")
text(545, 252, "POST /api/chat", font_body, "#ffffff")
text(545, 284, "GET /api/history/{session_id}", font_body, "#ffffff")
text(545, 316, "Validation, CORS, errors, startup initialization", font_body, "#ffffff")
text(545, 348, "app/main.py + app/api/routes.py", font_body, "#ffffff")
arrow((390, 265), (500, 265))
text(408, 235, "HTTP / JSON", font_small, "#65777b")

rounded_box((500, 485, 1100, 785), "#ffffff", header="#ef765d")
text(545, 502, "3. RAG + Educational Tutor Pipeline", font_head, "#ffffff")
text(545, 562, "Question classification: official or educational", font_body)
text(545, 596, "Sentence Transformers embedding", font_body)
text(545, 630, "FAISS similarity retrieval and relevance filtering", font_body)
text(545, 664, "Grounded prompt with source context", font_body)
text(545, 698, "General concept explanations when appropriate", font_body)
text(545, 732, "app/rag/retriever.py + prompt.py + llm.py", font_body)
arrow((800, 385), (800, 485))
text(820, 430, "QUESTION", font_small, "#65777b")

rounded_box((90, 485, 390, 655), "#ffffff", header="#173f4e")
text(120, 502, "4. Knowledge Sources", font_head, "#ffffff")
text(120, 560, "Verified society Markdown", font_body)
text(120, 590, "AI / ML / Data Science curriculum", font_body)
text(120, 620, "Internships, events, FAQ, contact", font_body)
arrow((390, 570), (500, 570))
text(402, 540, "INDEXED CONTENT", font_small, "#65777b")

rounded_box((1210, 485, 1510, 655), "#ffffff", header="#079bb4")
text(1240, 502, "5. Groq LLM", font_head, "#ffffff")
text(1240, 560, "Generates the final response", font_body)
text(1240, 590, "Uses grounded prompt context", font_body)
text(1240, 620, "Returns student-friendly Markdown", font_body)
arrow((1100, 635), (1210, 635))
text(1115, 605, "PROMPT", font_small, "#65777b")

rounded_box((500, 850, 1100, 930), "#ffffff")
text(545, 877, "6. SQLite conversation memory | session history and follow-ups", font_body)
arrow((800, 785), (800, 850))
text(820, 810, "SAVE TURN", font_small, "#65777b")

text(90, 735, "GROUNDING RULE", font_small, "#65777b")
text(90, 765, "Official society facts stay verified.", font_body)
text(90, 795, "Academic concepts can be taught.", font_body)

image.save("screenshots/system-architecture.png", "PNG", optimize=True)
