import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, ChatMessage } from '../../services/ai.ts';
import { Button } from './Button.tsx';
import toast from 'react-hot-toast';

interface ChatbotProps {
  projectId?: number;
  reviewId?: number;
}

const SUGGESTIONS = [
  'Explain what this code does',
  'Check for security vulnerabilities',
  'How can I optimize this code?',
  'Recommend refactoring changes'
];

export const Chatbot: React.FC<ChatbotProps> = ({ projectId, reviewId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize with a welcome message
  useEffect(() => {
    const welcome: ChatMessage = {
      role: 'assistant',
      content: reviewId
        ? `Hello! I am the Cobane AI Chatbot. I've analyzed this specific code review run and its static/AI findings. Ask me anything about how to optimize, explain, or fix issues in this file!`
        : `Hello! I am the Cobane AI Chatbot. I've analyzed your project's files and static metrics. Ask me about the codebase structure, optimization tips, or overall quality reviews!`
    };
    setMessages([welcome]);
  }, [projectId, reviewId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = { role: 'user', content: text };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    setInputValue('');
    setIsLoading(true);

    try {
      const payload = {
        project_id: projectId,
        review_id: reviewId,
        message: text,
        // Exclude first welcome message from API history
        history: updatedHistory.slice(1, -1)
      };

      const response = await sendChatMessage(payload);
      if (response.success && response.data) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response.data.response }
        ]);
      } else {
        toast.error('Failed to get response from AI.');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Error sending chat message.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage(inputValue);
    }
  };

  return (
    <div className="flex flex-col h-[550px] bg-gray-50 dark:bg-gray-900 border border-gray-250 dark:border-gray-700/80 rounded-2xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-750 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs font-bold text-gray-700 dark:text-gray-200 uppercase tracking-wider">
            Cobane AI Assistant
          </span>
        </div>
        <span className="text-xxs text-gray-400 font-mono">
          {reviewId ? `Context: Review Run #${reviewId}` : `Context: Project`}
        </span>
      </div>

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={index}
              className={`flex items-start space-x-2.5 max-w-[85%] ${
                isUser ? 'ml-auto flex-row-reverse space-x-reverse' : 'mr-auto'
              }`}
            >
              {/* Avatar icon */}
              <div
                className={`flex-shrink-0 h-8 w-8 rounded-xl flex items-center justify-center font-bold text-xs select-none ${
                  isUser
                    ? 'bg-primary-600 text-white'
                    : 'bg-gradient-to-tr from-indigo-500 to-primary-600 text-white'
                }`}
              >
                {isUser ? 'ME' : 'AI'}
              </div>

              {/* Message bubble */}
              <div
                className={`px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed shadow-xs whitespace-pre-wrap ${
                  isUser
                    ? 'bg-primary-600 text-white rounded-tr-none'
                    : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200/60 dark:border-gray-750 rounded-tl-none'
                }`}
              >
                {msg.content}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-start space-x-2.5 mr-auto max-w-[85%]">
            <div className="flex-shrink-0 h-8 w-8 rounded-xl flex items-center justify-center font-bold text-xs bg-gradient-to-tr from-indigo-500 to-primary-600 text-white">
              AI
            </div>
            <div className="px-3.5 py-3 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200/60 dark:border-gray-750 rounded-2xl rounded-tl-none shadow-xs flex items-center space-x-1">
              <span className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      {messages.length === 1 && !isLoading && (
        <div className="px-4 py-2 flex flex-wrap gap-2 bg-gray-50/50 dark:bg-gray-900/50 border-t border-gray-200/55 dark:border-gray-800/40">
          {SUGGESTIONS.map((sug, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(sug)}
              className="text-xs px-2.5 py-1.5 bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 rounded-lg border border-gray-200 dark:border-gray-750 hover:bg-primary-50 dark:hover:bg-primary-950/20 hover:border-primary-300 transition"
            >
              {sug}
            </button>
          ))}
        </div>
      )}

      {/* Input container */}
      <div className="p-3 bg-white dark:bg-gray-850 border-t border-gray-200 dark:border-gray-750 flex items-center space-x-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Ask a question about the code or findings..."
          className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-250 dark:border-gray-700/80 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-primary-500 dark:text-gray-200 disabled:opacity-60"
        />
        <Button
          onClick={() => handleSendMessage(inputValue)}
          disabled={isLoading || !inputValue.trim()}
          className="px-3.5 py-2 text-xs flex items-center space-x-1"
        >
          <span>Send</span>
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </Button>
      </div>
    </div>
  );
};
