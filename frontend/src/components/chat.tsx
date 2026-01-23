import React, { useState, useRef, useEffect } from 'react';

const Magna = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const messagesEndRef = useRef(null);

  const exampleQuestions = [
    "How much notice must a landlord give to end a periodic tenancy?",
    "What are an employer's obligations for trial periods?",
    "When can a company director be personally liable?",
    "What warranties apply to consumer goods under NZ law?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulated responses for the prototype demo
  const getSimulatedResponse = (query) => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('landlord') || lowerQuery.includes('tenancy') || lowerQuery.includes('tenant') || lowerQuery.includes('notice')) {
      return {
        text: `Under the **Residential Tenancies Act 1986** (as amended by the Residential Tenancies Amendment Act 2024), the notice periods for ending a periodic tenancy are:

**Landlord terminating:**
• **90 days** — for "no cause" termination (reintroduced 30 January 2025)
• **42 days** — where the landlord or family member needs to move in, or property sold with vacant possession required
• **14 days** — for serious rent arrears (21+ days overdue) or antisocial behaviour

**Tenant terminating:**
• **21 days** — standard notice period for periodic tenancies

**Fixed-term tenancies:**
• Cannot be terminated early by notice alone
• Landlord may end at expiry without reason (from 30 January 2025)
• Previously would automatically convert to periodic

Note: These rules changed significantly in January 2025. Earlier tenancies may have different terms.`,
        sources: [
          { title: "Residential Tenancies Act 1986, s 51", url: "https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM95518.html", section: "Section 51 - Termination by landlord" },
          { title: "Residential Tenancies Act 1986, s 51A", url: "https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM95528.html", section: "Section 51A - No-cause termination" },
          { title: "Residential Tenancies Amendment Act 2024", url: "https://www.legislation.govt.nz/act/public/2024/0054/latest/whole.html", section: "Amendment Act - 2024 changes" }
        ]
      };
    }
    
    if (lowerQuery.includes('employer') || lowerQuery.includes('trial') || lowerQuery.includes('employment')) {
      return {
        text: `Under the **Employment Relations Act 2000**, trial period provisions allow:

**Eligibility:**
• Trial periods of up to **90 days** are permitted
• Only available for **new employees** who have not previously worked for the employer
• Must be agreed in writing **before** employment starts

**Employer obligations:**
• The trial period clause must be in the employment agreement
• Employee must be given a reasonable opportunity to seek independent advice
• Cannot be used for employees who have worked for the employer before (in any capacity)

**During the trial period:**
• Employer may dismiss the employee and the employee cannot bring a personal grievance for unjustified dismissal
• Employee retains other employment rights (e.g., minimum wage, leave entitlements, health & safety)
• Good faith obligations still apply

**Key limitation:** The employee can still bring a personal grievance on other grounds (e.g., discrimination, harassment, unjustified disadvantage).`,
        sources: [
          { title: "Employment Relations Act 2000, s 67A", url: "https://www.legislation.govt.nz/act/public/2000/0024/latest/DLM6803002.html", section: "Section 67A - Trial periods" },
          { title: "Employment Relations Act 2000, s 67B", url: "https://www.legislation.govt.nz/act/public/2000/0024/latest/DLM6803005.html", section: "Section 67B - Limitations on trial provisions" }
        ]
      };
    }

    if (lowerQuery.includes('director') || lowerQuery.includes('liable') || lowerQuery.includes('company')) {
      return {
        text: `Under the **Companies Act 1993**, directors can be personally liable in several circumstances:

**Statutory personal liability:**
• **Reckless trading** (s 135) — if the company incurs obligations the director didn't believe could be performed
• **Duty to creditors** (s 136) — agreeing to company obligations that seriously damage creditors
• **Director duties breaches** (ss 131-138) — acting in bad faith, improper use of information/position

**Specific situations:**
• **Phoenix companies** (s 386A-386F) — prohibited from managing similar business after insolvency
• **Failure to keep records** (s 194) — can lead to personal liability for company debts
• **GST and PAYE** — directors can be personally liable for unpaid taxes under Tax Administration Act

**Defences:**
• Reliance on professional advice (s 138)
• Acting in good faith with reasonable care
• Insurance (permitted under s 162)

**Key principle:** The "corporate veil" generally protects directors, but courts will pierce it for fraud, sham arrangements, or where the company is merely an agent of the director.`,
        sources: [
          { title: "Companies Act 1993, s 135", url: "https://www.legislation.govt.nz/act/public/1993/0105/latest/DLM320887.html", section: "Section 135 - Reckless trading" },
          { title: "Companies Act 1993, s 136", url: "https://www.legislation.govt.nz/act/public/1993/0105/latest/DLM320889.html", section: "Section 136 - Duty in relation to obligations" },
          { title: "Companies Act 1993, s 131", url: "https://www.legislation.govt.nz/act/public/1993/0105/latest/DLM320877.html", section: "Section 131 - Duty to act in good faith" }
        ]
      };
    }

    if (lowerQuery.includes('consumer') || lowerQuery.includes('warranty') || lowerQuery.includes('goods') || lowerQuery.includes('guarantee')) {
      return {
        text: `Under the **Consumer Guarantees Act 1993**, goods sold to consumers must meet these guarantees:

**Automatic guarantees for goods:**
• **Acceptable quality** (s 6) — safe, durable, free from defects, acceptable in appearance
• **Fit for purpose** (s 8) — suitable for any purpose made known to the supplier
• **Match description** (s 9) — correspond with any description given
• **Match sample** (s 10) — if sold by sample, bulk must match
• **Reasonable price** (s 11) — if price not predetermined
• **Repairs and spare parts** (s 12) — available for reasonable time

**Consumer remedies (s 18-27):**
• **Minor failure:** Supplier can choose to repair, replace, or refund
• **Substantial failure:** Consumer can reject goods and get full refund OR keep goods and get compensation

**What is a "substantial failure"?**
• A reasonable consumer would not have bought the goods
• Goods are substantially unfit for normal purpose
• Goods are unsafe

**Key limitation:** Act does not apply to business-to-business transactions, auctions, or goods bought for re-supply.`,
        sources: [
          { title: "Consumer Guarantees Act 1993, s 6", url: "https://www.legislation.govt.nz/act/public/1993/0091/latest/DLM311807.html", section: "Section 6 - Guarantee of acceptable quality" },
          { title: "Consumer Guarantees Act 1993, s 18", url: "https://www.legislation.govt.nz/act/public/1993/0091/latest/DLM311858.html", section: "Section 18 - Options against suppliers" },
          { title: "Consumer Guarantees Act 1993, s 21", url: "https://www.legislation.govt.nz/act/public/1993/0091/latest/DLM311866.html", section: "Section 21 - Substantial failure" }
        ]
      };
    }

    // Default response for unknown queries
    return {
      text: `I found relevant information in New Zealand legislation regarding your query. Here's what the law says:

Based on my search of the legislation database, this topic may involve multiple Acts. For the most accurate and complete answer, I recommend:

1. Searching the specific Act on **legislation.govt.nz**
2. Consulting with a qualified New Zealand lawyer
3. Contacting **Community Law** for free legal assistance

Would you like me to search for something more specific? Try asking about:
• Tenancy rights and obligations
• Employment law and workplace rights
• Company and director duties
• Consumer protection guarantees`,
      sources: [
        { title: "New Zealand Legislation", url: "https://www.legislation.govt.nz", section: "Official legislation database" },
        { title: "Community Law", url: "https://communitylaw.org.nz", section: "Free legal help" }
      ]
    };
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    const response = getSimulatedResponse(input);
    const assistantMessage = {
      role: 'assistant',
      content: response.text,
      sources: response.sources
    };

    setMessages(prev => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleExampleClick = (question) => {
    setInput(question);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#ffffff',
      fontFamily: "'Source Serif 4', Georgia, serif",
      color: '#1a1a2e',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Subtle grid pattern overlay */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `
          linear-gradient(rgba(26, 26, 46, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(26, 26, 46, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '60px 60px',
        pointerEvents: 'none'
      }} />

      {/* Disclaimer Modal */}
      {showDisclaimer && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(8px)',
          padding: '20px'
        }}>
          <div style={{
            background: '#ffffff',
            border: '1px solid #e5e5e5',
            borderRadius: '16px',
            padding: '40px',
            maxWidth: '560px',
            boxShadow: '0 25px 80px rgba(0, 0, 0, 0.15)'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '24px',
              fontSize: '28px'
            }}>
              ⚖️
            </div>
            <h2 style={{
              fontFamily: "'Cormorant Garamond', Georgia, serif",
              fontSize: '28px',
              fontWeight: '600',
              marginBottom: '16px',
              color: '#1a1a2e',
              letterSpacing: '0.5px'
            }}>
              Important Notice
            </h2>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.7',
              color: '#64748b',
              marginBottom: '20px'
            }}>
              <strong style={{ color: '#1a1a2e' }}>Magna</strong> is an AI-powered information retrieval tool. It provides general information about New Zealand legislation only.
            </p>
            <div style={{
              background: '#fef3c7',
              border: '1px solid #fcd34d',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px'
            }}>
              <p style={{
                fontSize: '14px',
                lineHeight: '1.6',
                color: '#92400e',
                margin: 0
              }}>
                <strong style={{ color: '#78350f' }}>This is NOT legal advice.</strong> Information may be incomplete or outdated. Always verify with official sources and consult a qualified NZ lawyer for legal decisions.
              </p>
            </div>
            <button
              onClick={() => setShowDisclaimer(false)}
              style={{
                width: '100%',
                padding: '16px 32px',
                background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                fontSize: '16px',
                fontWeight: '600',
                fontFamily: "'Source Serif 4', Georgia, serif",
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 20px rgba(26, 26, 46, 0.2)'
              }}
              onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
            >
              I Understand — Continue
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header style={{
        borderBottom: '1px solid #e5e5e5',
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          maxWidth: '1000px',
          margin: '0 auto',
          padding: '20px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '44px',
              height: '44px',
              background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '22px',
              boxShadow: '0 4px 20px rgba(26, 26, 46, 0.15)'
            }}>
              ⚖️
            </div>
            <div>
              <h1 style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: '26px',
                fontWeight: '600',
                margin: 0,
                color: '#1a1a2e',
                letterSpacing: '1px'
              }}>
                Magna
              </h1>
              <p style={{
                fontSize: '11px',
                color: '#94a3b8',
                margin: 0,
                fontFamily: "'Inter', -apple-system, sans-serif",
                letterSpacing: '0.5px',
                textTransform: 'uppercase'
              }}>
                NZ Legal Assistant • Prototype
              </p>
            </div>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '20px'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: '#22c55e',
              borderRadius: '50%',
              boxShadow: '0 0 8px rgba(34, 197, 94, 0.5)'
            }} />
            <span style={{
              fontSize: '12px',
              color: '#15803d',
              fontFamily: "'Inter', -apple-system, sans-serif",
              fontWeight: '500'
            }}>
              Online
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '24px',
        minHeight: 'calc(100vh - 200px)'
      }}>
        {/* Welcome State */}
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            paddingTop: '60px',
            animation: 'fadeIn 0.6s ease-out'
          }}>
            <div style={{
              width: '80px',
              height: '80px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px',
              fontSize: '36px'
            }}>
              📜
            </div>
            <h2 style={{
              fontFamily: "'Cormorant Garamond', Georgia, serif",
              fontSize: '36px',
              fontWeight: '500',
              marginBottom: '12px',
              color: '#1a1a2e'
            }}>
              Ask about New Zealand Law
            </h2>
            <p style={{
              fontSize: '17px',
              color: '#64748b',
              maxWidth: '500px',
              margin: '0 auto 48px',
              lineHeight: '1.6'
            }}>
              Get instant answers grounded in legislation, with direct citations to official sources.
            </p>

            {/* Example Questions */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '12px',
              maxWidth: '700px',
              margin: '0 auto'
            }}>
              {exampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(question)}
                  style={{
                    padding: '16px 20px',
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    color: '#475569',
                    fontSize: '14px',
                    fontFamily: "'Source Serif 4', Georgia, serif",
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    lineHeight: '1.5'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#f1f5f9';
                    e.target.style.borderColor = '#cbd5e1';
                    e.target.style.color = '#1a1a2e';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = '#f8fafc';
                    e.target.style.borderColor = '#e2e8f0';
                    e.target.style.color = '#475569';
                  }}
                >
                  {question}
                </button>
              ))}
            </div>

            {/* Covered Acts */}
            <div style={{
              marginTop: '60px',
              padding: '24px',
              background: '#f8fafc',
              borderRadius: '12px',
              border: '1px solid #e2e8f0'
            }}>
              <p style={{
                fontSize: '12px',
                color: '#94a3b8',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginBottom: '12px',
                fontFamily: "'Inter', -apple-system, sans-serif"
              }}>
                Legislation Coverage (Prototype)
              </p>
              <p style={{
                fontSize: '13px',
                color: '#64748b',
                margin: 0,
                lineHeight: '1.8'
              }}>
                Residential Tenancies Act • Employment Relations Act • Companies Act • Consumer Guarantees Act • 
                Property Law Act • Fair Trading Act • Privacy Act • Building Act • Contract and Commercial Law Act • Resource Management Act
              </p>
            </div>
          </div>
        )}

        {/* Messages */}
        <div style={{ paddingBottom: '120px' }}>
          {messages.map((message, index) => (
            <div
              key={index}
              style={{
                marginBottom: '24px',
                animation: 'slideIn 0.3s ease-out'
              }}
            >
              {message.role === 'user' ? (
                <div style={{
                  display: 'flex',
                  justifyContent: 'flex-end'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)',
                    color: '#ffffff',
                    padding: '16px 20px',
                    borderRadius: '16px 16px 4px 16px',
                    maxWidth: '70%',
                    fontSize: '15px',
                    lineHeight: '1.6',
                    fontWeight: '500'
                  }}>
                    {message.content}
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      marginBottom: '16px'
                    }}>
                      <div style={{
                        width: '28px',
                        height: '28px',
                        background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px'
                      }}>
                        ⚖️
                      </div>
                      <span style={{
                        fontSize: '13px',
                        color: '#64748b',
                        fontFamily: "'Inter', -apple-system, sans-serif"
                      }}>
                        Magna
                      </span>
                    </div>
                    <div style={{
                      fontSize: '15px',
                      lineHeight: '1.8',
                      color: '#1e293b',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {message.content.split(/(\*\*.*?\*\*)/).map((part, i) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                          return <strong key={i} style={{ color: '#1a1a2e' }}>{part.slice(2, -2)}</strong>;
                        }
                        return part;
                      })}
                    </div>
                  </div>
                  
                  {/* Sources */}
                  {message.sources && (
                    <div style={{
                      background: '#fffbeb',
                      border: '1px solid #fde68a',
                      borderRadius: '12px',
                      padding: '16px'
                    }}>
                      <p style={{
                        fontSize: '11px',
                        color: '#92400e',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        marginBottom: '12px',
                        fontFamily: "'Inter', -apple-system, sans-serif"
                      }}>
                        📚 Sources
                      </p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {message.sources.map((source, i) => (
                          <a
                            key={i}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '10px 12px',
                              background: '#ffffff',
                              borderRadius: '8px',
                              textDecoration: 'none',
                              transition: 'all 0.2s ease',
                              border: '1px solid #fde68a'
                            }}
                            onMouseOver={(e) => {
                              e.currentTarget.style.background = '#fef3c7';
                            }}
                            onMouseOut={(e) => {
                              e.currentTarget.style.background = '#ffffff';
                            }}
                          >
                            <span style={{ color: '#d97706', fontSize: '14px' }}>→</span>
                            <div>
                              <p style={{
                                margin: 0,
                                fontSize: '13px',
                                color: '#92400e',
                                fontWeight: '500'
                              }}>
                                {source.title}
                              </p>
                              <p style={{
                                margin: 0,
                                fontSize: '11px',
                                color: '#b45309'
                              }}>
                                {source.section}
                              </p>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Disclaimer */}
                  <p style={{
                    fontSize: '11px',
                    color: '#64748b',
                    marginTop: '12px',
                    padding: '12px',
                    background: '#fef2f2',
                    border: '1px solid #fecaca',
                    borderRadius: '8px',
                    fontFamily: "'Inter', -apple-system, sans-serif"
                  }}>
                    ⚠️ This is AI-generated information, not legal advice. Always verify with official sources and consult a qualified NZ lawyer.
                  </p>
                </div>
              )}
            </div>
          ))}
          
          {/* Loading State */}
          {isLoading && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '20px',
              background: '#f8fafc',
              borderRadius: '16px',
              border: '1px solid #e2e8f0'
            }}>
              <div style={{
                display: 'flex',
                gap: '4px'
              }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: '8px',
                      height: '8px',
                      background: '#1a1a2e',
                      borderRadius: '50%',
                      animation: `pulse 1s ease-in-out ${i * 0.15}s infinite`
                    }}
                  />
                ))}
              </div>
              <span style={{ color: '#64748b', fontSize: '14px' }}>
                Searching legislation...
              </span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <div style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: 'linear-gradient(to top, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.95) 80%, transparent 100%)',
        padding: '24px',
        paddingTop: '40px'
      }}>
        <div style={{
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <form onSubmit={handleSubmit}>
            <div style={{
              display: 'flex',
              gap: '12px',
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '8px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)'
            }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about New Zealand legislation..."
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  padding: '12px 16px',
                  fontSize: '15px',
                  color: '#1a1a2e',
                  fontFamily: "'Source Serif 4', Georgia, serif"
                }}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                style={{
                  padding: '12px 24px',
                  background: input.trim() && !isLoading
                    ? 'linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%)'
                    : '#e2e8f0',
                  border: 'none',
                  borderRadius: '10px',
                  color: input.trim() && !isLoading ? '#ffffff' : '#94a3b8',
                  fontSize: '14px',
                  fontWeight: '600',
                  fontFamily: "'Inter', -apple-system, sans-serif",
                  cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease'
                }}
              >
                {isLoading ? '...' : 'Ask'}
              </button>
            </div>
          </form>
          <p style={{
            textAlign: 'center',
            fontSize: '11px',
            color: '#94a3b8',
            marginTop: '12px',
            fontFamily: "'Inter', -apple-system, sans-serif"
          }}>
            Prototype demonstration — Responses are simulated for demo purposes
          </p>
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Source+Serif+4:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 0.4; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1); }
        }
        
        * {
          box-sizing: border-box;
        }
        
        ::placeholder {
          color: #94a3b8;
        }
        
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(26, 26, 46, 0.2);
          border-radius: 3px;
        }
      `}</style>
    </div>
  );
};

export default Magna;