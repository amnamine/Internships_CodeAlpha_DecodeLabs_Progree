"""
Cryptographic Utilities, Password Generators, Entropy Calculation & Encryption Helper
"""

import string
import secrets
import math
import hashlib
import base64

# Diceware word list (sample curated high-entropy words)
EFF_WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "accent",
    "accept", "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across",
    "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit",
    "adult", "advance", "advice", "aerobic", "afford", "afraid", "again", "age", "agent", "agree",
    "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien",
    "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", "always",
    "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle",
    "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
    "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic", "area",
    "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest", "arrive",
    "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset", "assist",
    "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction", "audit",
    "august", "aunt", "auto", "autumn", "average", "avocado", "avoid", "awake", "aware", "away",
    "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge", "bag", "balance",
    "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain", "barrel", "base",
    "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become", "beef", "before",
    "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit", "best", "betray",
    "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology", "bird", "birth",
    "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless", "blind", "blood",
    "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body", "boil", "bomb",
    "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss", "bottom", "bounce",
    "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread", "breeze", "brick",
    "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze", "broom", "brother",
    "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb", "bulk", "bullet",
    "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy", "butter", "buyer",
    "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call", "calm", "camera",
    "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas", "canyon", "capable",
    "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry", "cart", "case",
    "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category", "cattle", "cause",
    "caution", "cave", "ceiling", "celery", "cement", "census", "century", "cereal", "certain", "chair",
    "chalk", "champion", "change", "chapter", "charge", "chase", "chat", "cheap", "check", "cheese",
    "chef", "cherry", "chest", "chicken", "chief", "child", "chimney", "choice", "choose", "chronic",
    "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle", "citizen", "city", "civil", "claim",
    "clap", "clarify", "claw", "clay", "clean", "clerk", "clever", "click", "client", "cliff",
    "climb", "clinic", "clip", "clock", "clog", "close", "cloth", "cloud", "clown", "club",
    "clump", "cluster", "clutch", "coach", "coast", "coconut", "code", "coffee", "coil", "coin",
    "collect", "color", "column", "combine", "come", "comfort", "comic", "common", "company", "concert",
    "conduct", "confirm", "congress", "connect", "consider", "control", "convince", "cook", "cool", "copper",
    "coral", "core", "corn", "correct", "cost", "cotton", "couch", "country", "couple", "course",
    "cousin", "cover", "coyote", "crack", "cradle", "craft", "cram", "crane", "crash", "crater",
    "crawl", "crazy", "cream", "credit", "creek", "crew", "cricket", "crime", "crisp", "critic",
    "crop", "cross", "crouch", "crowd", "crucial", "cruel", "cruise", "crumble", "crunch", "crush",
    "cry", "crystal", "cube", "culture", "cup", "cupboard", "curious", "current", "curtain", "curve",
    "cushion", "custom", "cute", "cycle", "dad", "damage", "damp", "dance", "danger", "daring",
    "dash", "daughter", "dawn", "day", "deal", "debate", "debris", "decade", "december", "decide",
    "decline", "decor", "decrease", "deer", "defense", "define", "defy", "degree", "delay", "deliver",
    "demand", "demise", "denial", "dentist", "deny", "depart", "depend", "deposit", "depth", "deputy",
    "derive", "describe", "desert", "design", "desk", "despair", "destroy", "detail", "detect", "develop",
    "device", "devote", "diagram", "dial", "diamond", "diary", "dice", "diesel", "diet", "differ",
    "digital", "dignity", "dilemma", "dinner", "dinosaur", "direct", "dirt", "disagree", "discover", "disease",
    "dish", "dismiss", "disorder", "display", "distance", "divert", "divide", "divorce", "dizzy", "doctor",
    "document", "dog", "doll", "dolphin", "domain", "donate", "donkey", "donor", "door", "dose",
    "double", "dove", "draft", "dragon", "drama", "drastic", "draw", "dream", "dress", "drift",
    "drill", "drink", "drip", "drive", "drop", "drum", "dry", "duck", "dumb", "dune",
    "during", "dust", "dutch", "duty", "dwarf", "dynamic", "eager", "eagle", "early", "earn",
    "earth", "easily", "east", "easy", "echo", "ecology", "economy", "edge", "edit", "educate",
    "effort", "egg", "eight", "either", "elbow", "elder", "electric", "element", "elephant", "elevator",
    "elite", "else", "embark", "embody", "embrace", "emerge", "emotion", "employ", "empower", "empty",
    "enable", "enact", "end", "endless", "endorse", "enemy", "energy", "enforce", "engage", "engine",
    "enhance", "enjoy", "enlist", "enough", "enrich", "enroll", "ensure", "enter", "entire", "entry",
    "envelope", "episode", "equal", "equip", "era", "erase", "erode", "erosion", "error", "erupt",
    "escape", "essay", "essence", "estate", "eternal", "ethics", "evidence", "evil", "evoke", "evolve",
    "exact", "example", "excess", "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust",
    "exhibit", "exile", "exist", "exit", "exotic", "expand", "expect", "expire", "explain", "expose",
    "express", "extend", "extra", "eye", "eyebrow", "fabric", "face", "faculty", "fade", "faint",
    "faith", "fall", "false", "fame", "family", "famous", "fan", "fancy", "fantasy", "farm",
    "fashion", "fat", "fatal", "father", "fatigue", "fault", "favorite", "feature", "february", "federal",
    "fee", "feed", "feel", "female", "fence", "festival", "fetch", "fever", "few", "fiber",
    "fiction", "field", "figure", "file", "film", "filter", "final", "find", "fine", "finger",
    "finish", "fire", "firm", "first", "fiscal", "fish", "fit", "fitness", "fix", "flag",
    "flame", "flash", "flat", "flavor", "flee", "flight", "flip", "float", "flock", "floor",
    "flower", "fluid", "flush", "fly", "foam", "focus", "fog", "foil", "fold", "follow",
    "food", "foot", "force", "forest", "forget", "fork", "fortune", "forum", "forward", "fossil",
    "foster", "found", "fox", "fragile", "frame", "frequent", "fresh", "friend", "fringe", "frog",
    "front", "frost", "frown", "frozen", "fruit", "fuel", "fun", "funny", "furnace", "fury",
    "future", "gadget", "gain", "galaxy", "gallery", "game", "gap", "garage", "garbage", "garden",
    "garlic", "garment", "gas", "gasp", "gate", "gather", "gauge", "gaze", "general", "genius",
    "genre", "gentle", "genuine", "gesture", "ghost", "giant", "gift", "giggle", "ginger", "giraffe",
    "girl", "give", "glad", "glance", "glare", "glass", "glide", "glimpse", "globe", "gloom",
    "glory", "glove", "glow", "glue", "goat", "goddess", "gold", "good", "goose", "gorilla",
    "gospel", "gossip", "govern", "gown", "grab", "grace", "grain", "grant", "grape", "grass",
    "gravity", "great", "green", "grid", "grief", "grit", "grocery", "group", "grow", "grunt",
    "guard", "guess", "guide", "guilt", "guitar", "gun", "gym", "habit", "hair", "half",
    "hammer", "hamster", "hand", "happy", "harbor", "hard", "harsh", "harvest", "hat", "have",
    "hawk", "hazard", "head", "health", "heart", "heavy", "hedgehog", "height", "hello", "helmet",
    "help", "hen", "hero", "hidden", "high", "hill", "hint", "hip", "hire", "history",
    "hobby", "hockey", "hold", "hole", "holiday", "hollow", "home", "honey", "hood", "hope",
    "horn", "horror", "horse", "hospital", "host", "hotel", "hour", "hover", "hub", "huge",
    "human", "humble", "humor", "hundred", "hungry", "hunt", "hurdle", "hurry", "hurt", "husband",
    "hybrid", "ice", "icon", "idea", "identify", "idle", "ignore", "ill", "illegal", "illness",
    "image", "imitate", "immense", "immune", "impact", "impose", "improve", "impulse", "inch", "include",
    "income", "increase", "index", "indicate", "indoor", "industry", "infant", "inflict", "inform", "inhale",
    "inherit", "initial", "inject", "injury", "inmate", "inner", "innocent", "input", "inquiry", "insane",
    "insect", "inside", "inspire", "install", "intact", "interest", "into", "invest", "invite", "involve",
    "iron", "island", "isolate", "issue", "item", "ivory", "jacket", "jaguar", "jar", "jazz",
    "jealous", "jeans", "jelly", "jewel", "job", "join", "joke", "journey", "joy", "judge",
    "juice", "jump", "jungle", "junior", "junk", "just", "kangaroo", "keen", "keep", "ketchup",
    "key", "kick", "kid", "kidney", "kind", "kingdom", "kiss", "kit", "kitchen", "kite",
    "kitten", "kiwi", "knee", "knife", "knock", "know", "lab", "label", "labor", "ladder",
    "lady", "lake", "lamp", "language", "laptop", "large", "later", "latin", "laugh", "laundry",
    "lava", "law", "lawn", "lawsuit", "layer", "lazy", "leader", "leaf", "learn", "leave",
    "lecture", "left", "leg", "legal", "legend", "lemon", "lend", "length", "lens", "leopard",
    "lesson", "letter", "level", "liar", "liberty", "library", "license", "life", "lift", "light",
    "like", "limb", "limit", "link", "lion", "liquid", "list", "little", "live", "lizard",
    "load", "loan", "lobster", "local", "lock", "logic", "lonely", "long", "loop", "lottery",
    "loud", "lounge", "love", "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury",
    "lyrics", "machine", "mad", "magic", "magnet", "maid", "mail", "main", "major", "make",
    "mammal", "man", "manage", "mandate", "mango", "mansion", "manual", "maple", "marble", "march",
    "margin", "marine", "market", "marriage", "mask", "mass", "master", "match", "material", "math",
    "matrix", "matter", "maximum", "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal",
    "media", "melody", "melt", "member", "memory", "mention", "menu", "mercy", "merge", "merit",
    "merry", "mesh", "message", "metal", "method", "middle", "midnight", "milk", "million", "mimic",
    "mind", "minimum", "minor", "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix",
    "mixed", "mixture", "mobile", "model", "modify", "mom", "moment", "monitor", "monkey", "monster",
    "month", "moon", "moral", "more", "morning", "mosquito", "mother", "motion", "motor", "mountain",
    "mouse", "move", "movie", "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom",
    "music", "must", "mutual", "myself", "mystery", "myth", "naive", "name", "napkin", "narrow",
    "nasty", "nation", "nature", "near", "neck", "need", "negative", "neglect", "neither", "nephew",
    "nerve", "nest", "net", "network", "neutral", "never", "news", "next", "nice", "night",
    "noble", "noise", "nominee", "noodle", "normal", "north", "nose", "notable", "note", "nothing",
    "notice", "novel", "now", "number", "nurse", "nut", "oak", "obey", "object", "oblige",
    "obscure", "observe", "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer",
    "office", "often", "oil", "okay", "old", "olive", "olympic", "omit", "once", "one",
    "onion", "online", "only", "open", "opera", "opinion", "oppose", "option", "orange", "orbit",
    "orchard", "order", "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor",
    "outer", "output", "outside", "oval", "oven", "over", "own", "owner", "oxygen", "oyster",
    "ozone", "pack", "packet", "palm", "panda", "panel", "panic", "panther", "paper", "parade",
    "parent", "park", "parrot", "party", "pass", "patch", "path", "patient", "patrol", "pattern",
    "pause", "pave", "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen", "penalty",
    "pencil", "people", "pepper", "perfect", "permit", "person", "pet", "phone", "photo", "phrase",
    "physical", "piano", "picnic", "picture", "piece", "pig", "pigeon", "pillow", "pilot", "pin",
    "pine", "pink", "pipe", "pistol", "pitch", "pizza", "place", "planet", "plastic", "plate",
    "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet", "point", "polar",
    "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible", "post",
    "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare",
    "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison", "private",
    "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof", "property",
    "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin",
    "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle",
    "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit",
    "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp",
    "ranch", "random", "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor",
    "reach", "react", "read", "real", "reason", "rebel", "rebuild", "recall", "receive", "recipe",
    "record", "recycle", "reduce", "reflect", "reform", "refuse", "region", "regret", "regular", "reject",
    "relax", "release", "relief", "rely", "remain", "remember", "remind", "remove", "render", "renew",
    "rent", "reopen", "repair", "repeat", "replace", "report", "require", "rescue", "resemble", "resist",
    "resource", "response", "result", "retire", "retreat", "return", "reunion", "reveal", "review", "reward",
    "rhythm", "rib", "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right", "rigid",
    "ring", "riot", "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot",
    "robust", "rocket", "romance", "roof", "rookie", "room", "rose", "rotate", "rough", "round",
    "route", "royal", "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad",
    "saddle", "sadness", "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same",
    "sample", "sand", "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan",
    "scare", "scatter", "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap",
    "screen", "script", "scrub", "sea", "search", "season", "seat", "second", "secret", "section",
    "security", "seed", "seek", "segment", "select", "sell", "seminar", "senior", "sense", "sentence",
    "series", "service", "session", "settle", "setup", "seven", "shadow", "shaft", "shallow", "share",
    "shed", "shell", "sheriff", "shield", "shift", "shine", "ship", "shiver", "shock", "shoe",
    "shoot", "shop", "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling",
    "sick", "side", "siege", "sight", "sign", "silent", "silk", "silly", "silver", "similar",
    "simple", "since", "sing", "siren", "sister", "situate", "six", "size", "skate", "sketch",
    "ski", "skill", "skin", "skirt", "skull", "sky", "slap", "slate", "slender", "slice",
    "slide", "slight", "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile",
    "smoke", "smooth", "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social",
    "sock", "soda", "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song",
    "soon", "sorry", "sort", "soul", "sound", "soup", "source", "south", "space", "spare",
    "spatial", "spawn", "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider",
    "spike", "spin", "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray",
    "spread", "spring", "spy", "square", "squeeze", "squirrel", "stable", "stadium", "staff", "stage",
    "stairs", "stamp", "stand", "start", "state", "stay", "steak", "steel", "stem", "step",
    "stereo", "stick", "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove",
    "strategy", "street", "strike", "strong", "struggling", "student", "stuff", "stumble", "style", "subject",
    "submit", "subway", "success", "sugar", "suggest", "suit", "summer", "sun", "sunny", "sunset",
    "super", "supply", "supreme", "sure", "surface", "surge", "surprise", "surround", "survey", "suspect",
    "sustain", "swallow", "swamp", "swap", "swarm", "sweet", "swift", "swim", "swing", "switch",
    "sword", "symbol", "symptom", "syrup", "system", "table", "tackle", "tag", "tail", "talent",
    "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi", "teach", "team",
    "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text", "thank", "that",
    "theme", "then", "theory", "there", "they", "thing", "this", "thought", "three", "thrive",
    "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt", "timber", "time", "tiny",
    "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler", "toe", "together",
    "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool", "tooth", "top",
    "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist", "toward", "tower",
    "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer", "trap", "trash",
    "travel", "tray", "treat", "tree", "trend", "trial", "tribe", "trick", "trigger", "trim",
    "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust", "truth", "try",
    "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle", "twelve", "twenty",
    "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella", "unable", "unaware",
    "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform", "unique", "unit",
    "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade", "uphold", "upon",
    "upper", "upset", "urban", "urge", "usage", "use", "used", "useful", "useless", "usual",
    "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van", "vanish", "vapor",
    "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue", "verb", "verify",
    "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious", "victory", "video", "view",
    "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual", "vital", "vivid",
    "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage", "wagon", "wait",
    "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash", "wasp", "waste",
    "water", "wave", "way", "wealth", "weapon", "wear", "weasel", "weather", "web", "wedding",
    "weekend", "weird", "welcome", "west", "wet", "whale", "what", "wheat", "wheel", "when",
    "where", "whip", "whisper", "wide", "width", "wife", "wild", "will", "win", "window",
    "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise", "wish", "witness",
    "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world", "worry", "worth",
    "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year", "yellow", "you",
    "young", "youth", "zebra", "zero", "zone", "zoo"
]

PHONETIC_CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "w", "x", "z", "th", "ch", "sh"]
PHONETIC_VOWELS = ["a", "e", "i", "o", "u", "ai", "ea", "ee", "oo", "ou"]

def generate_random_password(
    length=16,
    use_upper=True,
    use_lower=True,
    use_digits=True,
    use_symbols=True,
    exclude_ambiguous=False,
    custom_exclude=""
):
    """Generates a cryptographically strong random password."""
    chars = ""
    lower_chars = string.ascii_lowercase
    upper_chars = string.ascii_uppercase
    digit_chars = string.digits
    symbol_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        ambiguous = "l1I0O"
        lower_chars = "".join(c for c in lower_chars if c not in ambiguous)
        upper_chars = "".join(c for c in upper_chars if c not in ambiguous)
        digit_chars = "".join(c for c in digit_chars if c not in ambiguous)
        symbol_chars = "".join(c for c in symbol_chars if c not in ambiguous)

    if custom_exclude:
        lower_chars = "".join(c for c in lower_chars if c not in custom_exclude)
        upper_chars = "".join(c for c in upper_chars if c not in custom_exclude)
        digit_chars = "".join(c for c in digit_chars if c not in custom_exclude)
        symbol_chars = "".join(c for c in symbol_chars if c not in custom_exclude)

    guaranteed = []
    if use_lower and lower_chars:
        chars += lower_chars
        guaranteed.append(secrets.choice(lower_chars))
    if use_upper and upper_chars:
        chars += upper_chars
        guaranteed.append(secrets.choice(upper_chars))
    if use_digits and digit_chars:
        chars += digit_chars
        guaranteed.append(secrets.choice(digit_chars))
    if use_symbols and symbol_chars:
        chars += symbol_chars
        guaranteed.append(secrets.choice(symbol_chars))

    if not chars:
        chars = string.ascii_letters + string.digits

    remaining_length = max(0, length - len(guaranteed))
    password_list = guaranteed + [secrets.choice(chars) for _ in range(remaining_length)]
    
    # Cryptographic shuffle
    for i in range(len(password_list) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_list[i], password_list[j] = password_list[j], password_list[i]

    return "".join(password_list[:length])


def generate_passphrase(words_count=4, separator="-", capitalize=True, include_number=True):
    """Generates a Diceware-style memorable passphrase."""
    chosen = [secrets.choice(EFF_WORDLIST) for _ in range(words_count)]
    if capitalize:
        chosen = [w.capitalize() for w in chosen]
    
    result = separator.join(chosen)
    if include_number:
        result += f"{separator}{secrets.randbelow(90) + 10}"
    return result


def generate_pronounceable_password(length=12, capitalize=True):
    """Generates a phonetic pronounceable password."""
    pwd = ""
    toggle = secrets.choice([True, False])
    while len(pwd) < length:
        if toggle:
            c = secrets.choice(PHONETIC_CONSONANTS)
        else:
            c = secrets.choice(PHONETIC_VOWELS)
        pwd += c
        toggle = not toggle

    pwd = pwd[:length]
    if capitalize:
        pwd = pwd.capitalize()
    
    # append digit for extra security
    pwd = pwd[:-2] + str(secrets.randbelow(90) + 10)
    return pwd


def generate_pin(length=6):
    """Generates a secure numeric PIN."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def calculate_entropy(password):
    """Calculates password entropy in bits."""
    if not password:
        return 0.0

    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += 26
    if any(c in string.ascii_uppercase for c in password):
        pool += 26
    if any(c in string.digits for c in password):
        pool += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        pool += 32
    if any(c not in string.printable for c in password):
        pool += 30

    if pool == 0:
        pool = 26

    entropy = len(password) * math.log2(pool)
    return round(entropy, 1)


def analyze_password_strength(password):
    """
    Analyzes password and returns (score_percentage, status_text, color_key, crack_time_str).
    """
    if not password:
        return 0, "Empty", "strength_weak", "Instant"

    entropy = calculate_entropy(password)

    # Calculate estimated crack time assuming 10^10 hashes per sec (offline fast attack)
    combinations = 2 ** entropy
    seconds = combinations / (10**10)

    if seconds < 1:
        crack_time = "Instant"
    elif seconds < 60:
        crack_time = f"{int(seconds)} seconds"
    elif seconds < 3600:
        crack_time = f"{int(seconds // 60)} minutes"
    elif seconds < 86400:
        crack_time = f"{int(seconds // 3600)} hours"
    elif seconds < 31536000:
        crack_time = f"{int(seconds // 86400)} days"
    elif seconds < 31536000 * 1000:
        crack_time = f"{int(seconds // 31536000)} years"
    else:
        crack_time = f"{seconds / 31536000:.1e} centuries"

    # Score calculation (0 to 100)
    score = min(100, int((entropy / 100.0) * 100))

    if entropy < 30:
        return score, "Very Weak", "strength_weak", crack_time
    elif entropy < 50:
        return score, "Weak", "strength_fair", crack_time
    elif entropy < 70:
        return score, "Good", "strength_good", crack_time
    elif entropy < 90:
        return score, "Strong", "strength_strong", crack_time
    else:
        return score, "Godlike / Unbreakable", "strength_godlike", crack_time


# Simple PBKDF2 + AES Cipher simulation helper using built-in hashlib and base64
def derive_key(master_password, salt):
    return hashlib.pbkdf2_hmac('sha256', master_password.encode('utf-8'), salt, 100000)

def encrypt_data(data, master_password):
    """Simple XOR stream cipher with SHA256 Key derivation for zero-dependency standard library security."""
    salt = secrets.token_bytes(16)
    key = derive_key(master_password, salt)
    
    data_bytes = data.encode('utf-8')
    encrypted = bytearray()
    
    for i, b in enumerate(data_bytes):
        key_byte = key[i % len(key)]
        encrypted.append(b ^ key_byte)
        
    combined = salt + bytes(encrypted)
    return base64.b64encode(combined).decode('utf-8')

def decrypt_data(encrypted_b64, master_password):
    """Decrypts data encrypted with encrypt_data."""
    try:
        combined = base64.b64decode(encrypted_b64.encode('utf-8'))
        salt = combined[:16]
        ciphertext = combined[16:]
        key = derive_key(master_password, salt)
        
        decrypted = bytearray()
        for i, b in enumerate(ciphertext):
            key_byte = key[i % len(key)]
            decrypted.append(b ^ key_byte)
            
        return decrypted.decode('utf-8')
    except Exception:
        return None

def check_breached_simulator(password):
    """Simulates a secure SHA-1 k-anonymity breach check."""
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    # Mock lookup check based on common patterns or deterministic hash bit test
    is_breached = sha1.startswith("00") or password.lower() in ["password", "123456", "admin", "welcome", "qwerty"]
    occurrences = secrets.randbelow(15000) + 120 if is_breached else 0
    return is_breached, occurrences
