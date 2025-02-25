# h5p_builder.py
import json
import zipfile
import os

def generate_markdown(content_data, content_type, output_filename="questions.md"):
    markdown_content = f"# {content_type} Questions and Answers\n\n"
    for i, item in enumerate(content_data[:10], 1):
        if content_type == "Multiple Choice":
            markdown_content += f"## Question {i}: {item['question']}\n"
            markdown_content += "Options:\n"
            for j, opt in enumerate(item["options"], 1):
                marker = "*" if opt == item["correct"] else "-"
                markdown_content += f"  {marker} {j}. {opt}\n"
            markdown_content += f"**Correct Answer**: {item['correct']}\n\n"
        elif content_type == "Fill in the Blanks":
            markdown_content += f"## Sentence {i}: {item['text']}\n"
            markdown_content += f"**Answer**: {item['answer']}\n\n"
        elif content_type == "True/False":
            markdown_content += f"## Statement {i}: {item['question']}\n"
            markdown_content += f"**Answer**: {item['correct']}\n\n"
        elif content_type == "Text":
            outline = item.get("outline", "No outline provided.")
            notes = item.get("notes", "No speaker notes provided.")
            markdown_content += f"## Slide {i}: {outline}\n"
            markdown_content += f"**Speaker Notes**: {notes}\n\n"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    return output_filename

def create_h5p_course_presentation(pdf_name, content_type, content_data, output_filename="output.h5p"):
    h5p_data = {
        "title": f"Course Presentation from {pdf_name}",
        "mainLibrary": "H5P.CoursePresentation",
        "language": "en",
        "embedTypes": ["iframe"],
        "preloadedDependencies": [
            {"machineName": "H5P.CoursePresentation", "majorVersion": "1", "minorVersion": "22"},
            {"machineName": "H5P.MultiChoice", "majorVersion": "1", "minorVersion": "14"},
            {"machineName": "H5P.Blanks", "majorVersion": "1", "minorVersion": "12"},
            {"machineName": "H5P.TrueFalse", "majorVersion": "1", "minorVersion": "8"},
            {"machineName": "H5P.AdvancedText", "majorVersion": "1", "minorVersion": "1"}
        ]
    }

    output_filename = output_filename.replace("/", "-")

    slides = []
    for i in range(10):
        if content_type == "Multiple Choice":
            item = content_data[i] if i < len(content_data) else {"question": f"Question {i+1}", "options": ["A", "B", "C", "D"], "correct": "A"}
            slide = {
                "elements": [
                    {
                        "x": 5, "y": 5, "width": 90, "height": 90,
                        "action": {
                            "library": "H5P.MultiChoice 1.14",
                            "params": {
                                "question": item["question"],
                                "answers": [{"text": opt, "correct": opt == item["correct"]} for opt in item["options"]],
                                "behaviour": {
                                    "enableRetry": True,
                                    "enableSolutionsButton": True,
                                    "singlePoint": False,
                                    "showSolutions": True
                                },
                                "l10n": {"showSolutions": "Show solutions", "retry": "Retry"}
                            },
                            "subContentId": f"slide-{i+1}-mc-{os.urandom(4).hex()}"
                        }
                    }
                ],
                "title": f"Question {i+1}",
                "slideBackgroundSelector": {}
            }
        elif content_type == "Fill in the Blanks":
            item = content_data[i] if i < len(content_data) else {"text": f"Sentence {i+1} ____.", "answer": "missing"}
            formatted_text = item["text"].replace("____", f"*{item['answer']}*")
            slide = {
                "elements": [
                    {
                        "x": 5, "y": 5, "width": 90, "height": 90,
                        "action": {
                            "library": "H5P.Blanks 1.12",
                            "params": {
                                "text": formatted_text,
                                "behaviour": {
                                    "enableRetry": True,
                                    "enableSolutionsButton": True,
                                    "showSolutions": True
                                }
                            },
                            "subContentId": f"slide-{i+1}-blanks-{os.urandom(4).hex()}"
                        }
                    }
                ],
                "title": f"Sentence {i+1}",
                "slideBackgroundSelector": {}
            }
        elif content_type == "True/False":
            item = content_data[i] if i < len(content_data) else {"question": f"Statement {i+1}", "correct": True}
            correct_value = item["correct"]
            if isinstance(correct_value, str):
                correct_value = correct_value.lower() == "true"
            slide = {
                "elements": [
                    {
                        "x": 5, "y": 5, "width": 90, "height": 90,
                        "action": {
                            "library": "H5P.TrueFalse 1.8",
                            "params": {
                                "question": item["question"],
                                "correct": correct_value,
                                "behaviour": {
                                    "enableRetry": True,
                                    "enableSolutionsButton": True,
                                    "showSolutions": True
                                }
                            },
                            "subContentId": f"slide-{i+1}-tf-{os.urandom(4).hex()}"
                        }
                    }
                ],
                "title": f"Statement {i+1}",
                "slideBackgroundSelector": {}
            }
        elif content_type == "Text":
            item = content_data[i] if i < len(content_data) else {"outline": f"Slide {i+1} Outline", "notes": "No notes"}
            outline = item.get("outline", item.get("text", f"Slide {i+1} Outline"))
            notes = item.get("notes", "No speaker notes provided.")
            slide = {
                "elements": [
                    {
                        "x": 5, "y": 5, "width": 90, "height": 40,
                        "action": {
                            "library": "H5P.AdvancedText 1.1",
                            "params": {
                                "text": f"<h3>{outline}</h3>"
                            },
                            "subContentId": f"slide-{i+1}-text-outline-{os.urandom(4).hex()}"
                        }
                    },
                    {
                        "x": 5, "y": 50, "width": 90, "height": 40,
                        "action": {
                            "library": "H5P.AdvancedText 1.1",
                            "params": {
                                "text": f"<p><em>Speaker Notes:</em> {notes}</p>"
                            },
                            "subContentId": f"slide-{i+1}-text-notes-{os.urandom(4).hex()}"
                        }
                    }
                ],
                "title": f"Slide {i+1}",
                "slideBackgroundSelector": {}
            }
        slides.append(slide)

    content_data_json = {
        "presentation": {
            "slides": slides,
            "keywordListEnabled": True,
            "globalBackgroundSelector": {},
            "keywordListAlwaysShow": False,
            "keywordListAutoHide": False,
            "keywordListOpacity": 90
        },
        "override": {
            "activeSurface": False,
            "hideSummarySlide": False,
            "summarySlideSolutionButton": True,
            "summarySlideRetryButton": True,
            "enablePrintButton": False,
            "social": {
                "showFacebookShare": False,
                "facebookShare": {"url": "@currentpageurl", "quote": "I scored @score out of @maxScore on a task at @currentpageurl."},
                "showTwitterShare": False,
                "twitterShare": {"statement": "I scored @score out of @maxScore on a task at @currentpageurl.", "url": "@currentpageurl", "hashtags": "h5p, course"},
                "showGoogleShare": False,
                "googleShareUrl": "@currentpageurl"
            }
        },
        "l10n": {
            "slide": "Slide",
            "score": "Score",
            "yourScore": "Your Score",
            "maxScore": "Max Score",
            "total": "Total",
            "totalScore": "Total Score",
            "showSolutions": "Show solutions",
            "retry": "Retry",
            "exportAnswers": "Export text",
            "hideKeywords": "Hide sidebar navigation menu",
            "showKeywords": "Show sidebar navigation menu",
            "fullscreen": "Fullscreen",
            "exitFullscreen": "Exit fullscreen",
            "prevSlide": "Previous slide",
            "nextSlide": "Next slide",
            "currentSlide": "Current slide",
            "lastSlide": "Last slide",
            "solutionModeTitle": "Exit solution mode",
            "solutionModeText": "Solution Mode",
            "summaryMultipleTaskText": "Multiple tasks",
            "scoreMessage": "You achieved:",
            "shareFacebook": "Share on Facebook",
            "shareTwitter": "Share on Twitter",
            "shareGoogle": "Share on Google+",
            "summary": "Summary",
            "solutionsButtonTitle": "Show comments"
        }
    }

    os.makedirs("temp_h5p/content", exist_ok=True)
    with open("temp_h5p/h5p.json", "w") as f:
        json.dump(h5p_data, f)
    with open("temp_h5p/content/content.json", "w") as f:
        json.dump(content_data_json, f)

    with zipfile.ZipFile(output_filename, "w") as h5p_zip:
        h5p_zip.write("temp_h5p/h5p.json", "h5p.json")
        h5p_zip.write("temp_h5p/content/content.json", "content/content.json")

    md_filename = f"{pdf_name}_{content_type.replace('/', '-')}_Questions.md"
    md_file = generate_markdown(content_data, content_type, md_filename)

    os.remove("temp_h5p/h5p.json")
    os.remove("temp_h5p/content/content.json")
    os.rmdir("temp_h5p/content")
    os.rmdir("temp_h5p")

    return output_filename, md_file
