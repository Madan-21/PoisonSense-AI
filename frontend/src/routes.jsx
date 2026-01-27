import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Register from "./pages/Register";
import AiAssistant from "./pages/AiAssistant";
import FindHelp from "./pages/FindHelp";
import Profile from "./pages/Profile";
import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel";
import DoctorVerification from "./pages/DoctorVerification";
import PoisonCenters from "./pages/PoisonCenters";
import AnalyzePoison from "./pages/AnalyzePoison";
import PoisonManagement from "./pages/PoisonManagement";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/register" element={<Register />} />
      <Route path="/ai-assistant" element={<AiAssistant />} />
      <Route path="/find-help" element={<FindHelp />} />
      <Route path="/findhelp" element={<FindHelp />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/admin" element={<AdminPanel />} />
      <Route path="/doctor-verification" element={<DoctorVerification />} />
      <Route path="/poison-centers" element={<PoisonCenters />} />
      <Route path="/analyze-poison" element={<AnalyzePoison />} />
      <Route path="/poison-management" element={<PoisonManagement />} />
      <Route path="/antidotes" element={<PoisonManagement />} />
    </Routes>
  );
}
