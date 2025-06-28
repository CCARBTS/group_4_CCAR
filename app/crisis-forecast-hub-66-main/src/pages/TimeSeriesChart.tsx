// TimeSeriesChart.tsx

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// The shape of each data point after transformation
export interface TimeSeriesDataPoint {
  date: string; // e.g., "2024-W01"
  [country: string]: string | number;
}

// Props for the chart component
interface TimeSeriesChartProps {
  data: TimeSeriesDataPoint[];
  countries: string[]; // List of country names to display as separate lines
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ data, countries }) => {
  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        {countries.map((country, index) => (
          <Line
            key={country}
            type="monotone"
            dataKey={country}
            stroke={`hsl(${(index * 360) / countries.length}, 70%, 50%)`}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TimeSeriesChart;

