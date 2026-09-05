import React, { useState } from 'react';
import { getTraceability } from '../services/api';

export default function Traceability() {
    const [lotId, setLotId] = useState('');
    const [chain, setChain] = useState<any>(null);
    const [error, setError] = useState('');

    const search = async (event: React.FormEvent) => {
        event.preventDefault();
        setError('');
        try {
            setChain(await getTraceability(lotId));
        } catch (err: any) {
            setChain(null);
            setError(err.message);
        }
    };

    return (
        <div className="flex-1 overflow-auto p-6 absolute inset-0 bg-[#F8FAFC]"><div className="max-w-5xl mx-auto"><div className="mb-6"><h1 className="text-2xl font-semibold text-slate-900">Traceability</h1><p className="text-sm text-slate-500 mt-1">Follow a harvest lot through quality, inventory, orders, and shipments.</p></div><form onSubmit={search} className="flex gap-3 mb-6"><input required value={lotId} onChange={(event) => setLotId(event.target.value)} placeholder="Harvest lot ID, e.g. LOT-001" className="flex-1 border border-slate-300 rounded-md px-3 py-2 text-sm" /><button className="bg-slate-900 text-white rounded-md px-5 py-2 text-sm">Trace lot</button></form>{error && <p className="text-sm text-red-600 mb-4">{error}</p>}{chain && <div className="grid grid-cols-1 md:grid-cols-3 gap-4"><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Farm</h2><p>{chain.farm.id}</p><p className="text-sm text-slate-500">{chain.farm.name}</p></section><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Harvest Lot</h2><p>{chain.harvest_lot.id}</p><p className="text-sm text-slate-500">{chain.harvest_lot.weight_tons} tons, {chain.harvest_lot.status}</p></section><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Quality</h2>{chain.quality_inspections.map((inspection: any) => <p key={inspection.id}>{inspection.id}: {inspection.passed ? 'Passed' : 'Failed'}</p>)}</section><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Inventory</h2>{chain.inventory_batches.map((batch: any) => <p key={batch.id}>{batch.id}: {batch.available_tons.toFixed(2)} available</p>)}</section><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Orders</h2>{chain.orders.map((order: any) => <p key={order.id}>{order.id}: {order.status}</p>)}</section><section className="bg-white border border-slate-200 rounded-lg p-4"><h2 className="font-semibold mb-3">Shipments</h2>{chain.shipments.map((shipment: any) => <p key={shipment.id}>{shipment.id}: {shipment.status}</p>)}</section></div>}</div></div>
    );
}
