
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BookHeart,
  Plus,
  Activity,
  Brain,
  Mic,
  Settings,
  Heart,
  Sparkles
} from "lucide-react";

const navigation = [
  { label: "Overview", path: "/", icon: LayoutDashboard },
  { label: "My Journal", path: "/journal", icon: BookHeart },
  { label: "New Entry", path: "/new-entry", icon: Plus },
  { label: "Emotional History", path: "/history", icon: Activity },
  { label: "Patterns", path: "/patterns", icon: Brain },
  { label: "Voice Journal", path: "/voice", icon: Mic },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-20 flex h-screen w-64 flex-col border-r border-[#ecebfa] bg-white px-5 py-7">
      <div className="mb-12 flex items-center gap-3 px-2">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#8b9cf6] text-white">
          <Heart size={22} />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-[#33314d]">
            Emotion Journal
          </h1>
          <p className="text-xs text-gray-400">Your space to understand</p>
        </div>
      </div>

      <p className="mb-4 px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-gray-400">
        Workspace
      </p>

      <nav className="flex flex-col gap-2">
        {navigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive
                  ? "bg-[#eef0ff] text-[#697de0]"
                  : "text-gray-500 hover:bg-[#f7f7fc] hover:text-[#697de0]"
              }`
            }
          >
            <Icon size={19} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto">
        <div className="mb-5 rounded-2xl bg-gradient-to-br from-[#eef0ff] to-[#f5edff] p-4">
          <Sparkles className="mb-3 text-[#8b83dc]" size={20} />
          <p className="text-sm font-semibold text-[#454269]">
            A little space for yourself.
          </p>
          <p className="mt-1 text-xs leading-5 text-[#77749b]">
            Your experiences matter. Take a moment to reflect.
          </p>
        </div>

        <button className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-gray-500 hover:bg-gray-50">
          <Settings size={19} />
          Settings
        </button>
      </div>
    </aside>
  );
}