import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";

export default function App() {
  return (
    <>
    <Toaster position="top-right" />
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage/>} />
        <Route path="/articles" element={<HomePage/>} />
      </Routes>
    </>
    
  )
}