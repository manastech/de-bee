from google.appengine.api import users
from google.appengine.api import memcache
from util import readFile

availableLanguages = ['es', 'en']
languageData = {}

# Returns a default language to use based on the Accept-Language
# header of the given reuqest.
def getDefaultLanguage(request):
    global availableLanguages
    
    langs = request.headers['Accept-Language'].split(',')
    for lang in langs:
        for availableLang in availableLanguages:
            if lang == availableLang:
                return lang
    
    return 'en'

# Returns the preferred language of the current logged user, defaulting
# to the request header Accept-Language if none was previously selected
def getLanguage(request, user):
    # Try getting the preference from memcache
    key = '%s language' % user
    lang = memcache.get(key)
    
    # If it's not there, default and set in memcache
    if not lang:
        lang = getDefaultLanguage(request)
        memcache.set(key, lang)
        
    return lang

# Returns the preferred language of the current logged user, defaulting
# to the request header Accept-Language if none was previously selected
def getCurrentUsersLanguage(request):
    return getLanguage(request, users.get_current_user())

# Returns a localized text for the given key, in the given language
def _(key, language):
    global languageData
    
    # Load language data if it's not loaded yet
    if not (language in languageData):
        _initializeLanguageData(language)
    
    # Return value, or key if value is empty
    value = languageData[language][key]
    if value == "":
        value = key
    return value

def _initializeLanguageData(language):
    global languageData
    
    props = {}
    lines = readFile('locale/%s.properties' % language).split('\n')
    for line in lines:
        [key, value] = line.split('=', 1)
        props[key] = value.strip()
    languageData[language] = props
    
def addMasterKeys(model, lang):
    model['YouNeedAGoogleAccount'] = _('You need a Google Account', lang)
    model['AllRightsReserved'] = _('All rights reserved', lang)
    model['DevelopedBy'] = _('Developed by', lang)
    model['OriginalIdeaBy'] = _('Original idea by', lang) 