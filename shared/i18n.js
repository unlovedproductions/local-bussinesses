(function () {
  'use strict';

  var STORAGE_KEY = 'preferredLang';

  function detectLang() {
    var langs = navigator.languages && navigator.languages.length
      ? navigator.languages
      : [navigator.language || 'en'];

    for (var i = 0; i < langs.length; i++) {
      var code = langs[i].toLowerCase().split('-')[0];
      if (code === 'es') return 'es';
      if (code === 'en') return 'en';
    }
    return 'en';
  }

  function getStoredLang() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'en' || stored === 'es') return stored;
    } catch (e) {
      /* localStorage unavailable */
    }
    return null;
  }

  function setStoredLang(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* localStorage unavailable */
    }
  }

  function resolveLang() {
    return getStoredLang() || detectLang();
  }

  function applyTranslations(translations, lang) {
    document.documentElement.lang = lang;

    var titleKey = document.documentElement.getAttribute('data-i18n-title');
    if (titleKey && translations[lang] && translations[lang][titleKey]) {
      document.title = translations[lang][titleKey];
    }

    var elements = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < elements.length; i++) {
      var el = elements[i];
      var key = el.getAttribute('data-i18n');
      if (translations[lang] && translations[lang][key] !== undefined) {
        el.textContent = translations[lang][key];
      }
    }

    var htmlElements = document.querySelectorAll('[data-i18n-html]');
    for (var j = 0; j < htmlElements.length; j++) {
      var htmlEl = htmlElements[j];
      var htmlKey = htmlEl.getAttribute('data-i18n-html');
      if (translations[lang] && translations[lang][htmlKey] !== undefined) {
        htmlEl.innerHTML = translations[lang][htmlKey];
      }
    }

    var attrElements = document.querySelectorAll('[data-i18n-attr]');
    for (var k = 0; k < attrElements.length; k++) {
      var attrEl = attrElements[k];
      var attrSpec = attrEl.getAttribute('data-i18n-attr');
      var parts = attrSpec.split(':');
      if (parts.length === 2 && translations[lang] && translations[lang][parts[1]] !== undefined) {
        attrEl.setAttribute(parts[0], translations[lang][parts[1]]);
      }
    }

    updateToggleButtons(lang);
  }

  function updateToggleButtons(lang) {
    var buttons = document.querySelectorAll('[data-lang-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var btnLang = btn.getAttribute('data-lang-toggle');
      btn.classList.toggle('is-active', btnLang === lang);
      btn.setAttribute('aria-pressed', btnLang === lang ? 'true' : 'false');
    }
  }

  function initI18n(translations) {
    var lang = resolveLang();
    applyTranslations(translations, lang);

    var toggles = document.querySelectorAll('[data-lang-toggle]');
    for (var i = 0; i < toggles.length; i++) {
      toggles[i].addEventListener('click', function () {
        var selected = this.getAttribute('data-lang-toggle');
        if (selected !== 'en' && selected !== 'es') return;
        setStoredLang(selected);
        applyTranslations(translations, selected);
      });
    }
  }

  window.ChurchI18n = {
    detectLang: detectLang,
    resolveLang: resolveLang,
    applyTranslations: applyTranslations,
    initI18n: initI18n
  };
})();
