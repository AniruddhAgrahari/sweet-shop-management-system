import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setLoading(true);

    try {
      // Backend expects form-data (application/x-www-form-urlencoded)
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(
        'https://sweet-shop-management-system-production-df3f.up.railway.app/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // Save the access token to localStorage
      localStorage.setItem('access_token', response.data.access_token);
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Login failed. Please check your credentials and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);

    try {
      const payload = {
        username: username,
        email: email,
        password: password,
        role: "customer"
      };

      await axios.post(
        'https://sweet-shop-management-system-production-df3f.up.railway.app/auth/register',
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      setSuccessMessage('Registration successful! Please log in.');
      setIsRegistering(false);
      // Clear password field for security/convenience after registration
      setPassword('');
      setConfirmPassword('');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setError('');
    setSuccessMessage('');
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">🍬</div>
          <h1>Sweet Shop</h1>
          <p>Management System</p>
        </div>

        <form onSubmit={isRegistering ? handleRegister : handleLogin} className="login-form">
          {error && <div className="error-message">{error}</div>}
          {successMessage && <div className="success-message" style={{color: 'green', marginBottom: '1rem', textAlign: 'center'}}>{successMessage}</div>}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
          </div>

          {isRegistering && (
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                autoComplete="email"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete={isRegistering ? 'new-password' : 'current-password'}
            />
          </div>

          {isRegistering && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your password"
                required
                autoComplete="new-password"
              />
            </div>
          )}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? (isRegistering ? 'Registering...' : 'Logging in...') : (isRegistering ? 'Register' : 'Login')}
          </button>
        </form>

        <div className="login-footer">
          <button 
            onClick={toggleMode} 
            className="toggle-button"
            style={{
              background: 'none',
              border: 'none',
              color: '#007bff',
              cursor: 'pointer',
              textDecoration: 'underline',
              fontSize: '0.9rem',
              marginTop: '10px'
            }}
          >
            {isRegistering 
              ? "Already have an account? Login Here." 
              : "Need an account? Register Here."}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
