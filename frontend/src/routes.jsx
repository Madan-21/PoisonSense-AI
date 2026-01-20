import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import AiAssistant from "./pages/AiAssistant";
import FindHelp from "./pages/FindHelp";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/ai-assistant" element={<AiAssistant />} />
      <Route path="/find-help" element={<FindHelp />} />
    </Routes>
  );
}
