import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../dashboard.css';

const API_URL = 'http://127.0.0.1:8000';

function Dashboard() {
  const navigate = useNavigate();
  const [sweets, setSweets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [purchasingId, setPurchasingId] = useState(null);
  
  // Add Sweet Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    price: '',
    quantity: '',
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      Authorization: `Bearer ${token}`,
    };
  };

  const fetchSweets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/sweets/`, {
        headers: getAuthHeaders(),
      });
      setSweets(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load sweets. Please try again.');
      console.error('Error fetching sweets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSweets();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const handlePurchase = async (sweetId) => {
    try {
      setPurchasingId(sweetId);
      const response = await axios.post(
        `${API_URL}/sweets/${sweetId}/purchase`,
        {},
        { headers: getAuthHeaders() }
      );
      
      // Update the local state to reflect the purchase
      setSweets((prevSweets) =>
        prevSweets.map((sweet) =>
          sweet.id === sweetId
            ? { ...sweet, quantity: response.data.remaining_stock }
            : sweet
        )
      );
    } catch (err) {
      if (err.response?.status === 400) {
        alert(err.response.data.detail || 'Out of stock!');
      } else {
        alert('Purchase failed. Please try again.');
      }
      console.error('Error purchasing sweet:', err);
    } finally {
      setPurchasingId(null);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleAddSweet = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.name || !formData.category || !formData.price || !formData.quantity) {
      alert('Please fill in all fields.');
      return;
    }

    try {
      setFormLoading(true);
      const sweetData = {
        name: formData.name,
        category: formData.category,
        price: parseFloat(formData.price),
        quantity: parseInt(formData.quantity, 10),
      };

      await axios.post(`${API_URL}/sweets/`, sweetData, {
        headers: getAuthHeaders(),
      });

      // Clear form and hide it
      setFormData({ name: '', category: '', price: '', quantity: '' });
      setShowAddForm(false);
      
      // Refresh the sweets list
      await fetchSweets();
    } catch (err) {
      alert('Failed to add sweet. Please try again.');
      console.error('Error adding sweet:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const getCategoryEmoji = (category) => {
    const emojiMap = {
      chocolate: '🍫',
      candy: '🍬',
      cake: '🎂',
      cookie: '🍪',
      ice_cream: '🍦',
      default: '🍭',
    };
    return emojiMap[category?.toLowerCase()] || emojiMap.default;
  };

  return (
    <div className="dashboard">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="navbar-icon">🍬</span>
          <h1>Sweet Shop</h1>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          <span>Logout</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <div className="page-header">
          <h2>Our Sweets Collection</h2>
          <p>Browse and purchase your favorite treats!</p>
        </div>

        {/* Add Sweet Button */}
        <div className="admin-actions">
          <button
            className={`add-sweet-btn ${showAddForm ? 'active' : ''}`}
            onClick={() => setShowAddForm(!showAddForm)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            {showAddForm ? 'Cancel' : 'Add New Sweet'}
          </button>
        </div>

        {/* Add Sweet Form */}
        {showAddForm && (
          <div className="add-sweet-form-container">
            <form className="add-sweet-form" onSubmit={handleAddSweet}>
              <h3>Add New Sweet</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="name">Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    placeholder="e.g., Chocolate Truffle"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <input
                    type="text"
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleFormChange}
                    placeholder="e.g., Chocolate"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="price">Price ($)</label>
                  <input
                    type="number"
                    id="price"
                    name="price"
                    value={formData.price}
                    onChange={handleFormChange}
                    placeholder="e.g., 4.99"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="quantity">Quantity</label>
                  <input
                    type="number"
                    id="quantity"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleFormChange}
                    placeholder="e.g., 50"
                    min="0"
                    required
                  />
                </div>
              </div>
              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => {
                    setShowAddForm(false);
                    setFormData({ name: '', category: '', price: '', quantity: '' });
                  }}
                >
                  Cancel
                </button>
                <button type="submit" className="submit-btn" disabled={formLoading}>
                  {formLoading ? 'Adding...' : 'Add Sweet'}
                </button>
              </div>
            </form>
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading sweets...</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <p>{error}</p>
            <button onClick={fetchSweets} className="retry-btn">
              Try Again
            </button>
          </div>
        )}

        {!loading && !error && sweets.length === 0 && (
          <div className="empty-container">
            <span className="empty-icon">🍭</span>
            <p>No sweets available at the moment.</p>
          </div>
        )}

        {!loading && !error && sweets.length > 0 && (
          <div className="sweets-grid">
            {sweets.map((sweet) => (
              <div key={sweet.id} className="sweet-card">
                <div className="card-emoji">{getCategoryEmoji(sweet.category)}</div>
                <div className="card-content">
                  <h3 className="card-title">{sweet.name}</h3>
                  <span className="card-category">{sweet.category}</span>
                  <div className="card-details">
                    <div className="card-price">${sweet.price.toFixed(2)}</div>
                    <div className={`card-stock ${sweet.quantity === 0 ? 'out-of-stock' : ''}`}>
                      {sweet.quantity > 0 ? `${sweet.quantity} in stock` : 'Out of stock'}
                    </div>
                  </div>
                </div>
                <button
                  className={`buy-btn ${sweet.quantity === 0 ? 'disabled' : ''}`}
                  disabled={sweet.quantity === 0 || purchasingId === sweet.id}
                  onClick={() => handlePurchase(sweet.id)}
                >
                  {purchasingId === sweet.id
                    ? 'Purchasing...'
                    : sweet.quantity === 0
                    ? 'Out of Stock'
                    : 'Buy Now'}
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
