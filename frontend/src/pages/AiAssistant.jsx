import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { analysisApi } from '../api/analysisApi';
import { useAuth } from '../context/AuthContext';
import '../styles/AIAssessment.css';

const AiAssistant = () => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isEmergency, setIsEmergency] = useState(false);
  const [identifiedPoison, setIdentifiedPoison] = useState(null);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();
  
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: `Hello! 👋 I'm **PoisonSense AI**, your friendly assistant for poison information and emergency guidance.

I can help you with:
- 🧪 **Poison Information** - Learn about various toxic substances
- 💊 **Antidote Information** - What antidotes exist (for awareness)
- 🩺 **Symptom Identification** - Understand symptoms of poisoning
- 🏥 **Find Help** - Locate nearby hospitals and poison centers
- 🚨 **Emergency Guidance** - What to do in poisoning cases

**How can I assist you today?**

Just type your question, or try one of the quick actions below! 💬

---
⚠️ *If this is an emergency, please call **102** immediately!*

*I'm here to provide information and guidance. For medical treatment, always consult a healthcare professional.*`,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      isWelcome: true
    }
  ]);

  // Get user location on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => console.log('Location not available:', error)
      );
    }
  }, []);

  const quickActions = [
    '🧒 Child swallowed medicine',
    '🧴 Cleaning product ingestion',
    '🌿 Plant/mushroom ingestion',
    '🐍 Snake bite emergency',
    '🧪 Pesticide exposure',
    '💊 Drug overdose',
    '🔥 Chemical burn/acid',
    '🏥 Find nearest hospital'
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const chatWithAgent = async (userMessage) => {
    setIsTyping(true);
    
    try {
      console.log('Sending to Agentic AI:', userMessage);
      console.log('Session ID:', sessionId);
      console.log('Location:', userLocation);
      
      // Call the agentic AI chat endpoint
      const result = await analysisApi.chatWithAgent(userMessage, {
        latitude: userLocation?.latitude,
        longitude: userLocation?.longitude,
        sessionId: sessionId
      });
      
      console.log('Agent Response:', result);
      
      // Update session ID for conversation continuity
      if (result.session_id) {
        setSessionId(result.session_id);
      }
      
      // Update emergency status
      if (result.is_emergency) {
        setIsEmergency(true);
      }
      
      // Update identified poison
      if (result.identified_poison) {
        setIdentifiedPoison(result.identified_poison);
      }
      
      // Create response message
      const botResponse = {
        id: messages.length + 2,
        type: 'bot',
        text: result.message,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        analysisResult: result,
        isEmergency: result.is_emergency,
        toolsUsed: result.tools_used
      };
      
      setMessages(prev => [...prev, botResponse]);
      
    } catch (error) {
      console.error('Agent Error:', error);
      console.error('Error details:', error.response?.data);
      
      // Build error message with specific details
      let errorMessage = "I apologize, but I'm having trouble processing your request.";
      
      if (error.response?.status === 401) {
        errorMessage = "Please log in to use the AI analysis feature for full functionality. Basic emergency info is still available.";
      } else if (error.response?.status === 500) {
        errorMessage = "The AI service is temporarily unavailable. Please try again in a moment.";
      } else if (error.code === 'ERR_NETWORK') {
        errorMessage = "Cannot connect to the server. Please check if the backend is running.";
      }
      
      // Fallback to helpful response with emergency info
      const botResponse = {
        id: messages.length + 2,
        type: 'bot',
        text: `${errorMessage}

**🚨 For immediate help in Nepal:**
📞 **Emergency:** 102
☎️ **National Poison Centre (TUTH):** +977-1-4412505
🆘 **Toll-Free:** 1102

**Please provide more details:**
• What substance was involved?
• What symptoms are you observing?
• How long ago did exposure occur?
• What is the person's age and weight?

⚠️ *If this is a life-threatening emergency, call 102 immediately!*`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        isError: true
      };
      setMessages(prev => [...prev, botResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = () => {
    if (message.trim()) {
      const newMessage = {
        id: messages.length + 1,
        type: 'user',
        text: message,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, newMessage]);
      const sentMessage = message;
      setMessage('');
      chatWithAgent(sentMessage);
    }
  };

  const handleQuickAction = (action) => {
    // Remove emoji from the start of the action
    const cleanAction = action.replace(/^[^\w\s]+\s*/, '');
    
    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      text: cleanAction,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, newMessage]);
    chatWithAgent(cleanAction);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewConversation = () => {
    setMessages([{
      id: 1,
      type: 'bot',
      text: `Hi there! 👋 Starting a fresh conversation.

I'm **PoisonSense AI** - how can I help you today?

You can ask me about:
- Poison information and symptoms
- Antidotes and first aid guidance
- Finding nearby hospitals
- Emergency guidance

Just type your question! 💬

---
🚨 *Emergency? Call **102** immediately!*`,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }]);
    setSessionId(null);
    setIsEmergency(false);
    setIdentifiedPoison(null);
  };

  const handleEmergencyCall = () => {
    window.location.href = 'tel:102';
  };

  return (
    <div className="assessment-page">
      {/* Navigation */}
      <Navbar />

      <div className="assessment-container">
        {/* Header */}
        <header className="assessment-header">
          <button className="back-button" onClick={handleNewConversation} title="New Conversation">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="header-title">
            <h1>🤖 PoisonSense AI Agent</h1>
            <div className="status-indicator">
              <span className={`status-dot ${isEmergency ? 'emergency' : ''}`}></span>
              <span className="status-text">
                {isEmergency ? '🚨 Emergency Mode' : identifiedPoison ? `Identified: ${identifiedPoison}` : 'Active'}
              </span>
            </div>
          </div>
          <div className="header-actions">
            {sessionId && (
              <span className="session-badge" title="Conversation active">
                💬
              </span>
            )}
          </div>
        </header>

        {/* Main Content */}
        <main className="assessment-content">
          {/* Medical Disclaimer */}
          <div className={`disclaimer-box ${isEmergency ? 'emergency' : ''}`}>
            <div className="disclaimer-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke={isEmergency ? "#DC2626" : "#D97706"} strokeWidth="2"/>
                <path d="M12 8V12M12 16H12.01" stroke={isEmergency ? "#DC2626" : "#D97706"} strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <p className="disclaimer-text">
              {isEmergency 
                ? '🚨 EMERGENCY DETECTED - Call 102 immediately for life-threatening situations!'
                : 'Medical Disclaimer: This AI assistant provides guidance only. In emergencies, contact local emergency services immediately (102).'
              }
            </p>
          </div>

          {/* Chat Messages */}
          <div className="chat-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-wrapper ${msg.type} ${msg.isEmergency ? 'emergency' : ''}`}>
                {msg.type === 'bot' && (
                  <div className={`bot-avatar ${msg.isEmergency ? 'emergency' : ''}`}>
                    {msg.isEmergency ? '🚨' : '🤖'}
                  </div>
                )}
                <div className={`message-bubble ${msg.isEmergency ? 'emergency' : ''}`}>
                  <div 
                    className="message-text"
                    style={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{ 
                      __html: msg.text
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\n/g, '<br/>')
                    }}
                  />
                  <div className="message-footer">
                    <span className="message-time">{msg.time}</span>
                    {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                      <span className="tools-used" title={`Tools: ${msg.toolsUsed.join(', ')}`}>
                        🔧 {msg.toolsUsed.length} tools
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message-wrapper bot">
                <div className="bot-avatar">🤖</div>
                <div className="message-bubble typing">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">AI is analyzing...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Footer */}
        <footer className="assessment-footer">
          {/* Quick Actions */}
          <div className="quick-actions">
            <div className="quick-actions-scroll">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className="quick-action-btn"
                  onClick={() => handleQuickAction(action)}
                >
                  {action}
                </button>
              ))}
            </div>
          </div>

          {/* Input Area */}
          <div className="input-area">
            <button className="mic-button" title="Voice input (coming soon)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 1C10.34 1 9 2.34 9 4V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V4C15 2.34 13.66 1 12 1Z" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 19V23M8 23H16" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <textarea
              className="message-input"
              placeholder="Describe the situation in detail... (Press Enter to send)"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              rows="1"
            />
            <button 
              className={`send-button ${message.trim() ? 'active' : ''}`} 
              onClick={handleSendMessage}
              disabled={!message.trim() || isTyping}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="white"/>
              </svg>
            </button>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <Link to="/poison-management" className="view-results-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="9" stroke="white" strokeWidth="2"/>
                <path d="M12 8L12 12M12 16L12.01 16" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              View Poison Database & Antidotes
            </Link>
            <Link to="/find-help" className="view-results-btn secondary">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23C12 23 3 17 3 10C3 5.02944 7.02944 1 12 1C16.9706 1 21 5.02944 21 10Z" stroke="white" strokeWidth="2"/>
                <circle cx="12" cy="10" r="3" stroke="white" strokeWidth="2"/>
              </svg>
              Find Nearby Help
            </Link>
          </div>
        </footer>
      </div>

      {/* Floating Emergency Call Button */}
      <button 
        className={`floating-call-btn ${isEmergency ? 'emergency-pulse' : ''}`} 
        title="Call Emergency (102)"
        onClick={handleEmergencyCall}
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4741 21.8325 20.7293C21.7209 20.9845 21.5573 21.2136 21.3521 21.4019C21.1469 21.5901 20.9046 21.7335 20.6408 21.8227C20.3769 21.9119 20.0974 21.9451 19.82 21.92C16.7428 21.5856 13.787 20.5342 11.19 18.85C8.77383 17.3147 6.72534 15.2662 5.19 12.85C3.49998 10.2412 2.44824 7.271 2.12 4.18C2.09501 3.90347 2.12788 3.62476 2.2165 3.36162C2.30513 3.09849 2.44757 2.85669 2.63477 2.65162C2.82196 2.44655 3.04981 2.28271 3.30379 2.17052C3.55778 2.05833 3.83234 2.00026 4.11 2H7.11C7.59531 1.99522 8.06579 2.16708 8.43376 2.48353C8.80173 2.79999 9.04208 3.23945 9.11 3.72C9.23662 4.68007 9.47145 5.62273 9.81 6.53C9.94455 6.88792 9.97366 7.27691 9.89391 7.65088C9.81415 8.02485 9.62886 8.36811 9.36 8.64L8.09 9.91C9.51356 12.4135 11.5865 14.4864 14.09 15.91L15.36 14.64C15.6319 14.3711 15.9752 14.1858 16.3491 14.1061C16.7231 14.0263 17.1121 14.0555 17.47 14.19C18.3773 14.5286 19.3199 14.7634 20.28 14.89C20.7658 14.9585 21.2094 15.2032 21.5265 15.5775C21.8437 15.9518 22.0122 16.4296 22 16.92Z" fill="white"/>
        </svg>
        {isEmergency && <span className="emergency-text">CALL NOW</span>}
      </button>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default AiAssistant;
