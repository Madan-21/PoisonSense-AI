import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { analysisApi } from '../api/analysisApi';
import '../styles/PoisonManagement.css';

const PoisonManagement = () => {
  const [poisons, setPoisons] = useState([]);
  const [antidotes, setAntidotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('poisons');
  const [selectedPoison, setSelectedPoison] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Default data for when API fails
  const defaultPoisons = [
    {
      id: 1,
      name: 'Organophosphate',
      category: 'AGRICULTURAL',
      common_names: ['Malathion', 'Parathion', 'Chlorpyrifos'],
      symptoms_immediate: ['Excessive salivation', 'Lacrimation', 'Urination', 'Diarrhea', 'Emesis'],
      symptoms_delayed: ['Miosis', 'Bradycardia', 'Respiratory depression'],
      antidote: 'Atropine + Pralidoxime (2-PAM)',
      antidote_alternatives: ['Atropine alone'],
      typical_severity: 'SEVERE',
      first_aid: '1. Remove from exposure\n2. Remove clothing\n3. Wash skin\n4. Do NOT induce vomiting\n5. Call emergency'
    },
    {
      id: 2,
      name: 'Paracetamol Overdose',
      category: 'PHARMACEUTICAL',
      common_names: ['Acetaminophen', 'Tylenol', 'Crocin', 'Panadol'],
      symptoms_immediate: ['Nausea', 'Vomiting', 'Abdominal pain'],
      symptoms_delayed: ['Liver failure', 'Jaundice', 'Hepatic encephalopathy'],
      antidote: 'N-Acetylcysteine (NAC)',
      antidote_alternatives: ['Methionine'],
      typical_severity: 'MODERATE',
      first_aid: '1. Do not induce vomiting\n2. Activated charcoal if <2 hours\n3. Note time and amount\n4. Seek medical care'
    },
    {
      id: 3,
      name: 'Snake Venom (Neurotoxic)',
      category: 'NATURAL',
      common_names: ['Cobra', 'Krait', 'Elapid venom'],
      symptoms_immediate: ['Local pain', 'Swelling', 'Fang marks'],
      symptoms_delayed: ['Ptosis', 'Respiratory paralysis', 'Dysphagia'],
      antidote: 'Polyvalent Anti-Snake Venom (ASV)',
      antidote_alternatives: ['Neostigmine for neurotoxic'],
      typical_severity: 'CRITICAL',
      first_aid: '1. Keep calm\n2. Immobilize limb\n3. Remove jewelry\n4. Do NOT cut/suck\n5. Transport to hospital'
    },
    {
      id: 4,
      name: 'Rat Poison (Anticoagulant)',
      category: 'HOUSEHOLD',
      common_names: ['Warfarin', 'Brodifacoum', 'Ratol'],
      symptoms_immediate: ['Usually none for 24-48 hours'],
      symptoms_delayed: ['Bleeding gums', 'Bruising', 'Hematuria', 'Epistaxis'],
      antidote: 'Vitamin K1 (Phytonadione)',
      antidote_alternatives: ['Fresh Frozen Plasma', 'PCC'],
      typical_severity: 'SEVERE',
      first_aid: '1. Do not induce vomiting\n2. Note product and amount\n3. Seek medical attention\n4. Watch for bleeding 24-72h'
    },
    {
      id: 5,
      name: 'Methanol',
      category: 'INDUSTRIAL',
      common_names: ['Wood Alcohol', 'Spurious Liquor'],
      symptoms_immediate: ['Nausea', 'Headache', 'Inebriation'],
      symptoms_delayed: ['Visual disturbances', 'Blindness', 'Metabolic acidosis'],
      antidote: 'Fomepizole or Ethanol',
      typical_severity: 'CRITICAL',
      first_aid: '1. Call emergency\n2. Do not induce vomiting\n3. Note time and amount'
    },
    {
      id: 6,
      name: 'Kerosene/Petroleum',
      category: 'HOUSEHOLD',
      common_names: ['Kerosene', 'Petrol', 'Diesel'],
      symptoms_immediate: ['Coughing', 'Choking', 'Burning sensation'],
      symptoms_delayed: ['Chemical pneumonitis', 'Respiratory distress'],
      antidote: 'No specific antidote - supportive care',
      typical_severity: 'MODERATE',
      first_aid: '1. Do NOT induce vomiting\n2. Keep calm\n3. Remove from fumes\n4. Seek medical attention'
    }
  ];

  const defaultAntidotes = [
    { id: 1, name: 'Atropine Sulfate', generic_name: 'Atropine', effective_for: ['Organophosphate', 'Carbamate'], dosage: '2-4mg IV, repeat q5-10min' },
    { id: 2, name: 'Pralidoxime (2-PAM)', generic_name: 'Pralidoxime', effective_for: ['Organophosphate'], dosage: '1-2g IV over 30min' },
    { id: 3, name: 'N-Acetylcysteine (NAC)', generic_name: 'Acetylcysteine', effective_for: ['Paracetamol/Acetaminophen'], dosage: '150mg/kg IV over 1h, then 50mg/kg over 4h' },
    { id: 4, name: 'Polyvalent Anti-Snake Venom', generic_name: 'ASV', effective_for: ['Snake Envenomation'], dosage: '10 vials IV, may repeat' },
    { id: 5, name: 'Naloxone', generic_name: 'Naloxone', effective_for: ['Opioid Overdose'], dosage: '0.4-2mg IV/IM/SC' },
    { id: 6, name: 'Vitamin K1 (Phytonadione)', generic_name: 'Vitamin K', effective_for: ['Anticoagulant Rodenticide'], dosage: '10-25mg oral/IV' },
    { id: 7, name: 'Activated Charcoal', generic_name: 'Charcoal', effective_for: ['General Decontamination'], dosage: '1g/kg (max 50g)' },
    { id: 8, name: 'Fomepizole', generic_name: 'Fomepizole', effective_for: ['Methanol', 'Ethylene Glycol'], dosage: '15mg/kg loading, then 10mg/kg q12h' }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const poisonsRes = await analysisApi.listAllPoisons().catch(() => null);
      
      // Map API response to our expected format if needed
      if (poisonsRes && Array.isArray(poisonsRes) && poisonsRes.length > 0) {
        const mappedPoisons = poisonsRes.map((p, idx) => ({
          id: p.id || idx + 1,
          name: p.name || p.poison_name,
          category: p.category || 'GENERAL',
          common_names: p.common_names || p.aliases || [],
          symptoms_immediate: p.symptoms_immediate || p.symptoms || [],
          symptoms_delayed: p.symptoms_delayed || [],
          antidote: p.antidote || p.primary_antidote,
          antidote_alternatives: p.antidote_alternatives || [],
          typical_severity: p.typical_severity || p.severity || 'MODERATE',
          first_aid: p.first_aid || p.first_aid_steps?.join('\n')
        }));
        setPoisons(mappedPoisons);
      } else {
        setPoisons(defaultPoisons);
      }
      
      // Always use default antidotes for now
      setAntidotes(defaultAntidotes);
    } catch (err) {
      console.error('Error fetching data:', err);
      setPoisons(defaultPoisons);
      setAntidotes(defaultAntidotes);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(poisons.map(p => p.category).filter(Boolean))];

  const filteredPoisons = poisons.filter(poison => {
    const matchesSearch = poison.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poison.common_names?.some(n => n.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = categoryFilter === 'all' || poison.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const filteredAntidotes = antidotes.filter(antidote =>
    antidote.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    antidote.generic_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    antidote.effective_for?.some(e => e.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getSeverityClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'critical';
      case 'SEVERE': return 'severe';
      case 'MODERATE': return 'moderate';
      case 'MILD': return 'mild';
      default: return 'moderate';
    }
  };

  return (
    <div className="poison-management-page">
      <Navbar />
      
      {/* Header */}
      <header className="pm-header">
        <div className="pm-header-content">
          <h1>🧪 Poison Database & Antidotes</h1>
          <p>Comprehensive toxicology information with treatment protocols</p>
        </div>
      </header>

      <div className="pm-content">
        {/* Tabs */}
        <div className="pm-tabs">
          <button 
            className={`pm-tab-btn ${activeTab === 'poisons' ? 'active' : ''}`}
            onClick={() => setActiveTab('poisons')}
          >
            <span className="tab-icon">🧪</span>
            Poisons ({filteredPoisons.length})
          </button>
          <button 
            className={`pm-tab-btn ${activeTab === 'antidotes' ? 'active' : ''}`}
            onClick={() => setActiveTab('antidotes')}
          >
            <span className="tab-icon">💊</span>
            Antidotes ({filteredAntidotes.length})
          </button>
        </div>

        {/* Search Bar */}
        <div className="pm-search-bar">
          <input
            type="text"
            className="pm-search-input"
            placeholder={activeTab === 'poisons' ? "Search poisons by name or symptoms..." : "Search antidotes..."}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {activeTab === 'poisons' && (
            <select 
              className="pm-filter-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div className="pm-loading">
            <div className="pm-spinner"></div>
            <p>Loading data...</p>
          </div>
        ) : activeTab === 'poisons' ? (
          <div className="pm-cards-grid">
            {filteredPoisons.map((poison) => (
              <div 
                key={poison.id} 
                className={`pm-poison-card severity-${getSeverityClass(poison.typical_severity)}`}
                onClick={() => setSelectedPoison(poison)}
              >
                <div className={`pm-card-header severity-${getSeverityClass(poison.typical_severity)}`}>
                  <div className="pm-card-title">
                    <h3>
                      <span className="poison-icon">☠️</span>
                      {poison.name}
                    </h3>
                    <div className="pm-card-category">{poison.category}</div>
                    {poison.common_names && (
                      <div className="pm-card-aliases">
                        Also: {poison.common_names.slice(0, 3).join(', ')}
                      </div>
                    )}
                  </div>
                  <span className={`pm-severity-badge ${getSeverityClass(poison.typical_severity)}`}>
                    {poison.typical_severity || 'Unknown'}
                  </span>
                </div>
                
                <div className="pm-card-body">
                  <div className="pm-card-section">
                    <div className="pm-section-label symptoms">⚠️ Symptoms</div>
                    <div className="pm-symptom-tags">
                      {(poison.symptoms_immediate || []).slice(0, 4).map((symptom, i) => (
                        <span key={i} className="pm-symptom-tag">{symptom}</span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pm-card-section">
                    <div className="pm-section-label antidote">💊 Antidote</div>
                    <div className="pm-antidote-box">
                      {poison.antidote || 'Supportive care'}
                      {poison.antidote_alternatives && poison.antidote_alternatives.length > 0 && (
                        <div className="pm-antidote-alternatives">
                          Alt: {poison.antidote_alternatives.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="pm-card-footer">
                  <button className="pm-view-btn">View Details →</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="pm-cards-grid">
            {filteredAntidotes.map((antidote) => (
              <div key={antidote.id} className="pm-antidote-card">
                <div className="pm-antidote-header">
                  <span className="antidote-icon">💊</span>
                  <div>
                    <h3>{antidote.name}</h3>
                    <div className="pm-generic-name">{antidote.generic_name}</div>
                  </div>
                </div>
                <div className="pm-antidote-body">
                  <div className="pm-effective-for">
                    <strong>Effective For:</strong>
                    <div className="pm-effective-tags">
                      {(antidote.effective_for || []).map((item, i) => (
                        <span key={i} className="pm-effective-tag">{item}</span>
                      ))}
                    </div>
                  </div>
                  {antidote.dosage && (
                    <div className="pm-dosage">
                      <strong>Dosage:</strong> {antidote.dosage}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Emergency Banner */}
        <div className="pm-emergency-banner">
          <div className="pm-emergency-content">
            <span className="emergency-icon">🚨</span>
            <div className="pm-emergency-text">
              <strong>Emergency? Call immediately:</strong>
              <p>
                Nepal Emergency: <a href="tel:102">102</a> | 
                Poison Control (NPIC): <a href="tel:+977-1-4412505">+977-1-4412505</a> | 
                Toll-Free: <a href="tel:1102">1102</a>
              </p>
            </div>
          </div>
          <Link to="/ai-assistant" className="pm-ai-btn">
            🤖 Ask AI Assistant
          </Link>
        </div>
      </div>

      {/* Poison Detail Modal */}
      {selectedPoison && (
        <div className="pm-modal-overlay" onClick={() => setSelectedPoison(null)}>
          <div className="pm-modal" onClick={(e) => e.stopPropagation()}>
            <button className="pm-modal-close" onClick={() => setSelectedPoison(null)}>×</button>
            
            <div className="pm-modal-header">
              <h2>{selectedPoison.name}</h2>
              <span className={`pm-severity-badge ${getSeverityClass(selectedPoison.typical_severity)}`}>
                {selectedPoison.typical_severity}
              </span>
            </div>
            
            <div className="pm-modal-body">
              <div className="pm-modal-section">
                <h4>📋 Category</h4>
                <p>{selectedPoison.category}</p>
                {selectedPoison.common_names && (
                  <p className="pm-aliases">Also known as: {selectedPoison.common_names.join(', ')}</p>
                )}
              </div>
              
              <div className="pm-modal-section">
                <h4>⚠️ Immediate Symptoms</h4>
                <ul>
                  {(selectedPoison.symptoms_immediate || []).map((symptom, i) => (
                    <li key={i}>{symptom}</li>
                  ))}
                </ul>
              </div>
              
              {selectedPoison.symptoms_delayed && selectedPoison.symptoms_delayed.length > 0 && (
                <div className="pm-modal-section">
                  <h4>⏰ Delayed Symptoms</h4>
                  <ul>
                    {selectedPoison.symptoms_delayed.map((symptom, i) => (
                      <li key={i}>{symptom}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="pm-modal-section antidote-section">
                <h4>💊 Antidote</h4>
                <p className="pm-antidote-main">{selectedPoison.antidote || 'Supportive care only'}</p>
                {selectedPoison.antidote_alternatives && (
                  <p className="pm-antidote-alt">Alternatives: {selectedPoison.antidote_alternatives.join(', ')}</p>
                )}
              </div>
              
              {selectedPoison.first_aid && (
                <div className="pm-modal-section first-aid-section">
                  <h4>🩹 First Aid</h4>
                  <pre className="pm-first-aid">{selectedPoison.first_aid}</pre>
                </div>
              )}
            </div>
            
            <div className="pm-modal-footer">
              <Link to="/ai-assistant" className="pm-ask-ai-btn">
                🤖 Ask AI About This Poison
              </Link>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default PoisonManagement;