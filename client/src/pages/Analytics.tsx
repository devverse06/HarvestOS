import React, { useEffect, useState } from 'react';
import { getAnalyticsSummary } from '../services/api';

export default function Analytics() {
    const [summary, setSummary] = useState<any>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        getAnalyticsSummary().then(setSummary).catch((err) => setError(err.message));
    }, []);

    return <div className="flex-1 overflow-auto p-6 absolute inset-0 bg-[#F8FAFC]"><div className="max-w-6xl mx-auto"><div className="mb-6"><h1 className="text-2xl font-semibold text-slate-900">Operational Analytics</h1><p className="text-sm text-slate-500 mt-1">Aggregates calculated from PostgreSQL records.</p></div>{error && <p className="text-sm text-red-600">{error}</p>}{summary && <><div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"><div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Procurement volume</p><p className="text-2xl font-semibold">{summary.procurement_volume_tons.toFixed(2)} t</p></div><div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Available inventory</p><p className="text-2xl font-semibold">{summary.inventory_available_tons.toFixed(2)} t</p></div><div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Reserved inventory</p><p className="text-2xl font-semibold">{summary.inventory_reserved_tons.toFixed(2)} t</p></div></div><div className="grid grid-cols-1 md:grid-cols-2 gap-6"><div className="bg-white border border-slate-200 rounded-lg p-5"><h2 className="font-semibold mb-3">Orders by status</h2>{Object.entries(summary.orders_by_status).map(([status, count]) => <div key={status} className="flex justify-between py-2 border-b border-slate-100 text-sm"><span>{status}</span><strong>{String(count)}</strong></div>)}</div><div className="bg-white border border-slate-200 rounded-lg p-5"><h2 className="font-semibold mb-3">Shipments by status</h2>{Object.entries(summary.shipments_by_status).map(([status, count]) => <div key={status} className="flex justify-between py-2 border-b border-slate-100 text-sm"><span>{status}</span><strong>{String(count)}</strong></div>)}</div></div></>}</div></div>;
}
