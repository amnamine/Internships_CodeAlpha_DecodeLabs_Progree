import re
import random
import math

class ChatbotRuleEngine:
    def __init__(self):
        # Conversational state variables
        self.state = {
            "user_name": None,
            "session_turns": 0,
            "current_mode": "chat",  # modes: chat, game, riddle, math
            "mood": "neutral",       # mood of the user: happy, sad, angry, bored, neutral
            # Riddle mode state
            "current_riddle_index": 0,
            "riddle_attempts": 0,
            # Text adventure game state
            "game_room": "entrance",
            "game_inventory": [],
            "game_health": 100,
            "game_turns": 0
        }

        # Riddles Database
        self.riddles = [
            {
                "riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
                "answers": ["echo", "an echo"],
                "hint": "Think of what happens when you shout in a large, empty cave."
            },
            {
                "riddle": "The more of them you take, the more you leave behind. What are they?",
                "answers": ["footsteps", "footstep", "steps", "step"],
                "hint": "You make them when you walk."
            },
            {
                "riddle": "What has keys but can't open locks?",
                "answers": ["piano", "a piano", "keyboard", "a keyboard"],
                "hint": "It plays beautiful music, or you use it to type code."
            },
            {
                "riddle": "What is full of holes but still holds water?",
                "answers": ["sponge", "a sponge"],
                "hint": "You find it in the kitchen or bathroom, soaking up liquids."
            },
            {
                "riddle": "I am not alive, but I grow; I don't have lungs, but I need air; I don't have a mouth, but water kills me. What am I?",
                "answers": ["fire", "a fire", "flame"],
                "hint": "It warms you up in winter but burns things down."
            }
        ]

    def reset_state(self):
        """Reset state attributes back to initial values."""
        self.state["user_name"] = None
        self.state["session_turns"] = 0
        self.state["current_mode"] = "chat"
        self.state["mood"] = "neutral"
        self.state["current_riddle_index"] = 0
        self.state["riddle_attempts"] = 0
        self.state["game_room"] = "entrance"
        self.state["game_inventory"] = []
        self.state["game_health"] = 100
        self.state["game_turns"] = 0

    def preprocess_input(self, text):
        """Cleans and standardizes input for better matching."""
        text = text.lower().strip()
        # Remove common punctuation marks
        text = re.sub(r"[?.!,;:]", "", text)
        return text

    def get_response(self, raw_input):
        """Main routing engine utilizing rule hierarchies to select a response."""
        self.state["session_turns"] += 1
        clean_input = self.preprocess_input(raw_input)
        
        # 1. State-Specific Overrides (Game, Riddle Modes)
        if self.state["current_mode"] == "game":
            return self._handle_game_mode(clean_input)
        elif self.state["current_mode"] == "riddle":
            return self._handle_riddle_mode(clean_input)

        # 2. Emotional / Sentiment Detector (runs continuously)
        self._detect_sentiment(clean_input)

        # 3. Dynamic Mode Switches
        if any(w in clean_input for w in ["play game", "start game", "text adventure", "play a game"]):
            self.state["current_mode"] = "game"
            self.state["game_room"] = "entrance"
            self.state["game_inventory"] = []
            self.state["game_health"] = 100
            self.state["game_turns"] = 0
            return (
                "🎮 **Text Adventure Activated!** 🎮\n\n"
                "You find yourself standing at the entrance of a mysterious obsidian temple. "
                "The air is cold, and you see two passages: one leading **north** into darkness, "
                "and another leading **east** where a strange green light glows. "
                "What will you do? (Type 'north', 'east', 'look', or 'inventory')"
            )
        
        if any(w in clean_input for w in ["riddle", "ask me a riddle", "give me a riddle", "play riddles"]):
            self.state["current_mode"] = "riddle"
            self.state["current_riddle_index"] = random.randint(0, len(self.riddles) - 1)
            self.state["riddle_attempts"] = 0
            return (
                "🧠 **Riddle Mode Activated!** 🧠\n\n"
                "I will give you a riddle. Try to guess it! You can type **'hint'** for a hint or **'exit'** to quit.\n\n"
                f"**Riddle:** {self.riddles[self.state['current_riddle_index']]['riddle']}"
            )

        # 4. Master If-Elif-Else Decision Hierarchy (Pseudo-LLM Interface)

        # GREETINGS & INTRODUCTIONS
        if clean_input in ["hello", "hi", "hey", "greetings", "yo", "sup", "hola"]:
            greetings = [
                "Hello! I am Antigravity Chatbot. How can I assist you today?",
                "Hi there! Nice to meet you. What's on your mind?",
                "Greetings! I'm ready to chat. Ask me anything, or let's play a game!",
                "Hey! Hope you are having an amazing day. How can I help you?"
            ]
            return random.choice(greetings)

        elif "my name is" in clean_input or "call me" in clean_input:
            match = re.search(r"(?:my name is|call me)\s+(\w+)", clean_input)
            if match:
                self.state["user_name"] = match.group(1).capitalize()
                return f"Nice to meet you, {self.state['user_name']}! I will remember that. What should we explore next?"
            else:
                return "I couldn't quite catch your name. Could you say 'My name is [your name]'?"

        elif "what is my name" in clean_input or "do you know my name" in clean_input:
            if self.state["user_name"]:
                return f"Of course! Your name is {self.state['user_name']}. How are you doing today?"
            else:
                return "I don't know your name yet! What should I call you? (e.g., 'My name is Alice')"

        # IDENTITY & BOT INFOS
        elif "who are you" in clean_input or "what is your name" in clean_input:
            return (
                "I am **Antigravity Chatbot**, a highly advanced, rules-driven computational conversation partner. "
                "While I don't use a machine learning model, my logic consists of complex rules designed to "
                "emulate an intelligent LLM. I can write code snippets, solve math, play games, tell facts, and more!"
            )

        elif "who created you" in clean_input or "who made you" in clean_input:
            return "I was created by a talented developer using Python and Tkinter for a professional-grade software assignment."

        elif "how do you work" in clean_input or "are you an ai" in clean_input or "are you an llm" in clean_input:
            return (
                "I do not use a neural network or API calls. Instead, I process inputs using lexical analysis, "
                "state flowcharts, and a massive hierarchy of complex conditional pathways (`if-elif-else` rules). "
                "This keeps me fast, lightweight, and completely deterministic, yet responsive like an LLM!"
            )

        # CODING ASSISTANCE (Python, Web, JS)
        elif "python" in clean_input and ("code" in clean_input or "example" in clean_input or "how to" in clean_input):
            return (
                "🐍 **Python Code Assistant** 🐍\n\n"
                "Here is how you write a clean function with a docstring and type hinting in Python:\n\n"
                "```python\n"
                "def calculate_factorial(n: int) -> int:\n"
                "    \"\"\"Calculate the factorial of a non-negative integer.\"\"\"\n"
                "    if n < 0:\n"
                "        raise ValueError('Factorial is not defined for negative numbers')\n"
                "    return 1 if n <= 1 else n * calculate_factorial(n - 1)\n\n"
                "# Example usage:\n"
                "print(calculate_factorial(5)) # Output: 120\n"
                "```\n"
                "Python is renowned for readability. Let me know if you need help with list comprehensions or OOP!"
            )

        elif ("javascript" in clean_input or "js" in clean_input) and ("code" in clean_input or "example" in clean_input):
            return (
                "🌐 **JavaScript Assistant** 🌐\n\n"
                "Here is an asynchronous fetch helper using modern ES6+ `async/await` syntax:\n\n"
                "```javascript\n"
                "async function fetchData(url) {\n"
                "  try {\n"
                "    const response = await fetch(url);\n"
                "    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);\n"
                "    const data = await response.json();\n"
                "    return data;\n"
                "  } catch (error) {\n"
                "    console.error('Fetch failed:', error);\n"
                "  }\n"
                "}\n"
                "```\n"
                "JavaScript is asynchronous and single-threaded. Let me know if you want DOM manipulation or event handling tips!"
            )

        elif "html" in clean_input and "css" in clean_input:
            return (
                "🎨 **Web Design Structure** 🎨\n\n"
                "Here is a responsive centered grid card module using HTML & CSS:\n\n"
                "```html\n"
                "<div class='card-container'>\n"
                "  <div class='card'>\n"
                "    <h2>Aesthetic Design</h2>\n"
                "    <p>Premium UI/UX is built on consistent padding and clean font hierarchies.</p>\n"
                "  </div>\n"
                "</div>\n"
                "```\n"
                "```css\n"
                ".card-container {\n"
                "  display: grid;\n"
                "  place-items: center;\n"
                "  min-height: 200px;\n"
                "}\n"
                ".card {\n"
                "  background: linear-gradient(135deg, #1e1e2f, #252540);\n"
                "  border-radius: 12px;\n"
                "  border: 1px solid rgba(255, 255, 255, 0.1);\n"
                "  padding: 24px;\n"
                "  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);\n"
                "}\n"
                "```"
            )

        # UTILITIES: MATH & CALCULATOR
        elif "calculate" in clean_input or "solve" in clean_input or "math" in clean_input:
            # Try to parse expressions like: solve 5 * 10 or calculate 20 / 4
            expr_match = re.search(r"(?:calculate|solve|what is)\s+([\d+\-*/\s().]+)", clean_input)
            if expr_match:
                expr = expr_match.group(1).strip()
                try:
                    # Safe evaluation of basic mathematical strings
                    if re.match(r"^[\d+\-*/\s().]+$", expr):
                        result = eval(expr)
                        return f"🔢 **Math Calculator**\n\nThe result of `{expr}` is **{result}**."
                    else:
                        return "I can only evaluate basic expressions containing numbers, parentheses, and arithmetic operators (+, -, *, /)."
                except Exception:
                    return "Sorry, I couldn't evaluate that math expression. Please check if it's formatted correctly (e.g., 'calculate 15 * (4 + 2)')."
            else:
                return (
                    "I have a built-in math solver! Try typing:\n"
                    "- *'calculate 25 * 4 + 100'*\n"
                    "- *'solve (45 - 5) / 2'*"
                )

        # INTERESTING FACTS & DATABASE LOOKUPS
        elif "fact" in clean_input or "tell me something interesting" in clean_input:
            facts = [
                "🌌 **Space Fact:** One day on Venus is longer than one year on Venus. It takes Venus 243 Earth days to rotate once on its axis, but only 225 Earth days to travel around the sun.",
                "🦖 **History Fact:** Cleopatra lived closer in time to the Moon landings than she did to the construction of the Great Pyramid of Giza.",
                "🐙 **Biology Fact:** Octopuses have three hearts, nine brains, and blue blood.",
                "🍌 **Botanical Fact:** Bananas are berries, but strawberries are not!",
                "💻 **Computing Fact:** The first computer bug was a real moth found trapped in a relay by computer pioneer Grace Hopper in 1947."
            ]
            return random.choice(facts)

        elif "quote" in clean_input or "motivation" in clean_input:
            quotes = [
                "✨ *'The only way to do great work is to love what you do.'* — Steve Jobs",
                "🌟 *'Believe you can and you're halfway there.'* — Theodore Roosevelt",
                "⚡ *'Success is not final, failure is not fatal: it is the courage to continue that counts.'* — Winston Churchill",
                "🎨 *'Creativity is intelligence having fun.'* — Albert Einstein",
                "🚀 *'Do not wait to strike till the iron is hot; but make it hot by striking.'* — William Butler Yeats"
            ]
            return random.choice(quotes)

        elif "joke" in clean_input or "tell me a joke" in clean_input:
            jokes = [
                "Why do programmers wear glasses?\n\nBecause they can't C#!",
                "How many programmers does it take to change a light bulb?\n\nNone, that's a hardware problem!",
                "Why did the database administrator leave his wife?\n\nShe had one-to-many relationships.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "What is a programmer's favorite hangout place?\n\nfoo bar!"
            ]
            return random.choice(jokes)

        # USER SENTIMENT ADAPTIVE ANSWERS
        elif self.state["mood"] == "sad":
            cheer_ups = [
                "I noticed you might be feeling down. Remember that it's okay to feel this way. Want to hear a joke or play a riddle game to distract you?",
                "I'm here for you! Life can be tough sometimes, but you're doing great. Tell me what's on your mind.",
                "Sending you positive digital vibes! ✨ If you want, we can do some coding or just talk about space facts."
            ]
            # Reset mood so we don't spam comforting messages
            self.state["mood"] = "neutral"
            return random.choice(cheer_ups)

        elif self.state["mood"] == "angry":
            calm_downs = [
                "I hear you, and I understand you're frustrated. Let's take a deep breath. How can I help resolve this with you?",
                "I apologize if I said something incorrect. I am a rule-based engine, and sometimes my logic might be limited. Let's try again!",
                "Take it easy! I'm just code, but I want to make this chat pleasant. What can we do to turn things around?"
            ]
            self.state["mood"] = "neutral"
            return random.choice(calm_downs)

        # GENERAL CONVERSATIONAL FILLERS / LLM EMULATION
        elif "help" in clean_input or "capabilities" in clean_input or "what can you do" in clean_input:
            return (
                "🔧 **Antigravity Chatbot Capabilities Menu** 🔧\n\n"
                "I can perform a wide range of interactive tasks. Try saying:\n"
                "- 🎮 **'Play game'** to enter a state-based adventure game.\n"
                "- 🧠 **'Ask me a riddle'** to play a trivia puzzle.\n"
                "- 🐍 **'Python code example'** to view coding syntax blocks.\n"
                "- 🔢 **'Calculate 20 + (50 * 3)'** to use my arithmetic solver.\n"
                "- 🌌 **'Tell me a fact'** to learn trivia.\n"
                "- ⚡ **'Give me motivation'** for inspiring quotes."
            )
        
        elif "thank" in clean_input or "thanks" in clean_input:
            return "You are very welcome! Helping you is my top priority. What's next?"

        elif "bye" in clean_input or "goodbye" in clean_input or "exit" in clean_input:
            return "Goodbye! It was a pleasure chatting. Feel free to launch me anytime you need assistant!"

        # FALLBACK / SMART SUGGESTIONS
        else:
            fallbacks = [
                "That's an interesting point! While I don't fully understand that, did you know I can assist with Python code, do math operations, or play interactive text adventures? Type 'help' to see my commands.",
                "Hmm, my rule-based matrix didn't find a direct correlation for that input. Could you rephrase it, or would you like to hear an interesting space fact?",
                "I am listening! But my current keywords don't match that exact phrasing. Try asking me to 'tell a joke' or 'ask a riddle'!",
                "I am processing your input... 🧠 It seems outside my standard syntax dictionary. Type 'help' to get a list of topics I excel at!"
            ]
            return random.choice(fallbacks)

    def _detect_sentiment(self, text):
        """Analyzes string for emotional markers and adjusts bot mood state."""
        sad_keywords = ["sad", "depressed", "unhappy", "cry", "lonely", "hate my", "bad day", "hurt"]
        angry_keywords = ["angry", "mad", "pissed", "shut up", "stupid bot", "hate you", "useless", "garbage"]
        happy_keywords = ["happy", "excited", "glad", "awesome", "great", "wonderful", "cool", "nice"]

        if any(w in text for w in sad_keywords):
            self.state["mood"] = "sad"
        elif any(w in text for w in angry_keywords):
            self.state["mood"] = "angry"
        elif any(w in text for w in happy_keywords):
            self.state["mood"] = "happy"

    def _handle_riddle_mode(self, clean_input):
        """Dedicated riddle logic loop."""
        riddle_data = self.riddles[self.state["current_riddle_index"]]
        
        if "exit" in clean_input or "quit" in clean_input:
            self.state["current_mode"] = "chat"
            return "Exiting Riddle Mode. Back to general chat! How can I help you now?"
        
        if "hint" in clean_input:
            return f"💡 **Hint:** {riddle_data['hint']}"

        # Check answers
        if any(ans in clean_input for ans in riddle_data["answers"]):
            self.state["current_mode"] = "chat"
            return (
                "🎉 **Correct!** 🎉\n\n"
                f"You got it! The answer was indeed **{riddle_data['answers'][0].upper()}**.\n"
                "Riddle mode completed successfully. Returning to main chat."
            )
        else:
            self.state["riddle_attempts"] += 1
            if self.state["riddle_attempts"] >= 3:
                self.state["current_mode"] = "chat"
                return (
                    "❌ **Three incorrect attempts!** ❌\n\n"
                    f"The correct answer was **{riddle_data['answers'][0].upper()}**.\n"
                    "Let's go back to standard chat. Type 'ask a riddle' if you want to try a new one!"
                )
            else:
                return f"Hmm, that's not it. Try again! (Attempts: {self.state['riddle_attempts']}/3). Type 'hint' if you are stuck."

    def _handle_game_mode(self, clean_input):
        """Dedicated state-machine for text adventure game."""
        self.state["game_turns"] += 1
        
        if "exit" in clean_input or "quit" in clean_input:
            self.state["current_mode"] = "chat"
            return "Exiting Text Adventure. Back to general chat!"

        room = self.state["game_room"]
        inventory = self.state["game_inventory"]

        if room == "entrance":
            if "north" in clean_input:
                self.state["game_room"] = "dark_hall"
                return (
                    "🚶‍♂️ You walk north into the dark hallway. "
                    "You hear dripping water. Suddenly, you stumble upon a shiny **silver key** lying on a pedestal. "
                    "To the north is a heavy **iron door**. To the south is the temple entrance. "
                    "What will you do? (Type 'take key', 'north', 'south')"
                )
            elif "east" in clean_input:
                self.state["game_room"] = "glowing_chamber"
                return (
                    "🚶‍♂️ You step east into the chamber with the green light. "
                    "An ancient stone altar holds a golden goblet filled with a glowing **elixir**. "
                    "A massive sleeping **stone golem** lies nearby. "
                    "What will you do? (Type 'take elixir', 'west')"
                )
            elif "look" in clean_input:
                return "You see the dark path to the north, the glowing chamber to the east, and the wilderness behind you to the south."
            else:
                return "Invalid direction. You can go 'north' or 'east'."

        elif room == "dark_hall":
            if "take key" in clean_input or "grab key" in clean_input:
                if "key" not in inventory:
                    inventory.append("key")
                    return "🗝️ You picked up the silver key. What now? (Type 'north' or 'south')"
                return "You already have the key."
            elif "north" in clean_input:
                if "key" in inventory:
                    self.state["current_mode"] = "chat"
                    return (
                        "🎉 **Victory!** 🎉\n\n"
                        "You unlock the heavy iron door with the silver key. "
                        "Inside, you find a treasure chest filled with gold coins and mystical artifacts! "
                        "You have successfully beaten the text adventure game! Returning to main chat."
                    )
                else:
                    return "🔒 The heavy iron door is locked. You need a key to open it. (Type 'south' to go back)"
            elif "south" in clean_input:
                self.state["game_room"] = "entrance"
                return "Back at the temple entrance. You can go 'north' or 'east'."
            else:
                return "You can 'take key', go 'north' to the door, or 'south' to the entrance."

        elif room == "glowing_chamber":
            if "take elixir" in clean_input or "drink elixir" in clean_input:
                self.state["current_mode"] = "chat"
                return (
                    "💀 **Game Over!** 💀\n\n"
                    "As you grab the elixir, the stone golem awakens with a roar! "
                    "It slams its giant fist down, trapping you. "
                    "Perhaps taking mysterious glowing items from sleeping giants wasn't wise! "
                    "Returning to chat mode."
                )
            elif "west" in clean_input:
                self.state["game_room"] = "entrance"
                return "Back at the temple entrance. You can go 'north' or 'east'."
            else:
                return "You can 'take elixir' (risky) or go 'west' back to the entrance."

        return "Unknown command in text adventure. Type 'exit' to quit."
