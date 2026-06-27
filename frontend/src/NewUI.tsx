import React, { useState } from 'react';
import './NewUI.css';

interface LoginState {
  isLoggedIn: boolean;
  username: string;
}

interface PredictionResult {
  predicted_class: string;
  confidence: number;
  solution: string | {
    problem: string;
    occurrence: string;
    natural_remedies: string | string[];
    chemical_remedies: string | string[];
    additional_advice: string;
  };
  prediction_type: string;
  issue_name?: string;
  type_name?: string;
  health_status?: string;
  requires_review?: boolean;
}

const NewUI: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<'home' | 'products' | 'analyser' | 'help'>('home');
  const [loginState, setLoginState] = useState<LoginState>({ isLoggedIn: false, username: '' });
  const [loginForm, setLoginForm] = useState({ username: '', password: '', rememberMe: false });
  const [registerForm, setRegisterForm] = useState({ 
    fullName: '', 
    email: '', 
    phone: '', 
    password: '', 
    confirmPassword: '' 
  });
  const [showRegister, setShowRegister] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  
  // Accordion state for features
  const [expandedFeature, setExpandedFeature] = useState<number | null>(null);
  
  // Analyser state
  const [selectedCrop, setSelectedCrop] = useState('rice');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<PredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Sample data for India's crop ranking
  const cropRankings = [
    { crop: 'Rice', rank: 2, production: '195.4 million tonnes' },
    { crop: 'Wheat', rank: 2, production: '109.5 million tonnes' },
    { crop: 'Sugarcane', rank: 2, production: '405.4 million tonnes' },
    { crop: 'Cotton', rank: 1, production: '36.5 million bales' },
  ];

  // Sample market prices by state
  const marketPrices = [
    { crop: 'Rice', state: 'Punjab', price: '₹2,200/quintal', trend: 'up' },
    { crop: 'Rice', state: 'Haryana', price: '₹2,150/quintal', trend: 'stable' },
    { crop: 'Wheat', state: 'Uttar Pradesh', price: '₹2,015/quintal', trend: 'up' },
    { crop: 'Wheat', state: 'Madhya Pradesh', price: '₹2,000/quintal', trend: 'down' },
    { crop: 'Cotton', state: 'Gujarat', price: '₹7,500/quintal', trend: 'up' },
    { crop: 'Cotton', state: 'Maharashtra', price: '₹7,350/quintal', trend: 'stable' },
    { crop: 'Sugarcane', state: 'Uttar Pradesh', price: '₹350/quintal', trend: 'stable' },
    { crop: 'Tomato', state: 'Karnataka', price: '₹35/kg', trend: 'down' },
  ];

  // Sample pesticides and fertilizers
  const pesticides = [
    { name: 'Neem Oil', type: 'Organic Pesticide', price: '₹450/liter', rating: 4.5 },
    { name: 'Chlorpyrifos 20% EC', type: 'Chemical Pesticide', price: '₹380/liter', rating: 4.2 },
    { name: 'Mancozeb 75% WP', type: 'Fungicide', price: '₹520/kg', rating: 4.6 },
    { name: 'Imidacloprid 17.8% SL', type: 'Insecticide', price: '₹680/liter', rating: 4.4 },
  ];

  const fertilizers = [
    { name: 'Urea (46-0-0)', type: 'Nitrogen Fertilizer', price: '₹268/50kg', rating: 4.7 },
    { name: 'DAP (18-46-0)', type: 'Phosphatic Fertilizer', price: '₹1,350/50kg', rating: 4.5 },
    { name: 'NPK (10-26-26)', type: 'Complex Fertilizer', price: '₹850/50kg', rating: 4.6 },
    { name: 'Vermicompost', type: 'Organic Fertilizer', price: '₹180/10kg', rating: 4.8 },
  ];

  // Government portals
  const govPortals = {
    central: [
      { name: 'PM-KISAN Portal', url: 'https://pmkisan.gov.in/', description: 'Direct income support to farmers' },
      { name: 'Soil Health Card', url: 'https://soilhealth.dac.gov.in/', description: 'Soil testing and health monitoring' },
      { name: 'PMFBY', url: 'https://pmfby.gov.in/', description: 'Pradhan Mantri Fasal Bima Yojana' },
    ],
    state: [
      { state: 'Haryana', name: 'Meri Fasal Mera Byora', url: 'https://fasal.haryana.gov.in/' },
      { state: 'Karnataka', name: 'RaitaMitra', url: 'https://raitamitra.karnataka.gov.in/' },
      { state: 'Tamil Nadu', name: 'TNAU Agritech Portal', url: 'https://agritech.tnau.ac.in/' },
      { state: 'Telangana', name: 'Rythu Bandhu', url: 'https://www.telangana.gov.in/departments/agriculture' },
      { state: 'Andhra Pradesh', name: 'AP Agriculture', url: 'https://www.apagrisnet.gov.in/' },
    ],
  };

  // App features
  const appFeatures = [
    { 
      icon: '🌾', 
      title: 'Multi-Crop Support', 
      description: 'Detect diseases in Rice, Wheat, Corn, Tomato, Potato, Cotton & Sugarcane' 
    },
    { 
      icon: '🔬', 
      title: 'AI-Powered Analysis', 
      description: '92% accuracy with EfficientNet-B0 and ResNet models' 
    },
    { 
      icon: '💡', 
      title: 'Smart Recommendations', 
      description: 'Get natural and chemical remedy suggestions powered by Gemini AI' 
    },
    { 
      icon: '📊', 
      title: 'Market Intelligence', 
      description: 'Real-time crop prices across major Indian states' 
    },
    { 
      icon: '🌍', 
      title: 'Multi-language Support', 
      description: 'Available in Hindi, English, and regional languages' 
    },
    { 
      icon: '📱', 
      title: 'Mobile Friendly', 
      description: 'Responsive design for smartphones and tablets' 
    },
  ];

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock validation
    if (loginForm.username === '' || loginForm.password === '') {
      setLoginError('Please enter both username and password');
      return;
    }
    if (loginForm.password.length < 6) {
      setLoginError('Invalid password. Password must be at least 6 characters.');
      setShowForgotPassword(true);
      return;
    }
    // Simulate successful login
    setLoginState({ isLoggedIn: true, username: loginForm.username });
    setLoginError('');
    setShowForgotPassword(false);
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (registerForm.password !== registerForm.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }
    // Simulate successful registration
    alert('Registration successful! Please login.');
    setShowRegister(false);
    setLoginForm({ ...loginForm, username: registerForm.email });
  };

  const handleLogout = () => {
    setLoginState({ isLoggedIn: false, username: '' });
    setCurrentPage('home');
  };

  const renderHealthStatus = (healthStatus?: string) => {
    if (!healthStatus) return null;
    
    const statusIcons: Record<string, string> = {
      Healthy: '✅',
      Unhealthy: '❌',
      Unknown: '❓',
    };

    return (
      <div className="health-status-badge">
        <span className="status-icon">{statusIcons[healthStatus] || '❓'}</span>
        <span className="status-text">{healthStatus}</span>
      </div>
    );
  };

  const renderSolution = (solution: PredictionResult['solution']) => {
    if (typeof solution === 'string') {
      return <div className="solution-text">{solution}</div>;
    }

    return (
      <div className="solution-structured">
        {solution.problem && (
          <div className="solution-section">
            <h4>Problem:</h4>
            <p>{solution.problem}</p>
          </div>
        )}
        {solution.occurrence && (
          <div className="solution-section">
            <h4>Occurrence:</h4>
            <p>{solution.occurrence}</p>
          </div>
        )}
        {solution.natural_remedies && (
          <div className="solution-section">
            <h4>🌿 Natural Remedies:</h4>
            {Array.isArray(solution.natural_remedies) ? (
              <ul className="recommendations-list">
                {solution.natural_remedies.map((remedy, index) => (
                  <li key={index}>{remedy}</li>
                ))}
              </ul>
            ) : (
              <p>{solution.natural_remedies}</p>
            )}
          </div>
        )}
        {solution.chemical_remedies && (
          <div className="solution-section">
            <h4>🧪 Chemical Remedies:</h4>
            {Array.isArray(solution.chemical_remedies) ? (
              <ul className="recommendations-list">
                {solution.chemical_remedies.map((remedy, index) => (
                  <li key={index}>{remedy}</li>
                ))}
              </ul>
            ) : (
              <p>{solution.chemical_remedies}</p>
            )}
          </div>
        )}
        {solution.additional_advice && (
          <div className="solution-section">
            <h4>💡 Additional Advice:</h4>
            <p>{solution.additional_advice}</p>
          </div>
        )}
      </div>
    );
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file
      if (!file.type.startsWith('image/')) {
        setLoginError('Please select a valid image file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setLoginError('File size must be less than 10MB');
        return;
      }
      
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
      setLoginError('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !selectedCrop) {
      alert('Please select an image first!');
      return;
    }
    
    setIsAnalyzing(true);
    setLoginError(''); // Reset any previous errors
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('crop', selectedCrop);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));

        if (response.status === 429) {
          setLoginError('Too many requests. Please wait a moment and try again.');
        } else if (response.status === 413) {
          setLoginError('File is too large. Please select a smaller image.');
        } else {
          setLoginError(errorData.detail || 'Prediction failed. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setLoginError('Network error. Please check if the backend server is running at http://localhost:8000');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderNavbar = () => (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <span className="brand-icon">🌾</span>
          <span className="brand-name">KrishiSetu</span>
        </div>
        <div className="navbar-menu">
          <a 
            className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            Home
          </a>
          <a 
            className={`nav-link ${currentPage === 'products' ? 'active' : ''}`}
            onClick={() => setCurrentPage('products')}
          >
            Products
          </a>
          <a 
            className={`nav-link ${currentPage === 'analyser' ? 'active' : ''}`}
            onClick={() => setCurrentPage('analyser')}
          >
            Analyser
          </a>
          <a 
            className={`nav-link ${currentPage === 'help' ? 'active' : ''}`}
            onClick={() => setCurrentPage('help')}
          >
            Help
          </a>
          {loginState.isLoggedIn ? (
            <div className="user-menu">
              <span className="username">👤 {loginState.username}</span>
              <button className="logout-btn" onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <button className="login-register-btn" onClick={() => setCurrentPage('home')}>
              Login / Register
            </button>
          )}
        </div>
      </div>
    </nav>
  );

  const renderHomePage = () => (
    <div className={`home-page ${loginState.isLoggedIn ? 'logged-in' : ''}`}>
      {/* Dynamic Left Side */}
      <div className="home-dynamic-section">
        <div className="hero-section">
          <h1 className="hero-title">Empowering Agriculture with AI Intelligence</h1>
          <p className="hero-subtitle">
            Detect plant diseases instantly, access real-time market prices, and connect with experts 
            using our advanced machine learning platform designed for modern farming.
          </p>
          {!loginState.isLoggedIn && (
            <button className="cta-button" onClick={() => setCurrentPage('analyser')}>
              Start Detection →
            </button>
          )}
        </div>

        {/* India's Crop Rankings */}
        <div className="section-card">
          <h2 className="section-title">🇮🇳 India's Global Crop Rankings</h2>
          <div className="rankings-grid">
            {cropRankings.map((item, index) => (
              <div key={index} className="ranking-card">
                <div className="ranking-badge">#{item.rank}</div>
                <h3>{item.crop}</h3>
                <p className="production-text">{item.production}</p>
                <p className="rank-label">World Rank</p>
              </div>
            ))}
          </div>
        </div>

        {/* App Features Accordion */}
        <div className="section-card">
          <h2 className="section-title">✨ Platform Features</h2>
          <div className="accordion-container">
            {appFeatures.map((feature, index) => (
              <div key={index} className="accordion-item">
                <div 
                  className={`accordion-title ${expandedFeature === index ? 'expanded' : ''}`}
                  onClick={() => setExpandedFeature(expandedFeature === index ? null : index)}
                >
                  <div className="accordion-title-content">
                    <span className="accordion-icon">{feature.icon}</span>
                    <span className="accordion-title-text">{feature.title}</span>
                  </div>
                  <span className="accordion-chevron">
                    {expandedFeature === index ? '▼' : '▶'}
                  </span>
                </div>
                {expandedFeature === index && (
                  <div className="accordion-panel">
                    <p>{feature.description}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* About Project */}
        <div className="section-card">
          <h2 className="section-title">📖 About KrishiSetu</h2>
          <div className="about-content">
            <p>
              KrishiSetu is a cloud-based platform that integrates machine learning, data analytics, 
              and user-friendly interfaces to assist farmers in managing crop health. Our AI models 
              achieve 92% accuracy in detecting diseases across 7 major crops including Rice, Wheat, 
              Corn, Tomato, Potato, Cotton, and Sugarcane.
            </p>
            <div className="stats-row">
              <div className="stat-item">
                <h3>50,000+</h3>
                <p>Training Images</p>
              </div>
              <div className="stat-item">
                <h3>92%</h3>
                <p>Accuracy Rate</p>
              </div>
              <div className="stat-item">
                <h3>7</h3>
                <p>Supported Crops</p>
              </div>
              <div className="stat-item">
                <h3>9</h3>
                <p>Pest Categories</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Static Right Side - Login Box (only shown when not logged in) */}
      {!loginState.isLoggedIn && (
        <div className="home-static-section">
          {!showRegister ? (
            <div className="login-box">
              <h2 className="login-title">Welcome Back</h2>
              <p className="login-subtitle">Enter your details to access your dashboard</p>
              
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label>Phone Number or Email</label>
                  <input
                    type="text"
                    placeholder="Enter phone or email"
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    className="form-input"
                  />
                </div>

                {loginError && (
                  <div className="error-message">
                    ⚠️ {loginError}
                  </div>
                )}

                <div className="form-options">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={loginForm.rememberMe}
                      onChange={(e) => setLoginForm({ ...loginForm, rememberMe: e.target.checked })}
                    />
                    <span>Remember me for 30 days</span>
                  </label>
                  {showForgotPassword && (
                    <a href="#" className="forgot-password">Forgot Password?</a>
                  )}
                </div>

                <button type="submit" className="submit-btn">
                  Sign In
                </button>

                <div className="divider">
                  <span>OR CONTINUE WITH</span>
                </div>

                <button type="button" className="otp-btn">
                  📱 Login with OTP
                </button>

                <p className="register-link">
                  Don't have an account yet? {' '}
                  <a href="#" onClick={(e) => { e.preventDefault(); setShowRegister(true); }}>
                    Register as a Farmer
                  </a>
                </p>
              </form>

              <div className="instant-diagnostics">
                <div className="instant-icon">🔍</div>
                <p>Instant Diagnostics</p>
                <span>Detect disease early with 92% accuracy</span>
              </div>
            </div>
          ) : (
            // Registration Form
            <div className="login-box register-box">
              <h2 className="login-title">Register as a Farmer</h2>
              <p className="login-subtitle">Join our community to secure your harvest</p>
              
              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    placeholder="Enter your full name"
                    value={registerForm.fullName}
                    onChange={(e) => setRegisterForm({ ...registerForm, fullName: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    placeholder="your.email@example.com"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    placeholder="10-digit mobile number"
                    value={registerForm.phone}
                    onChange={(e) => setRegisterForm({ ...registerForm, phone: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    placeholder="Create a strong password"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Confirm Password</label>
                  <input
                    type="password"
                    placeholder="Re-enter password"
                    value={registerForm.confirmPassword}
                    onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>

                <button type="submit" className="submit-btn">
                  Create Account
                </button>

                <p className="register-link">
                  Already have an account? {' '}
                  <a href="#" onClick={(e) => { e.preventDefault(); setShowRegister(false); }}>
                    Sign In
                  </a>
                </p>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderProductsPage = () => (
    <div className="products-page">
      <div className="page-header">
        <h1>Market & Products</h1>
        <p>Real-time crop prices and quality agricultural inputs</p>
      </div>

      {/* Market Prices Section */}
      <div className="section-card">
        <h2 className="section-title">📊 Market Prices by State</h2>
        <div className="market-grid">
          {marketPrices.map((item, index) => (
            <div key={index} className="market-card">
              <div className="market-header">
                <h3>{item.crop}</h3>
                <span className={`trend-badge ${item.trend}`}>
                  {item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➡️'}
                </span>
              </div>
              <p className="state-name">{item.state}</p>
              <p className="price">{item.price}</p>
              <p className="trend-text">
                {item.trend === 'up' ? 'Rising' : item.trend === 'down' ? 'Falling' : 'Stable'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Pesticides Section */}
      <div className="section-card">
        <h2 className="section-title">🛡️ Pesticides & Fungicides</h2>
        <div className="products-grid">
          {pesticides.map((item, index) => (
            <div key={index} className="product-card">
              <div className="product-image">
                <div className="placeholder-icon">🧪</div>
              </div>
              <div className="product-info">
                <h3>{item.name}</h3>
                <p className="product-type">{item.type}</p>
                <div className="product-footer">
                  <span className="product-price">{item.price}</span>
                  <span className="product-rating">⭐ {item.rating}</span>
                </div>
                <button className="add-cart-btn">View Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fertilizers Section */}
      <div className="section-card">
        <h2 className="section-title">🌱 Fertilizers</h2>
        <div className="products-grid">
          {fertilizers.map((item, index) => (
            <div key={index} className="product-card">
              <div className="product-image">
                <div className="placeholder-icon">💊</div>
              </div>
              <div className="product-info">
                <h3>{item.name}</h3>
                <p className="product-type">{item.type}</p>
                <div className="product-footer">
                  <span className="product-price">{item.price}</span>
                  <span className="product-rating">⭐ {item.rating}</span>
                </div>
                <button className="add-cart-btn">View Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalyserPage = () => (
    <div className="analyser-page">
      <div className="page-header">
        <h1>Plant Disease Analyser</h1>
        <p>Upload an image to detect crop diseases with AI-powered precision</p>
      </div>

      <div className="analyser-content">
        <div className="analyser-left">
          <div className="upload-section">
            <h3>Select Crop Type</h3>
            <select 
              className="crop-select"
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              <option value="rice">🌾 Rice</option>
              <option value="wheat">🌾 Wheat</option>
              <option value="corn">🌽 Corn/Maize</option>
              <option value="tomato">🍅 Tomato</option>
              <option value="potato">🥔 Potato</option>
              <option value="cotton">⚪ Cotton</option>
              <option value="sugarcane">🎋 Sugarcane</option>
            </select>
          </div>

          <div className="upload-section">
            <h3>Upload Plant Image</h3>
            {loginError && (
              <div className="error-message">
                ⚠️ {loginError}
              </div>
            )}
            <label className="file-upload-area">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input-hidden"
              />
              <div className="upload-placeholder">
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" className="preview-image" />
                ) : (
                  <>
                    <div className="upload-icon">📸</div>
                    <p>Click or Drag Image Here</p>
                    <span>Supports: JPG, PNG (Max 10MB)</span>
                  </>
                )}
              </div>
            </label>
          </div>

          <button 
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
          >
            {isAnalyzing ? '🔄 Analyzing...' : '🔬 Analyze Now'}
          </button>
        </div>

        <div className="analyser-right">
          {analysisResult ? (
            <div className="results-section">
              <div className="result-header">
                <h2>Analysis Results</h2>
                <span className="confidence-badge">
                  Confidence: {(analysisResult.confidence * 100).toFixed(1)}%
                </span>
              </div>

              <div className="result-info">
                <div className="info-row">
                  <span className="label">Crop:</span>
                  <span className="value">{selectedCrop.charAt(0).toUpperCase() + selectedCrop.slice(1)}</span>
                </div>
                <div className="info-row">
                  <span className="label">Detected:</span>
                  <span className="value disease-name">{analysisResult.predicted_class}</span>
                </div>
                <div className="info-row">
                  <span className="label">Type:</span>
                  <span className="value">{analysisResult.prediction_type}</span>
                </div>
                {analysisResult.health_status && (
                  <div className="info-row">
                    <span className="label">Health Status:</span>
                    {renderHealthStatus(analysisResult.health_status)}
                  </div>
                )}
                {analysisResult.requires_review && (
                  <div className="review-notice">
                    ⚠️ This result requires expert review for confirmation
                  </div>
                )}
              </div>

              {analysisResult.solution && (
                <div className="recommendations">
                  <h3>💡 Recommendations</h3>
                  {renderSolution(analysisResult.solution)}
                </div>
              )}

              <button className="new-analysis-btn" onClick={() => {
                setAnalysisResult(null);
                setSelectedFile(null);
                setPreviewUrl('');
                setLoginError('');
              }}>
                📋 New Analysis
              </button>
            </div>
          ) : (
            <div className="placeholder-section">
              <div className="placeholder-icon-large">🔬</div>
              <h3>Waiting for Analysis</h3>
              <p>Select a crop type and upload an image to get started</p>
              <div className="info-cards">
                <div className="info-card">
                  <h4>🎯 High Accuracy</h4>
                  <p>92% detection rate</p>
                </div>
                <div className="info-card">
                  <h4>⚡ Fast Results</h4>
                  <p>Results in seconds</p>
                </div>
                <div className="info-card">
                  <h4>🤖 AI-Powered</h4>
                  <p>EfficientNet-B0 model</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderHelpPage = () => (
    <div className="help-page">
      <div className="page-header">
        <h1>Help & Support</h1>
        <p>Access government schemes, portals, and agricultural resources</p>
      </div>

      {/* Central Government Portals */}
      <div className="section-card">
        <h2 className="section-title">🏛️ Central Government Portals</h2>
        <div className="portals-grid">
          {govPortals.central.map((portal, index) => (
            <div key={index} className="portal-card">
              <div className="portal-icon">🔗</div>
              <h3>{portal.name}</h3>
              <p>{portal.description}</p>
              <a href={portal.url} target="_blank" rel="noopener noreferrer" className="portal-link">
                Visit Portal →
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* State Government Portals */}
      <div className="section-card">
        <h2 className="section-title">🗺️ State Government Portals</h2>
        <div className="state-portals-grid">
          {govPortals.state.map((portal, index) => (
            <div key={index} className="state-portal-card">
              <div className="state-header">
                <span className="state-badge">{portal.state}</span>
                <h3>{portal.name}</h3>
              </div>
              <a href={portal.url} target="_blank" rel="noopener noreferrer" className="portal-link">
                Visit Portal →
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Contact Support */}
      <div className="section-card">
        <h2 className="section-title">📞 Contact & Support</h2>
        <div className="contact-grid">
          <div className="contact-card">
            <div className="contact-icon">📱</div>
            <h3>Kisan Call Centre</h3>
            <p className="contact-value">1800-180-1551</p>
            <p className="contact-desc">Toll-free helpline (Available 6 AM - 10 PM)</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon">💬</div>
            <h3>WhatsApp Support</h3>
            <p className="contact-value">+91-XXXXXXXXXX</p>
            <p className="contact-desc">Get instant support via WhatsApp</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon">✉️</div>
            <h3>Email Support</h3>
            <p className="contact-value">support@krishisetu.in</p>
            <p className="contact-desc">Response within 24 hours</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon">🌐</div>
            <h3>Weather Alert</h3>
            <p className="contact-value">IMD Weather Updates</p>
            <p className="contact-desc">Get localized weather forecasts</p>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="section-card">
        <h2 className="section-title">❓ Frequently Asked Questions</h2>
        <div className="faq-list">
          <details className="faq-item">
            <summary>How accurate is the disease detection?</summary>
            <p>Our AI models achieve 92% accuracy on average, trained on over 50,000 images across multiple crops.</p>
          </details>
          <details className="faq-item">
            <summary>Which crops are supported?</summary>
            <p>Currently supporting Rice, Wheat, Corn, Tomato, Potato, Cotton, and Sugarcane with more crops coming soon.</p>
          </details>
          <details className="faq-item">
            <summary>Is the service free for farmers?</summary>
            <p>Yes! KrishiSetu is completely free for all Indian farmers as part of our mission to support agriculture.</p>
          </details>
          <details className="faq-item">
            <summary>How do I get market price updates?</summary>
            <p>Visit the Products page to see real-time market prices across different states, updated daily.</p>
          </details>
        </div>
      </div>
    </div>
  );

  return (
    <div className="new-ui-app">
      {renderNavbar()}
      <main className="main-content">
        {currentPage === 'home' && renderHomePage()}
        {currentPage === 'products' && renderProductsPage()}
        {currentPage === 'analyser' && renderAnalyserPage()}
        {currentPage === 'help' && renderHelpPage()}
      </main>
      <footer className="footer">
        <p>© 2024 KrishiSetu. All rights reserved. | Empowering farmers with AI-powered plant health detection</p>
      </footer>
    </div>
  );
};

export default NewUI;
