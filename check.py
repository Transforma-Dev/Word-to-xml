import spacy
import re

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Sample input text
element_text = "diffusion patterns at different leakage pressures: (a) downwind diffusion distance, (b) lateral diffusion distance, (c) maximum coverage area, and (d) farthest diffusion distance."

# Process the text with the NLP model
doc = nlp(element_text)

# Convert text to lowercase except for the first letter
text = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])

# Capitalize the first letter of the text
text = text.strip().capitalize()

# Remove extra spaces around commas and inside parentheses
text = re.sub(r'\s+([,.])', r'\1', text)  # Remove space before commas and periods
text = re.sub(r'\(\s*', '(', text)     # Remove space after opening parenthesis
text = re.sub(r'\s*\)', ')', text)     # Remove space before closing parenthesis

print(text)
