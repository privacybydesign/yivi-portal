import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en/translation.json';
import nl from './locales/nl/translation.json';

const resources = {
  en: { translation: en },
  nl: { translation: nl }
};

const storedLanguage =
  typeof window !== 'undefined' && localStorage.getItem('language');

i18n.use(initReactI18next).init({
  resources,
  lng: storedLanguage || 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }
});

export default i18n;
