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

# Download necessary NLTK packages (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class GamifiedLearningAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Gamified Learning Assistant")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
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
        self.speech_recognition_result = ""
        self.questions_answered = 0
        self.correct_answers = 0
        
        # Initialize components
        self.speech_recognizer = SpeechRecognizer()
        self.question_generator = QuestionGenerator()
        self.nlp_analyzer = NLPAnalyzer()
        
        # Load user data
        self.load_user_data()
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(
            main_frame, 
            text="Learning Adventure", 
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        header_label.pack(pady=10)
        
        # AI Tutor icon (using text as placeholder)
        tutor_frame = tk.Frame(
            main_frame, 
            bg="#e6f2ff", 
            width=100, 
            height=100,
            highlightbackground="#3399ff",
            highlightthickness=2,
            borderwidth=0
        )
        tutor_frame.pack(pady=10)
        tutor_frame.pack_propagate(False)
        
        tutor_icon = tk.Label(
            tutor_frame,
            text="🧠",
            font=("Arial", 40),
            bg="#e6f2ff"
        )
        tutor_icon.pack(expand=True)
        
        # Current subject label
        self.subject_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.subject_label.pack(pady=5)
        
        # Progress frame
        self.progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        
        # Level and XP labels
        self.level_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        
        self.xp_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        
        # Interaction frame
        self.interaction_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.interaction_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Question label
        self.question_label = tk.Label(
            self.interaction_frame,
            text="",
            font=("Arial", 12),
            bg="#f5f5f5",
            wraplength=500,
            justify=tk.LEFT,
            relief=tk.GROOVE,
            padx=10,
            pady=10
        )
        
        # Answer entry
        self.answer_entry = tk.Text(
            self.interaction_frame,
            height=4,
            width=50,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        
        # Voice input button
        self.voice_button = tk.Button(
            self.interaction_frame,
            text="🎤 Speak Your Answer",
            command=self.toggle_speech_recognition,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        
        # Submit button
        self.submit_button = tk.Button(
            self.interaction_frame,
            text="Submit Answer",
            command=self.evaluate_user_response,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        
        # Start session button
        self.start_button = tk.Button(
            self.interaction_frame,
            text="Start Learning Session",
            command=self.show_subject_selection,
            bg="#3f51b5",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.start_button.pack(pady=20)
        
        # Feedback frame (initially hidden)
        self.feedback_frame = tk.Frame(
            self.root,
            bg="#333333",
            padx=20,
            pady=20
        )
        
        self.feedback_title = tk.Label(
            self.feedback_frame,
            text="",
            font=("Arial", 16, "bold"),
            bg="#333333",
            fg="#ffffff"
        )
        self.feedback_title.pack(pady=10)
        
        self.feedback_text = tk.Label(
            self.feedback_frame,
            text="",
            font=("Arial", 12),
            bg="#333333",
            fg="#ffffff",
            wraplength=400,
            justify=tk.CENTER
        )
        self.feedback_text.pack(pady=10)
        
        self.continue_button = tk.Button(
            self.feedback_frame,
            text="Continue",
            command=self.continue_to_next_question,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.continue_button.pack(pady=10)
    
    def update_ui_for_session(self):
        if self.is_session_active:
            # Update subject label
            self.subject_label.config(text=f"Current Subject: {self.current_subject}")
            
            # Show progress elements
            self.progress_bar.pack(pady=5)
            self.level_label.pack(pady=2)
            self.xp_label.pack(pady=2)
            
            # Update progress display
            self.progress_bar['value'] = self.progress * 100
            self.level_label.config(text=f"Level {self.current_level}")
            self.xp_label.config(text=f"XP: {self.experience_points}")
            
            # Hide start button, show interaction elements
            self.start_button.pack_forget()
            self.question_label.pack(fill=tk.X, padx=10, pady=10)
            self.answer_entry.pack(fill=tk.X, padx=10, pady=5)
            self.voice_button.pack(pady=5)
            self.submit_button.pack(pady=10)
            
            # Set question text
            self.question_label.config(text=self.current_prompt)
        else:
            # Hide session elements
            self.progress_bar.pack_forget()
            self.level_label.pack_forget()
            self.xp_label.pack_forget()
            self.question_label.pack_forget()
            self.answer_entry.pack_forget()
            self.voice_button.pack_forget()
            self.submit_button.pack_forget()
            
            # Show start button
            self.start_button.pack(pady=20)
            
            # Clear subject
            self.subject_label.config(text="")
    
    def show_subject_selection(self):
        subjects = ["Mathematics", "Science", "History", "Language Arts", "Programming"]
        
        # Create a new top-level window
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select a Subject")
        selection_window.geometry("400x400")
        selection_window.configure(bg="#f0f0f0")
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        # Title
        title_label = tk.Label(
            selection_window,
            text="Select a Subject",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=20)
        
        # Subject buttons
        for subject in subjects:
            subject_button = tk.Button(
                selection_window,
                text=subject,
                command=lambda s=subject: self.start_session(s, selection_window),
                bg="#e6f2ff",
                font=("Arial", 12),
                padx=20,
                pady=10,
                width=20
            )
            subject_button.pack(pady=5)
        
        # Cancel button
        cancel_button = tk.Button(
            selection_window,
            text="Cancel",
            command=selection_window.destroy,
            bg="#f0f0f0",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        cancel_button.pack(pady=20)
    
    def start_session(self, subject, selection_window=None):
        self.current_subject = subject
        self.is_session_active = True
        
        # Load saved level and XP if available
        if subject in self.user_data:
            self.current_level = self.user_data[subject].get("level", 1)
            self.experience_points = self.user_data[subject].get("xp", 0)
        else:
            self.current_level = 1
            self.experience_points = 0
            self.user_data[subject] = {"level": 1, "xp": 0}
        
        # Close selection window if provided
        if selection_window:
            selection_window.destroy()
        
        # Update UI for active session
        self.update_ui_for_session()
        
        # Load first question
        self.load_next_question()
    
    def load_next_question(self):
        question = self.question_generator.generate_question(
            subject=self.current_subject,
            difficulty=self.current_level
        )
        
        self.current_prompt = question["prompt"]
        self.showing_feedback = False
        self.answer_entry.delete("1.0", tk.END)
        self.progress = float(self.questions_answered % 5) / 5.0
        
        # Update UI
        self.question_label.config(text=self.current_prompt)
        self.progress_bar['value'] = self.progress * 100
    
    def evaluate_user_response(self):
        # Get user's answer from text entry
        self.user_response = self.answer_entry.get("1.0", tk.END).strip()
        
        if not self.user_response:
            messagebox.showinfo("Input Required", "Please enter your answer.")
            return
        
        # Analyze response
        analysis_result = self.nlp_analyzer.analyze_response(
            user_response=self.user_response,
            subject=self.current_subject,
            expected_concepts=self.question_generator.get_current_question_concepts()
        )
        
        self.is_correct_answer = analysis_result["is_correct"]
        self.feedback_message = analysis_result["feedback"]
        
        # Update stats
        self.questions_answered += 1
        if self.is_correct_answer:
            self.correct_answers += 1
            self.experience_points += 10 * self.current_level
            
            # Level up check
            if self.experience_points >= self.current_level * 50:
                self.current_level += 1
                self.feedback_message += f"\n\nCongratulations! You've reached Level {self.current_level}!"
                
                # Save progress
                self.user_data[self.current_subject]["level"] = self.current_level
                self.user_data[self.current_subject]["xp"] = self.experience_points
                self.save_user_data()
        
        # Show feedback
        self.show_feedback()
    
    def show_feedback(self):
        self.showing_feedback = True
        
        # Update feedback frame content
        self.feedback_title.config(
            text="Great Job!" if self.is_correct_answer else "Not Quite Right",
            fg="#4CAF50" if self.is_correct_answer else "#FF9800"
        )
        self.feedback_text.config(text=self.feedback_message)
        
        # Show feedback frame
        self.feedback_frame.place(
            relx=0.5, 
            rely=0.5, 
            anchor=tk.CENTER,
            width=500,
            height=300
        )
    
    def continue_to_next_question(self):
        # Hide feedback
        self.feedback_frame.place_forget()
        self.showing_feedback = False
        
        # Load next question
        self.load_next_question()
    
    def toggle_speech_recognition(self):
        if self.is_listening:
            self.speech_recognizer.stop_recording()
            self.voice_button.config(
                text="🎤 Speak Your Answer",
                bg="#4CAF50"
            )
        else:
            self.voice_button.config(
                text="🔴 Listening...",
                bg="#F44336"
            )
            
            # Start recording in a new thread
            threading.Thread(
                target=self.start_speech_recognition,
                daemon=True
            ).start()
        
        self.is_listening = not self.is_listening
    
    def start_speech_recognition(self):
        result = self.speech_recognizer.record()
        
        # Update UI in main thread
        self.root.after(0, lambda: self.process_speech_result(result))
    
    def process_speech_result(self, result):
        if result:
            self.answer_entry.delete("1.0", tk.END)
            self.answer_entry.insert(tk.END, result)
        
        # Reset button state
        self.is_listening = False
        self.voice_button.config(
            text="🎤 Speak Your Answer",
            bg="#4CAF50"
        )
    
    def load_user_data(self):
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Try to load existing data
        try:
            with open('data/user_progress.json', 'r') as f:
                self.user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with empty data if file doesn't exist or is invalid
            self.user_data = {}
    
    def save_user_data(self):
        # Save user data to file
        with open('data/user_progress.json', 'w') as f:
            json.dump(self.user_data, f, indent=2)
    
    def run(self):
        self.root.mainloop()


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_recording = False
    
    def record(self):
        self.is_recording = True
        
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=5.0)
                
                # Convert speech to text
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
        # In a real app, this would load from a database or API
        return {
            "Mathematics": {
                1: [
                    {
                        "prompt": "What is 5 + 7?",
                        "concepts": ["addition", "single digit", "basic math"]
                    },
                    {
                        "prompt": "What is 8 × 4?",
                        "concepts": ["multiplication", "single digit", "basic math"]
                    }
                ],
                2: [
                    {
                        "prompt": "What is the area of a rectangle with length 6 and width 4?",
                        "concepts": ["area", "rectangle", "multiplication"]
                    }
                ],
                3: [
                    {
                        "prompt": "Solve for x: 3x + 2 = 14",
                        "concepts": ["algebra", "equations", "solving for variable"]
                    }
                ],
                4: [
                    {
                        "prompt": "What is the derivative of f(x) = x² + 3x + 2?",
                        "concepts": ["calculus", "derivatives", "polynomial"]
                    }
                ]
            },
            "Science": {
                1: [
                    {
                        "prompt": "What are the three states of matter?",
                        "concepts": ["states of matter", "basic science", "solid", "liquid", "gas"]
                    }
                ],
                2: [
                    {
                        "prompt": "What is photosynthesis?",
                        "concepts": ["photosynthesis", "plants", "biology", "energy"]
                    }
                ],
                3: [
                    {
                        "prompt": "Explain how photosynthesis works.",
                        "concepts": ["photosynthesis", "biology", "plants", "chlorophyll", "carbon dioxide", "water", "sunlight"]
                    }
                ],
                4: [
                    {
                        "prompt": "Describe quantum entanglement.",
                        "concepts": ["quantum physics", "entanglement", "advanced physics", "particles"]
                    }
                ]
            },
            "Programming": {
                1: [
                    {
                        "prompt": "What does the print function do in programming?",
                        "concepts": ["print", "output", "basic programming", "display"]
                    }
                ],
                2: [
                    {
                        "prompt": "What is a variable in programming?",
                        "concepts": ["variable", "data storage", "programming basics"]
                    }
                ],
                3: [
                    {
                        "prompt": "Explain the concept of a for loop.",
                        "concepts": ["loops", "iteration", "control flow", "repetition"]
                    }
                ],
                4: [
                    {
                        "prompt": "Describe how recursion works and provide an example.",
                        "concepts": ["recursion", "functions", "advanced programming", "call stack"]
                    }
                ]
            },
            "History": {
                1: [
                    {
                        "prompt": "Who was the first President of the United States?",
                        "concepts": ["president", "united states", "george washington", "american history"]
                    }
                ]
            },
            "Language Arts": {
                1: [
                    {
                        "prompt": "What is the difference between a noun and a verb?",
                        "concepts": ["noun", "verb", "grammar", "parts of speech"]
                    }
                ]
            }
        }
    
    def generate_question(self, subject, difficulty):
        # Ensure difficulty is within available range
        available_levels = list(self.question_bank.get(subject, {}).keys())
        
        if not available_levels:
            # Default generic question if subject not found
            self.current_question = {
                "prompt": f"Tell me what you know about {subject}.",
                "concepts": [subject, "general knowledge"]
            }
            return self.current_question
        
        # Use highest available difficulty if requested is too high
        actual_difficulty = min(difficulty, max(available_levels))
        
        # Find questions for this difficulty
        questions = self.question_bank[subject][actual_difficulty]
        
        # Select random question
        self.current_question = random.choice(questions)
        return self.current_question
    
    def get_current_question_concepts(self):
        return self.current_question.get("concepts", []) if self.current_question else []


class NLPAnalyzer:
    def __init__(self):
        # Initialize NLP tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text):
        # Tokenize and lemmatize
        tokens = word_tokenize(text.lower())
        return [
            self.lemmatizer.lemmatize(word) 
            for word in tokens 
            if word.isalpha() and word not in self.stop_words
        ]
    
    def analyze_response(self, user_response, subject, expected_concepts):
        # Preprocess user response
        processed_response = self.preprocess_text(user_response)
        
        # Match keywords (basic implementation)
        matched_concepts = []
        for concept in expected_concepts:
            concept_words = self.preprocess_text(concept)
            if any(word in processed_response for word in concept_words):
                matched_concepts.append(concept)
        
        # Calculate match percentage
        match_percentage = len(matched_concepts) / len(expected_concepts) if expected_concepts else 0
        
        # Subject-specific analysis
        if subject == "Mathematics":
            # Check for specific number answers
            if "addition" in expected_concepts and "12" in user_response:
                return {
                    "is_correct": True,
                    "feedback": "That's right! 5 + 7 = 12. Great job with your addition.",
                    "concepts_identified": ["addition", "correct calculation"],
                    "confidence_score": 0.95
                }
            elif "multiplication" in expected_concepts and "32" in user_response:
                return {
                    "is_correct": True,
                    "feedback": "Correct! 8 × 4 = 32. You're good at multiplication!",
                    "concepts_identified": ["multiplication", "correct calculation"],
                    "confidence_score": 0.95
                }
            elif "area" in expected_concepts and "24" in user_response:
                return {
                    "is_correct": True,
                    "feedback": "That's right! The area is length × width = 6 × 4 = 24 square units.",
                    "concepts_identified": ["area", "correct calculation"],
                    "confidence_score": 0.9
                }
            elif "algebra" in expected_concepts and ("4" in user_response or "x = 4" in user_response.lower()):
                return {
                    "is_correct": True,
                    "feedback": "Correct! 3x + 2 = 14 means x = 4. Good algebra skills!",
                    "concepts_identified": ["algebra", "equation solving"],
                    "confidence_score": 0.9
                }
            elif "calculus" in expected_concepts and "2x + 3" in user_response:
                return {
                    "is_correct": True,
                    "feedback": "Excellent! The derivative of f(x) = x² + 3x + 2 is indeed 2x + 3.",
                    "concepts_identified": ["calculus", "derivatives"],
                    "confidence_score": 0.95
                }
        
        elif subject == "Science":
            if "states of matter" in expected_concepts:
                if all(state in user_response.lower() for state in ["solid", "liquid", "gas"]):
                    return {
                        "is_correct": True,
                        "feedback": "Correct! The three states of matter are solid, liquid, and gas.",
                        "concepts_identified": ["states of matter"],
                        "confidence_score": 0.95
                    }
            elif "photosynthesis" in expected_concepts:
                photosynthesis_keywords = ["light", "sunlight", "carbon dioxide", "water", "chlorophyll", "oxygen"]
                if sum(keyword in user_response.lower() for keyword in photosynthesis_keywords) >= 3:
                    return {
                        "is_correct": True,
                        "feedback": "Great explanation of photosynthesis! You correctly identified how plants use light, carbon dioxide, and water to create energy.",
                        "concepts_identified": ["photosynthesis", "plant biology"],
                        "confidence_score": 0.85
                    }
        
        elif subject == "Programming":
            if "print" in expected_concepts:
                output_keywords = ["output", "display", "screen", "console", "show"]
                if any(keyword in user_response.lower() for keyword in output_keywords):
                    return {
                        "is_correct": True,
                        "feedback": "That's right! The print function outputs or displays information to the user.",
                        "concepts_identified": ["output", "basic programming"],
                        "confidence_score": 0.9
                    }
            elif "loops" in expected_concepts:
                loop_keywords = ["repeat", "iteration", "iterative", "multiple times", "cycle"]
                if any(keyword in user_response.lower() for keyword in loop_keywords):
                    return {
                        "is_correct": True,
                        "feedback": "Good explanation of for loops! They're used to repeat operations for iteration.",
                        "concepts_identified": ["loops", "iteration"],
                        "confidence_score": 0.85
                    }
        
        # Generic evaluation based on concept matching
        if match_percentage >= 0.7:
            return {
                "is_correct": True,
                "feedback": f"Great answer! You covered {len(matched_concepts)} out of {len(expected_concepts)} key concepts.",
                "concepts_identified": matched_concepts,
                "confidence_score": match_percentage
            }
        else:
            # Generic incorrect response
            return {
                "is_correct": False,
                "feedback": f"That's not quite right. Let's try to understand the concept better. The key points to consider are: {', '.join(expected_concepts)}.",
                "concepts_identified": matched_concepts,
                "confidence_score": match_percentage
            }


if __name__ == "__main__":
    root = tk.Tk()
    app = GamifiedLearningAssistant(root)
    app.run()
