import React, { useMemo } from 'react';
import { ShieldAlert } from 'lucide-react';

const TopAttackers = ({ alerts }) => {
    const topIps = useMemo(() => {
        const counts = {};
        alerts.forEach(alert => {
            if (alert.src_ip) {
                counts[alert.src_ip] = (counts[alert.src_ip] || 0) + 1;
            }
        });

        return Object.entries(counts)
            .map(([ip, count]) => ({ ip, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
    }, [alerts]);

    return (
        <div className="glass-card p-4 h-full flex flex-col">
            <h2 className="text-sm font-bold mb-3 flex items-center gap-2 text-slate-700 border-b border-slate-200 pb-2 uppercase tracking-wide">
                <ShieldAlert className="text-red-500" size={16}/> Top Attacking IPs
            </h2>
            <div className="flex-1">
                {topIps.length > 0 ? (
                    <div className="space-y-3">
                        {topIps.map((item, idx) => (
                            <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-black/5 border border-black/10">
                                <div className="flex items-center gap-3">
                                    <span className="text-slate-600 font-bold text-lg w-4">{idx + 1}.</span>
                                    <span className="font-mono text-sky-600 font-medium">{item.ip}</span>
                                </div>
                                <div className="px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-bold">
                                    {item.count} Alerts
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="h-full flex items-center justify-center text-slate-600">
                        No attack data available.
                    </div>
                )}
            </div>
        </div>
    );
};

export default TopAttackers;
