
import { ArrowUpRight, BookOpen, Heart, Sparkles } from "lucide-react";

const stats = [
  { label: "Journal Entries", value: "24", note: "Your recorded experiences", icon: BookOpen },
  { label: "Reflections", value: "18", note: "Moments of self-reflection", icon: Heart },
  { label: "Patterns Discovered", value: "06", note: "Suggestions to explore", icon: Sparkles },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[28px] bg-gradient-to-r from-[#e8eaff] via-[#eeebff] to-[#f5edff] p-9">
        <div className="relative z-10 max-w-xl">
          <p className="mb-3 text-sm font-semibold text-[#7775b4]">
            YOUR PERSONAL EMOTIONAL SPACE
          </p>
          <h1 className="text-3xl font-bold leading-tight tracking-tight text-[#353252]">
            Every experience tells a story.
          </h1>
          <p className="mt-3 max-w-md text-sm leading-6 text-[#77749b]">
            Take a moment to understand your experiences, explore your emotions,
            and notice the patterns that make you who you are.
          </p>
          <a
            href="/new-entry"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#858fe8] px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-200/50 transition hover:bg-[#727edb]"
          >
            Write a new entry <ArrowUpRight size={17} />
          </a>
        </div>
        <div className="absolute -right-8 -top-16 h-72 w-72 rounded-full border-[35px] border-white/30" />
        <div className="absolute -bottom-32 right-32 h-64 w-64 rounded-full bg-white/20 blur-2xl" />
      </section>

      <section>
        <div className="mb-5">
          <h2 className="text-xl font-bold text-[#34324d]">Your overview</h2>
          <p className="mt-1 text-sm text-gray-400">A snapshot of your journey.</p>
        </div>

        <div className="grid grid-cols-3 gap-5">
          {stats.map(({ label, value, note, icon: Icon }) => (
            <div key={label} className="rounded-2xl border border-[#efedf7] bg-white p-6 shadow-sm shadow-gray-100/50">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">{label}</span>
                <div className="rounded-xl bg-[#f0f0ff] p-2.5 text-[#858fe8]">
                  <Icon size={20} />
                </div>
              </div>
              <p className="mt-5 text-3xl font-bold text-[#353252]">{value}</p>
              <p className="mt-2 text-xs text-gray-400">{note}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-3 gap-5">
        <div className="col-span-2 rounded-2xl border border-[#efedf7] bg-white p-6">
          <h2 className="font-bold text-[#34324d]">Your emotional journey</h2>
          <p className="mt-1 text-sm text-gray-400">
            Your experiences and self-reported feelings will appear here.
          </p>
          <div className="flex h-52 items-center justify-center">
            <div className="text-center">
              <Heart className="mx-auto mb-3 text-[#aaa9e9]" size={30} />
              <p className="text-sm text-gray-400">Your timeline starts with your first entry.</p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-[#efedf7] bg-white p-6">
          <Sparkles className="mb-4 text-[#8b83dc]" size={22} />
          <h2 className="font-bold text-[#34324d]">A gentle reminder</h2>
          <p className="mt-3 text-sm leading-6 text-gray-500">
            Your emotions don't define you. This is a space to explore your experiences
            without judgment or pressure.
          </p>
        </div>
      </section>
    </div>
  );
}