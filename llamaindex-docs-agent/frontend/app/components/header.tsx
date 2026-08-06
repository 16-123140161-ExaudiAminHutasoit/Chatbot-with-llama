import Image from "next/image";

export default function Header() {
  return (
    <div className="z-10 max-w-5xl w-full my-4 rounded-2xl overflow-hidden shadow-lg border-t-4 border-[#9B51E0] bg-[#062459]">
      <div className="p-4 sm:p-5 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Left Side: Official BPS Lampung Selatan Logo & Title */}
        <div className="flex items-center gap-3">
          <Image
            src="/bps-lamsel-logo.svg"
            alt="BADAN PUSAT STATISTIK KABUPATEN LAMPUNG SELATAN"
            width={380}
            height={68}
            className="h-12 sm:h-14 w-auto object-contain"
            priority
          />
        </div>

        {/* Right Side: Chatbot Info & WhatsApp Action */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden lg:flex flex-col text-right">
            <span className="text-xs font-bold text-blue-200 tracking-wide">
              Sensus Ekonomi 2026 (SE2026)
            </span>
            <span className="text-[10px] text-blue-300">
              Asisten Virtual Resmi Lamsel
            </span>
          </div>

          <a
            href="https://wa.me/6282175001803"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-4 py-2.5 rounded-xl shadow-md transition-all hover:scale-105 active:scale-95"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.705 1.754zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/>
            </svg>
            <span>Chat WA BPS Lamsel</span>
          </a>
        </div>
      </div>
    </div>
  );
}



