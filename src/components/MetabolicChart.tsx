
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

const MetabolicChart = () => {
  // Sample data representing glucose patterns
  const data = [
    { time: '6:00', beforeMeals: 95, afterMeals: 120, withWalk: 105, withoutWalk: 140 },
    { time: '8:00', beforeMeals: 110, afterMeals: 160, withWalk: 125, withoutWalk: 175 },
    { time: '10:00', beforeMeals: 100, afterMeals: 145, withWalk: 110, withoutWalk: 155 },
    { time: '12:00', beforeMeals: 105, afterMeals: 150, withWalk: 115, withoutWalk: 165 },
    { time: '14:00', beforeMeals: 95, afterMeals: 135, withWalk: 105, withoutWalk: 150 },
    { time: '16:00', beforeMeals: 90, afterMeals: 125, withWalk: 100, withoutWalk: 140 },
    { time: '18:00', beforeMeals: 100, afterMeals: 170, withWalk: 130, withoutWalk: 185 },
    { time: '20:00', beforeMeals: 110, afterMeals: 180, withWalk: 140, withoutWalk: 195 },
    { time: '22:00', beforeMeals: 105, afterMeals: 155, withWalk: 120, withoutWalk: 170 },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{`Time: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value} mg/dL`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            stroke="#666"
            fontSize={12}
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            domain={[80, 200]}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Reference line for normal glucose range */}
          <ReferenceLine y={140} stroke="#ff6b6b" strokeDasharray="2 2" />
          
          <Line 
            type="monotone" 
            dataKey="withWalk" 
            stroke="#10b981" 
            strokeWidth={3}
            dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
            name="With Post-Meal Walk"
          />
          <Line 
            type="monotone" 
            dataKey="withoutWalk" 
            stroke="#ef4444" 
            strokeWidth={3}
            dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
            name="Without Walk"
          />
          <Line 
            type="monotone" 
            dataKey="beforeMeals" 
            stroke="#6366f1" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Baseline"
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 text-sm text-gray-600">
        <div className="flex flex-wrap gap-4 justify-center">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span>With Post-Meal Walk</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span>Without Walk</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-0.5 bg-indigo-500 mr-2"></div>
            <span>Baseline</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-0.5 bg-red-400 mr-2" style={{ borderTop: '2px dashed #ff6b6b' }}></div>
            <span>High Glucose Threshold</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetabolicChart;
