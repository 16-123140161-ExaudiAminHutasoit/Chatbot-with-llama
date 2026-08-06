import { Shell, User2 } from "lucide-react";
import Image from "next/image";

export default function ChatAvatar({ role }: { role: string }) {
  if (role === "user") {
    return (
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
        <User2 className="h-4 w-4" />
      </div>
    );
  }

  if (role === "function") {
    return (
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
        <Shell className="h-4 w-4 text-sky-400" />
      </div>
    );
  }

  return (
    <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg border border-slate-200 bg-white p-0.5 shadow-sm">
      <Image
        className="rounded-md object-contain"
        src="/bps-logo.svg"
        alt="Logo BPS"
        width={24}
        height={24}
        priority
      />
    </div>
  );

}
