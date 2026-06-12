import React, { useState, useEffect } from 'react';
import { wsManager } from '../services/websocket';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { getAlerts, getStats, getFlows, clearData } from '../services/api';
import LiveAlerts from './LiveAlerts';
import AttackTable from './AttackTable';
import TrafficGraph from './TrafficGraph';
import ProtocolChart from './ProtocolChart';
import ServiceChart from './ServiceChart';
import StateChart from './StateChart';
import PortChart from './PortChart';
import TopAttackers from './TopAttackers';
import BandwidthGraph from './BandwidthGraph';
import { Shield, Activity, AlertTriangle, Database, Network, Server, Wifi, RefreshCw, Download } from 'lucide-react';

const Dashboard = () => {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState({ total_flows: 0, attacks: 0, normal: 0 });
    const [recentFlows, setRecentFlows] = useState([]);
    const [wsStatus, setWsStatus] = useState('Connecting...');
    const [loading, setLoading] = useState(true);

    const initData = async () => {
        try {
            const [initialAlerts, initialStats, initialFlows] = await Promise.all([
                getAlerts(),
                getStats(),
                getFlows()
            ]);
            setAlerts(initialAlerts || []);
            setStats(initialStats || { total_flows: 0, attacks: 0, normal: 0 });
            if (initialFlows && initialFlows.length > 0) {
                setRecentFlows(initialFlows.map(f => ({
                    ...f,
                    time: f.timestamp ? f.timestamp.split(' ')[1] : new Date().toLocaleTimeString()
                })));
            } else {
                setRecentFlows([]);
            }
        } catch (err) {
            console.error("Initialization failed:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = async () => {
        await clearData();
        setAlerts([]);
        setStats({ total_flows: 0, attacks: 0, normal: 0 });
        setRecentFlows([]);
        await initData();
    };

    const handleDownloadPDF = async () => {
        try {
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pageWidth = pdf.internal.pageSize.getWidth();
            
            // Header
            pdf.setFontSize(22);
            pdf.setTextColor(14, 165, 233); // Sky-500
            pdf.text("AEGISGAN Security Analysis Report", pageWidth / 2, 20, { align: 'center' });
            
            pdf.setFontSize(10);
            pdf.setTextColor(100);
            pdf.text(`Generated on: ${new Date().toLocaleString()}`, pageWidth / 2, 28, { align: 'center' });
            
            // Summary Statistics
            pdf.setFontSize(14);
            pdf.setTextColor(15, 23, 42); // slate-900
            pdf.text("1. Executive Summary", 14, 40);
            
            pdf.setFontSize(11);
            pdf.setTextColor(71, 85, 105); // slate-600
            pdf.text(`Total Flows Analyzed: ${stats.total_flows}`, 20, 50);
            pdf.text(`Normal Traffic: ${stats.normal}`, 20, 58);
            pdf.text(`Attacks Detected: ${stats.attacks}`, 20, 66);
            
            const health = stats.total_flows > 0 ? ((stats.normal / stats.total_flows) * 100).toFixed(1) + '%' : '100%';
            pdf.text(`Overall Traffic Health: ${health}`, 20, 74);
            
            const avgConfidence = alerts.length > 0 
                ? (alerts.reduce((acc, a) => acc + (a.confidence || 0), 0) / alerts.length * 100).toFixed(1) + '%' 
                : 'N/A';
            pdf.text(`Average Threat Confidence: ${avgConfidence}`, 20, 82);
            
            // 2. Traffic Distribution
            pdf.setFontSize(14);
            pdf.setTextColor(15, 23, 42);
            pdf.text("2. Traffic Distribution", 14, 98);
            
            const protoCounts = {};
            const serviceCounts = {};
            const portCounts = {};
            
            recentFlows.forEach(flow => {
                const proto = (flow.proto || 'unknown').toUpperCase();
                protoCounts[proto] = (protoCounts[proto] || 0) + 1;
                
                const service = (flow.service && flow.service !== '-') ? flow.service.toUpperCase() : 'OTHER';
                serviceCounts[service] = (serviceCounts[service] || 0) + 1;
                
                if (flow.dst_port) {
                    portCounts[flow.dst_port] = (portCounts[flow.dst_port] || 0) + 1;
                }
            });
            
            const protoData = Object.entries(protoCounts).map(([k, v]) => [k, v.toString()]).sort((a,b) => b[1]-a[1]).slice(0, 5);
            const serviceData = Object.entries(serviceCounts).map(([k, v]) => [k, v.toString()]).sort((a,b) => b[1]-a[1]).slice(0, 5);
            const portData = Object.entries(portCounts).map(([k, v]) => [k, v.toString()]).sort((a,b) => b[1]-a[1]).slice(0, 5);
            
            autoTable(pdf, {
                startY: 104,
                head: [['Protocol', 'Count']],
                body: protoData.length ? protoData : [['N/A', '0']],
                theme: 'grid',
                tableWidth: 50,
                margin: { left: 14 }
            });
            
            autoTable(pdf, {
                startY: 104,
                head: [['Service', 'Count']],
                body: serviceData.length ? serviceData : [['N/A', '0']],
                theme: 'grid',
                tableWidth: 50,
                margin: { left: 74 }
            });
            
            autoTable(pdf, {
                startY: 104,
                head: [['Dest Port', 'Count']],
                body: portData.length ? portData : [['N/A', '0']],
                theme: 'grid',
                tableWidth: 50,
                margin: { left: 134 }
            });
            
            const maxFinalY1 = Math.max(
                pdf.previousAutoTable ? pdf.previousAutoTable.finalY : 148,
                104 + (Math.max(protoData.length, serviceData.length, portData.length) + 1) * 8
            );
            
            // 3. Threat Forensics & Intelligence
            const section3Y = maxFinalY1 + 15;
            pdf.setFontSize(14);
            pdf.setTextColor(15, 23, 42);
            pdf.text("3. Threat Forensics & Intelligence", 14, section3Y);
            
            const attackerCounts = {};
            const classCounts = {};
            
            alerts.forEach(alert => {
                if (alert.src_ip) {
                    attackerCounts[alert.src_ip] = (attackerCounts[alert.src_ip] || 0) + 1;
                }
                const label = alert.label || alert.prediction || 'Unknown';
                classCounts[label] = (classCounts[label] || 0) + 1;
            });
            
            const topAttackers = Object.entries(attackerCounts)
                .map(([ip, count]) => [ip, count.toString()])
                .sort((a, b) => parseInt(b[1]) - parseInt(a[1]))
                .slice(0, 5);
                
            const classData = Object.entries(classCounts)
                .map(([cls, count]) => [cls, count.toString()])
                .sort((a, b) => parseInt(b[1]) - parseInt(a[1]))
                .slice(0, 5);

            autoTable(pdf, {
                startY: section3Y + 6,
                head: [['Top Source IPs', 'Alert Count']],
                body: topAttackers.length ? topAttackers : [['N/A', '0']],
                theme: 'grid',
                headStyles: { fillColor: [220, 38, 38] }, // Red
                tableWidth: 80,
                margin: { left: 14 }
            });
            
            autoTable(pdf, {
                startY: section3Y + 6,
                head: [['Threat Classification', 'Count']],
                body: classData.length ? classData : [['N/A', '0']],
                theme: 'grid',
                headStyles: { fillColor: [15, 23, 42] }, // Slate-900
                tableWidth: 80,
                margin: { left: 104 }
            });
            
            // 4. Advanced Threat Alerts
            const section4Y = (pdf.previousAutoTable ? pdf.previousAutoTable.finalY : section3Y + 40) + 15;
            
            pdf.setFontSize(14);
            pdf.setTextColor(15, 23, 42);
            pdf.text("4. Advanced Threat Alerts (Up to 50)", 14, section4Y);
            
            const alertData = alerts.slice(0, 50).map(alert => [
                alert.timestamp ? alert.timestamp.split(' ')[1] : new Date().toLocaleTimeString(),
                alert.label || alert.prediction || 'UNKNOWN',
                alert.src_ip || 'N/A',
                alert.dst_ip || 'N/A',
                alert.confidence ? (alert.confidence * 100).toFixed(1) + '%' : '-',
                alert.duration ? alert.duration.toFixed(2) + 's' : '-',
                alert.sbytes || '0',
                alert.dbytes || '0',
                alert.state || '-'
            ]);
            
            if (alertData.length > 0) {
                autoTable(pdf, {
                    startY: section4Y + 6,
                    head: [['Time', 'Class', 'Src IP', 'Dst IP', 'Conf', 'Dur', 'SrcB', 'DstB', 'State']],
                    body: alertData,
                    theme: 'striped',
                    headStyles: { fillColor: [220, 38, 38] },
                    styles: { fontSize: 8, cellPadding: 1.5 },
                    margin: { left: 14, right: 14 }
                });
            } else {
                pdf.setFontSize(11);
                pdf.setTextColor(71, 85, 105);
                pdf.text("No recent threats detected.", 14, section4Y + 10);
            }

            // 5. Normal Traffic Sample
            const section5Y = alertData.length > 0 ? pdf.lastAutoTable.finalY + 15 : section4Y + 20;
            pdf.setFontSize(14);
            pdf.setTextColor(15, 23, 42);
            pdf.text("5. Recent Normal Traffic Sample", 14, section5Y);

            const normalFlows = recentFlows.filter(f => !f.prediction || f.prediction === 'Normal' || f.prediction === 'normal').slice(0, 20);
            const normalData = normalFlows.map(f => [
                f.time || f.timestamp || new Date().toLocaleTimeString(),
                f.src_ip || (f.id ? f.id.orig_h : null) || 'N/A',
                f.dest_ip || f.dst_ip || (f.id ? f.id.resp_h : null) || 'N/A',
                f.proto || 'N/A',
                f.service || 'N/A'
            ]);

            if (normalData.length > 0) {
                autoTable(pdf, {
                    startY: section5Y + 6,
                    head: [['Timestamp', 'Source IP', 'Dest IP', 'Protocol', 'Service']],
                    body: normalData,
                    theme: 'striped',
                    headStyles: { fillColor: [16, 185, 129] }, // Emerald
                    styles: { fontSize: 9 },
                    margin: { left: 14, right: 14 }
                });
            } else {
                pdf.setFontSize(11);
                pdf.setTextColor(71, 85, 105);
                pdf.text("No recent normal traffic available.", 14, section5Y + 10);
            }
            
            pdf.save('AegisGAN_Analysis_Report.pdf');
        } catch (err) {
            console.error("PDF generation failed:", err);
        }
    };

    useEffect(() => {
        // Initial Fetch
        initData();

        // Subscribe to global WebSocket stream
        const unsubscribe = wsManager.subscribe((message) => {
            if (!message || !message.type) return;

            if (message.type === 'WS_STATUS') {
                setWsStatus(message.data);
                return;
            }

            if (message.type === 'ALERT') {
                setAlerts((prev) => [message.data, ...prev].slice(0, 50));
                setStats((prev) => ({
                    ...prev,
                    attacks: (prev.attacks || 0) + 1,
                    total_flows: (prev.total_flows || 0) + 1
                }));
            } else if (message.type === 'FLOW') {
                setStats((prev) => ({
                    ...prev,
                    normal: (prev.normal || 0) + 1,
                    total_flows: (prev.total_flows || 0) + 1
                }));
            }

            if (message.data) {
                setRecentFlows((prev) => [...prev, { ...message.data, time: new Date().toLocaleTimeString() }].slice(-50));
            }
        });

        return () => {
            unsubscribe();
        };
    }, []);

    return (
        <div className="bg-slate-50 text-slate-900 min-h-screen overflow-x-auto custom-scrollbar">
            {/* The min-w-[1400px] guarantees the layout NEVER wraps or stacks vertically */}
            <div id="dashboard-content" className="p-6 min-w-[1400px] max-w-[1920px] mx-auto space-y-6">

                {/* 1. HEADER BAR (100% width, 70px) */}
                <header className="flex justify-between items-center h-[70px]">
                    <div className="flex items-center">
                        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                            AEGISGAN Dashboard
                        </h1>
                    </div>
                    <div className="flex items-center gap-4">
                        <button 
                            onClick={handleDownloadPDF}
                            className="px-4 py-2 glass-card text-xs font-bold text-slate-700 flex items-center gap-2 hover:bg-slate-200 transition-colors cursor-pointer"
                        >
                            <Download size={14} className="text-sky-500" /> Download PDF
                        </button>
                        <div className="px-4 py-2 glass-card flex items-center gap-3 border-emerald-500/30 bg-emerald-500/10">
                            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.8)]"></span>
                            <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider">System Live</span>
                        </div>
                        <div className="px-4 py-2 glass-card text-xs font-mono text-slate-500 flex items-center gap-2">
                            <Activity size={14} className="text-sky-500" /> Sync: Real-time
                        </div>
                    </div>
                </header>

                {/* TOP SECTION: SPLIT LEFT (Charts) and RIGHT (KPIs) */}
                <div className="grid grid-cols-12 gap-6">

                    {/* LEFT PART: CHARTS AND GRAPHS (9 columns) */}
                    <div className="col-span-9 space-y-6">
                        <div className="grid grid-cols-3 gap-6">
                            {/* Row 1 */}
                            <div className="glass-card p-4 flex flex-col h-[280px] col-span-1">
                                <h2 className="text-xs font-bold mb-2 flex items-center gap-2 text-slate-500 border-b border-slate-200/80 pb-2 uppercase tracking-widest">
                                    <Activity className="text-sky-500" size={14} /> Threat Confidence
                                </h2>
                                <div className="flex-1 min-h-0"><TrafficGraph data={recentFlows} /></div>
                            </div>
                            <div className="glass-card p-4 flex flex-col h-[280px] col-span-1">
                                <h2 className="text-xs font-bold mb-2 flex items-center gap-2 text-slate-500 border-b border-slate-200/80 pb-2 uppercase tracking-widest">
                                    <Network className="text-emerald-500" size={14} /> Bandwidth
                                </h2>
                                <div className="flex-1 min-h-0"><BandwidthGraph data={recentFlows} /></div>
                            </div>
                            <div className="h-[280px] col-span-1">
                                <ProtocolChart flows={recentFlows} />
                            </div>

                            {/* Row 2 */}
                            <div className="h-[280px] col-span-1">
                                <ServiceChart flows={recentFlows} />
                            </div>
                            <div className="h-[280px] col-span-1">
                                <StateChart flows={recentFlows} />
                            </div>
                            <div className="h-[280px] col-span-1">
                                <PortChart flows={recentFlows} />
                            </div>
                        </div>
                    </div>

                    {/* RIGHT PART: NUMBERING THINGS (KPIs) (3 columns) */}
                    <div className="col-span-3 space-y-6 flex flex-col">
                        <StatCard title="Total Flows" value={stats.total_flows} icon={<Database size={28} />} color="var(--primary)" />
                        <StatCard title="Attacks Detected" value={stats.attacks} icon={<AlertTriangle size={28} />} color="var(--danger)" />
                        <StatCard title="Normal Traffic" value={stats.normal} icon={<Shield size={28} />} color="var(--success)" />
                        <StatCard 
                            title="Traffic Health" 
                            value={stats.total_flows > 0 ? ((stats.normal / stats.total_flows) * 100).toFixed(1) + '%' : '100%'} 
                            icon={<Activity size={28} />} 
                            color="var(--warning)" 
                        />
                    </div>

                </div>

                {/* BOTTOM SECTION: SCORING / THREATS / HISTORY */}
                <div className="space-y-6">

                    {/* THREAT INTELLIGENCE SECTION */}
                    <div className="grid grid-cols-12 gap-6 h-[350px]">
                        {/* A) Top Attacking IPs */}
                        <div className="col-span-4 h-full">
                            <TopAttackers alerts={alerts} />
                        </div>
                        {/* B) Live Threat Feed */}
                        <div className="col-span-8 h-full">
                            <div className="glass-card p-4 h-full flex flex-col border-t-2 border-t-red-500/50">
                                <h2 className="text-xs font-bold mb-3 flex items-center gap-2 text-red-600 border-b border-slate-200/80 pb-2 uppercase tracking-widest shrink-0">
                                    <AlertTriangle size={14} /> Live Threat Feed
                                </h2>
                                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                    <LiveAlerts alerts={alerts.slice(0, 15)} />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* FORENSIC DETECTION HISTORY */}
                    <div className="h-[400px]">
                        <div className="glass-card p-4 h-full flex flex-col">
                            <h2 className="text-xs font-bold mb-3 flex items-center gap-2 text-slate-500 border-b border-slate-200/80 pb-2 uppercase tracking-widest shrink-0">
                                Forensic Detection History
                            </h2>
                            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                <AttackTable alerts={alerts} />
                            </div>
                        </div>
                    </div>

                    {/* SYSTEM FOOTER STATUS BAR */}
                    <div className="h-[60px]">
                        <footer className="glass-card px-6 flex items-center gap-8 text-xs font-mono text-slate-600 h-full border-t border-slate-200">
                            <div className="flex items-center gap-2">
                                <Wifi size={14} className={wsStatus === 'Connected' ? "text-emerald-500" : "text-amber-500"} />
                                <span>WebSocket: <strong className="text-slate-800">{wsStatus}</strong></span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Server size={14} className="text-purple-500" />
                                <span>ML: <strong className="text-slate-800">Online</strong></span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Database size={14} className={wsStatus === 'Connected' ? "text-sky-500" : "text-slate-400"} />
                                <span>Logs: <strong className="text-slate-800">{wsStatus === 'Connected' ? 'Active' : 'Waiting'}</strong></span>
                            </div>
                            <div className="flex items-center gap-2 ml-auto">
                                <span className="text-slate-500 font-bold">Core v1.1.0</span>
                            </div>
                        </footer>
                    </div>

                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, icon, color }) => (
    <div className="glass-card p-6 flex-1 flex flex-col justify-center border-l-4" style={{ borderLeftColor: color }}>
        <div className="flex items-center justify-between w-full">
            <div>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mb-2">{title}</p>
                <p className="text-4xl font-bold text-slate-900">{value}</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-100 border border-black/5" style={{ color: color }}>
                {icon}
            </div>
        </div>
    </div>
);

export default Dashboard;
