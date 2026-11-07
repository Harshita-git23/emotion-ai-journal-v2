
import { useState } from "react";
import { Heart, Sparkles, Eye, EyeOff } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();

  const [isSignup, setIsSignup] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (isSignup) {
        await register(email, password);
      } else {
        await login(email, password);
      }

      navigate("/");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Something went wrong. Please try again."
      );
    }
  };

  return (
    <div className="flex min-h-screen bg-[#f7f7fc]">
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-to-br from-[#858fe8] to-[#b5a8e9] p-14 text-white lg:flex">
        <div className="flex items-center gap-3">
          <Heart size={28} />
          <span className="text-xl font-bold">Emotion Journal</span>
        </div>

        <div className="max-w-lg">
          <Sparkles size={30} className="mb-6" />
          <h1 className="text-5xl font-bold leading-tight">
            Understand yourself, one experience at a time.
          </h1>
          <p className="mt-6 leading-7 text-white/80">
            A private space to document experiences, explore emotions,
            and discover patterns over time.
          </p>
        </div>

        <p className="text-sm text-white/70">
          Your experiences. Your reflections. Your story.
        </p>
      </div>

      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-md rounded-3xl border border-[#efedf7] bg-white p-9 shadow-sm">
          <div className="mb-8 lg:hidden">
            <Heart className="mb-3 text-[#858fe8]" size={30} />
            <h1 className="text-xl font-bold text-[#353252]">
              Emotion Journal
            </h1>
          </div>

          <h2 className="text-2xl font-bold text-[#353252]">
            {isSignup ? "Create your account" : "Welcome back"}
          </h2>

          <p className="mt-2 text-sm text-gray-400">
            {isSignup
              ? "Begin your personal reflection journey."
              : "Continue exploring your experiences."}
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-[#45435f]">
                Email address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-xl border border-[#eae9f5] bg-[#fcfcff] px-4 py-3 text-sm outline-none focus:border-[#858fe8]"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-[#45435f]">
                Password
              </label>

              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full rounded-xl border border-[#eae9f5] bg-[#fcfcff] px-4 py-3 pr-12 text-sm outline-none focus:border-[#858fe8]"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-3.5 text-gray-400"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && (
              <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#858fe8] py-3.5 text-sm font-semibold text-white transition hover:bg-[#727edb] disabled:opacity-60"
            >
              {loading
                ? "Please wait..."
                : isSignup
                  ? "Create account"
                  : "Sign in"}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-gray-400">
            {isSignup ? "Already have an account?" : "New to Emotion Journal?"}

            <button
              onClick={() => {
                setIsSignup(!isSignup);
                setError("");
              }}
              className="ml-2 font-semibold text-[#858fe8]"
            >
              {isSignup ? "Sign in" : "Create account"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
