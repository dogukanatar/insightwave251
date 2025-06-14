import React from "react";

export function Logo({ className = "" }) {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className="relative">
        <div className="w-10 h-10 bg-gradient-to-r from-gray-600 to-black rounded-full flex items-center justify-center">
          <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
            <div className="w-3 h-3 bg-black rounded-full"></div>
          </div>
        </div>
        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full border-2 border-white"></div>
      </div>
      <div>
        <span className="text-xl font-bold text-gray-900">INSTWAVE</span>
        <p className="text-xs text-gray-600 -mt-1">AI Research Digest</p>
      </div>
    </div>
  );
}
