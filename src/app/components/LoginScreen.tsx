import { useState } from "react";
import { Pill, Mail, Lock, User, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../../lib/auth";

export function LoginScreen({ darkMode }: { darkMode: boolean }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const inputClass = `w-full flex items-center rounded-xl px-4 py-3 min-h-[48px] ${
    darkMode
      ? "bg-gray-800 border border-gray-700 text-white placeholder-gray-500"
      : "bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400"
  }`;

  return (
    <div
      className={`min-h-screen flex items-center justify-center px-4 ${
        darkMode ? "bg-gray-950" : "bg-gray-50"
      }`}
    >
      <div
        className={`w-full max-w-md rounded-2xl p-8 ${
          darkMode
            ? "bg-gray-900 border border-gray-800"
            : "bg-white border border-gray-100 shadow-lg"
        }`}
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-blue-500 flex items-center justify-center shadow-lg mb-3">
            <Pill className="w-7 h-7 text-white" />
          </div>
          <h1
            className={`text-2xl font-bold ${darkMode ? "text-white" : "text-blue-900"}`}
          >
            MediGuide
          </h1>
          <p
            className={`text-sm ${darkMode ? "text-blue-400" : "text-blue-500"}`}
          >
            AI Pharmaceutical Assistant
          </p>
        </div>

        {/* Tab switcher */}
        <div
          className={`flex rounded-xl p-1 mb-6 ${
            darkMode ? "bg-gray-800" : "bg-gray-100"
          }`}
        >
          {(["login", "register"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setMode(tab);
                setError("");
              }}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                mode === tab
                  ? darkMode
                    ? "bg-blue-600 text-white shadow"
                    : "bg-white text-blue-600 shadow"
                  : darkMode
                    ? "text-gray-400"
                    : "text-gray-500"
              }`}
            >
              {tab === "login" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div className="relative">
              <User
                className={`absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 ${
                  darkMode ? "text-gray-500" : "text-gray-400"
                }`}
              />
              <input
                type="text"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className={`${inputClass} pl-11`}
              />
            </div>
          )}

          <div className="relative">
            <Mail
              className={`absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 ${
                darkMode ? "text-gray-500" : "text-gray-400"
              }`}
            />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className={`${inputClass} pl-11`}
            />
          </div>

          <div className="relative">
            <Lock
              className={`absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 ${
                darkMode ? "text-gray-500" : "text-gray-400"
              }`}
            />
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className={`${inputClass} pl-11 pr-11`}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                darkMode ? "text-gray-500" : "text-gray-400"
              }`}
            >
              {showPassword ? (
                <EyeOff className="w-5 h-5" />
              ) : (
                <Eye className="w-5 h-5" />
              )}
            </button>
          </div>

          {error && (
            <div className="px-4 py-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-blue-500 text-white font-semibold text-sm min-h-[48px] shadow-md disabled:opacity-50 active:scale-[0.98] transition-transform"
          >
            {loading
              ? "Please wait..."
              : mode === "login"
                ? "Sign In"
                : "Create Account"}
          </button>
        </form>

        <p
          className={`mt-6 text-center text-xs ${
            darkMode ? "text-gray-500" : "text-gray-400"
          }`}
        >
          Not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
}
