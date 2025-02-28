import tkinter as tk
from tkinter import ttk, messagebox
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

# [SpeechRecognizer, QuestionGenerator, NLPAnalyzer classes remain unchanged]

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
        self.current_video_path = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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

    # [create_ui, configure_styles remain unchanged]

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
        logging.info(f"Progress updated: Level {self.current_level}, XP {self.experience_points}, Progress {self.progress}")

    def handle_submission(self):
        try:
            self.user_response = self.answer_entry.get("1.0", tk.END).strip()
            if not self.user_response:
                messagebox.showwarning("Input Error", "Please provide an answer before submitting.")
                return
            logging.info(f"Submitting response: {self.user_response}")
            self.evaluate_user_response()
            logging.info(f"Submission processed for {self.current_subject} - Question {self.questions_answered}")
        except Exception as e:
            logging.error(f"Submission error: {str(e)}")
            messagebox.showerror("Error", f"Submission failed: {str(e)}")

    # [start_video, stop_video, update_video_frame remain unchanged]

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
            logging.info(f"Session started for {subject} at Level {self.current_level}")
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
            logging.info(f"Loaded question: {self.current_prompt}")
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
            
            logging.info(f"Answer evaluated: Correct={self.is_correct_answer}, Questions={self.questions_answered}")
            
            if self.is_correct_answer:
                self.correct_answers += 1
                xp_gain = 10 * self.current_level
                self.experience_points += xp_gain
                logging.info(f"XP gained: {xp_gain}, Total XP: {self.experience_points}")
                
                # Check for level up
                xp_needed = self.current_level * 50
                if self.experience_points >= xp_needed:
                    self.current_level += 1
                    self.feedback_message += f"\n\nLevel Up! You've reached Level {self.current_level}!"
                    self.user_data[self.current_subject]["level"] = self.current_level
                    logging.info(f"Level up to {self.current_level}")
                
                self.user_data[self.current_subject]["xp"] = self.experience_points
                self.save_user_data()
                self.update_progress_display()
            
            self.show_feedback()
        except Exception as e:
            logging.error(f"Response evaluation error: {str(e)}")
            self.feedback_message = f"Error processing response: {str(e)}"
            self.show_feedback()

    def show_feedback(self):
        self.showing_feedback = True
        self.feedback_title.config(
            text="Well Done!" if self.is_correct_answer else "Let's Review",
            foreground="#2ecc71" if self.is_correct_answer else "#e74c3c"
        )
        self.feedback_text.config(text=self.feedback_message)
        self.feedback_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        logging.info("Showing feedback")

    def continue_to_next_question(self):
        try:
            self.feedback_frame.place_forget()
            self.showing_feedback = False
            self.load_next_question()
            logging.info("Continuing to next question")
        except Exception as e:
            logging.error(f"Continue error: {str(e)}")
            messagebox.showerror("Error", "Failed to load next question")

    # [toggle_speech_recognition, start_speech_recognition, process_speech_result remain unchanged]

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
            logging.info("User data saved")
        except Exception as e:
            logging.error(f"Failed to save user data: {str(e)}")

    def on_closing(self):
        self.stop_video()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# [SpeechRecognizer, QuestionGenerator, NLPAnalyzer classes remain unchanged]

if __name__ == "__main__":
    root = tk.Tk()
    app = GamifiedLearningAssistant(root)
    app.run()
