import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import speech_recognition as sr
import threading
import json
import os
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import cv2
import logging
from PIL import Image, ImageTk
import time

# Setup logging
logging.basicConfig(
    filename='learning_assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# NLTK downloads
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Define supporting classes first
class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_recording = False
    
    def record(self):
        self.is_recording = True
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5.0)
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            return "No speech detected"
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results from speech recognition service"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            self.is_recording = False
    
    def stop_recording(self):
        self.is_recording = False

class QuestionGenerator:
    def __init__(self):
        self.current_question = None
        self.question_bank = self._initialize_question_bank()
    
    def _initialize_question_bank(self):
        return {
            "Mathematics": {
                1: [{"prompt": "What is 5 + 7?", "concepts": ["addition", "basic math"]}],
                2: [{"prompt": "What is 8 × 4?", "concepts": ["multiplication", "basic math"]}]
            },
            "Science": {
                1: [{"prompt": "What are the three states of matter?", 
                     "concepts": ["states of matter", "basic science"]}]
            }
            # Add more subjects and questions as needed
        }
    
    def generate_question(self, subject, difficulty):
        available_levels = list(self.question_bank.get(subject, {}).keys())
        if not available_levels:
            self.current_question = {"prompt": f"Tell me about {subject}.", "concepts": [subject]}
            return self.current_question
        
        actual_difficulty = min(difficulty, max(available_levels))
        questions = self.question_bank[subject][actual_difficulty]
        self.current_question = random.choice(questions)
        return self.current_question
    
    def get_current_question_concepts(self):
        return self.current_question.get("concepts", []) if self.current_question else []

class NLPAnalyzer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        return [self.lemmatizer.lemmatize(word) for word in tokens 
                if word.isalpha() and word not in self.stop_words]
    
    def analyze_response(self, user_response, subject, expected_concepts):
        processed_response = self.preprocess_text(user_response)
        matched_concepts = [concept for concept in expected_concepts 
                          if any(word in processed_response 
                               for word in self.preprocess_text(concept))]
        
        match_percentage = len(matched_concepts) / len(expected_concepts) if expected_concepts else 0
        
        if subject == "Mathematics" and "addition" in expected_concepts and "12" in user_response:
            return {"is_correct": True, "feedback": "Correct! 5 + 7 = 12"}
        elif match_percentage >= 0.7:
            return {"is_correct": True, 
                   "feedback": f"Good job! Covered {len(matched_concepts)}/{len(expected_concepts)} concepts"}
        else:
            return {"is_correct": False, 
                   "feedback": f"Let's review: {', '.join(expected_concepts)}"}

# Now define the main class
class GamifiedLearningAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Gamified Learning Assistant")
        self.root.geometry("800x650")
        self.root.configure(bg="#f5f5f5")
        
        self.initialize_variables()
        self.speech_recognizer = SpeechRecognizer()
        self.question_generator = QuestionGenerator()
        self.nlp_analyzer = NLPAnalyzer()
        self.load_user_data()
        self.create_ui()
        self.video_active = False
        self.video_capture = None

    def initialize_variables(self):
        self.current_subject = ""
        self.is_session_active = False
        self.current_level = 1
        self.experience_points = 0
        self.progress = 0.0
        self.current_prompt = ""
        self.user_response = ""
        self.showing_feedback = False
        self.feedback_message = ""
        self.is_correct_answer = False
        self.is_listening = False
        self.questions_answered = 0
        self.correct_answers = 0

    def create_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.main_frame, text="Learning Adventure", 
                 font=("Helvetica", 26, "bold"), foreground="#2c3e50").pack(pady=15)
        
        self.tutor_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.tutor_frame.pack(pady=10, fill=tk.X)
        self.tutor_display = ttk.Label(self.tutor_frame)
        self.tutor_display.pack(expand=True)
        
        self.subject_label = ttk.Label(self.main_frame, text="", font=("Helvetica", 12, "bold"))
        self.subject_label.pack(pady=5)
        
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, 
                                          mode='determinate', style="Custom.Horizontal.TProgressbar")
        
        self.level_label = ttk.Label(self.progress_frame, font=("Helvetica", 10))
        self.xp_label = ttk.Label(self.progress_frame, font=("Helvetica", 10))
        
        self.interaction_frame = ttk.Frame(self.main_frame)
        self.interaction_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.question_label = ttk.Label(self.interaction_frame, font=("Helvetica", 12), 
                                      wraplength=600, justify=tk.LEFT, style="Question.TLabel")
        
        self.answer_entry = tk.Text(self.interaction_frame, height=4, width=60, 
                                  font=("Helvetica", 10), relief=tk.FLAT, borderwidth=1, bg="#ffffff")
        
        self.button_frame = ttk.Frame(self.interaction_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        self.voice_button = ttk.Button(self.button_frame, text="🎤 Speak", 
                                     command=self.toggle_speech_recognition, style="Accent.TButton")
        
        self.submit_button = ttk.Button(self.button_frame, text="Submit", 
                                      command=self.handle_submission, style="Primary.TButton")
        
        self.start_button = ttk.Button(self.interaction_frame, text="Begin Learning Journey", 
                                     command=self.show_subject_selection, style="Primary.TButton")
        self.start_button.pack(pady=20)
        
        self.feedback_frame = ttk.Frame(self.root, style="Feedback.TFrame")
        self.feedback_title = ttk.Label(self.feedback_frame, font=("Helvetica", 16, "bold"))
        self.feedback_title.pack(pady=10)
        self.feedback_text = ttk.Label(self.feedback_frame, font=("Helvetica", 12), 
                                     wraplength=450, justify=tk.CENTER)
        self.feedback_text.pack(pady=10)
        self.continue_button = ttk.Button(self.feedback_frame, text="Next", 
                                        command=self.continue_to_next_question, style="Accent.TButton")
        self.continue_button.pack(pady=10)
        
        self.configure_styles()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("Question.TLabel", background="#f0f0f0", padding=10)
        style.configure("Feedback.TFrame", background="#34495e")
        style.configure("Primary.TButton", font=("Helvetica", 10, "bold"))
        style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="#dfe6e9", background="#2ecc71")

    def update_ui_for_session(self):
        if self.is_session_active:
            self.subject_label.config(text=f"Subject: {self.current_subject}")
            self.progress_bar.pack(pady=5)
            self.level_label.pack(pady=2)
            self.xp_label.pack(pady=2)
            self.update_progress_display()
            self.start_button.pack_forget()
            self.question_label.pack(fill=tk.X, padx=10, pady=10)
            self.answer_entry.pack(fill=tk.X, padx=10, pady=5)
            self.button_frame.pack(fill=tk.X, pady=5)
            self.voice_button.pack(side=tk.LEFT, padx=5)
            self.submit_button.pack(side=tk.LEFT, padx=5)
            self.question_label.config(text=self.current_prompt)
            self.start_video()
        else:
            self.stop_video()
            for widget in (self.progress_bar, self.level_label, self.xp_label,
                         self.question_label, self.answer_entry, self.button_frame):
                widget.pack_forget()
            self.start_button.pack(pady=20)
            self.subject_label.config(text="")

    def update_progress_display(self):
        self.progress_bar['value'] = self.progress * 100
        self.level_label.config(text=f"Level {self.current_level}")
        self.xp_label.config(text=f"XP: {self.experience_points}")

    def handle_submission(self):
        try:
            self.user_response = self.answer_entry.get("1.0", tk.END).strip()
            if not self.user_response:
                messagebox.showwarning("Input Error", "Please provide an answer before submitting.")
                return
            self.evaluate_user_response()
            logging.info(f"Submission processed for {self.current_subject} - Question {self.questions_answered}")
        except Exception as e:
            logging.error(f"Submission error: {str(e)}")
            messagebox.showerror("Error", "An error occurred while processing your submission.")

    def start_video(self):
        if not self.video_active:
            try:
                self.video_capture = cv2.VideoCapture(0)
                self.video_active = True
                self.update_video_frame()
                logging.info("Video feed started")
            except Exception as e:
                logging.error(f"Failed to start video: {str(e)}")
                self.tutor_display.config(text="🧠", font=("Arial", 40))

    def stop_video(self):
        if self.video_active:
            self.video_active = False
            if self.video_capture:
                self.video_capture.release()
            self.tutor_display.config(text="🧠", font=("Arial", 40))
            logging.info("Video feed stopped")

    def update_video_frame(self):
        if self.video_active and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (200, 150))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.tutor_display.imgtk = imgtk
                self.tutor_display.configure(image=imgtk)
            self.root.after(33, self.update_video_frame)

    def show_subject_selection(self):
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Choose Your Subject")
        selection_window.geometry("400x450")
        selection_window.configure(bg="#f5f5f5")
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        ttk.Label(selection_window, text="Select Your Learning Path", 
                 font=("Helvetica", 16, "bold")).pack(pady=20)
        
        subjects = ["Mathematics", "Science", "History", "Language Arts", "Programming"]
        for subject in subjects:
            ttk.Button(selection_window, text=subject, 
                      command=lambda s=subject: self.start_session(s, selection_window),
                      style="Primary.TButton").pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Button(selection_window, text="Cancel", 
                  command=selection_window.destroy, style="Accent.TButton").pack(pady=20)

    def start_session(self, subject, selection_window=None):
        try:
            self.current_subject = subject
            self.is_session_active = True
            if subject in self.user_data:
                self.current_level = self.user_data[subject].get("level", 1)
                self.experience_points = self.user_data[subject].get("xp", 0)
            else:
                self.user_data[subject] = {"level": 1, "xp": 0}
            if selection_window:
                selection_window.destroy()
            self.update_ui_for_session()
            self.load_next_question()
            logging.info(f"Session started for {subject}")
        except Exception as e:
            logging.error(f"Session start error: {str(e)}")
            messagebox.showerror("Error", "Failed to start session.")

    def load_next_question(self):
        try:
            question = self.question_generator.generate_question(
                subject=self.current_subject,
                difficulty=self.current_level
            )
            self.current_prompt = question["prompt"]
            self.showing_feedback = False
            self.answer_entry.delete("1.0", tk.END)
            self.progress = float(self.questions_answered % 5) / 5.0
            self.update_ui_for_session()
        except Exception as e:
            logging.error(f"Question loading error: {str(e)}")
            self.current_prompt = "Error loading question. Please try again."

    def evaluate_user_response(self):
        try:
            analysis_result = self.nlp_analyzer.analyze_response(
                user_response=self.user_response,
                subject=self.current_subject,
                expected_concepts=self.question_generator.get_current_question_concepts()
            )
            self.is_correct_answer = analysis_result["is_correct"]
            self.feedback_message = analysis_result["feedback"]
            self.questions_answered += 1
            if self.is_correct_answer:
                self.correct_answers += 1
                xp_gain = 10 * self.current_level
                self.experience_points += xp_gain
                if self.experience_points >= self.current_level * 50:
                    self.current_level += 1
                    self.feedback_message += f"\n\nLevel Up! You've reached Level {self.current_level}!"
                    self.user_data[self.current_subject]["level"] = self.current_level
                self.user_data[self.current_subject]["xp"] = self.experience_points
                self.save_user_data()
            self.show_feedback()
        except Exception as e:
            logging.error(f"Response evaluation error: {str(e)}")
            self.feedback_message = "Error processing your response."
            self.show_feedback()

    def show_feedback(self):
        self.showing_feedback = True
        self.feedback_title.config(
            text="Well Done!" if self.is_correct_answer else "Let's Review",
            foreground="#2ecc71" if self.is_correct_answer else "#e74c3c"
        )
        self.feedback_text.config(text=self.feedback_message)
        self.feedback_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def continue_to_next_question(self):
        self.feedback_frame.place_forget()
        self.showing_feedback = False
        self.load_next_question()

    def toggle_speech_recognition(self):
        if self.is_listening:
            self.speech_recognizer.stop_recording()
            self.voice_button.config(text="🎤 Speak", style="Accent.TButton")
        else:
            self.voice_button.config(text="🔴 Listening", style="Accent.TButton")
            threading.Thread(target=self.start_speech_recognition, daemon=True).start()
        self.is_listening = not self.is_listening

    def start_speech_recognition(self):
        result = self.speech_recognizer.record()
        self.root.after(0, lambda: self.process_speech_result(result))

    def process_speech_result(self, result):
        if result:
            self.answer_entry.delete("1.0", tk.END)
            self.answer_entry.insert(tk.END, result)
        self.is_listening = False
        self.voice_button.config(text="🎤 Speak", style="Accent.TButton")

    def load_user_data(self):
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            with open('data/user_progress.json', 'r') as f:
                self.user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_data = {}
            logging.info("Initialized new user data")

    def save_user_data(self):
        try:
            with open('data/user_progress.json', 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save user data: {str(e)}")

    def run(self):
        self.root.mainloop()
        self.stop_video()

if __name__ == "__main__":
    root = tk.Tk()
    app = GamifiedLearningAssistant(root)
    app.run()
