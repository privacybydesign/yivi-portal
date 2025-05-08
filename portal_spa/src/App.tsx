// src/App.tsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import "./App.css"; // App-Specific Styles (Logo, Layout)

function App() {
  return (
    <div id="root">
      <Routes>
        <Route path="/" element={<HomePage />} />
      </Routes>
    </div>
  );
}

export default App;
