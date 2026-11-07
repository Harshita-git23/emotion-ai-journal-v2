
import { Outlet } from "react-router-dom";
import { Bell, Search } from "lucide-react";
import Sidebar from "../components/Sidebar";
import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function DashboardLayout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
    logout();
    navigate("/login");
    };
  return (
    <div className="min-h-screen bg-[#f7f7fc]">
      <Sidebar />

      <main className="ml-64 min-h-screen">
        <header className="sticky top-0 z-10 flex h-[76px] items-center justify-between border-b border-[#eeedf5] bg-white/90 px-10 backdrop-blur">
          <div>
            <p className="text-sm text-gray-400">Your personal space</p>
            <p className="font-semibold text-[#34324d]">Emotion Journal</p>
          </div>

          <div className="flex items-center gap-5">
            <button className="text-gray-400 hover:text-[#8b9cf6]">
              <Search size={20} />
            </button>
            <button className="relative text-gray-400 hover:text-[#8b9cf6]">
              <Bell size={20} />
            </button>
            <div className="flex items-center gap-3">
                <span className="hidden text-sm text-gray-500 sm:block">
                    {user?.email}
                </span>

                <button
                    onClick={handleLogout}
                    title="Logout"
                    className="rounded-xl p-2 text-gray-400 hover:bg-red-50 hover:text-red-500"
                >
                    <LogOut size={19} />
                </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1500px] p-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}