import React from 'react';

const GoatCodeFlutterPreview = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
      padding: '40px',
      fontFamily: "'JetBrains Mono', monospace",
      color: '#e0e0e0'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h1 style={{
            fontSize: '48px',
            fontWeight: '800',
            background: 'linear-gradient(135deg, #00ff9d 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '16px',
            letterSpacing: '2px'
          }}>
            🐐 GOATCODE FLUTTER
          </h1>
          <p style={{ 
            fontSize: '24px', 
            color: '#00ff9d', 
            marginBottom: '8px',
            letterSpacing: '3px',
            fontWeight: '600'
          }}>
            FULLY FUNCTIONAL PRODUCTION APP
          </p>
          <p style={{ fontSize: '16px', color: '#888' }}>
            Complete Flutter application with real architecture, not just UI mockups
          </p>
        </div>

        {/* Status Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '20px',
          marginBottom: '60px'
        }}>
          {[
            { emoji: '✅', title: 'Fully Functional', desc: 'Real state management & API' },
            { emoji: '🎨', title: 'Premium UI', desc: 'Dark theme, animations, responsive' },
            { emoji: '📱', title: 'Multi-Platform', desc: 'iOS, Android, Web, Desktop' },
            { emoji: '🚀', title: 'Production Ready', desc: 'Clean architecture, type-safe' }
          ].map((item, i) => (
            <div key={i} style={{
              padding: '24px',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid rgba(0, 255, 157, 0.2)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>{item.emoji}</div>
              <div style={{ 
                fontSize: '14px', 
                color: '#00ff9d', 
                fontWeight: '700',
                marginBottom: '8px',
                letterSpacing: '1px'
              }}>
                {item.title}
              </div>
              <div style={{ fontSize: '12px', color: '#888' }}>{item.desc}</div>
            </div>
          ))}
        </div>

        {/* App Structure */}
        <div style={{ 
          background: 'rgba(0, 0, 0, 0.4)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: '12px',
          padding: '40px',
          marginBottom: '40px'
        }}>
          <h2 style={{ 
            fontSize: '28px', 
            color: '#00d4ff', 
            marginBottom: '32px',
            letterSpacing: '1px'
          }}>
            📱 App Structure
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            
            {/* File Structure */}
            <div>
              <h3 style={{ color: '#00ff9d', fontSize: '18px', marginBottom: '16px' }}>
                📁 Complete Project
              </h3>
              <pre style={{
                background: 'rgba(0, 0, 0, 0.5)',
                padding: '20px',
                borderRadius: '8px',
                fontSize: '12px',
                lineHeight: '1.8',
                color: '#aaa',
                border: '1px solid rgba(0, 255, 157, 0.2)'
              }}>
{`goatcode_flutter/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── models.dart
│   │   └── models.g.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   └── providers.dart
│   ├── screens/
│   │   ├── home_screen.dart
│   │   ├── agent_control_screen.dart
│   │   ├── architecture_screen.dart
│   │   ├── tools_stats_screen.dart
│   │   └── metrics_screen.dart
│   └── widgets/
│       ├── metric_card.dart
│       └── execution_log_widget.dart
├── pubspec.yaml
└── README.md`}
              </pre>
            </div>

            {/* Features */}
            <div>
              <h3 style={{ color: '#00ff9d', fontSize: '18px', marginBottom: '16px' }}>
                ⚡ What Works
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  'Task creation & execution',
                  'Real-time log streaming',
                  'Live metrics dashboard',
                  'Architecture visualization',
                  'Tool statistics tracking',
                  'State management (Riverpod)',
                  'Mock & real API support',
                  'WebSocket integration',
                  'Responsive design',
                  'Error handling',
                  'Loading states',
                  'Production patterns'
                ].map((feature, i) => (
                  <div key={i} style={{
                    padding: '12px 16px',
                    background: 'rgba(0, 255, 157, 0.05)',
                    border: '1px solid rgba(0, 255, 157, 0.2)',
                    borderRadius: '6px',
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    <span style={{ color: '#00ff9d', fontSize: '16px' }}>✓</span>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Start */}
        <div style={{ 
          background: 'rgba(0, 0, 0, 0.4)',
          border: '1px solid rgba(0, 255, 157, 0.2)',
          borderRadius: '12px',
          padding: '40px',
          marginBottom: '40px'
        }}>
          <h2 style={{ 
            fontSize: '28px', 
            color: '#00ff9d', 
            marginBottom: '24px',
            letterSpacing: '1px'
          }}>
            🚀 Quick Start (3 Commands)
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {[
              { num: '1', cmd: 'tar -xzf goatcode_flutter.tar.gz && cd goatcode_flutter', desc: 'Extract project' },
              { num: '2', cmd: 'flutter pub get', desc: 'Install dependencies' },
              { num: '3', cmd: 'flutter run', desc: 'Launch app' }
            ].map((step, i) => (
              <div key={i} style={{ display: 'flex', gap: '20px', alignItems: 'start' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #00ff9d, #00d4ff)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px',
                  fontWeight: '800',
                  color: '#0a0a0a',
                  flexShrink: 0
                }}>
                  {step.num}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#888', 
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}>
                    {step.desc}
                  </div>
                  <pre style={{
                    background: 'rgba(0, 0, 0, 0.5)',
                    padding: '12px 16px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    color: '#00ff9d',
                    border: '1px solid rgba(0, 255, 157, 0.2)',
                    margin: 0,
                    fontFamily: "'JetBrains Mono', monospace"
                  }}>
                    {step.cmd}
                  </pre>
                </div>
              </div>
            ))}
          </div>

          <div style={{
            marginTop: '32px',
            padding: '20px',
            background: 'rgba(0, 212, 255, 0.1)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎉</div>
            <div style={{ fontSize: '16px', color: '#00d4ff', fontWeight: '600' }}>
              App launches with working mock backend!
            </div>
            <div style={{ fontSize: '13px', color: '#888', marginTop: '8px' }}>
              No additional setup required. Start coding immediately.
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
          marginBottom: '40px'
        }}>
          {[
            { title: 'State Management', items: ['Riverpod', 'AsyncValue', 'StateNotifier', 'Providers'] },
            { title: 'UI Components', items: ['Google Fonts', 'Lucide Icons', 'Animations', 'Responsive'] },
            { title: 'Backend', items: ['Dio HTTP', 'WebSocket', 'Mock Service', 'JSON'] }
          ].map((section, i) => (
            <div key={i} style={{
              padding: '24px',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px'
            }}>
              <h3 style={{ 
                fontSize: '16px', 
                color: '#00d4ff', 
                marginBottom: '16px',
                fontWeight: '700',
                letterSpacing: '1px'
              }}>
                {section.title}
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {section.items.map((item, j) => (
                  <div key={j} style={{
                    fontSize: '13px',
                    color: '#aaa',
                    paddingLeft: '12px',
                    borderLeft: '2px solid rgba(0, 212, 255, 0.3)'
                  }}>
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer CTA */}
        <div style={{
          padding: '48px',
          background: 'linear-gradient(135deg, rgba(0, 255, 157, 0.1), rgba(0, 212, 255, 0.1))',
          border: '2px solid rgba(0, 255, 157, 0.3)',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <h2 style={{ 
            fontSize: '32px', 
            marginBottom: '16px',
            background: 'linear-gradient(135deg, #00ff9d 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: '800',
            letterSpacing: '1px'
          }}>
            The Prompt is 20%. This is the 80%.
          </h2>
          <p style={{ fontSize: '18px', color: '#aaa', marginBottom: '32px', lineHeight: '1.6' }}>
            A complete, production-ready Flutter application demonstrating real agent architecture.<br/>
            Not just prompts. Not just UI mockups. Real engineering.
          </p>
          <div style={{ 
            display: 'inline-block',
            padding: '16px 40px',
            background: 'linear-gradient(135deg, #00ff9d, #00d4ff)',
            borderRadius: '8px',
            fontSize: '18px',
            fontWeight: '800',
            color: '#0a0a0a',
            letterSpacing: '2px',
            boxShadow: '0 4px 20px rgba(0, 255, 157, 0.3)'
          }}>
            READY TO DEPLOY 🚀
          </div>
        </div>

      </div>
    </div>
  );
};

export default GoatCodeFlutterPreview;
