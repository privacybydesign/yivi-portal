import React from "react";

const statusColors: Record<string, string> = {
  draft: "bg-gray-200 text-gray-800",
  pending: "bg-yellow-200 text-yellow-800",
  rejected: "bg-red-200 text-red-800",
  accepted: "bg-green-200 text-green-800",
  published: "bg-blue-200 text-blue-800",
  unknown: "bg-gray-400 text-white",
};

type StatusBadgeProps = {
  status: string;
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const badgeClass =
    statusColors[status.toLowerCase()] || statusColors["unknown"];

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${badgeClass}`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

export default StatusBadge;
