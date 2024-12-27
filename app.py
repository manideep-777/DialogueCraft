from flask import Flask, render_template, request
from difflib import ndiff
import nltk
from nltk.corpus import wordnet

# Ensure you have the necessary NLTK data
nltk.download('wordnet')

app = Flask(__name__)

def generate_alternatives(dialogue):
    """
    Generate alternative versions of the dialogue.
    """
    alternatives = [
        synonym_replacement(dialogue),
        change_tone(dialogue),
        change_verb_tense(dialogue)
    ]
    return alternatives

def synonym_replacement(dialogue):
    """
    Replace words in the dialogue with their synonyms.
    """
    words = dialogue.split()
    new_words = []

    for word in words:
        synonyms = wordnet.synsets(word)
        if synonyms:
            # Take the first synonym (if available)
            synonym = synonyms[0].lemmas()[0].name()
            new_words.append(synonym if synonym != word else word)
        else:
            new_words.append(word)

    return ' '.join(new_words)

def change_tone(dialogue):
    """
    Simulate a casual tone shift.
    """
    formal_phrases = {
        "would you mind": "can you",
        "please": "hey",
        "thank you": "thanks",
        "excuse me": "yo"
    }
    words = dialogue.split()
    new_words = [formal_phrases.get(word.lower(), word) for word in words]
    return ' '.join(new_words)

def change_verb_tense(dialogue):
    """
    Alter verb tense: Converts present to past tense.
    """
    return dialogue.replace("is", "was").replace("will", "would")

def analyze_differences(original, alternative):
    """
    Analyze differences between the original and alternative dialogues.
    Categorizes the differences into added, removed, and unchanged text.
    """
    diff = list(ndiff(original.split(), alternative.split()))
    added = [word[2:] for word in diff if word.startswith('+ ')]
    removed = [word[2:] for word in diff if word.startswith('- ')]
    unchanged = [word[2:] for word in diff if word.startswith('  ')]

    return {
        "added": added,
        "removed": removed,
        "unchanged": unchanged
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    dialogue = request.form.get('dialogue')

    # Generate alternative versions
    alternatives = generate_alternatives(dialogue)

    # Analyze differences for each alternative
    differences = [
        {"alternative": alt, "analysis": analyze_differences(dialogue, alt)}
        for alt in alternatives
    ]

    # Generate best version based on the length of unchanged text
    best_version_data = max(
        differences,
        key=lambda diff: len(diff["analysis"]["unchanged"])
    )

    best_version = best_version_data["alternative"]

    return {
        'original': dialogue,
        'alternatives': alternatives,
        'differences': differences,
        'best_version': best_version
    }

if __name__ == '__main__':
    app.run(debug=True)
