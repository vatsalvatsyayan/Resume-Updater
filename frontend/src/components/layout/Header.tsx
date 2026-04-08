import { useUser, UserButton } from "@clerk/clerk-react";

interface HeaderProps {
  onTailorResume?: () => void;
}

export function Header({ onTailorResume }: HeaderProps) {
  const { user } = useUser();

  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <div className="text-lg font-semibold">Resume Updater</div>

        <div className="flex items-center gap-4">
          {onTailorResume && (
            <button
              type="button"
              onClick={onTailorResume}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
            >
              Tailor Resume
            </button>
          )}

          {user && <UserButton />}
        </div>
      </div>
    </header>
  );
}