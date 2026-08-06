import { Node } from "./chat/chat.interface";
import { useEffect, useState } from "react";

interface NodeBoxProps {
  node: Node;
  onClick: () => void;
  isSelected: boolean;
}

const NodeBox: React.FC<NodeBoxProps> = ({ node, onClick, isSelected }) => {
  return (
    <div
      className={`p-3 cursor-pointer rounded-lg border border-gray-300 ${
        isSelected ? "bg-blue-200" : ""
      }`}
      onClick={onClick}
    >
      <h2 className="text-sm font-bold mb-1">{node.title}</h2>
      <p className="text-xs w-64 h-8 overflow-hidden">{node.summary}</p>
    </div>
  );
};

interface NodeListProps {
  nodes: Node[];
  selectedNodeId: string;
  onNodeClick: (nodeId: string) => void;
}

const NodeList: React.FC<NodeListProps> = ({
  nodes,
  onNodeClick,
  selectedNodeId,
}) => {
  if (nodes.length === 0) return;
  // console.log(nodes);
  // const [selectedNodeId, setSelectedNodeId] = useState(nodes[0].id || "");

  const handleNodeClick = (nodeId: string) => {
    // setSelectedNodeId(nodeId);
    onNodeClick(nodeId);
  };

  return (
    <div className="flex flex-wrap gap-2">
      {nodes.map((node) => (
        <NodeBox
          key={node.id}
          node={node}
          onClick={() => handleNodeClick(node.id)}
          isSelected={selectedNodeId === node.id}
        />
      ))}
    </div>
  );
};

interface NodeDetailsProps {
  url: string;
}

const NodeDetails: React.FC<NodeDetailsProps> = ({ url }) => {
  if (!url) return;
  // console.log(url);
  return (
    <div className="mt-2">
      <iframe
        src={url}
        className="w-[50vw] rounded-lg h-[80vh] border border-gray-300"
      />
    </div>
  );
};

interface NodePreviewProps {
  nodes: Node[];
}

export const NodePreview: React.FC<NodePreviewProps> = ({ nodes }) => {
  if (nodes.length === 0) return null;

  return (
    <div className="p-4 bg-white/90 dark:bg-zinc-800/90 rounded-2xl border border-blue-100 dark:border-zinc-700 shadow-md">
      <h3 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-blue-600"></span>
        Sumber Rujukan Dokumen BPS
      </h3>
      <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
        {nodes.map((node, i) => (
          <div
            key={node.id || i}
            className="p-3 bg-blue-50/50 dark:bg-zinc-700/50 rounded-xl border border-blue-100 dark:border-zinc-600"
          >
            <h4 className="text-xs font-bold text-gray-800 dark:text-gray-200 mb-1">
              📌 {node.title || "Dokumen Sensus BPS"}
            </h4>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              {node.summary || "Bagian dokumen terkait yang digunakan oleh AI untuk menyusun jawaban."}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

