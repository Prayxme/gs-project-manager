import { useAppSettings } from "../../shared/settings";

const IDIOMAS = ["en", "es"];

export default function LanguageSwitch() {
  const { lang, setLang } = useAppSettings();
  return (
    <div className="flex items-center rounded-full bg-black/20 p-0.5 text-[11px] font-extrabold">
      {IDIOMAS.map((code) => (
        <button
          key={code}
          onClick={() => setLang(code)}
          className={`px-2.5 py-1 rounded-full transition ${
            lang === code ? "bg-[#4C956C] text-white" : "text-on-header-muted hover:text-on-header"
          }`}
        >
          {code.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
