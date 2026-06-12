import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { PieChart as PieChartIcon } from 'lucide-react';

const COLORS = ['#38bdf8', '#fbbf24', '#f87171', '#34d399', '#a78bfa'];

const ProtocolChart = ({ flows }) => {
    // Process data to count protocols
    const chartData = useMemo(() => {
        const counts = {};
        flows.forEach(flow => {
            const proto = (flow.proto || 'unknown').toUpperCase();
            counts[proto] = (counts[proto] || 0) + 1;
        });

        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }, [flows]);

    return (
        <div className="glass-card p-4 h-full flex flex-col">
            <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-slate-300 border-b border-slate-800 pb-2 uppercase tracking-wide">
                <PieChartIcon className="text-sky-500" size={16}/> Protocol Distribution
            </h2>
            <div className="flex-1 w-full relative">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
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
                            <Legend verticalAlign="bottom" height={36} iconType="circle" />
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

export default ProtocolChart;
