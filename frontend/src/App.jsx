import { Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import DashboardPage from './pages/DashboardPage';
import PromptNewPage from './pages/PromptNewPage';
import PromptDetailPage from './pages/PromptDetailPage';
import PromptEditPage from './pages/PromptEditPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/prompts/new" element={<PromptNewPage />} />
        <Route path="/prompts/:id" element={<PromptDetailPage />} />
        <Route path="/prompts/:id/edit" element={<PromptEditPage />} />
      </Route>
    </Routes>
  );
}
