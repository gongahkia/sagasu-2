import { useState } from 'react';
import axios from 'axios';

export default function ScraperControl() {
  const [taskId, setTaskId] = useState<string | null>(null);

  const triggerScrape = async () => {
    const response = await axios.post('/api/scrape', {
      buildings: ['Li Ka Shing Library'],
      floors: ['Level 1'],
      facility_types: ['Classroom'],
      equipment: ['Projector']
    });
    
    setTaskId(response.data.task_id);
  };

  return (
    <div>
      <button onClick={triggerScrape}>Run Scraper</button>
      {taskId && <TaskStatus taskId={taskId} />}
    </div>
  );
}