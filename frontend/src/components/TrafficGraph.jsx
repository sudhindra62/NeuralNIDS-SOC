import React from 'react';
import { 
    LineChart, Line, XAxis, YAxis, CartesianGrid, 
    Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';

const TrafficGraph = ({ data }) => {
    // Process data to show flow volume over time
    const chartData = data.map((flow, index) => ({
        index,
        confidence: flow.confidence || 0,
        time: flow.time,
        isAttack: flow.label !== 'Normal' ? 1 : 0
    }));

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                    <defs>
                        <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis 
                        dataKey="time" 
                        hide 
                    />
                    <YAxis 
                        stroke="#64748b" 
                        fontSize={12} 
                        tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                    />
                    <Tooltip 
                        contentStyle={{ 
                            backgroundColor: 'rgba(255,255,255,0.9)', 
                            border: '1px solid rgba(0,0,0,0.1)',
                            borderRadius: '8px',
                            color: '#0f172a'
                        }}
                    />
                    <Area 
                        type="monotone" 
                        dataKey="confidence" 
                        stroke="#38bdf8" 
                        strokeWidth={3}
                        fillOpacity={1} 
                        fill="url(#colorConf)" 
                        animationDuration={500}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TrafficGraph;
