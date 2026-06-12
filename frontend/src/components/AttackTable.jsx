import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Activity, ShieldAlert, Cpu } from 'lucide-react';

const AttackTable = ({ alerts }) => {
    const [expandedRow, setExpandedRow] = useState(null);

    const toggleRow = (idx) => {
        if (expandedRow === idx) {
            setExpandedRow(null);
        } else {
            setExpandedRow(idx);
        }
    };

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="text-slate-600 text-xs uppercase tracking-wider border-b border-black/5">
                        <th className="pb-4 font-medium w-8"></th>
                        <th className="pb-4 font-medium">Timestamp</th>
                        <th className="pb-4 font-medium">Classification</th>
                        <th className="pb-4 font-medium">Source IP</th>
                        <th className="pb-4 font-medium">Destination IP</th>
                        <th className="pb-4 font-medium">Service</th>
                        <th className="pb-4 font-medium text-right">Confidence</th>
                    </tr>
                </thead>
                <tbody className="text-sm">
                    {alerts.map((alert, idx) => (
                        <React.Fragment key={idx}>
                            <tr 
                                onClick={() => toggleRow(idx)}
                                className="border-b border-black/5 hover:bg-black/5 transition-colors cursor-pointer"
                            >
                                <td className="py-4 text-slate-600">
                                    {expandedRow === idx ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                                </td>
                                <td className="py-4 text-slate-600 font-mono text-xs">{alert?.timestamp || 'N/A'}</td>
                                <td className="py-4">
                                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                                        alert?.label === 'Normal' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
                                    }`}>
                                        {alert?.label || 'Unknown'}
                                    </span>
                                </td>
                                <td className="py-4 font-mono text-slate-700">{alert?.src_ip || 'N/A'}</td>
                                <td className="py-4 font-mono text-slate-700">{alert?.dst_ip || 'N/A'}</td>
                                <td className="py-4 uppercase text-[10px] tracking-widest text-slate-600">{alert?.service || 'N/A'}</td>
                                <td className="py-4 text-right font-bold text-sky-400">
                                    {((alert?.confidence || 0) * 100).toFixed(1)}%
                                </td>
                            </tr>
                            {expandedRow === idx && (
                                <tr className="bg-slate-100/50 border-b border-black/5">
                                    <td colSpan="7" className="p-4">
                                        <div className="grid grid-cols-3 gap-6 text-xs text-slate-600">
                                            <div>
                                                <h4 className="flex items-center gap-1 font-bold text-slate-700 mb-2 border-b border-black/10 pb-1">
                                                    <Cpu size={14} className="text-sky-500" /> ML Features
                                                </h4>
                                                <ul className="space-y-1 font-mono">
                                                    <li><span className="text-slate-600">Duration:</span> {alert?.duration?.toFixed(4) || 0}s</li>
                                                    <li><span className="text-slate-600">Src Bytes:</span> {alert?.sbytes || 0}</li>
                                                    <li><span className="text-slate-600">Dst Bytes:</span> {alert?.dbytes || 0}</li>
                                                    <li><span className="text-slate-600">State:</span> {alert?.state || '-'}</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <h4 className="flex items-center gap-1 font-bold text-slate-700 mb-2 border-b border-black/10 pb-1">
                                                    <Activity size={14} className="text-purple-500" /> Payload Data
                                                </h4>
                                                <div className="bg-slate-200/50 p-2 rounded border border-black/5 font-mono text-[10px] text-slate-600 overflow-x-auto whitespace-pre-wrap">
                                                    {`Protocol: ${(alert?.proto || 'UNKNOWN').toUpperCase()}
Service: ${(alert?.service || 'UNKNOWN').toUpperCase()}
[Encrypted/Truncated Payload Frame...]`}
                                                </div>
                                            </div>
                                            <div>
                                                <h4 className="flex items-center gap-1 font-bold text-slate-700 mb-2 border-b border-black/10 pb-1">
                                                    <ShieldAlert size={14} className="text-emerald-500" /> System Action
                                                </h4>
                                                <div className="space-y-1">
                                                    <p><span className="text-slate-600">Rule Triggered:</span> {alert?.label === 'Normal' ? 'Traffic Logging' : `CNN-LSTM Anomaly: ${alert?.label}`}</p>
                                                    <p>
                                                        <span className="text-slate-600">Response:</span>{' '}
                                                        {alert?.label === 'Normal' ? (
                                                            <span className="text-emerald-400">Monitored</span>
                                                        ) : (
                                                            <span className="text-amber-500">Alerted & Logged</span>
                                                        )}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    ))}
                </tbody>
            </table>
            {alerts.length === 0 && (
                <div className="py-12 text-center text-slate-600">
                    No detection history available.
                </div>
            )}
        </div>
    );
};

export default AttackTable;
