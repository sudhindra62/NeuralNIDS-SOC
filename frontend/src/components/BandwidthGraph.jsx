import React from 'react';
import { 
    AreaChart, Area, XAxis, YAxis, CartesianGrid, 
    Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity } from 'lucide-react';

const BandwidthGraph = ({ data }) => {
    // Process data to show sbytes and dbytes over time
    const chartData = data.map((flow, index) => ({
        index,
        time: flow.time,
        sbytes: flow.sbytes || 0,
        dbytes: flow.dbytes || 0
    }));

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                    <defs>
                        <linearGradient id="colorSbytes" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#34d399" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#34d399" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorDbytes" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#a78bfa" stopOpacity={0}/>
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="time" hide />
                    <YAxis 
                        stroke="#64748b" 
                        fontSize={12} 
                        tickFormatter={(val) => {
                            if (val >= 1000000) return `${(val / 1000000).toFixed(1)} MB`;
                            if (val >= 1000) return `${(val / 1000).toFixed(1)} KB`;
                            return `${val} B`;
                        }}
                    />
                    <Tooltip 
                        contentStyle={{ 
                            backgroundColor: 'rgba(255,255,255,0.9)', 
                            border: '1px solid rgba(0,0,0,0.1)',
                            borderRadius: '8px',
                            color: '#0f172a'
                        }}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Area 
                        type="monotone" 
                        dataKey="sbytes" 
                        name="Source Bytes"
                        stroke="#34d399" 
                        strokeWidth={2}
                        fillOpacity={1} 
                        fill="url(#colorSbytes)" 
                        animationDuration={500}
                    />
                    <Area 
                        type="monotone" 
                        dataKey="dbytes" 
                        name="Destination Bytes"
                        stroke="#a78bfa" 
                        strokeWidth={2}
                        fillOpacity={1} 
                        fill="url(#colorDbytes)" 
                        animationDuration={500}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default BandwidthGraph;
