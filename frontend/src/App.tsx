import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LandingPage, ProfileFormPage, SuccessPage, ApplicationsPage } from '@/pages';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/profile" element={<ProfileFormPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/success" element={<SuccessPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
