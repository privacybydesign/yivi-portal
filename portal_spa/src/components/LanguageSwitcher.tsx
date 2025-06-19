import { useTranslation } from 'react-i18next';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const toggle = () => {
    const newLang = i18n.language === 'en' ? 'nl' : 'en';
    i18n.changeLanguage(newLang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('language', newLang);
    }
  };

  return (
    <button onClick={toggle} className="text-sm px-2 py-1">
      {i18n.language === 'en' ? 'NL' : 'EN'}
    </button>
  );
}
