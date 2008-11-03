from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from ajax import redirectPage
from io import readFile

availableLanguages = ['es', 'en']
languageData = {}

# Returns a default language to use based on the Accept-Language
# header of the given reuqest.
def getDefaultLanguage(handler):
    cookie = 'lang' in handler.request.cookies
    if cookie:
        return ensureLanguage(handler.request.cookies['lang'])
    
    global availableLanguages
    
    langs = handler.request.headers['Accept-Language'].split(',')
    for lang in langs:
        for availableLang in availableLanguages:
            if lang == availableLang:
                return lang
    
    return 'en'

# Returns the preferred language of the current logged user, defaulting
# to the request header Accept-Language if none was previously selected
def getLanguage(handler, user):
    # Try getting the preference from memcache
    key = '%s language' % user
    lang = memcache.get(key)
    
    # If it's not there, default and set in memcache
    if not lang:
        lang = getDefaultLanguage(handler)
        memcache.set(key, lang)
        
    return lang

def ensureLanguage(lang):
    global availableLanguages
    for availableLang in availableLanguages:
        if lang == availableLang:
            return lang
    return 'en' 

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
        [key, value] = line.split(':=', 1)
        props[key] = value.strip()
    languageData[language] = props
    
def addMasterKeys(model, lang):
    model['lang'] = lang
    model['YouNeedAGoogleAccount'] = _('You need a Google Account', lang)
    model['AllRightsReserved'] = _('All rights reserved', lang)
    model['DevelopedBy'] = _('Developed by', lang)
    model['OriginalIdeaBy'] = _('Original idea by', lang)
    model['Hello'] = _('Hello', lang)
    model['Logout'] = _('Logout', lang)
    
    global availableLanguages
    for availableLang in availableLanguages:
         model['%sSelected' % availableLang] = lang == availableLang
         
class ChangeLanguageHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        lang = ensureLanguage(self.request.get('lang'))
        
        # Set cookie
        self.response.headers['Set-Cookie'] = str('lang=%s; path=/;' % lang)
        
        # Set memcache if possible
        if user:
            key = '%s language' % user
            memcache.set(key, lang)
        
        redirectPage(self, '/')