import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AgentMessage } from '@/types/claim';
import { 
  MessageSquare, 
  Bot, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  ArrowRight,
  User
} from 'lucide-react';

interface AgentConversationProps {
  messages: string[];
  conversationDuration: number;
  totalAgents: number;
}

export const AgentConversation: React.FC<AgentConversationProps> = ({
  messages,
  conversationDuration,
  totalAgents
}) => {
  const [expandedMessage, setExpandedMessage] = useState<number | null>(null);

  // Parse the message strings to extract agent information
  const parseMessages = (messages: string[]): AgentMessage[] => {
    return messages.map((msgStr, index) => {
      try {
        // Remove the outer quotes and parse the JSON-like string
        const cleanStr = msgStr.replace(/^'|'$/g, '');
        const parsed = JSON.parse(cleanStr);
        return {
          content: parsed.content,
          role: parsed.role,
          name: parsed.name,
          timestamp: new Date(Date.now() + index * 1000).toISOString()
        };
      } catch (error) {
        // Fallback for malformed messages
        return {
          content: msgStr,
          role: 'system',
          name: 'System',
          timestamp: new Date(Date.now() + index * 1000).toISOString()
        };
      }
    });
  };

  const parsedMessages = parseMessages(messages);

  const getAgentIcon = (agentName: string) => {
    switch (agentName) {
      case 'Fraud_Detection_Specialist':
        return <AlertCircle className="h-4 w-4" />;
      case 'Medical_Validator':
        return <CheckCircle className="h-4 w-4" />;
      case 'Billing_Fraud_Validator':
        return <MessageSquare className="h-4 w-4" />;
      case 'Policy_Balance_Validator':
        return <CheckCircle className="h-4 w-4" />;
      case 'Policy_Adjustment_Coordinator':
        return <ArrowRight className="h-4 w-4" />;
      case 'Decision_Coordinator':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Bot className="h-4 w-4" />;
    }
  };

  const getAgentColor = (agentName: string) => {
    const colors = {
      'Fraud_Detection_Specialist': 'bg-red-100 border-red-200 text-red-800',
      'Medical_Validator': 'bg-blue-100 border-blue-200 text-blue-800',
      'Billing_Fraud_Validator': 'bg-yellow-100 border-yellow-200 text-yellow-800',
      'Policy_Balance_Validator': 'bg-green-100 border-green-200 text-green-800',
      'Policy_Adjustment_Coordinator': 'bg-purple-100 border-purple-200 text-purple-800',
      'Decision_Coordinator': 'bg-indigo-100 border-indigo-200 text-indigo-800',
    };
    return colors[agentName as keyof typeof colors] || 'bg-gray-100 border-gray-200 text-gray-800';
  };

  const formatContent = (content: string) => {
    // Split content by ### for headers and format
    const sections = content.split('###').filter(section => section.trim());
    
    return sections.map((section, index) => {
      const lines = section.trim().split('\\n').filter(line => line.trim());
      if (lines.length === 0) return null;
      
      const isHeader = lines[0].includes('**') && lines[0].length < 100;
      
      return (
        <div key={index} className="mb-4">
          {isHeader && (
            <h4 className="font-semibold text-sm mb-2 text-foreground">
              {lines[0].replace(/\*\*/g, '')}
            </h4>
          )}
          <div className="space-y-1">
            {lines.slice(isHeader ? 1 : 0).map((line, lineIndex) => {
              if (line.includes('**') && line.includes(':')) {
                const [label, ...value] = line.split(':');
                return (
                  <div key={lineIndex} className="text-xs">
                    <span className="font-medium">
                      {label.replace(/\*\*/g, '')}:
                    </span>
                    <span className="ml-1 text-gray-500">
                      {value.join(':').replace(/\*\*/g, '')}
                    </span>
                  </div>
                );
              }
              return (
                <p key={lineIndex} className="text-xs text-gray-500">
                  {line.replace(/\*\*/g, '')}
                </p>
              );
            })}
          </div>
        </div>
      );
    });
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Agent Conversation Flow
          </CardTitle>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <User className="h-4 w-4" />
              <span>{totalAgents} agents</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{conversationDuration.toFixed(1)}s</span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="max-h-96 overflow-y-auto">
          <div className="space-y-4 p-6">
            {parsedMessages.map((message, index) => (
              <div 
                key={index} 
                className="agent-message border-l-4 border-gray-200 pl-4"
                style={{
                  borderLeftColor: `hsl(${(index * 60) % 360}, 70%, 60%)`
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getAgentIcon(message.name)}
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getAgentColor(message.name)}`}
                    >
                      {message.name.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                  <span className="text-xs text-gray-500">
                    Step {index + 1}
                  </span>
                </div>
                
                <div 
                  className={`bg-gray-100/30 rounded-lg p-3 cursor-pointer transition-all hover:bg-gray-100/50 ${
                    expandedMessage === index ? 'max-h-none' : 'max-h-32 overflow-hidden'
                  }`}
                  onClick={() => setExpandedMessage(
                    expandedMessage === index ? null : index
                  )}
                >
                  {expandedMessage === index ? (
                    <div className="prose prose-sm max-w-none">
                      {formatContent(message.content)}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500 line-clamp-4">
                      {message.content.replace(/\*\*/g, '').replace(/###/g, '').substring(0, 200)}...
                    </p>
                  )}
                </div>
                
                {expandedMessage !== index && (
                  <button 
                    className="text-xs text-primary hover:underline mt-2"
                    onClick={() => setExpandedMessage(index)}
                  >
                    Click to expand
                  </button>
                )}
                
                {index < parsedMessages.length - 1 && (
                  <div className="flex justify-center mt-4">
                    <ArrowRight className="h-4 w-4 text-gray-500" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
