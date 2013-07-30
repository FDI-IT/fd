import unicodedata

def unicode_to_ascii(unicode_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode_str)
    return nkfd_form.encode('ASCII','ignore') 