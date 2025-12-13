import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../dashboard.css';
import { getUserRole } from '../authUtils';

const API_URL = 'http://127.0.0.1:8000';

function Dashboard() {
  const userRole = getUserRole();
  const isAdmin = userRole === 'admin';
  const navigate = useNavigate();
  const [sweets, setSweets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [purchasingId, setPurchasingId] = useState(null);

  // Quantity selector per sweet id
  const [purchaseQtyById, setPurchaseQtyById] = useState({});

  // Simple toast popup state
  const [toastMessage, setToastMessage] = useState('');
  const toastTimerRef = useRef(null);
  
  // Add Sweet Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    price: '',
    quantity: '',
  });

  // Filter State (Flipkart-style drawer)
  const [queryName, setQueryName] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    category: true,
    price: true,
  });
  const [categorySearch, setCategorySearch] = useState('');
  const [categoryOptions, setCategoryOptions] = useState([]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      Authorization: `Bearer ${token}`,
    };
  };

  const fetchSweets = async (override = null) => {
    const state = override || {
      queryName,
      selectedCategories,
      priceMin,
      priceMax,
    };

    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (state.queryName?.trim()) params.append('name', state.queryName.trim());
      if (state.selectedCategories?.length) params.append('category', state.selectedCategories.join(','));
      if (state.priceMin !== '' && state.priceMin !== null && state.priceMin !== undefined) params.append('min_price', state.priceMin);
      if (state.priceMax !== '' && state.priceMax !== null && state.priceMax !== undefined) params.append('max_price', state.priceMax);

      const url = `${API_URL}/sweets/search?${params.toString()}`;
      
      const response = await axios.get(url, {
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

  const fetchCategoryOptions = async () => {
    try {
      const response = await axios.get(`${API_URL}/sweets/`, {
        headers: getAuthHeaders(),
      });
      const all = Array.isArray(response.data) ? response.data : [];
      const categories = Array.from(
        new Set(
          all
            .map((s) => (s?.category ?? '').toString().trim())
            .filter(Boolean)
        )
      ).sort((a, b) => a.localeCompare(b));
      setCategoryOptions(categories);
    } catch (err) {
      // Non-fatal: filtering still works, user just won't see category suggestions
      console.error('Error fetching categories:', err);
    }
  };

  useEffect(() => {
    fetchCategoryOptions();
    fetchSweets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const hasActiveFilters = Boolean(
    queryName.trim() || selectedCategories.length || priceMin !== '' || priceMax !== ''
  );
  const activeFilterCount =
    (queryName.trim() ? 1 : 0) +
    (selectedCategories.length ? 1 : 0) +
    (priceMin !== '' || priceMax !== '' ? 1 : 0);

  const handleSearchSubmit = (e) => {
    if (e?.preventDefault) e.preventDefault();
    fetchSweets();
  };

  const handleClearAll = () => {
    setQueryName('');
    setSelectedCategories([]);
    setPriceMin('');
    setPriceMax('');
    setCategorySearch('');
    fetchSweets({ queryName: '', selectedCategories: [], priceMin: '', priceMax: '' });
  };

  const toggleCategory = (category) => {
    setSelectedCategories((prev) => {
      if (prev.includes(category)) return prev.filter((c) => c !== category);
      return [...prev, category];
    });
  };

  const toggleSection = (key) => {
    setExpandedSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const getPurchaseQty = (sweet) => {
    const raw = purchaseQtyById?.[sweet.id];
    const parsed = Number.parseInt(raw, 10);
    const safe = Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
    const max = Number(sweet.quantity || 0);
    if (max <= 0) return 1;
    return Math.min(safe, max);
  };

  const adjustQty = (sweet, delta) => {
    const current = getPurchaseQty(sweet);
    const max = Number(sweet.quantity || 0);
    const next = Math.min(max, Math.max(1, current + delta));
    setPurchaseQtyById((prev) => ({ ...prev, [sweet.id]: next }));
  };

  const handlePurchase = async (sweet, quantity) => {
    try {
      setPurchasingId(sweet.id);
      const response = await axios.post(
        `${API_URL}/sweets/${sweet.id}/purchase?quantity=${encodeURIComponent(quantity)}`,
        {},
        { headers: getAuthHeaders() }
      );
      
      // Update the local state to reflect the purchase
      setSweets((prevSweets) =>
        prevSweets.map((s) =>
          s.id === sweet.id
            ? { ...s, quantity: response.data.remaining_stock }
            : s
        )
      );

      // Reset qty back to 1 (or keep it capped) after successful purchase
      setPurchaseQtyById((prev) => ({ ...prev, [sweet.id]: 1 }));

      // Success popup
      const purchasedQty = response.data?.purchased_qty ?? quantity;
      const baseMsg = response.data?.message || 'Purchase successful';
      setToastMessage(`${baseMsg}${purchasedQty ? ` (x${purchasedQty})` : ''}`);
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
      toastTimerRef.current = setTimeout(() => setToastMessage(''), 2500);
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

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

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
      {toastMessage && (
        <div className="toast-container" aria-live="polite" aria-atomic="true">
          <div className="toast toast-success">{toastMessage}</div>
        </div>
      )}
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
          <h2>{isAdmin ? 'Admin Page' : 'Our Sweets Collection'}</h2>
          {!isAdmin && <p>Browse and purchase your favorite treats!</p>}
        </div>

        {/* Search + Filters (Flipkart-style) */}
        <div className="search-container">
          <form className="search-form" onSubmit={handleSearchSubmit}>
            <div className="search-input-wrapper">
              <svg className="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                type="text"
                className="search-input"
                placeholder="Search sweets by name..."
                value={queryName}
                onChange={(e) => setQueryName(e.target.value)}
              />
              {queryName && (
                <button type="button" className="clear-search-btn" onClick={() => setQueryName('')}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              )}
            </div>

            <button type="button" className="filter-open-btn" onClick={() => setIsFilterOpen(true)}>
              Filters{activeFilterCount ? ` (${activeFilterCount})` : ''}
            </button>

            <button type="submit" className="search-btn">
              Search
            </button>

            {hasActiveFilters && (
              <button type="button" className="clear-results-btn" onClick={handleClearAll}>
                Clear
              </button>
            )}
          </form>
        </div>

        {isFilterOpen && (
          <div className="filter-overlay" role="dialog" aria-modal="true" onClick={() => setIsFilterOpen(false)}>
            <aside className="filter-drawer" onClick={(e) => e.stopPropagation()}>
              <div className="filter-header">
                <h3>Filters</h3>
                <button type="button" className="filter-close-btn" onClick={() => setIsFilterOpen(false)} aria-label="Close filters">
                  ×
                </button>
              </div>

              <div className="filter-body">
                <button type="button" className="filter-section-title" onClick={() => toggleSection('category')}>
                  <span>Category</span>
                  <span className={`filter-caret ${expandedSections.category ? 'open' : ''}`}>▾</span>
                </button>
                {expandedSections.category && (
                  <div className="filter-section-content">
                    <input
                      className="filter-section-search"
                      type="text"
                      placeholder="Search category"
                      value={categorySearch}
                      onChange={(e) => setCategorySearch(e.target.value)}
                    />
                    <div className="filter-checkbox-list">
                      {categoryOptions
                        .filter((c) => c.toLowerCase().includes(categorySearch.trim().toLowerCase()))
                        .map((category) => (
                          <label key={category} className="filter-checkbox-item">
                            <input
                              type="checkbox"
                              checked={selectedCategories.includes(category)}
                              onChange={() => toggleCategory(category)}
                            />
                            <span>{category}</span>
                          </label>
                        ))}
                      {categoryOptions.length === 0 && (
                        <div className="filter-empty">No categories found</div>
                      )}
                    </div>
                  </div>
                )}

                <button type="button" className="filter-section-title" onClick={() => toggleSection('price')}>
                  <span>Price</span>
                  <span className={`filter-caret ${expandedSections.price ? 'open' : ''}`}>▾</span>
                </button>
                {expandedSections.price && (
                  <div className="filter-section-content">
                    <div className="filter-price-row">
                      <input
                        className="filter-price-input"
                        type="number"
                        min="0"
                        placeholder="Min"
                        value={priceMin}
                        onChange={(e) => setPriceMin(e.target.value)}
                      />
                      <span className="filter-price-sep">to</span>
                      <input
                        className="filter-price-input"
                        type="number"
                        min="0"
                        placeholder="Max"
                        value={priceMax}
                        onChange={(e) => setPriceMax(e.target.value)}
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="filter-footer">
                <button type="button" className="filter-clear-btn" onClick={handleClearAll}>
                  Clear All
                </button>
                <button
                  type="button"
                  className="filter-apply-btn"
                  onClick={() => {
                    fetchSweets();
                    setIsFilterOpen(false);
                  }}
                >
                  Apply
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* Add Sweet Button */}
        <div className="admin-actions">
          {isAdmin && (
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
          )}
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
            <p>{hasActiveFilters ? 'No sweets match your filters.' : 'No sweets available at the moment.'}</p>
            {hasActiveFilters && (
              <button className="retry-btn" onClick={handleClearAll}>
                Clear Filters
              </button>
            )}
          </div>
        )}

        {!loading && !error && sweets.length > 0 && (
          <div className="sweets-grid">
            {sweets.map((sweet) => (
              <div key={sweet.id} className="sweet-card">
                <div className="card-media">
                  {sweet.image_url ? (
                    <img
                      className="sweet-image"
                      src={sweet.image_url}
                      alt={sweet.name}
                      loading="lazy"
                    />
                  ) : (
                    <span className="card-emoji">{getCategoryEmoji(sweet.category)}</span>
                  )}
                </div>
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
                {!isAdmin && (
                  <div className="qty-row">
                    <div className="qty-stepper" aria-label="Select quantity">
                      <button
                        type="button"
                        className="qty-btn"
                        onClick={() => adjustQty(sweet, -1)}
                        disabled={sweet.quantity <= 0 || purchasingId === sweet.id || getPurchaseQty(sweet) <= 1}
                        aria-label="Decrease quantity"
                      >
                        −
                      </button>
                      <span className="qty-value" aria-label="Selected quantity">
                        {getPurchaseQty(sweet)}
                      </span>
                      <button
                        type="button"
                        className="qty-btn"
                        onClick={() => adjustQty(sweet, +1)}
                        disabled={
                          sweet.quantity <= 0 ||
                          purchasingId === sweet.id ||
                          getPurchaseQty(sweet) >= sweet.quantity
                        }
                        aria-label="Increase quantity"
                      >
                        +
                      </button>
                    </div>

                    <button
                      className={`buy-btn ${sweet.quantity === 0 ? 'disabled' : ''}`}
                      disabled={sweet.quantity === 0 || purchasingId === sweet.id}
                      onClick={() => handlePurchase(sweet, getPurchaseQty(sweet))}
                    >
                    {purchasingId === sweet.id
                      ? 'Purchasing...'
                      : sweet.quantity === 0
                      ? 'Out of Stock'
                      : 'Buy Now'}
                    </button>
                  </div>
                )}
                {isAdmin && (
                  <div className="admin-card-actions" style={{ marginTop: '10px', display: 'flex', gap: '5px' }}>
                    <button
                      className="buy-btn"
                      style={{ backgroundColor: '#2196F3', flex: 1 }}
                      onClick={async () => {
                        const qtyStr = prompt('Enter quantity to restock:', '10');
                        if (!qtyStr) return;
                        const qty = parseInt(qtyStr, 10);
                        if (isNaN(qty) || qty <= 0) {
                          alert('Invalid quantity');
                          return;
                        }
                        try {
                          const response = await axios.post(
                            `${API_URL}/sweets/${sweet.id}/restock?quantity=${qty}`,
                            {},
                            { headers: getAuthHeaders() }
                          );
                          // Update local state
                          setSweets((prev) =>
                            prev.map((s) =>
                              s.id === sweet.id ? { ...s, quantity: response.data.new_stock } : s
                            )
                          );
                          alert(`Restocked! New quantity: ${response.data.new_stock}`);
                        } catch (err) {
                          console.error(err);
                          alert('Restock failed');
                        }
                      }}
                    >
                      Restock
                    </button>
                    <button
                      className="buy-btn"
                      style={{ backgroundColor: '#f44336', flex: 1 }}
                      onClick={async () => {
                        if (!window.confirm(`Are you sure you want to delete "${sweet.name}"?`)) return;
                        try {
                          await axios.delete(`${API_URL}/sweets/${sweet.id}`, {
                            headers: getAuthHeaders(),
                          });
                          // Remove from local state
                          setSweets((prev) => prev.filter((s) => s.id !== sweet.id));
                        } catch (err) {
                          console.error(err);
                          alert('Delete failed');
                        }
                      }}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
