import { Dispatch, SetStateAction } from 'react';
import './FilterPanel.css';

const VALID_BUILDING = [
  "Li Ka Shing Library", "School of Law", "School of Accountancy", 
  "School of Economics", "Administration Building"
];

const VALID_FLOOR = [
  "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", 
  "Level 6", "Level 7", "Level 8", "Level 9"
];

const VALID_FACILITY_TYPE = [
  "Classroom", "Meeting Room", "Study Area", "Computer Lab", 
  "Presentation Room", "Seminar Room"
];

const VALID_EQUIPMENT = [
  "Projector", "Whiteboard", "Video Conferencing", "Classroom PC",
  "Document Camera", "Wireless Presentation"
];

interface FilterPanelProps {
  filters: {
    buildings: string[];
    floors: string[];
    facilityTypes: string[];
    equipment: string[];
  };
  onFilterChange: Dispatch<SetStateAction<any>>;
  onScrape: () => void;
  loading: boolean;
}

export default function FilterPanel({ 
  filters, onFilterChange, onScrape, loading 
}: FilterPanelProps) {
  const handleFilterChange = (type: string) => (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Array.from(e.target.selectedOptions, option => option.value);
    onFilterChange(prev => ({ ...prev, [type]: selected }));
  };

  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>Building</label>
        <select
          multiple
          value={filters.buildings}
          onChange={handleFilterChange('buildings')}
        >
          {VALID_BUILDING.map(building => (
            <option key={building} value={building}>{building}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Floor</label>
        <select
          multiple
          value={filters.floors}
          onChange={handleFilterChange('floors')}
        >
          {VALID_FLOOR.map(floor => (
            <option key={floor} value={floor}>{floor}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Facility Type</label>
        <select
          multiple
          value={filters.facilityTypes}
          onChange={handleFilterChange('facilityTypes')}
        >
          {VALID_FACILITY_TYPE.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Equipment</label>
        <select
          multiple
          value={filters.equipment}
          onChange={handleFilterChange('equipment')}
        >
          {VALID_EQUIPMENT.map(equip => (
            <option key={equip} value={equip}>{equip}</option>
          ))}
        </select>
      </div>

      <button 
        onClick={onScrape} 
        disabled={loading}
        className="scrape-button"
      >
        {loading ? 'Searching...' : 'Find Available Rooms'}
      </button>
    </div>
  );
}