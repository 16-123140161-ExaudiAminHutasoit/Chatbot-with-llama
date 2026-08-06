"use client";

import { Message, useChat } from "ai/react";
import { ChatInput, ChatMessages } from "./ui/chat";
import { useMemo } from "react";
import { transformMessages } from "./transform";
import useNodes from "../hooks/useNodes";
import { NodePreview } from "./ui/nodes";

export default function ChatSection() {
  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
  } = useChat({
    api: process.env.NEXT_PUBLIC_CHAT_API,
  });

  const { nodes, setNodes } = useNodes();

  const mergeFunctionMessages = (messages: Message[]): Message[] => {
    // only allow the last function message to be shown
    return messages.filter(
      (msg, i) => msg.role !== "function" || i === messages.length - 1
    );
  };

  const transformedMessages = useMemo(() => {
    // return mergeFunctionMessages(transformMessages(messages));
    return transformMessages(messages, setNodes);
  }, [messages]);

  return (
    <div className="w-full max-w-5xl space-y-4">
      <div className="flex flex-col lg:flex-row gap-6 w-full">
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          <ChatMessages
            messages={transformedMessages}
            isLoading={isLoading}
            reload={reload}
            stop={stop}
          />
          <ChatInput
            input={input}
            handleSubmit={handleSubmit}
            handleInputChange={handleInputChange}
            isLoading={isLoading}
          />
        </div>
        {nodes.length > 0 && (
          <div className="w-full lg:w-80 shrink-0">
            <NodePreview nodes={nodes} />
          </div>
        )}
      </div>
    </div>
  );

}
