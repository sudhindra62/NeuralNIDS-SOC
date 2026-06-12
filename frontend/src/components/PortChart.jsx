import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MonitorDot } from 'lucide-react';

const PortChart = ({ flows }) => {
    // Process data to count destination ports
    const chartData = useMemo(() => {
        const counts = {};
        flows.forEach(flow => {
            if (flow.dst_port) {
                const port = `Port ${flow.dst_port}`;
                counts[port] = (counts[port] || 0) + 1;
            }
        });

        return Object.entries(counts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 5); // top 5 ports
    }, [flows]);

    return (
        <div className="glass-card p-4 h-full flex flex-col">
            <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-slate-300 border-b border-slate-800 pb-2 uppercase tracking-wide">
                <MonitorDot className="text-purple-500" size={16}/> Top Target Ports
            </h2>
            <div className="flex-1 w-full relative">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={chartData}
                            layout="vertical"
                            margin={{ top: 5, right: 30, left: 30, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                            <XAxis type="number" hide />
                            <YAxis 
                                dataKey="name" 
                                type="category" 
                                axisLine={false}
                                tickLine={false}
                                stroke="#64748b"
                                width={65}
                            />
                            <Tooltip 
                                cursor={{fill: 'rgba(255,255,255,0.05)'}}
                                contentStyle={{ 
                                    backgroundColor: 'rgba(255,255,255,0.9)', 
                                    border: '1px solid rgba(0,0,0,0.1)',
                                    borderRadius: '8px',
                                    color: '#0f172a'
                                }}
                            />
                            <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={20} />
                        </BarChart>
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

export default PortChart;
