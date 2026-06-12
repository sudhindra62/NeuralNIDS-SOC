import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Link2 } from 'lucide-react';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const StateChart = ({ flows }) => {
    // Process data to count connection states
    const chartData = useMemo(() => {
        const counts = {};
        flows.forEach(flow => {
            const state = (flow.state && flow.state !== '-') ? flow.state.toUpperCase() : 'OTHER';
            counts[state] = (counts[state] || 0) + 1;
        });

        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }, [flows]);

    return (
        <div className="glass-card p-4 h-full flex flex-col">
            <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-slate-300 border-b border-slate-800 pb-2 uppercase tracking-wide">
                <Link2 className="text-blue-500" size={16}/> Connection States
            </h2>
            <div className="flex-1 w-full relative">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={80}
                                paddingAngle={2}
                                dataKey="value"
                                stroke="none"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip 
                                contentStyle={{ 
                                    backgroundColor: 'rgba(255,255,255,0.9)', 
                                    border: '1px solid rgba(0,0,0,0.1)',
                                    borderRadius: '8px',
                                    color: '#0f172a'
                                }}
                            />
                            <Legend verticalAlign="bottom" height={36} iconType="square" />
                        </PieChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-slate-500">
                        Waiting for traffic...
                    </div>
                )}
            </div>
        </div>
    );
};

export default StateChart;
