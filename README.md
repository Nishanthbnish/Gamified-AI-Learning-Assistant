---

### **📌 Gamified AI Learning Assistant - Setup Instructions**  

---

## **🚀 Install Python**
- Download and install Python from [python.org](https://www.python.org/) (**Python 3.7+ recommended**).  
- Make sure to check **"Add Python to PATH"** during installation.

---

## **📂 Create a Project Directory**
1. Create a new folder for your project.  
2. Open a terminal/command prompt and navigate to this folder.

---

## **📦 Install Required Libraries**
Run the following command to install the necessary packages:  
```bash
pip install nltk SpeechRecognition PyAudio
```
**⚠️ PyAudio Installation Issues? Try these fixes:**  
- **Windows:**  
  ```bash
  pip install pipwin  
  pipwin install pyaudio  
  ```
- **macOS:**  
  ```bash
  brew install portaudio  
  pip install pyaudio  
  ```
- **Linux (Ubuntu/Debian):**  
  ```bash
  sudo apt-get install python3-pyaudio  
  ```

---

## **📜 Create Python File**
1. Create a new file named **`gamified_learning_assistant.py`**.  
2. Copy and paste the entire code from your code artifact into this file.

---

## **▶️ Run the Application**
Execute the script using:  
```bash
python gamified_learning_assistant.py
```
✅ The application should open in a new window.

---

## **🔹 Important Notes**  

### **🛠 First-time Setup**
- The first time you run the application, it will download **NLTK data packages** (`punkt`, `stopwords`, and `wordnet`).  
- This might take a few moments but happens **only once**.

### **🎤 Speech Recognition**
- The app uses your **microphone** for speech recognition.  
- Ensure your **microphone is properly connected** and **permissions are granted**.  
- An **internet connection** is required for **Google Speech Recognition**.

### **💾 User Data Storage**
- Your progress is stored in a **JSON file** inside a `data` folder.  
- This folder is **automatically created** in the same directory as the script.

---

## **❗ Troubleshooting**
- **Microphone Issues?** Check your **microphone settings** and **permissions**.  
- **PyAudio Error?** Try the alternative installation methods listed above.  

---

## **✨ Application Features**
✔ **Subject Selection:** Choose from Mathematics, Science, History, Language Arts, or Programming.  
✔ **Adaptive Difficulty:** Questions adjust based on your skill level.  
✔ **Voice Input:** Answer questions verbally using your microphone.  
✔ **Progress Tracking:** Saves your experience points and level.  
✔ **Gamification:** Earn XP and level up as you answer correctly.  
✔ **NLP Analysis:** Uses **Natural Language Processing** to analyze responses.

📌 _This project uses a simple NLP implementation. For production, consider integrating advanced NLP models like OpenAI’s GPT for better answer analysis._

---

**💡 Enjoy your learning journey! 🚀**  

Would you like any additional changes? 😊
