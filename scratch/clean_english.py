import os, glob, re

screens_dir = r'c:\Users\ASUS\OneDrive\Pictures\college 5th sem\SIH\frontend\screens'
files = glob.glob(os.path.join(screens_dir, '*.html'))

# Specific translations and replacements for clean English
replacements = [
    # Welcome & Landing
    ('यहाँ शुरू करें', ''),
    ('पढ़कर सुनाएं', ''),
    ('पढ़कर सुनाएं', ''),
    ('/ पढ़कर सुनाएं', ''),
    ('Read Aloud / पढ़कर सुनाएं', 'Read Aloud'),
    ('Tap to Start\nयहाँ शुरू करें', 'Tap to Start'),
    ('Tap to begin your journey in English or Hindi.', 'Tap the screen below to begin your consultation check-in.'),
    ('अपनी भाषा चुनें', ''),
    ('Choose your language\nअपनी भाषा चुनें', 'Choose your language'),
    ('आगे बढ़ें / Next', 'Next / Continue'),
    ('आगे बढ़ें', 'Next'),
    ('भाषा चुनी गई: हिंदी', 'Language selected: English'),
    ('भाषा निवडली: मराठी', 'Language selected: Marathi'),
    
    # Common Hindi text in medical forms
    ('रोगी का नाम', 'Patient Full Name'),
    ('आयु', 'Age'),
    ('लिंग', 'Gender'),
    ('पुरुष', 'Male'),
    ('महिला', 'Female'),
    ('अन्य', 'Other'),
    ('मोबाइल नंबर', 'Mobile Number'),
    ('पता', 'Address'),
    ('लक्षण', 'Symptoms'),
    ('सीने में दर्द', 'Chest Pain'),
    ('बुखार', 'Fever'),
    ('खांसी', 'Cough'),
    ('सांस फूलना', 'Shortness of Breath'),
    ('पेट दर्द', 'Abdominal Pain'),
    ('सिरदर्द', 'Headache'),
    ('चोट', 'Injury'),
    ('हाँ', 'Yes'),
    ('नहीं', 'No'),
    ('पुष्टि करें', 'Confirm'),
    ('जारी रखें', 'Continue'),
    ('वापस', 'Back'),
    ('आपातकालीन', 'Emergency'),
    ('मदद चाहिए', 'Need Help'),
    ('कृपया प्रतीक्षा करें', 'Please wait')
]

cleaned_count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Clean dangling slash before or after Hindi text: e.g. "English / " or " / English"
    content = re.sub(r'\s*/\s*([A-Za-z]+)', r'\1', content)
    content = re.sub(r'([A-Za-z]+)\s*/\s*$', r'\1', content)
    
    # If file was modified, save it
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        cleaned_count += 1
        print(f'Cleaned English localization in: {os.path.basename(f)}')

print(f'Successfully standardized {cleaned_count} screens to clean English.')
