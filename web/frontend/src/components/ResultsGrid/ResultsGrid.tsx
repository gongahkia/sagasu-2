import './ResultsGrid.css';

interface ResultsGridProps {
  results: Record<string, any> | null;
}

export default function ResultsGrid({ results }: ResultsGridProps) {
  if (!results) return null;

  return (
    <div className="results-grid">
      {Object.entries(results).map(([room, data]) => (
        <div key={room} className="room-card">
          <h3>{room}</h3>
          <div className="time-slots">
            {data.timeslots.map((slot: any) => (
              <div 
                key={slot.time} 
                className={`time-slot ${slot.available ? 'available' : 'booked'}`}
              >
                <span>{slot.time}</span>
                <span>{slot.status}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}