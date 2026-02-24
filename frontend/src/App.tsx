import React, { useState } from 'react';
import './App.css';

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
  health_status?: string; // Added health_status field
}

interface ErrorState {
  message: string;
  type: 'error' | 'warning' | 'info';
}

const SUPPORTED_CROPS = [
  { value: 'rice', label: 'Rice' },
  { value: 'wheat', label: 'Wheat' },
  { value: 'corn', label: 'Corn/Maize' },
  { value: 'tomato', label: 'Tomato' },
  { value: 'potato', label: 'Potato' },
  { value: 'cotton', label: 'Cotton' },
  { value: 'sugarcane', label: 'Sugarcane' }
];

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedCrop, setSelectedCrop] = useState<string>('rice');
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);

  const validateFile = (file: File): string | null => {
    if (!file.type.startsWith('image/')) {
      return 'Please select a valid image file (JPG, PNG, etc.)';
    }
    if (file.size > 10 * 1024 * 1024) {
      return 'File size must be less than 10MB';
    }
    if (file.name.length > 255) {
      return 'File name is too long';
    }
    return null;
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const validationError = validateFile(file);
      if (validationError) {
        setError({ message: validationError, type: 'error' });
        return;
      }
      setSelectedFile(file);
      setPrediction(null);
      setError(null);
    }
  };

  const renderHealthStatus = (healthStatus: string) => {
    const statusIcons: Record<string, string> = {
      Healthy: '✅',
      Unhealthy: '❌',
      Good: '😊',
      Average: '😐',
      Bad: '😟',
    };

    const primaryStatus = healthStatus === 'Healthy' || healthStatus === 'Unhealthy' ? healthStatus : null;
    const secondaryStatus = primaryStatus ? null : healthStatus;

    return (
      <div className="health-status">
        {primaryStatus && (
          <div className="primary-status">
            <h4>Health Status:</h4>
            <p>
              {statusIcons[primaryStatus]} {primaryStatus}
            </p>
          </div>
        )}
        {secondaryStatus && (
          <div className="secondary-status">
            <h4>Condition:</h4>
            <p>
              {statusIcons[secondaryStatus]} {secondaryStatus}
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderSolution = (solution: PredictionResult['solution'], healthStatus: string) => {
    return (
      <div>
        {renderHealthStatus(healthStatus)}
        {typeof solution === 'string' ? (
          <div className="solution-text">{solution}</div>
        ) : (
          <div className="solution-structured">
            {solution.problem && (
              <div className="solution-section">
                <h5>Problem:</h5>
                <p>{solution.problem}</p>
              </div>
            )}
            {solution.occurrence && (
              <div className="solution-section">
                <h5>Occurrence:</h5>
                <p>{solution.occurrence}</p>
              </div>
            )}
            {solution.natural_remedies && (
              <div className="solution-section">
                <h5>Natural Remedies:</h5>
                {Array.isArray(solution.natural_remedies) ? (
                  <ul>
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
                <h5>Chemical Remedies:</h5>
                {Array.isArray(solution.chemical_remedies) ? (
                  <ul>
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
                <h5>Additional Advice:</h5>
                <p>{solution.additional_advice}</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !selectedCrop) return;

    setLoading(true);
    setError(null);
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
        setPrediction(result);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));

        if (response.status === 429) {
          setError({ message: 'Too many requests. Please wait a moment and try again.', type: 'warning' });
        } else if (response.status === 413) {
          setError({ message: 'File is too large. Please select a smaller image.', type: 'error' });
        } else {
          setError({ message: errorData.detail || 'Prediction failed. Please try again.', type: 'error' });
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setError({ 
        message: 'Network error. Please check your connection and try again.', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="main-wrapper">
        <div className="header">
          <h1>KrishiSetu - Plant Health Detection</h1>
        </div>
        
        <div className="content-container">
          <div className="sidebar">
            <h3>Market Prices</h3>
            <div className="price-item">Rice: ₹2,500/quintal</div>
            <div className="price-item">Wheat: ₹2,200/quintal</div>
            <div className="price-item">Corn: ₹1,800/quintal</div>
            
            <h3>Government Schemes</h3>
            <div className="scheme-item">PM-KISAN</div>
            <div className="scheme-item">Crop Insurance</div>
            <div className="scheme-item">Soil Health Card</div>
          </div>

          <div className="main-content">
            <div className="upload-section">
              {error && (
                <div className={`error-message ${error.type}`}>
                  {error.message}
                </div>
              )}
              
              <div className="crop-selection">
                <label htmlFor="crop-select">Select Crop Type:</label>
                <select 
                  id="crop-select"
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  className="crop-select"
                >
                  {SUPPORTED_CROPS.map(crop => (
                    <option key={crop.value} value={crop.value}>
                      {crop.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="file-upload-area">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="file-input"
                  id="file-input"
                />
                <label htmlFor="file-input" className="file-input-label">
                  {selectedFile ? (
                    <span>Selected: {selectedFile.name}</span>
                  ) : (
                    <span>Click to select an image file</span>
                  )}
                </label>
              </div>
              
              {selectedFile && (
                <div className="file-preview">
                  <img 
                    src={URL.createObjectURL(selectedFile)} 
                    alt="Selected crop" 
                    className="preview-image"
                  />
                </div>
              )}
              
              <button 
                onClick={handleAnalyze}
                disabled={!selectedFile || !selectedCrop || loading}
                className="analyze-btn"
              >
                {loading ? 'Analyzing...' : 'Analyze Plant Health'}
              </button>
            </div>

            {prediction && (
              <div className="result-section">
                {prediction.solution && (
                  <div className="suggestions">
                    <h4>Recommended Solution:</h4>
                    {renderSolution(prediction.solution, prediction.health_status || 'Unknown')}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="sidebar">
            <h3>Emergency Contacts</h3>
            <div className="contact-item">Agri Helpline: 1800-180-1551</div>
            <div className="contact-item">Kisan Call: 1800-180-1551</div>
            <div className="contact-item">Weather Alert: 1916</div>
            
            <h3>Quick Tips</h3>
            <div className="tip-item">Water early morning</div>
            <div className="tip-item">Check soil moisture</div>
            <div className="tip-item">Monitor weather forecast</div>
          </div>
        </div>
        
        <div className="footer">
          <p>&copy; 2024 KrishiSetu. All rights reserved. | Empowering farmers with AI-powered plant health detection.</p>
        </div>
      </div>
    </div>
  );
}

export default App;