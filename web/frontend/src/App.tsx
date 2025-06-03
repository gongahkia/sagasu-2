import { useState } from 'react';
import axios from 'axios';
import './App.css';
import './styles/theme.css';
import Header from './components/Header/Header';
import FilterPanel from './components/FilterPanel/FilterPanel';
import ResultsGrid from './components/ResultsGrid/ResultsGrid';

function App() {
  const [filters, setFilters] = useState({
    buildings: ['Li Ka Shing Library'],
    floors: ['Level 1'],
    facilityTypes: ['Classroom'],
    equipment: ['Projector']
  });

  const [results, setResults] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleScrape = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/scrape', {
        ...filters,
        email: process.env.REACT_APP_SMU_EMAIL,
        password: process.env.REACT_APP_SMU_PASSWORD
      });
      
      const taskId = response.data.task_id;
      await pollResults(taskId);
    } catch (error) {
      console.error('Scraping failed:', error);
    }
    setLoading(false);
  };

  const pollResults = async (taskId: string) => {
    // Implementation similar to previous example
  };

  return (
    <div className="app-container">
      <Header />
      
      <div className="main-content">
        <FilterPanel 
          filters={filters}
          onFilterChange={setFilters}
          onScrape={handleScrape}
          loading={loading}
        />
        
        <ResultsGrid results={results} />
      </div>
    </div>
  );
}

export default App;