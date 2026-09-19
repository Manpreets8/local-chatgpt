import { useState } from "react";

import { loginUser, registerUser, setAuthToken } from "../services/api.js";

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isRegister = mode === "register";

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError("");
    setPassword("");
    setConfirmPassword("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (isRegister && password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }
    if (isRegister && password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setIsSubmitting(true);
    try {
      const data = isRegister
        ? await registerUser(email, password)
        : await loginUser(email, password);
      setAuthToken(data.access_token);
      onAuthenticated(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">Local ChatGPT</div>
        <h1 className="auth-heading">{isRegister ? "Create your account" : "Welcome back"}</h1>
        <p className="auth-subheading">
          {isRegister
            ? "Sign up to save your conversations and documents."
            : "Log in to continue where you left off."}
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-label" htmlFor="auth-email">
            Email
          </label>
          <input
            id="auth-email"
            type="email"
            className="auth-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            required
          />

          <label className="auth-label" htmlFor="auth-password">
            Password
          </label>
          <input
            id="auth-password"
            type="password"
            className="auth-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={isRegister ? "At least 8 characters" : "Your password"}
            autoComplete={isRegister ? "new-password" : "current-password"}
            required
          />

          {isRegister && (
            <>
              <label className="auth-label" htmlFor="auth-confirm-password">
                Confirm password
              </label>
              <input
                id="auth-confirm-password"
                type="password"
                className="auth-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your password"
                autoComplete="new-password"
                required
              />
            </>
          )}

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="auth-submit-button" disabled={isSubmitting}>
            {isSubmitting ? "Please wait…" : isRegister ? "Sign up" : "Log in"}
          </button>
        </form>

        <div className="auth-switch">
          {isRegister ? (
            <>
              Already have an account?{" "}
              <button type="button" className="auth-switch-link" onClick={() => switchMode("login")}>
                Log in
              </button>
            </>
          ) : (
            <>
              Don't have an account?{" "}
              <button
                type="button"
                className="auth-switch-link"
                onClick={() => switchMode("register")}
              >
                Sign up
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
