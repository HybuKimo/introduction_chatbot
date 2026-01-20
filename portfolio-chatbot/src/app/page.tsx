'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          session_id: sessionId || undefined
        })
      });

      if (!response.ok) {
        throw new Error('네트워크 오류가 발생했습니다.');
      }

      const data = await response.json();
      
      // 세션 ID 저장
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      // 회사가 감지되었으면 알림
      if (data.detected_company) {
        setTimeout(() => {
          const companyMessage: Message = {
            id: (Date.now() + 2).toString(),
            content: `💼 ${data.detected_company} 관련 질문으로 인식했습니다. 더 구체적인 답변을 도와드릴게요!`,
            isUser: false,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, companyMessage]);
        }, 500);
      }

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white py-6">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold">신준희</h1>
          <p className="text-xl mt-2 opacity-90">WEB DEVELOPER</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Left Side - Profile */}
          <div className="flex flex-col">
            {/* Profile Image */}
            <div className="mb-6">
              <div className="w-80 h-80 bg-gray-300 rounded-lg mx-auto lg:mx-0 flex items-center justify-center">
                <span className="text-gray-500">프로필 사진</span>
              </div>
              <h2 className="text-2xl font-bold text-center lg:text-left mt-4">신준희</h2>
            </div>
            
            {/* Profile Description */}
            <div className="space-y-4">
              <div className="flex items-start space-x-2">
                <span className="text-green-500 mt-1">✓</span>
                <div>
                  <h3 className="font-semibold">편리함을 추구하고</h3>
                  <p className="text-gray-600 text-sm">편의점은 불이 꺼지지 않고 밤새 고객이 원하는 것들을 제공해 줍니다.</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-500 mt-1">✓</span>
                <div>
                  <h3 className="font-semibold">의로움으로 세상을 도우고</h3>
                  <p className="text-gray-600 text-sm">올바른 가치관으로 세상에 도움이 되는 개발을 지향합니다.</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <span className="text-green-500 mt-1">✓</span>
                <div>
                  <h3 className="font-semibold">점점 발전하는</h3>
                  <p className="text-gray-600 text-sm">편의점같은 개발자가 되고 싶습니다!</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Chatbot */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">💬 무엇이든 물어보세요!</h2>
            
            {/* Messages Container */}
            <div className="border rounded-lg h-96 mb-4 p-4 overflow-y-auto bg-gray-50">
              {messages.length === 0 ? (
                <div className="text-gray-500 text-center mt-20">
                  <p>안녕하세요! 신준희에 대해 궁금한 것이 있으시면</p>
                  <p>아래에 메시지를 입력해주세요.</p>
                  <div className="mt-4 text-sm">
                    <p>💡 예시 질문:</p>
                    <p>• 어떤 프로젝트 경험이 있나요?</p>
                    <p>• 네이버에 지원하는 이유는?</p>
                    <p>• 주요 기술 스택은 무엇인가요?</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.isUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-white border shadow-sm'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.isUser ? 'text-blue-100' : 'text-gray-400'
                        }`}>
                          {message.timestamp.toLocaleTimeString('ko-KR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white border shadow-sm rounded-lg px-4 py-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
            
            {/* Input Container */}
            <div className="flex space-x-2">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="메시지를 입력하세요..."
                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button 
                onClick={sendMessage}
                disabled={isLoading || !inputValue.trim()}
                className={`px-6 py-2 rounded-lg transition-colors ${
                  isLoading || !inputValue.trim()
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white`}
              >
                {isLoading ? '...' : '전송'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
