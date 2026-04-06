import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { loginUser } from "../services/authService";
import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  // 1. Setup state for the form inputs
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [signingIn, setSigningIn] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(""); // Clear previous errors
    setSigningIn(true);

    try {
      const data = await loginUser(email, password);
      login(data.access_token);
      navigate("/ask");
    } catch (err) {
      setError(err.message || "Invalid email or password");
    } finally {
      setSigningIn(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Welcome back</h1>
        <p className="login-subtitle">Sign in to Smart Campus</p>

        {/* Show error message if login fails */}
        {error && (
          <p style={{ color: "#ff4d4d", fontSize: "0.9rem" }}>{error}</p>
        )}

        <form onSubmit={handleSignIn}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              placeholder="you@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="login-btn" disabled={signingIn}>
            {signingIn ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="login-footer">
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
