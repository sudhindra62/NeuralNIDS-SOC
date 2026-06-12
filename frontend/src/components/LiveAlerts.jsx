import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LiveAlerts = ({ alerts }) => {
    return (
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
            <AnimatePresence initial={false}>
                {alerts.map((alert, idx) => (
                    <motion.div
                        key={alert.timestamp + idx}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 shadow-sm"
                    >
                        <div className="flex justify-between items-start mb-1">
                            <span className="text-sm font-bold text-red-500 uppercase tracking-wider">
                                {alert.label}
                            </span>
                            <span className="text-[10px] text-slate-600 font-mono">
                                {alert.timestamp ? alert.timestamp.split(' ')[1] : 'N/A'}
                            </span>
                        </div>
                        <div className="text-sm font-mono text-slate-700 font-medium">
                            {alert.src_ip} <span className="text-red-600">→</span> {alert.dst_ip}
                        </div>
                        <div className="mt-2 flex items-center gap-2">
                            <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-red-500" 
                                    style={{ width: `${alert.confidence * 100}%` }}
                                ></div>
                            </div>
                            <span className="text-[10px] text-slate-600 font-medium">
                                {(alert.confidence * 100).toFixed(0)}% Conf.
                            </span>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
            {alerts.length === 0 && (
                <div className="text-center py-12 text-slate-600">
                    <p>No active threats detected.</p>
                    <p className="text-xs mt-2">Listening for incoming logs...</p>
                </div>
            )}
        </div>
    );
};

export default LiveAlerts;
