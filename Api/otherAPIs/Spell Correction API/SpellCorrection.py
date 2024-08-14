def predict(text):
    checker=SpellCheck()
    corrected_text=checker.spell_corrector(text)
    return '**Corrected Text\n'+corrected_text