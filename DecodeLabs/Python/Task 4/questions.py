"""
Question Bank for General Knowledge Quiz
Contains rich, easy-to-understand questions across diverse categories.
"""

QUESTIONS = [
    # Geography
    {
        "id": 1,
        "category": "Geography",
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "answer": "Paris",
        "explanation": "Paris has been the capital of France since 987 AD and is known as the City of Light.",
        "hint": "It is famous for the Eiffel Tower!"
    },
    {
        "id": 2,
        "category": "Geography",
        "question": "Which is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"],
        "answer": "Pacific Ocean",
        "explanation": "The Pacific Ocean covers over 30% of Earth's total surface area.",
        "hint": "Its name means 'peaceful'."
    },
    {
        "id": 3,
        "category": "Geography",
        "question": "In which country can you find the Pyramids of Giza?",
        "options": ["Mexico", "Egypt", "Greece", "Peru"],
        "answer": "Egypt",
        "explanation": "The Great Pyramid of Giza is the oldest of the Seven Wonders of the Ancient World.",
        "hint": "Think of Pharaohs and the River Nile!"
    },
    {
        "id": 4,
        "category": "Geography",
        "question": "What is the smallest country in the world by area?",
        "options": ["Monaco", "Vatican City", "San Marino", "Liechtenstein"],
        "answer": "Vatican City",
        "explanation": "Vatican City measures just 0.49 square kilometers (0.19 sq miles).",
        "hint": "It is located completely inside the city of Rome."
    },
    {
        "id": 5,
        "category": "Geography",
        "question": "Which continent is known as the 'Land Down Under'?",
        "options": ["Africa", "South America", "Australia", "Antarctica"],
        "answer": "Australia",
        "explanation": "Australia is called the 'Land Down Under' because it lies entirely in the Southern Hemisphere.",
        "hint": "Home to kangaroos and koalas!"
    },
    {
        "id": 6,
        "category": "Geography",
        "question": "What river is the longest in the world?",
        "options": ["Amazon River", "Nile River", "Mississippi River", "Yangtze River"],
        "answer": "Nile River",
        "explanation": "The Nile flows northwards through northeastern Africa for approximately 6,650 km.",
        "hint": "It flows through Egypt into the Mediterranean."
    },
    {
        "id": 7,
        "category": "Geography",
        "question": "What is the capital city of Japan?",
        "options": ["Kyoto", "Osaka", "Tokyo", "Hiroshima"],
        "answer": "Tokyo",
        "explanation": "Tokyo is the world's most populous metropolitan area.",
        "hint": "Host of the 2020 Summer Olympics!"
    },

    # Science & Nature
    {
        "id": 8,
        "category": "Science & Nature",
        "question": "What gas do plants absorb from the atmosphere for photosynthesis?",
        "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
        "answer": "Carbon Dioxide",
        "explanation": "Plants take in Carbon Dioxide ($CO_2$) and release Oxygen ($O_2$).",
        "hint": "It is what humans exhale."
    },
    {
        "id": 9,
        "category": "Science & Nature",
        "question": "What is the chemical symbol for Gold?",
        "options": ["Go", "Ag", "Au", "Fe"],
        "answer": "Au",
        "explanation": "Au comes from the Latin word for gold, 'Aurum', meaning shining dawn.",
        "hint": "Starts with 'A'!"
    },
    {
        "id": 10,
        "category": "Science & Nature",
        "question": "How many planets are in our Solar System?",
        "options": ["7", "8", "9", "10"],
        "answer": "8",
        "explanation": "Since Pluto was reclassified as a dwarf planet in 2006, our solar system officially has 8 planets.",
        "hint": "Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune."
    },
    {
        "id": 11,
        "category": "Science & Nature",
        "question": "What is the hardest natural substance on Earth?",
        "options": ["Gold", "Iron", "Diamond", "Titanium"],
        "answer": "Diamond",
        "explanation": "Diamond scores a maximum 10 on the Mohs scale of mineral hardness.",
        "hint": "Made of pure carbon under extreme pressure."
    },
    {
        "id": 12,
        "category": "Science & Nature",
        "question": "Which organ in the human body pumps blood?",
        "options": ["Brain", "Lungs", "Liver", "Heart"],
        "answer": "Heart",
        "explanation": "The human heart beats about 100,000 times a day to pump blood throughout the body.",
        "hint": "It is in your chest!"
    },
    {
        "id": 13,
        "category": "Science & Nature",
        "question": "What color are flamingos born with naturally?",
        "options": ["Pink", "Grey", "White", "Orange"],
        "answer": "Grey",
        "explanation": "Flamingos are born grey/white; their diet of shrimp and algae turns them pink!",
        "hint": "They aren't born pink!"
    },
    {
        "id": 14,
        "category": "Science & Nature",
        "question": "Which metal is liquid at room temperature?",
        "options": ["Mercury", "Lead", "Silver", "Copper"],
        "answer": "Mercury",
        "explanation": "Mercury (element symbol Hg) has a melting point of -38.83 °C.",
        "hint": "Used in old-fashioned glass thermometers."
    },

    # History & Culture
    {
        "id": 15,
        "category": "History & Culture",
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Claude Monet"],
        "answer": "Leonardo da Vinci",
        "explanation": "Leonardo da Vinci painted the Mona Lisa in the early 16th century.",
        "hint": "Italian Renaissance polymath and master artist."
    },
    {
        "id": 16,
        "category": "History & Culture",
        "question": "In which year did the Titanic sink?",
        "options": ["1905", "1912", "1920", "1939"],
        "answer": "1912",
        "explanation": "The RMS Titanic hit an iceberg and sank on April 15, 1912.",
        "hint": "Just before World War I."
    },
    {
        "id": 17,
        "category": "History & Culture",
        "question": "Who was the first person to step on the Moon?",
        "options": ["Buzz Aldrin", "Yuri Gagarin", "Neil Armstrong", "Michael Collins"],
        "answer": "Neil Armstrong",
        "explanation": "Neil Armstrong stepped onto the Moon on July 20, 1969, saying 'That's one small step for man...'",
        "hint": "Commander of Apollo 11."
    },
    {
        "id": 18,
        "category": "History & Culture",
        "question": "Which ancient civilization built the Colosseum in Rome?",
        "options": ["Greeks", "Romans", "Egyptians", "Persians"],
        "answer": "Romans",
        "explanation": "The Colosseum was constructed by the Roman Empire around 70-80 AD.",
        "hint": "It is located in Italy!"
    },

    # Pop Culture & Entertainment
    {
        "id": 19,
        "category": "Pop Culture & Entertainment",
        "question": "What is the name of Mickey Mouse's pet dog?",
        "options": ["Goofy", "Pluto", "Snoopy", "Buster"],
        "answer": "Pluto",
        "explanation": "Pluto is Mickey's loyal pet dog created by Walt Disney Productions.",
        "hint": "Shares its name with a dwarf planet!"
    },
    {
        "id": 20,
        "category": "Pop Culture & Entertainment",
        "question": "Which superhero is also known as the 'Dark Knight'?",
        "options": ["Superman", "Spider-Man", "Batman", "Iron Man"],
        "answer": "Batman",
        "explanation": "Batman protects Gotham City as the Dark Knight.",
        "hint": "He wears a cowl with bat ears!"
    },
    {
        "id": 21,
        "category": "Pop Culture & Entertainment",
        "question": "In Harry Potter, what house does Harry belong to?",
        "options": ["Slytherin", "Hufflepuff", "Ravenclaw", "Gryffindor"],
        "answer": "Gryffindor",
        "explanation": "The Sorting Hat placed Harry Potter in Gryffindor, known for bravery.",
        "hint": "The mascot is a golden lion!"
    },
    {
        "id": 22,
        "category": "Pop Culture & Entertainment",
        "question": "Which animated movie features the famous song 'Let It Go'?",
        "options": ["Moana", "Tangled", "Frozen", "Brave"],
        "answer": "Frozen",
        "explanation": "'Let It Go' was sung by Queen Elsa (Idina Menzel) in Disney's Frozen (2013).",
        "hint": "Features Queen Elsa and Olaf the Snowman!"
    },
    {
        "id": 23,
        "category": "Pop Culture & Entertainment",
        "question": "What flavor is the drink Sprite?",
        "options": ["Orange", "Lemon-Lime", "Cola", "Grape"],
        "answer": "Lemon-Lime",
        "explanation": "Sprite is a crisp, clear lemon-lime flavored carbonated soft drink.",
        "hint": "A green can with citrus taste!"
    },

    # Sports & Games
    {
        "id": 24,
        "category": "Sports & Games",
        "question": "How many players are on the field for one team in a standard soccer (football) match?",
        "options": ["9", "10", "11", "12"],
        "answer": "11",
        "explanation": "Each soccer team fields 11 players including 1 goalkeeper.",
        "hint": "10 outfield players + 1 goalkeeper."
    },
    {
        "id": 25,
        "category": "Sports & Games",
        "question": "How many rings are on the official Olympic flag?",
        "options": ["4", "5", "6", "7"],
        "answer": "5",
        "explanation": "The 5 rings represent the five inhabited continents of the world.",
        "hint": "Blue, yellow, black, green, and red!"
    },
    {
        "id": 26,
        "category": "Sports & Games",
        "question": "What sport is played at Wimbledon?",
        "options": ["Golf", "Cricket", "Tennis", "Polo"],
        "answer": "Tennis",
        "explanation": "Wimbledon is the oldest tennis tournament in the world, founded in 1877.",
        "hint": "Played on grass courts with rackets."
    },
    {
        "id": 27,
        "category": "Sports & Games",
        "question": "In bowling, what is it called when you knock down all 10 pins on your first roll?",
        "options": ["Spare", "Strike", "Turkey", "Gutter"],
        "answer": "Strike",
        "explanation": "A strike scores 10 points plus the total pins knocked down on the next two rolls.",
        "hint": "Represented by an 'X' on the scoreboard!"
    },

    # Food & Cuisine
    {
        "id": 28,
        "category": "Food & Cuisine",
        "question": "Which country is famous for inventing Pizza and Pasta?",
        "options": ["France", "Spain", "Italy", "Greece"],
        "answer": "Italy",
        "explanation": "Modern pizza originated in Naples, Italy, and pasta has been an Italian staple for centuries.",
        "hint": "Boot-shaped country in Europe!"
    },
    {
        "id": 29,
        "category": "Food & Cuisine",
        "question": "What fruit is known for having its seeds on the outside?",
        "options": ["Banana", "Strawberry", "Apple", "Peach"],
        "answer": "Strawberry",
        "explanation": "Strawberries are unique because their small yellow seeds cover the exterior skin.",
        "hint": "Red, heart-shaped sweet berry!"
    },
    {
        "id": 30,
        "category": "Food & Cuisine",
        "question": "What is the main ingredient in guacamole?",
        "options": ["Tomato", "Avocado", "Cucumber", "Onion"],
        "answer": "Avocado",
        "explanation": "Guacamole is a creamy Mexican dip traditionally made with mashed ripe avocados.",
        "hint": "A creamy green fruit!"
    }
]

def get_categories():
    """Returns list of unique categories."""
    cats = sorted(list(set(q["category"] for q in QUESTIONS)))
    return ["All Categories"] + cats

def filter_questions(category="All Categories", count=3):
    """Returns a shuffled sample of questions filtered by category."""
    import random
    if category == "All Categories":
        pool = QUESTIONS.copy()
    else:
        pool = [q for q in QUESTIONS if q["category"] == category]
    
    random.shuffle(pool)
    return pool[:min(count, len(pool))]
